#!/usr/bin/env python3
"""Classify Catalyst history against Cardano Vision 2030 and publish rollups.

The classifier is deterministic and intentionally conservative. Challenge names
take precedence; proposal text is used for broad/open challenges. Every proposal
is retained in the audit CSV, including low-confidence classifications.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

Json = dict[str, Any]

FUND_YEARS = {
    1: 2020,
    2: 2021,
    3: 2021,
    4: 2021,
    5: 2021,
    6: 2021,
    7: 2022,
    8: 2022,
    9: 2022,
    10: 2023,
    11: 2024,
    12: 2024,
    13: 2024,
    14: 2025,
    15: 2026,
}

PILLARS: dict[str, Json] = {
    "P1": {
        "name": "Infrastructure & Research Excellence",
        "description": "Protocol, scaling, interoperability, security, resilience, and research.",
    },
    "P2": {
        "name": "Adoption & Utility",
        "description": (
            "Useful products, high-value verticals, experience, identity, "
            "and developer experience."
        ),
    },
    "P3": {
        "name": "Governance",
        "description": (
            "Participation, decision systems, treasury processes, auditability, and policy."
        ),
    },
    "P4": {
        "name": "Community & Ecosystem Growth",
        "description": (
            "Talent, education, outreach, regional communities, and ecosystem narrative."
        ),
    },
    "P5": {
        "name": "Ecosystem Sustainability & Resilience",
        "description": (
            "Treasury economics, SPO incentives, decentralization, and long-term network health."
        ),
    },
    "PX": {
        "name": "Ambiguous / cross-pillar",
        "description": "Insufficient evidence for one defensible primary pillar.",
    },
}

SCENARIO_2027: dict[str, Json] = {
    "P1": {
        "allocation_percent": 20,
        "rationale": "Strategic floor for the framework's technical foundation.",
        "subcategories": {
            "L1/L2 scalability": 7,
            "Security and resilience": 5,
            "Interoperability and ZK": 5,
            "Research and client diversity": 3,
        },
    },
    "P2": {
        "allocation_percent": 45,
        "rationale": "Largest envelope, preserving the dominant historical demand signal.",
        "subcategories": {
            "High-value verticals": 15,
            "Developer experience": 10,
            "Payments, wallets, and UX": 8,
            "Identity and enterprise compliance": 7,
            "Integrations and adoption pilots": 5,
        },
    },
    "P3": {
        "allocation_percent": 10,
        "rationale": "Strategic floor for accessible governance and accountable treasury cycles.",
        "subcategories": {
            "Governance tools and access": 4,
            "Treasury seasons and accountability": 3,
            "Participation, incentives, and research": 3,
        },
    },
    "P4": {
        "allocation_percent": 15,
        "rationale": "Historical demand retained after funding the three strategic floors.",
        "subcategories": {
            "Talent and education": 5,
            "Regional and localized adoption": 4,
            "Community tooling and events": 3,
            "Ecosystem narrative and evidence": 3,
        },
    },
    "P5": {
        "allocation_percent": 10,
        "rationale": "Strategic floor for network economics and long-term resilience.",
        "subcategories": {
            "SPO roles and decentralization": 4,
            "Treasury and tokenomics": 3,
            "Network economics and L2 value return": 2,
            "Operational resilience": 1,
        },
    },
}

# Ordered, high-confidence mappings based on the proposal's original challenge.
CHALLENGE_RULES: list[tuple[str, str, str]] = [
    (
        r"catalyst systems|catalyst fund operations|distributed decision|drep|daos? "
        r"|auditability|community advisor|rapid funding|legal|lobbying",
        "P3",
        "governance-systems",
    ),
    (r"spo |stake pool|global sustainable indep", "P5", "stake-pool-resilience"),
    (
        r"scaling|cross-chain|interoperability|emerging threat|development & infrastructure",
        "P1",
        "protocol-and-infrastructure",
    ),
    (
        r"grow africa|grow east asia|grow india|grow latin|community hub|community event"
        r"|multilingual|students|onboarding|outreach|accelerator|mentors|film \+ media",
        "P4",
        "community-and-talent",
    ),
    (
        r"developer ecosystem|cardano open: developers|open source|dapps?|products"
        r"|integrations|defi|identity|prism|business solutions|nft|gamers|nation building"
        r"|metadata|migration|enterprise|use case|cardano partners"
        r"|catalyst value onboarding|coti|singularitynet|blockfrost|nmkr",
        "P2",
        "products-and-developer-experience",
    ),
]

# Text scoring handles open/miscellaneous categories. Phrases may overlap; the
# winning pillar must lead by at least two points or the row remains ambiguous.
TEXT_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "P1": {
        "protocol-and-scaling": (
            "hydra",
            "mithril",
            "ouroboros",
            "consensus",
            "layer 2",
            "scalability",
            "throughput",
            "node client",
            "sidechain",
        ),
        "security-and-research": (
            "formal methods",
            "cryptography",
            "security audit",
            "vulnerability",
            "research paper",
            "zero knowledge",
            "zk proof",
            "interoperability",
            "cross-chain",
            "bridge",
        ),
    },
    "P2": {
        "defi-and-payments": (
            "defi",
            "dex",
            "lending",
            "stablecoin",
            "payments",
            "wallet",
            "liquidity",
            "financial inclusion",
        ),
        "identity-and-enterprise": (
            "identity",
            "credential",
            "atala prism",
            "ssi",
            "supply chain",
            "traceability",
            "enterprise",
            "real world asset",
            "rwa",
        ),
        "products-and-developer-experience": (
            "dapp",
            "smart contract",
            "sdk",
            "api",
            "developer tool",
            "plutus",
            "aiken",
            "haskell",
            "marketplace",
            "gaming",
            "nft",
        ),
    },
    "P3": {
        "governance-participation": (
            "governance",
            "drep",
            "voting",
            "delegation",
            "constitutional",
            "decision making",
            "dao",
        ),
        "funding-and-accountability": (
            "catalyst",
            "proposal assessment",
            "community reviewer",
            "auditability",
            "treasury process",
            "funding mechanism",
        ),
    },
    "P4": {
        "education-and-talent": (
            "education",
            "course",
            "training",
            "student",
            "university",
            "bootcamp",
            "hackathon",
            "workshop",
            "developer onboarding",
        ),
        "community-and-regional-growth": (
            "community",
            "hub",
            "meetup",
            "event",
            "africa",
            "latam",
            "latin america",
            "east asia",
            "japan",
            "vietnam",
            "multilingual",
        ),
        "communications-and-outreach": (
            "marketing",
            "media",
            "podcast",
            "content",
            "awareness",
            "outreach",
            "ambassador",
        ),
    },
    "P5": {
        "stake-pool-resilience": (
            "stake pool",
            "spo",
            "block producer",
            "pool operator",
            "decentralization",
        ),
        "treasury-and-tokenomics": (
            "treasury management",
            "treasury yield",
            "tokenomics",
            "network economics",
            "multi-asset treasury",
            "value retention",
        ),
    },
}


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def classify(proposal: Json) -> tuple[str, str, str, str]:
    challenge = normalize(proposal.get("challenge"))
    for pattern, pillar, subcategory in CHALLENGE_RULES:
        if re.search(pattern, challenge):
            return pillar, subcategory, "high", "challenge"

    text = " ".join(
        normalize(proposal.get(field))
        for field in ("title", "summary", "problem", "solution", "definition_of_success")
    )
    scores: dict[str, int] = defaultdict(int)
    best_subcategory: dict[str, tuple[int, str]] = {}
    for pillar, groups in TEXT_RULES.items():
        for subcategory, phrases in groups.items():
            score = sum(1 for phrase in phrases if phrase in text)
            scores[pillar] += score
            if score > best_subcategory.get(pillar, (0, ""))[0]:
                best_subcategory[pillar] = (score, subcategory)
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    if ranked and ranked[0][1] >= 2:
        margin = ranked[0][1] - (ranked[1][1] if len(ranked) > 1 else 0)
        if margin >= 2:
            pillar = ranked[0][0]
            return pillar, best_subcategory[pillar][1], "medium", "proposal-text"
    return "PX", "ambiguous-or-cross-pillar", "low", "unresolved"


def is_funded(proposal: Json) -> bool:
    return proposal.get("funding_status") in {"approved", "leftover"}


def is_delivered(proposal: Json) -> bool:
    # Restrict completion to funded proposals. Some source rows carry a reused
    # completion status despite an official not-approved/over-budget outcome.
    return is_funded(proposal) and proposal.get("project_status") == "complete"


def blank_rollup(dimension: str, value: int, pillar: str, currency: str) -> Json:
    return {
        dimension: value,
        "pillar": pillar,
        "pillar_name": PILLARS[pillar]["name"],
        "currency": currency,
        "requested_proposals": 0,
        "requested_amount": 0.0,
        "funded_proposals": 0,
        "funded_amount": 0.0,
        "delivered_proposals": 0,
        "delivered_amount": 0.0,
    }


def aggregate(rows: list[Json], dimension: str) -> list[Json]:
    rollups: dict[tuple[int, str, str], Json] = {}
    for row in rows:
        value = int(row[dimension])
        key = (value, row["pillar"], row["currency"])
        record = rollups.setdefault(
            key, blank_rollup(dimension, value, row["pillar"], row["currency"])
        )
        record["requested_proposals"] += 1
        record["requested_amount"] += row["amount_requested"] or 0
        if row["funded"]:
            record["funded_proposals"] += 1
            record["funded_amount"] += row["amount_received"] or 0
        if row["delivered"]:
            record["delivered_proposals"] += 1
            record["delivered_amount"] += row["amount_received"] or 0
    return sorted(
        rollups.values(), key=lambda row: (row[dimension], row["pillar"], row["currency"])
    )


def aggregate_subcategories(rows: list[Json], dimension: str) -> list[Json]:
    rollups: dict[tuple[int, str, str, str], Json] = {}
    for row in rows:
        value = int(row[dimension])
        key = (value, row["pillar"], row["subcategory"], row["currency"])
        record = rollups.setdefault(
            key,
            {
                **blank_rollup(dimension, value, row["pillar"], row["currency"]),
                "subcategory": row["subcategory"],
            },
        )
        record["requested_proposals"] += 1
        record["requested_amount"] += row["amount_requested"] or 0
        if row["funded"]:
            record["funded_proposals"] += 1
            record["funded_amount"] += row["amount_received"] or 0
        if row["delivered"]:
            record["delivered_proposals"] += 1
            record["delivered_amount"] += row["amount_received"] or 0
    return sorted(
        rollups.values(),
        key=lambda row: (row[dimension], row["pillar"], row["subcategory"], row["currency"]),
    )


def build_2027_scenario(rows: list[Json], example_total_ada: float = 100_000_000) -> Json:
    eligible = [
        row
        for row in rows
        if 2021 <= row["year"] <= 2025 and row["funded"] and row["pillar"] in SCENARIO_2027
    ]
    funded_total = len(eligible)
    funded_counts: dict[str, int] = defaultdict(int)
    for row in eligible:
        funded_counts[row["pillar"]] += 1

    pillars: list[Json] = []
    subcategories: list[Json] = []
    for pillar, definition in SCENARIO_2027.items():
        allocation_percent = definition["allocation_percent"]
        pillars.append(
            {
                "pillar": pillar,
                "pillar_name": PILLARS[pillar]["name"],
                "historical_funded_proposals": funded_counts[pillar],
                "historical_funded_share_percent": round(
                    funded_counts[pillar] / funded_total * 100, 1
                ),
                "allocation_percent": allocation_percent,
                "example_allocation_ada": example_total_ada * allocation_percent / 100,
                "rationale": definition["rationale"],
            }
        )
        for subcategory, percent in definition["subcategories"].items():
            subcategories.append(
                {
                    "pillar": pillar,
                    "pillar_name": PILLARS[pillar]["name"],
                    "subcategory": subcategory,
                    "allocation_percent": percent,
                    "example_allocation_ada": example_total_ada * percent / 100,
                }
            )
    return {
        "label": "Hypothetical 2027 allocation",
        "currency": "ADA",
        "example_total": example_total_ada,
        "baseline_years": "2021-2025",
        "baseline_measure": "classified funded proposal count",
        "historical_funded_proposals": funded_total,
        "method": (
            "Set strategic floors of 20% for P1, 10% for P3, and 10% for P5; "
            "split the remaining 60% between P2 and P4 in their historical funded-count "
            "ratio, then round to whole percentages."
        ),
        "pillars": pillars,
        "subcategories": subcategories,
    }


def write_csv(path: Path, rows: list[Json]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def format_amount(value: float, currency: str) -> str:
    symbol = {"ADA": "₳", "USD": "$", "USDM": "USDM "}.get(currency, "")
    return f"{symbol}{value:,.0f}"


def write_markdown(path: Path, payload: Json) -> None:
    by_year = payload["by_year"]
    lines = [
        "# Cardano funding priorities through the Vision 2030 lens",
        "",
        f"Generated from the archive snapshot on {payload['meta']['source_snapshot'][:10]}. ",
        "This is a retrospective classification: Vision 2030 did not govern the earlier funds.",
        "",
        "## What the measures mean",
        "",
        "- **Requested:** every proposal and its requested amount.",
        "- **Funded:** official `approved` or `leftover` outcomes and recorded received amount.",
        "- **Delivered:** funded proposals whose archived project status is `complete`.",
        (
            "- **Delivered amount:** recorded award value of those completed proposals, "
            "not audited spend."
        ),
        "- Amounts are never converted or added across currencies.",
        "",
        "## Annual allocation history",
        "",
        (
            "| Year | Pillar | Currency | Requests | Requested | Funded | Funded amount "
            "| Delivered | Delivered amount |"
        ),
        "|---:|---|:---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in by_year:
        if row["requested_proposals"] == 0:
            continue
        requested_amount = format_amount(row["requested_amount"], row["currency"])
        funded_amount = format_amount(row["funded_amount"], row["currency"])
        delivered_amount = format_amount(row["delivered_amount"], row["currency"])
        lines.append(
            f"| {row['year']} | {row['pillar']} - {row['pillar_name']} | {row['currency']} "
            f"| {row['requested_proposals']:,} | {requested_amount} "
            f"| {row['funded_proposals']:,} | {funded_amount} "
            f"| {row['delivered_proposals']:,} | {delivered_amount} |"
        )
    scenario = payload["scenario_2027"]
    lines += [
        "",
        "## Hypothetical 2027 allocation",
        "",
        (
            "This planning scenario uses a 100 million ADA example. It is not a forecast or "
            "approved budget. Historical shares use classified funded-proposal counts from "
            f"{scenario['baseline_years']}, excluding ambiguous rows."
        ),
        "",
        scenario["method"],
        "",
        "| Pillar | Historical funded share | Proposed share | Example allocation |",
        "|---|---:|---:|---:|",
    ]
    for row in scenario["pillars"]:
        lines.append(
            f"| {row['pillar']} - {row['pillar_name']} "
            f"| {row['historical_funded_share_percent']:.1f}% "
            f"| {row['allocation_percent']:.0f}% "
            f"| {format_amount(row['example_allocation_ada'], 'ADA')} |"
        )
    lines += [
        "",
        "The floors intentionally prevent historical category design from locking future "
        "allocations into persistent underinvestment in infrastructure, governance, and "
        "network sustainability. See `2027-subcategory-allocation.csv` for the proposed "
        "internal envelopes.",
    ]
    lines += [
        "",
        "## Interpretation limits",
        "",
        (
            "The classification assigns one primary pillar to prevent double counting. "
            "Challenge-based matches are high confidence; broad/open challenges use "
            "deterministic proposal-text scoring; unresolved cases remain in `PX`. Delivery "
            "evidence is weakest for Funds 2-5, partial for Funds 6-9, milestone-based from "
            "Fund 10 onward, and still accruing for recent funds. Fund 15 has no final "
            "funding results in this snapshot."
        ),
        "",
        (
            "See `classification-audit.csv` for every assignment and `methodology.md` for "
            "the full taxonomy and rules."
        ),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(repo_root: Path) -> Json:
    source_path = repo_root / "data/consolidated/all_proposals.json"
    proposals: list[Json] = json.loads(source_path.read_text(encoding="utf-8"))
    classified: list[Json] = []
    for proposal in proposals:
        pillar, subcategory, confidence, basis = classify(proposal)
        fund = int(proposal["fund"])
        classified.append(
            {
                "proposal_id": proposal["proposal_id"],
                "fund": fund,
                "year": FUND_YEARS[fund],
                "title": proposal["title"],
                "challenge": proposal.get("challenge") or "",
                "pillar": pillar,
                "pillar_name": PILLARS[pillar]["name"],
                "subcategory": subcategory,
                "classification_confidence": confidence,
                "classification_basis": basis,
                "currency": proposal.get("currency") or "UNKNOWN",
                "amount_requested": proposal.get("amount_requested"),
                "amount_received": proposal.get("amount_received"),
                "funding_status": proposal["funding_status"],
                "project_status": proposal["project_status"],
                "funded": is_funded(proposal),
                "delivered": is_delivered(proposal),
            }
        )
    source_snapshot = max(
        json.loads(path.read_text(encoding="utf-8"))["normalized_at"]
        for path in (repo_root / "data/funds").glob("fund-*/_meta.json")
    )
    confidence_counts: dict[str, int] = defaultdict(int)
    for row in classified:
        confidence_counts[row["classification_confidence"]] += 1
    payload: Json = {
        "meta": {
            "generated_at": source_snapshot,
            "source_snapshot": source_snapshot,
            "proposal_count": len(classified),
            "taxonomy_source": "https://product.cardano.intersectmbo.org/vision/strategy-2030/",
            "confidence_counts": dict(sorted(confidence_counts.items())),
            "fund_years": FUND_YEARS,
        },
        "pillars": PILLARS,
        "by_fund": aggregate(classified, "fund"),
        "by_year": aggregate(classified, "year"),
        "scenario_2027": build_2027_scenario(classified),
    }
    out_dir = repo_root / "reports/funding-priorities-vision-2030"
    write_csv(out_dir / "classification-audit.csv", classified)
    write_csv(out_dir / "by-fund.csv", payload["by_fund"])
    write_csv(out_dir / "by-year.csv", payload["by_year"])
    write_csv(out_dir / "by-fund-subcategory.csv", aggregate_subcategories(classified, "fund"))
    write_csv(out_dir / "by-year-subcategory.csv", aggregate_subcategories(classified, "year"))
    write_csv(out_dir / "2027-pillar-allocation.csv", payload["scenario_2027"]["pillars"])
    write_csv(
        out_dir / "2027-subcategory-allocation.csv",
        payload["scenario_2027"]["subcategories"],
    )
    write_markdown(out_dir / "report.md", payload)
    (repo_root / "site/funding-priorities-data.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    build(args.repo_root.resolve())


if __name__ == "__main__":
    main()
