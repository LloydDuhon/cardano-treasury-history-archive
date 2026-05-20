#!/usr/bin/env python3
"""
Build dashboard/data.js from the canonical archive reports.

This is intended to live in `etl/scripts/` of cardano-treasury-history-archive
(or be called from the existing `generate_treasury_fund_reports.py` after the
reports themselves regenerate).

Reads:
  data/_raw/hydra_voting/cardano-budget-2026.json
  reports/treasury-fund-2/proposer-history.csv
  reports/treasury-fund-2/scope-similarity.csv
  reports/treasury-fund-2/work-overlap-review.csv
  reports/treasury-fund-2/tf1-ekklesia-reconciliation.csv
  reports/treasury-fund-2/identity-bridge-2025.csv

Writes:
  site/data.js                       (window.__TREASURY_DATA = {...};)
  site/data.json                     (same payload, JSON)

Usage:
  python build_dashboard_data.py [--repo-root .] [--out site]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

JsonRow = dict[str, Any]


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def parse_float(x: object) -> float | None:
    if x is None or x == "":
        return None
    try:
        return float(str(x))
    except ValueError:
        return None


def load_current_proposals(hydra_path: Path) -> tuple[list[JsonRow], str | None, str | None]:
    raw = json.loads(hydra_path.read_text())
    out: list[JsonRow] = []
    for p in raw["proposals_response"]["data"]:
        md = p.get("metaData") or {}
        cp = md.get("contractingParty") or {}
        proposer = (
            (md.get("proposerDetails") or {}).get("name")
            or cp.get("companyName")
            or cp.get("legalName")
            or "(unnamed)"
        ).strip()
        out.append(
            {
                "id": p["_id"],
                "title": p.get("title", ""),
                "proposer": proposer,
                "entityType": cp.get("legalEntityType"),
                "requested_ada": md.get("totalBudget", 0) or 0,
                "summary": p.get("summary", ""),
                "status": p.get("status"),
                "submittedAt": p.get("submittedAt"),
            }
        )
    return out, raw.get("fetched_at"), raw.get("source_url")


def canonicalize_proposers(proposals: list[JsonRow]) -> None:
    """Pick the most-common spelling per normalized key; rewrite in place."""
    tally: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in proposals:
        tally[norm_name(p["proposer"])][p["proposer"]] += 1
    canon = {k: max(v.items(), key=lambda kv: kv[1])[0] for k, v in tally.items()}
    for p in proposals:
        p["proposer"] = canon[norm_name(p["proposer"])]


def aggregate_history(history_csv: Path) -> dict[str, JsonRow]:
    """Return {proposer_name: aggregated_history_dict}."""
    by_proposer: defaultdict[str, dict[str, JsonRow]] = defaultdict(dict)
    with history_csv.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (r["current_proposer_name"] or "").strip()
            projects = by_proposer.setdefault(key, {})
            pid = r["historical_project_id"]
            # Dedup: same historical project may appear once per current proposal
            if pid in projects:
                continue
            projects[pid] = {
                "source": r["source"],
                "project_id": pid,
                "title": r["historical_title"],
                "status": r["historical_status"],
                "funding_status": r["funding_status"],
                "amount_ada": parse_float(r["amount_ada"]),
                "amount_original": r["amount_original"],
                "ongoing": r["ongoing"] == "yes",
                "delivery_flags": r["delivery_flags"],
                "source_url": r["source_url"],
                "match_confidence": r["match_confidence"],
                "match_score": parse_float(r["match_score"]) or 0.0,
            }

    out: dict[str, JsonRow] = {}
    for name, proj_map in by_proposer.items():
        projects = list(proj_map.values())
        by_cat = [p for p in projects if p["source"] == "Project Catalyst"]
        by_tf1 = [p for p in projects if p["source"] == "Treasury Fund 1"]

        def sum_ada(arr: list[JsonRow]) -> float:
            return sum((p["amount_ada"] or 0) for p in arr)

        out[name] = {
            "projects": projects,
            "catalystProjects": len(by_cat),
            "catalystAda": sum_ada(by_cat),
            "tf1Projects": len(by_tf1),
            "tf1Ada": sum_ada(by_tf1),
            "totalAda": sum_ada(projects),
            "withdrawnAda": sum_ada([p for p in projects if p["status"] == "withdrawn"]),
            "pausedAda": sum_ada([p for p in projects if p["status"] == "paused"]),
            "ongoing": sum(1 for p in projects if p["ongoing"]),
            "complete": sum(1 for p in projects if p["status"] == "complete"),
            "totalProjects": len(projects),
            "hasDeliveryFlag": any(
                p["delivery_flags"] and not p["delivery_flags"].lower().startswith("no documented")
                for p in projects
            ),
        }
    return out


def index_similarity(path: Path) -> dict[str, list[JsonRow]]:
    by_proposal: defaultdict[str, list[JsonRow]] = defaultdict(list)
    with path.open() as f:
        for r in csv.DictReader(f):
            by_proposal[r["current_proposal_id"]].append(
                {
                    "source": r["source"],
                    "historical_project_id": r["historical_project_id"],
                    "historical_title": r["historical_title"],
                    "historical_status": r["historical_status"],
                    "similarity": parse_float(r["similarity"]) or 0.0,
                    "confidence": r["confidence"],
                    "rationale": r["rationale"],
                    "source_url": r["source_url"],
                }
            )
    return dict(by_proposal)


def include_overlap_row(row: JsonRow) -> bool:
    confidence = row["match_confidence"]
    if confidence in {"high", "medium"}:
        return True
    if confidence == "low":
        return (parse_float(row["work_overlap_percent"]) or 0) >= 35
    return False


def adjudication_label(model: str) -> str:
    if model == "manual-console-adjudication":
        return "Human Reviewed"
    if model:
        return "AI Matched"
    return "Not Reviewed"


def index_work_overlap(path: Path) -> dict[str, list[JsonRow]]:
    by_proposal: defaultdict[str, list[JsonRow]] = defaultdict(list)
    if not path.exists():
        return {}
    with path.open() as f:
        for r in csv.DictReader(f):
            if not include_overlap_row(r):
                continue
            ai_model = r.get("ai_model", "")
            by_proposal[r["current_proposal_id"]].append(
                {
                    "historical_source": r["historical_source"],
                    "historical_project_id": r["historical_project_id"],
                    "historical_title": r["historical_title"],
                    "historical_status": r["historical_status"],
                    "funding_status": r["funding_status"],
                    "previously_funded": r["previously_funded"],
                    "amount_original": r["amount_original"],
                    "historical_proposer_names": r["historical_proposer_names"],
                    "retrieval_rank": int(parse_float(r["retrieval_rank"]) or 0),
                    "retrieval_score": parse_float(r["retrieval_score"]) or 0.0,
                    "match_confidence": r["match_confidence"],
                    "work_overlap_percent": int(parse_float(r["work_overlap_percent"]) or 0),
                    "overlap_type": r["overlap_type"],
                    "previously_proposed": str(r["previously_proposed"]).lower() == "true",
                    "previously_funded_relevance": r["previously_funded_relevance"],
                    "same_or_related_proposer": r["same_or_related_proposer"],
                    "overlap_evidence": r["overlap_evidence"],
                    "funding_evidence": r["funding_evidence"],
                    "relationship_evidence": r["relationship_evidence"],
                    "review_notes": r["review_notes"],
                    "ai_model": ai_model,
                    "adjudication_source": adjudication_label(ai_model),
                    "source_url": r["source_url"],
                }
            )
    for rows in by_proposal.values():
        rows.sort(
            key=lambda row: (
                {"high": 0, "medium": 1, "low": 2}.get(row["match_confidence"], 9),
                -row["work_overlap_percent"],
                row["retrieval_rank"],
            )
        )
    return dict(by_proposal)


def index_identity_bridge(path: Path) -> dict[str, list[JsonRow]]:
    by_proposal: defaultdict[str, list[JsonRow]] = defaultdict(list)
    with path.open() as f:
        for r in csv.DictReader(f):
            by_proposal[r["current_proposal_id"]].append(
                {
                    "budget_2025_title": r["budget_2025_title"],
                    "company_name": r["company_name"],
                    "group_name": r["group_name"],
                    "social_handles": r["social_handles"],
                    "domain": r["company_domain"],
                    "public_champion": r["public_champion"],
                    "on_behalf": r["submitted_on_behalf"],
                    "budget_2025_cost_ada": parse_float(r["budget_2025_cost_ada"]),
                    "threshold_reached": r["threshold_reached"].lower() == "true",
                    "vote_summary": r["vote_summary"],
                    "match_confidence": r["match_confidence"],
                    "match_score": parse_float(r["match_score"]) or 0.0,
                }
            )
    return dict(by_proposal)


def load_tf1_reconciliation(path: Path) -> list[JsonRow]:
    rows: list[JsonRow] = []
    with path.open() as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "tf1_project_id": r["tf1_project_id"],
                    "tf1_title": r["tf1_title"],
                    "tf1_vendor_label": r["tf1_vendor_label"],
                    "tf1_status": r["tf1_status"],
                    "tf1_total_contract_ada": parse_float(r["tf1_total_contract_ada"]),
                    "budget_2025_title": r["budget_2025_title"],
                    "company_name": r["company_name"],
                    "match_confidence": r["match_confidence"],
                    "source_url": r["source_url"],
                }
            )
    return rows


def load_report_summary(path: Path) -> JsonRow:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def build(repo_root: Path, out_dir: Path) -> None:
    proposals, fetched_at, source_url = load_current_proposals(
        repo_root / "data" / "_raw" / "hydra_voting" / "cardano-budget-2026.json"
    )
    raw_unique_proposers = len({str(p["proposer"]) for p in proposals})
    canonicalize_proposers(proposals)

    proposer_history = aggregate_history(
        repo_root / "reports" / "treasury-fund-2" / "proposer-history.csv"
    )
    similarity = index_similarity(
        repo_root / "reports" / "treasury-fund-2" / "scope-similarity.csv"
    )
    work_overlap = index_work_overlap(
        repo_root / "reports" / "treasury-fund-2" / "work-overlap-review.csv"
    )
    identity_bridge = index_identity_bridge(
        repo_root / "reports" / "treasury-fund-2" / "identity-bridge-2025.csv"
    )
    tf1_reconciliation = load_tf1_reconciliation(
        repo_root / "reports" / "treasury-fund-2" / "tf1-ekklesia-reconciliation.csv"
    )
    summary = load_report_summary(repo_root / "reports" / "treasury-fund-2" / "_summary.json")

    # Per-proposer current-proposal map
    proposer_proposals: dict[str, JsonRow] = {}
    for p in proposals:
        e = proposer_proposals.setdefault(
            p["proposer"], {"name": p["proposer"], "proposalIds": [], "requestedAda": 0}
        )
        e["proposalIds"].append(p["id"])
        e["requestedAda"] += p["requested_ada"]

    total_requested = sum(p["requested_ada"] for p in proposals)
    unique_proposers = len(proposer_proposals)
    proposers_with_history = sum(
        1
        for name in proposer_proposals
        if proposer_history.get(name, {}).get("totalProjects", 0) > 0
    )
    multi_proposers = sum(1 for v in proposer_proposals.values() if len(v["proposalIds"]) > 1)
    total_historical_ada = sum(v["totalAda"] for v in proposer_history.values())
    proposals_with_work_overlap = sum(1 for rows in work_overlap.values() if rows)
    ai_overlap_matches = sum(
        1
        for rows in work_overlap.values()
        for row in rows
        if row["adjudication_source"] == "AI Matched"
    )
    human_overlap_matches = sum(
        1
        for rows in work_overlap.values()
        for row in rows
        if row["adjudication_source"] == "Human Reviewed"
    )

    payload = {
        "meta": {
            "generated_at": fetched_at,
            "snapshot_source": source_url,
            "total_proposals": len(proposals),
            "unique_proposers": unique_proposers,
            "raw_unique_proposers": summary.get("current_unique_proposers", raw_unique_proposers),
            "proposers_with_history": proposers_with_history,
            "raw_proposers_with_history": summary.get(
                "proposers_with_prior_history",
                proposers_with_history,
            ),
            "total_requested_ada": total_requested,
            "total_historical_ada": total_historical_ada,
            "multi_proposal_proposers": multi_proposers,
            "work_overlap_triage_matches": sum(len(rows) for rows in work_overlap.values()),
            "proposals_with_work_overlap": proposals_with_work_overlap,
            "ai_work_overlap_matches": ai_overlap_matches,
            "human_work_overlap_matches": human_overlap_matches,
            "entity_resolution_merges": {"MLabsLTD": "MLabs LTD"},
        },
        "proposals": proposals,
        "proposerHistory": proposer_history,
        "proposerProposals": proposer_proposals,
        "similarity": similarity,
        "workOverlap": work_overlap,
        "identityBridge": identity_bridge,
        "tf1Reconciliation": tf1_reconciliation,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (out_dir / "data.json").write_text(json_text)
    (out_dir / "data.js").write_text(f"window.__TREASURY_DATA = {json_text};\n")
    print(f"Wrote {out_dir / 'data.js'} ({len(json_text):,} bytes)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--repo-root",
        default=".",
        help="Path to cardano-treasury-history-archive root",
    )
    ap.add_argument("--out", default="site", help="Output directory (data.js + data.json)")
    args = ap.parse_args()
    build(Path(args.repo_root).resolve(), Path(args.out).resolve())
