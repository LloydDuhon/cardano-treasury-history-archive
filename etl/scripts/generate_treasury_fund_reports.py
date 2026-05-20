"""Generate Treasury Fund 2 proposer history and scope-similarity reports.

Inputs:
    data/_raw/hydra_voting/cardano-budget-2026.json
    data/consolidated/all_proposals.json
    data/consolidated/all_proposers.json
    data/consolidated/all_milestones.json
    data/historical/treasury-fund-01/projects.json
    data/historical/treasury-fund-01/vendors.json
    data/historical/treasury-fund-01/milestones.json
    data/_raw/intersect_budget_2025/reconciliation.json
    data/_raw/builderdao_taptools/projects.json

Outputs:
    reports/treasury-fund-2/proposer-history.md
    reports/treasury-fund-2/proposer-history.csv
    reports/treasury-fund-2/scope-similarity.md
    reports/treasury-fund-2/scope-similarity.csv
    reports/treasury-fund-2/identity-bridge-2025.csv
    reports/treasury-fund-2/identity-bridge-2025.md
    reports/treasury-fund-2/tf1-ekklesia-reconciliation.csv
    reports/treasury-fund-2/tf1-ekklesia-reconciliation.md
    reports/treasury-fund-2/onchain-treasury-reconciliation.csv
    reports/treasury-fund-2/onchain-treasury-reconciliation.md
    reports/treasury-fund-2/builderdao-disbursements.csv
    reports/treasury-fund-2/builderdao-disbursements.md
    reports/treasury-fund-2/_summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
DEFAULT_REPORT_ROOT = REPO_ROOT / "reports" / "treasury-fund-2"
CURRENT_SNAPSHOT = DEFAULT_DATA_ROOT / "_raw" / "hydra_voting" / "cardano-budget-2026.json"
BUDGET_2025_SNAPSHOT = DEFAULT_DATA_ROOT / "_raw" / "intersect_budget_2025" / "reconciliation.json"
BUILDERDAO_SNAPSHOT = DEFAULT_DATA_ROOT / "_raw" / "builderdao_taptools" / "projects.json"
BUILDERDAO_DASHBOARD_URL = "https://cbdao.taptools.io/"
BUILDERDAO_PARENT_TF1_PROJECT_ID = "EMI-0004-25"

FUNDED_STATUSES = {"approved", "leftover"}
ONGOING_PROJECT_STATUSES = {"in_progress"}
NEGATIVE_PROJECT_STATUSES = {"cancelled", "stalled"}
NEGATIVE_MILESTONE_STATUSES = {"rejected", "stalled", "withdrawn"}
COMPLETED_PROJECT_STATUSES = {"complete"}
TF1_ONGOING_STATUSES = {"active", "paused", "mixed"}
TF1_NEGATIVE_STATUSES = {"withdrawn", "paused"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "cardano",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "project",
    "proposal",
    "the",
    "this",
    "to",
    "with",
}
NAME_STOPWORDS = STOPWORDS | {
    "cardano",
    "committee",
    "dao",
    "foundation",
    "group",
    "labs",
    "ltd",
    "network",
}
FUNDING_MATCH_STOPWORDS = STOPWORDS | {
    "ada",
    "administered",
    "amount",
    "budget",
    "calls",
    "committee",
    "fund",
    "funds",
    "gatherings",
    "core",
    "critical",
    "enhancement",
    "intersect",
    "loan",
    "local",
    "maintenance",
    "requested",
    "service",
    "services",
    "sustaining",
    "tool",
    "tooling",
    "tools",
    "treasury",
    "withdraw",
    "withdrawal",
    "workshops",
}


@dataclass(frozen=True)
class CurrentProposal:
    proposal_id: str
    proposer_id: str
    proposer_name: str
    title: str
    summary: str
    budget: float
    status: str
    submitted_at: str


@dataclass(frozen=True)
class NameMatch:
    source: str
    entity_id: str
    display_name: str
    score: float
    confidence: str


# Maintainer-reviewed current-proposer bridges that cannot be inferred from
# source names alone. Five Binaries is owned by Marek Mahut; Marek's prior
# Catalyst history is represented in the archive by this LidoNation proposer ID.
MANUAL_CURRENT_PROPOSER_CATALYST_MATCHES: dict[str, tuple[NameMatch, ...]] = {
    "five binaries": (
        NameMatch(
            source="Project Catalyst",
            entity_id="p-lido-c269e96b-eb38-4343-a5d7-41e17399505a",
            display_name="Marek Mahut / Proposer c269e96b (Five Binaries owner)",
            score=1.0,
            confidence="high",
        ),
    ),
}


@dataclass(frozen=True)
class HistoryRecord:
    current_proposal_id: str
    current_proposer_name: str
    source: str
    match_name: str
    match_score: float
    match_confidence: str
    historical_project_id: str
    historical_title: str
    historical_status: str
    funding_status: str
    amount_ada: float | None
    amount_original: str
    final_outputs: str
    delivery_flags: str
    ongoing: str
    source_url: str


@dataclass(frozen=True)
class SimilarityRecord:
    current_proposal_id: str
    current_title: str
    current_proposer_name: str
    source: str
    historical_project_id: str
    historical_title: str
    historical_status: str
    similarity: float
    confidence: str
    rationale: str
    source_url: str


@dataclass(frozen=True)
class IdentityBridgeRecord:
    current_proposal_id: str
    current_title: str
    current_proposer_name: str
    budget_2025_proposal_id: str
    budget_2025_title: str
    match_name: str
    match_score: float
    match_confidence: str
    company_name: str
    group_name: str
    social_handles: str
    company_domain: str
    public_champion: str
    submitted_on_behalf: str
    budget_2025_cost_ada: float
    threshold_reached: str
    vote_summary: str
    source_url: str


@dataclass(frozen=True)
class TF1ReconciliationRecord:
    tf1_project_id: str
    tf1_title: str
    tf1_vendor_label: str
    tf1_status: str
    tf1_total_contract_ada: float
    budget_2025_proposal_id: str
    budget_2025_title: str
    budget_2025_cost_ada: float
    match_score: float
    match_confidence: str
    match_basis: str
    company_name: str
    group_name: str
    social_handles: str
    company_domain: str
    public_champion: str
    submitted_on_behalf: str
    threshold_reached: str
    source_url: str


@dataclass(frozen=True)
class OnchainTreasuryReconciliationRecord:
    onchain_proposal_id: str
    onchain_title: str
    onchain_status: str
    onchain_total_withdrawal_ada: float
    onchain_withdrawal_count: int
    proposed_epoch: str
    enacted_epoch: str
    meta_url: str
    tf1_overlap: str
    tf1_project_ids: str
    tf1_titles: str
    tf1_statuses: str
    tf1_total_contract_ada: float
    amount_delta_ada: float
    match_confidence: str
    match_score: float
    match_basis: str
    counting_guidance: str


@dataclass(frozen=True)
class BuilderDAODisbursementRecord:
    recipient_name: str
    project_slug: str
    round: int
    funded: str
    downstream_amount_ada: float
    parent_tf1_project_id: str
    parent_tf1_title: str
    matched_tf2_proposer_names: str
    metrics_summary: str
    proposal_url: str
    website_url: str
    source_url: str
    counting_guidance: str


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_json_dict(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _read_json_records(path: Path) -> list[dict[str, Any]]:
    payload = _read_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Expected JSON list at {path}")
    return [item for item in payload if isinstance(item, dict)]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def _normalize_name(value: str | None) -> str:
    text = (value or "").casefold()
    text = text.replace("&", " and ")
    text = re.sub(
        r"\b(llc|ltd|limited|gmbh|inc|company|corp|corporation)\b",
        " ",
        text,
    )
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _aliases(value: str | None) -> set[str]:
    normalized = _normalize_name(value)
    aliases = {normalized} if normalized else set()
    if normalized in {"iog", "input output", "input output global", "input output engineering"}:
        aliases.update({"iog", "input output", "input output global", "input output engineering"})
    if "input output" in normalized:
        aliases.add("iog")
    if normalized == "mlabsltd":
        aliases.add("mlabs")
    if normalized == "intersectmbo":
        aliases.add("intersect")
    if "lido nation" in normalized:
        aliases.add("lido nation")
    if "2 lovelaces" in normalized:
        aliases.add("2 lovelaces")
    if "rare evo" in normalized:
        aliases.add("rare evo")
    if "scrib3" in normalized:
        aliases.add("scrib3")
    if normalized == "no witness labs":
        aliases.add("nowitness labs")
    return {alias for alias in aliases if alias}


def _tokenize(value: str | None) -> list[str]:
    text = (value or "").casefold()
    tokens = re.findall(r"[a-z0-9][a-z0-9-]{1,}", text)
    return [token for token in tokens if token not in STOPWORDS and len(token) > 2]


def _token_jaccard(left: str, right: str) -> float:
    a = set(_tokenize(left))
    b = set(_tokenize(right))
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _text_similarity(left: str, right: str) -> float:
    normalized_left = _normalize_name(left)
    normalized_right = _normalize_name(right)
    if not normalized_left or not normalized_right:
        return 0.0
    seq = SequenceMatcher(None, normalized_left, normalized_right).ratio()
    containment = 0.0
    if len(normalized_left) > 8 and normalized_left in normalized_right:
        containment = 0.95
    if len(normalized_right) > 8 and normalized_right in normalized_left:
        containment = 0.95
    return max(seq, containment, _token_jaccard(left, right))


def _funding_match_text(value: str | None) -> str:
    text = (value or "").casefold()
    text = text.replace("&", " and ")
    text = re.sub(r"₳?\s*\d[\d,]*(?:\.\d+)?\s*(?:ada|m)?", " ", text)
    text = re.sub(r"\b20\d{2}\b", " ", text)
    text = re.sub(r"\(\s*\d+\s*of\s*\d+\s*\)|\(\s*\d+of\d+\s*\)", " ", text)
    text = re.sub(
        r"\b(llc|ltd|limited|gmbh|inc|company|corp|corporation|fz|sa)\b",
        " ",
        text,
    )
    tokens = re.findall(r"[a-z0-9][a-z0-9-]{1,}", text)
    return " ".join(
        token for token in tokens if token not in FUNDING_MATCH_STOPWORDS and len(token) > 2
    )


def _funding_text_similarity(left: str, right: str) -> float:
    normalized_left = _funding_match_text(left)
    normalized_right = _funding_match_text(right)
    if not normalized_left or not normalized_right:
        return 0.0
    seq = SequenceMatcher(None, normalized_left, normalized_right).ratio()
    left_tokens = set(normalized_left.split())
    right_tokens = set(normalized_right.split())
    jaccard = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    containment = 0.0
    if len(normalized_left) >= 5 and normalized_left in normalized_right:
        containment = 0.95
    if len(normalized_right) >= 5 and normalized_right in normalized_left:
        containment = 0.95
    return max(seq, jaccard, containment)


def _meaningful_name_tokens(value: str) -> set[str]:
    return {token for token in _tokenize(value) if token not in NAME_STOPWORDS}


def _has_meaningful_name_overlap(left: str, right: str) -> bool:
    left_tokens = _meaningful_name_tokens(left)
    right_tokens = _meaningful_name_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    return bool(left_tokens & right_tokens)


def _name_score(left: str, right: str) -> float:
    left_aliases = _aliases(left)
    right_aliases = _aliases(right)
    if not left_aliases or not right_aliases:
        return 0.0
    if left_aliases & right_aliases:
        return 1.0
    best = 0.0
    for a in left_aliases:
        for b in right_aliases:
            seq = SequenceMatcher(None, a, b).ratio()
            containment = 0.92 if (len(a) > 4 and a in b) or (len(b) > 4 and b in a) else 0.0
            best = max(best, seq, containment, _token_jaccard(a, b))
    return best


def _name_in_text_score(name: str, text: str) -> float:
    normalized_text = f" {_normalize_name(text)} "
    best = 0.0
    for alias in _aliases(name):
        if len(alias) < 4:
            continue
        if f" {alias} " in normalized_text:
            best = max(best, 0.88 if " " in alias else 0.82)
    return best


def _confidence(score: float, *, high: float, medium: float) -> str:
    if score >= high:
        return "high"
    if score >= medium:
        return "medium"
    return "low"


def _text_for_proposal(proposal: dict[str, Any]) -> str:
    parts = [
        proposal.get("title"),
        proposal.get("summary"),
        proposal.get("problem"),
        proposal.get("solution"),
        proposal.get("definition_of_success"),
        proposal.get("challenge"),
    ]
    return "\n".join(str(p) for p in parts if p)


def _text_for_tf1_project(project: dict[str, Any], milestones: Sequence[dict[str, Any]]) -> str:
    parts = [project.get("title"), project.get("description")]
    project_id = project.get("project_id")
    parts.extend(m.get("description") for m in milestones if m.get("project_id") == project_id)
    parts.extend(
        m.get("acceptance_criteria")
        for m in milestones
        if m.get("project_id") == project.get("project_id")
    )
    return "\n".join(str(p) for p in parts if p)


def _load_current(snapshot_path: Path) -> tuple[str, list[CurrentProposal]]:
    snapshot = _read_json_dict(snapshot_path)
    fetched_at = str(snapshot.get("fetched_at") or "")
    response = snapshot.get("proposals_response")
    response = response if isinstance(response, dict) else {}
    proposals = response.get("data") if isinstance(response, dict) else []
    if not isinstance(proposals, list):
        raise ValueError("Hydra voting snapshot missing proposals_response.data list")
    current: list[CurrentProposal] = []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            continue
        metadata_raw = proposal.get("metaData")
        metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
        proposer_raw = metadata.get("proposerDetails")
        proposer = proposer_raw if isinstance(proposer_raw, dict) else {}
        current.append(
            CurrentProposal(
                proposal_id=str(proposal.get("_id") or ""),
                proposer_id=str(proposal.get("proposerId") or ""),
                proposer_name=str(proposer.get("name") or ""),
                title=str(proposal.get("title") or ""),
                summary=str(proposal.get("summary") or ""),
                budget=float(metadata.get("totalBudget") or 0),
                status=str(proposal.get("status") or ""),
                submitted_at=str(proposal.get("submittedAt") or ""),
            )
        )
    return fetched_at, current


def _load_budget_2025(snapshot_path: Path) -> tuple[str, list[dict[str, Any]]]:
    if not snapshot_path.exists():
        return "", []
    snapshot = _read_json_dict(snapshot_path)
    fetched_at = str(snapshot.get("fetched_at") or "")
    response = snapshot.get("proposals_response")
    response = response if isinstance(response, dict) else {}
    proposal_data = response.get("data")
    proposals = proposal_data if isinstance(proposal_data, list) else []
    return fetched_at, [item for item in proposals if isinstance(item, dict)]


def _load_builderdao_projects(snapshot_path: Path) -> list[dict[str, Any]]:
    if not snapshot_path.exists():
        return []
    snapshot = _read_json_dict(snapshot_path)
    if snapshot.get("error") is True:
        raise ValueError(f"BuilderDAO snapshot reports error: {snapshot.get('msg')}")
    projects = snapshot.get("data")
    if not isinstance(projects, list):
        raise ValueError("BuilderDAO snapshot missing data list")
    return [item for item in projects if isinstance(item, dict)]


def _match_entities(
    current_name: str,
    catalyst_proposers: Sequence[dict[str, Any]],
    tf1_vendors: Sequence[dict[str, Any]],
) -> list[NameMatch]:
    matches: list[NameMatch] = list(
        MANUAL_CURRENT_PROPOSER_CATALYST_MATCHES.get(_normalize_name(current_name), ())
    )
    seen = {(match.source, match.entity_id) for match in matches}
    for proposer in catalyst_proposers:
        name = str(proposer.get("display_name") or "")
        if _normalize_name(name) in {"anonymous", "unknown"}:
            continue
        score = _name_score(current_name, name)
        key = ("Project Catalyst", str(proposer.get("proposer_id") or ""))
        if score >= 0.74 and key not in seen:
            matches.append(
                NameMatch(
                    source="Project Catalyst",
                    entity_id=key[1],
                    display_name=name,
                    score=score,
                    confidence=_confidence(score, high=0.92, medium=0.82),
                )
            )
            seen.add(key)
    for vendor in tf1_vendors:
        name = str(vendor.get("display_name") or "")
        score = _name_score(current_name, name)
        key = ("Treasury Fund 1", str(vendor.get("vendor_id") or ""))
        if score >= 0.74 and key not in seen:
            matches.append(
                NameMatch(
                    source="Treasury Fund 1",
                    entity_id=key[1],
                    display_name=name,
                    score=score,
                    confidence=_confidence(score, high=0.92, medium=0.82),
                )
            )
            seen.add(key)
    matches.sort(key=lambda m: (m.score, m.source), reverse=True)
    return matches


def _amount_original(proposal: dict[str, Any]) -> str:
    amount = proposal.get("amount_received")
    if amount is None:
        amount = proposal.get("amount_requested")
    currency = proposal.get("currency") or "UNKNOWN"
    if amount is None:
        return f"unknown {currency}"
    return f"{float(amount):,.2f} {currency}"


def _amount_ada(proposal: dict[str, Any]) -> float | None:
    if proposal.get("currency") != "ADA":
        return None
    amount = proposal.get("amount_received")
    if amount is None:
        amount = proposal.get("amount_requested")
    return float(amount or 0)


def _proposal_url(proposal: dict[str, Any]) -> str:
    links_raw = proposal.get("links")
    links = links_raw if isinstance(links_raw, dict) else {}
    for key in (
        "lidonation_url",
        "projectcatalyst_io_url",
        "milestones_url",
        "catalyst_voices_url",
    ):
        value = links.get(key)
        if value:
            return str(value)
    return ""


def _budget_2025_data(proposal: dict[str, Any]) -> dict[str, Any]:
    data = proposal.get("data")
    return data if isinstance(data, dict) else {}


def _budget_2025_inner_data(proposal: dict[str, Any]) -> dict[str, Any]:
    data = _budget_2025_data(proposal).get("data")
    return data if isinstance(data, dict) else {}


def _budget_2025_owner(proposal: dict[str, Any]) -> dict[str, Any]:
    owner = _budget_2025_inner_data(proposal).get("owner_info")
    return owner if isinstance(owner, dict) else {}


def _budget_2025_identity_values(proposal: dict[str, Any]) -> list[str]:
    owner = _budget_2025_owner(proposal)
    inner = _budget_2025_inner_data(proposal)
    values = [
        proposal.get("name"),
        inner.get("name"),
        owner.get("company_name"),
        owner.get("group_name"),
        owner.get("social_handles"),
        owner.get("company_domain_name"),
        owner.get("proposal_public_champion"),
        owner.get("key_info_to_identify_group"),
    ]
    ignored = {"", "beneficiary listed above", "submission lead listed above"}
    return [
        str(value).strip()
        for value in values
        if value and _normalize_name(str(value)) not in ignored
    ]


def _budget_2025_source_url(proposal: dict[str, Any]) -> str:
    proposal_id = str(proposal.get("_id") or "")
    ballot_id = str(proposal.get("ballotId") or "")
    if proposal_id and ballot_id:
        return f"https://2025budget.intersectmbo.org/ballots/{ballot_id}/proposals/{proposal_id}"
    return "https://2025budget.intersectmbo.org/"


def _budget_2025_vote_summary(proposal: dict[str, Any]) -> str:
    result = proposal.get("result")
    result = result if isinstance(result, dict) else {}
    result_rows = result.get("results")
    rows = result_rows if isinstance(result_rows, list) else []
    parts = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label") or row.get("value") or "")
        count = int(row.get("count") or 0)
        voting_power = float(row.get("votingPower") or 0)
        parts.append(f"{label}: count={count}, voting_power={voting_power:,.0f}")
    return "; ".join(parts)


def _tf1_title_variants(project: dict[str, Any]) -> list[str]:
    title = str(project.get("title") or "")
    vendor = str(project.get("vendor_label") or "")
    variants = [title]
    if vendor and title.casefold().startswith(vendor.casefold()):
        stripped = re.sub(rf"^{re.escape(vendor)}\s*[-:]\s*", "", title, flags=re.IGNORECASE)
        if stripped and stripped != title:
            variants.append(stripped)

    comma_part_whitelist = {
        "dolos",
        "eternl",
        "gerolamo",
        "nftcdn",
        "opshin",
        "pallas",
        "plutarch",
        "pycardano",
        "scalus",
        "zkfold",
    }

    def add_comma_parts(value: str) -> None:
        for part in value.split(","):
            part = part.strip()
            normalized = _funding_match_text(part)
            tokens = normalized.split()
            if len(tokens) >= 2 or normalized in comma_part_whitelist:
                variants.append(part)

    if " - " in title:
        right_side = title.split(" - ", 1)[1]
        variants.append(right_side)
        add_comma_parts(right_side)
    add_comma_parts(title)
    variants.append(
        re.sub(r"\(\s*\d+\s*of\s*\d+\s*\)|\(\s*\d+of\d+\s*\)", "", title, flags=re.IGNORECASE)
    )
    return [variant.strip() for variant in variants if variant.strip()]


def _amount_similarity(left: float, right: float) -> float:
    if left <= 0 or right <= 0:
        return 0.0
    ratio = min(left, right) / max(left, right)
    if ratio >= 0.98:
        return 1.0
    if ratio >= 0.90:
        return 0.92
    if ratio >= 0.75:
        return 0.80
    return ratio


def _tf1_budget_2025_score(
    project: dict[str, Any],
    budget_2025_proposal: dict[str, Any],
) -> tuple[float, str]:
    budget_data = _budget_2025_data(budget_2025_proposal)
    title = str(budget_2025_proposal.get("name") or budget_data.get("name") or "")
    title_score = max(
        (_text_similarity(variant, title) for variant in _tf1_title_variants(project)),
        default=0.0,
    )
    amount_score = _amount_similarity(
        float(project.get("total_contract_ada") or 0),
        float(budget_data.get("cost") or 0),
    )
    owner_values = _budget_2025_identity_values(budget_2025_proposal)
    vendor = str(project.get("vendor_label") or "")
    owner_score = max((_name_score(vendor, value) for value in owner_values), default=0.0)
    combined = max(title_score, (title_score * 0.75) + (amount_score * 0.25))
    if owner_score >= 0.92 and title_score >= 0.45:
        combined = max(
            combined,
            (title_score * 0.70) + (owner_score * 0.20) + (amount_score * 0.10),
        )
    basis = f"title={title_score:.2f}; amount={amount_score:.2f}; " f"owner={owner_score:.2f}"
    return combined, basis


def _onchain_match_parts(withdrawal: dict[str, Any]) -> list[str]:
    title = str(withdrawal.get("title") or "")
    abstract = str(withdrawal.get("abstract") or "")
    rationale = str(withdrawal.get("rationale") or "")
    motivation = str(withdrawal.get("motivation") or "")
    bold_titles = re.findall(r"\*\*([^*]{4,180})\*\*", "\n".join([abstract, rationale]))
    parts = [
        title,
        *bold_titles[:6],
        abstract[:450],
        rationale[:300],
        motivation[:250],
    ]
    return [part for part in parts if part]


def _tf1_onchain_score(
    project: dict[str, Any],
    withdrawal: dict[str, Any],
) -> tuple[float, str, str, float, float]:
    onchain_parts = _onchain_match_parts(withdrawal)
    onchain_title = str(withdrawal.get("title") or "")
    direct_title_score = max(
        (
            _funding_text_similarity(variant, onchain_title)
            for variant in _tf1_title_variants(project)
        ),
        default=0.0,
    )
    title_score = max(
        (
            _funding_text_similarity(variant, part)
            for variant in _tf1_title_variants(project)
            for part in onchain_parts
        ),
        default=0.0,
    )
    amount_score = _amount_similarity(
        float(project.get("total_contract_ada") or 0),
        float(withdrawal.get("total_withdrawal_ada") or 0),
    )
    onchain_total = float(withdrawal.get("total_withdrawal_ada") or 0)
    score = max(title_score, (title_score * 0.85) + (amount_score * 0.15))
    if onchain_total < 1_000:
        confidence = "low"
    elif direct_title_score >= 0.86 and amount_score >= 0.03:
        confidence = "high"
    elif title_score >= 0.86 and amount_score >= 0.90:
        confidence = "high"
    elif title_score >= 0.86 and amount_score >= 0.05:
        confidence = "high"
    elif direct_title_score >= 0.55 and amount_score >= 0.20:
        confidence = "medium"
    elif title_score >= 0.55 and amount_score >= 0.90:
        confidence = "medium"
    else:
        confidence = "low"
    basis = (
        f"title={title_score:.2f}; direct_title={direct_title_score:.2f}; amount={amount_score:.2f}"
    )
    return score, confidence, basis, amount_score, direct_title_score


def _tf1_reconciliation_identity_values(record: TF1ReconciliationRecord) -> list[str]:
    return [
        record.tf1_vendor_label,
        record.company_name,
        record.group_name,
        record.social_handles,
        record.company_domain,
        record.public_champion,
        record.budget_2025_title,
        record.tf1_title,
    ]


def _final_outputs(
    proposal: dict[str, Any],
    milestones_by_proposal: dict[str, list[dict[str, Any]]],
) -> str:
    milestones = milestones_by_proposal.get(str(proposal.get("proposal_id") or ""), [])
    closeouts = [m for m in milestones if m.get("is_closeout")]
    if closeouts:
        out = closeouts[-1]
        links = [out.get("closeout_report_url"), out.get("closeout_video_url")]
        link_text = "; ".join(str(link) for link in links if link)
        return " | ".join(
            part
            for part in [
                str(out.get("title") or "Project closeout"),
                str(out.get("description") or ""),
                f"links: {link_text}" if link_text else "",
            ]
            if part
        )
    accepted = [m for m in milestones if m.get("status") == "accepted"]
    if accepted:
        out = accepted[-1]
        evidence_raw = out.get("evidence")
        evidence = evidence_raw if isinstance(evidence_raw, list) else []
        evidence_urls = [
            str(e.get("url")) for e in evidence if isinstance(e, dict) and e.get("url")
        ]
        return " | ".join(
            part
            for part in [
                str(out.get("title") or "Latest accepted milestone"),
                str(out.get("description") or ""),
                f"evidence: {'; '.join(evidence_urls[:3])}" if evidence_urls else "",
            ]
            if part
        )
    if proposal.get("project_status") == "complete":
        return "Marked complete in source data; no closeout artifact captured in interim dataset."
    return "No final output captured in interim dataset."


def _delivery_flags(
    proposal: dict[str, Any],
    milestones_by_proposal: dict[str, list[dict[str, Any]]],
) -> str:
    flags: list[str] = []
    project_status = str(proposal.get("project_status") or "")
    if project_status in NEGATIVE_PROJECT_STATUSES:
        flags.append(f"project_status={project_status}")
    milestones = milestones_by_proposal.get(str(proposal.get("proposal_id") or ""), [])
    bad_counts = Counter(
        str(m.get("status") or "")
        for m in milestones
        if str(m.get("status") or "") in NEGATIVE_MILESTONE_STATUSES
    )
    flags.extend(f"{status}_milestones={count}" for status, count in sorted(bad_counts.items()))
    if not flags:
        return "No documented non-delivery signal in dataset."
    return "; ".join(flags)


def _tf1_outputs(
    project: dict[str, Any],
    tf1_milestones_by_project: dict[str, list[dict[str, Any]]],
) -> str:
    milestones = tf1_milestones_by_project.get(str(project.get("project_id") or ""), [])
    matured = [m for m in milestones if m.get("status") == "Matured"]
    if matured:
        return " | ".join(
            str(m.get("description") or m.get("acceptance_criteria") or m.get("title") or "")
            for m in matured[-2:]
            if m.get("description") or m.get("acceptance_criteria") or m.get("title")
        )
    return "No Matured milestone output captured; see milestone status counts."


def _builderdao_project_id(project: dict[str, Any]) -> str:
    slug = str(project.get("slug") or "")
    if slug:
        return f"builderdao-{slug}"
    return f"builderdao-{_normalize_name(str(project.get('name') or '')).replace(' ', '-')}"


def _builderdao_metrics_summary(project: dict[str, Any], limit: int = 4) -> str:
    metrics = project.get("metrics")
    if not isinstance(metrics, list):
        return "No KPI metrics captured in dashboard snapshot."
    parts: list[str] = []
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        label = str(metric.get("label") or metric.get("key") or "").strip()
        if not label:
            continue
        unit = str(metric.get("unit") or "").strip()
        value = metric.get("value")
        goal = metric.get("goal")
        if value is None and goal is None:
            continue
        value_text = f"{value:g}" if isinstance(value, int | float) else str(value)
        goal_text = f"{goal:g}" if isinstance(goal, int | float) else str(goal)
        if unit and unit != "int":
            value_text = f"{value_text} {unit}"
            goal_text = f"{goal_text} {unit}"
        parts.append(f"{label}: {value_text} / goal {goal_text}")
        if len(parts) >= limit:
            break
    return "; ".join(parts) if parts else "No KPI metrics captured in dashboard snapshot."


def _builderdao_counting_guidance() -> str:
    return (
        "Downstream recipient detail only; do not add to treasury totals because the "
        f"parent TF1/on-chain payment is counted under {BUILDERDAO_PARENT_TF1_PROJECT_ID}."
    )


def _builderdao_match_score(current_name: str, recipient_name: str) -> float:
    score = _name_score(current_name, recipient_name)
    if score >= 0.74:
        return score
    return 0.0


def _make_tf1_reconciliation(
    tf1_projects: Sequence[dict[str, Any]],
    budget_2025_proposals: Sequence[dict[str, Any]],
) -> list[TF1ReconciliationRecord]:
    records: list[TF1ReconciliationRecord] = []
    for project in tf1_projects:
        scored = [
            (*_tf1_budget_2025_score(project, proposal), proposal)
            for proposal in budget_2025_proposals
        ]
        if not scored:
            continue
        score, basis, proposal = max(scored, key=lambda item: item[0])
        owner = _budget_2025_owner(proposal)
        budget_data = _budget_2025_data(proposal)
        records.append(
            TF1ReconciliationRecord(
                tf1_project_id=str(project.get("project_id") or ""),
                tf1_title=str(project.get("title") or ""),
                tf1_vendor_label=str(project.get("vendor_label") or ""),
                tf1_status=str(project.get("status") or ""),
                tf1_total_contract_ada=float(project.get("total_contract_ada") or 0),
                budget_2025_proposal_id=str(budget_data.get("id") or proposal.get("_id") or ""),
                budget_2025_title=str(proposal.get("name") or budget_data.get("name") or ""),
                budget_2025_cost_ada=float(budget_data.get("cost") or 0),
                match_score=score,
                match_confidence=_confidence(score, high=0.86, medium=0.68),
                match_basis=basis,
                company_name=str(owner.get("company_name") or ""),
                group_name=str(owner.get("group_name") or ""),
                social_handles=str(owner.get("social_handles") or ""),
                company_domain=str(owner.get("company_domain_name") or ""),
                public_champion=str(owner.get("proposal_public_champion") or ""),
                submitted_on_behalf=str(owner.get("submited_on_behalf") or ""),
                threshold_reached=str(proposal.get("thresholdReached") or False).lower(),
                source_url=_budget_2025_source_url(proposal),
            )
        )
    records.sort(key=lambda r: (_normalize_name(r.tf1_title), -r.match_score))
    return records


def _make_onchain_treasury_reconciliation(
    tf1_projects: Sequence[dict[str, Any]],
    onchain_withdrawals: Sequence[dict[str, Any]],
) -> list[OnchainTreasuryReconciliationRecord]:
    matched_by_onchain: dict[str, list[tuple[dict[str, Any], float, str, str]]] = defaultdict(list)
    possible_tf1_withdrawals = [
        withdrawal
        for withdrawal in onchain_withdrawals
        if int(withdrawal.get("proposed_epoch") or 0) <= 590
    ]
    for project in tf1_projects:
        candidates: list[tuple[float, str, str, float, float, dict[str, Any]]] = []
        for withdrawal in possible_tf1_withdrawals:
            score, confidence, basis, amount_score, direct_title_score = _tf1_onchain_score(
                project, withdrawal
            )
            if confidence != "low":
                candidates.append(
                    (score, confidence, basis, amount_score, direct_title_score, withdrawal)
                )
        if not candidates:
            continue
        if any(direct_title_score >= 0.86 for _, _, _, _, direct_title_score, _ in candidates):
            candidates = [candidate for candidate in candidates if candidate[4] >= 0.86]
        if any(amount_score >= 0.90 for _, _, _, amount_score, _, _ in candidates):
            candidates = [candidate for candidate in candidates if candidate[3] >= 0.90]
        best_score = max(score for score, *_ in candidates)
        for score, confidence, basis, _, _, withdrawal in candidates:
            if score < best_score - 0.02:
                continue
            onchain_id = str(
                withdrawal.get("withdrawal_action_id") or withdrawal.get("proposal_id") or ""
            )
            matched_by_onchain[onchain_id].append((project, score, confidence, basis))

    records: list[OnchainTreasuryReconciliationRecord] = []
    for withdrawal in onchain_withdrawals:
        onchain_id = str(
            withdrawal.get("withdrawal_action_id") or withdrawal.get("proposal_id") or ""
        )
        matches = matched_by_onchain.get(onchain_id, [])
        if any(confidence == "high" for _, _, confidence, _ in matches):
            matches = [match for match in matches if match[2] == "high"]
        tf1_total = sum(float(project.get("total_contract_ada") or 0) for project, *_ in matches)
        onchain_total = float(withdrawal.get("total_withdrawal_ada") or 0)
        if matches:
            confidences = [confidence for _, _, confidence, _ in matches]
            confidence = "medium" if "medium" in confidences else "high"
            score = min(score for _, score, _, _ in matches)
            guidance = (
                "TF1 overlap: use the on-chain row as the treasury action and TF1 rows for "
                "contract/milestone detail; do not add these amounts together."
            )
        else:
            confidence = "none"
            score = 0.0
            guidance = (
                "No TF1 overlap found in this archive; treat as an independent on-chain "
                "treasury withdrawal candidate unless another source reconciles it."
            )
        records.append(
            OnchainTreasuryReconciliationRecord(
                onchain_proposal_id=str(withdrawal.get("proposal_id") or onchain_id),
                onchain_title=str(withdrawal.get("title") or ""),
                onchain_status=str(withdrawal.get("status") or ""),
                onchain_total_withdrawal_ada=onchain_total,
                onchain_withdrawal_count=int(withdrawal.get("withdrawal_count") or 0),
                proposed_epoch=str(withdrawal.get("proposed_epoch") or ""),
                enacted_epoch=str(withdrawal.get("enacted_epoch") or ""),
                meta_url=str(withdrawal.get("meta_url") or ""),
                tf1_overlap="yes" if matches else "no",
                tf1_project_ids="; ".join(
                    str(project.get("project_id") or "") for project, *_ in matches
                ),
                tf1_titles="; ".join(str(project.get("title") or "") for project, *_ in matches),
                tf1_statuses="; ".join(str(project.get("status") or "") for project, *_ in matches),
                tf1_total_contract_ada=tf1_total,
                amount_delta_ada=onchain_total - tf1_total,
                match_confidence=confidence,
                match_score=score,
                match_basis="; ".join(
                    f"{project.get('project_id')}: {basis}" for project, _, _, basis in matches
                ),
                counting_guidance=guidance,
            )
        )
    records.sort(
        key=lambda r: (r.tf1_overlap != "yes", r.onchain_status, r.onchain_title.casefold())
    )
    return records


def _make_builderdao_disbursements(
    builderdao_projects: Sequence[dict[str, Any]],
    current: Sequence[CurrentProposal],
    tf1_projects: Sequence[dict[str, Any]],
) -> list[BuilderDAODisbursementRecord]:
    tf1_parent = next(
        (
            project
            for project in tf1_projects
            if str(project.get("project_id") or "") == BUILDERDAO_PARENT_TF1_PROJECT_ID
        ),
        {},
    )
    parent_title = str(tf1_parent.get("title") or "Cardano Builder DAO")
    records: list[BuilderDAODisbursementRecord] = []
    for project in builderdao_projects:
        if project.get("isFunded") is not True:
            continue
        recipient = str(project.get("name") or "")
        matched_names = sorted(
            {
                proposal.proposer_name
                for proposal in current
                if _builderdao_match_score(proposal.proposer_name, recipient) >= 0.74
                and (
                    _builderdao_match_score(proposal.proposer_name, recipient) >= 1.0
                    or _has_meaningful_name_overlap(proposal.proposer_name, recipient)
                )
            }
        )
        records.append(
            BuilderDAODisbursementRecord(
                recipient_name=recipient,
                project_slug=str(project.get("slug") or ""),
                round=int(project.get("round") or 0),
                funded="yes",
                downstream_amount_ada=float(project.get("fundsRequested") or 0),
                parent_tf1_project_id=BUILDERDAO_PARENT_TF1_PROJECT_ID,
                parent_tf1_title=parent_title,
                matched_tf2_proposer_names="; ".join(matched_names),
                metrics_summary=_builderdao_metrics_summary(project),
                proposal_url=str(project.get("proposalURL") or ""),
                website_url=str(project.get("websiteURL") or ""),
                source_url=BUILDERDAO_DASHBOARD_URL,
                counting_guidance=_builderdao_counting_guidance(),
            )
        )
    records.sort(key=lambda r: (r.round, -r.downstream_amount_ada, r.recipient_name.casefold()))
    return records


def _make_history(
    current: Sequence[CurrentProposal],
    catalyst_proposals: Sequence[dict[str, Any]],
    catalyst_proposers: Sequence[dict[str, Any]],
    catalyst_milestones: Sequence[dict[str, Any]],
    tf1_projects: Sequence[dict[str, Any]],
    tf1_vendors: Sequence[dict[str, Any]],
    tf1_milestones: Sequence[dict[str, Any]],
    tf1_reconciliation_records: Sequence[TF1ReconciliationRecord],
    builderdao_projects: Sequence[dict[str, Any]],
) -> list[HistoryRecord]:
    proposals_by_proposer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for proposal in catalyst_proposals:
        for proposer_id in proposal.get("proposer_ids") or []:
            proposals_by_proposer[str(proposer_id)].append(proposal)
    milestones_by_proposal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for milestone in catalyst_milestones:
        milestones_by_proposal[str(milestone.get("proposal_id") or "")].append(milestone)
    tf1_projects_by_vendor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for project in tf1_projects:
        tf1_projects_by_vendor[str(project.get("vendor_id") or "")].append(project)
    tf1_milestones_by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for milestone in tf1_milestones:
        tf1_milestones_by_project[str(milestone.get("project_id") or "")].append(milestone)
    tf1_projects_by_id = {str(project.get("project_id") or ""): project for project in tf1_projects}

    records: list[HistoryRecord] = []
    for current_proposal in current:
        seen_catalyst_ids: set[str] = set()
        seen_tf1_ids: set[str] = set()
        matches = _match_entities(current_proposal.proposer_name, catalyst_proposers, tf1_vendors)
        for match in matches:
            if match.source == "Project Catalyst":
                for proposal in proposals_by_proposer.get(match.entity_id, []):
                    if proposal.get("funding_status") not in FUNDED_STATUSES:
                        continue
                    proposal_id = str(proposal.get("proposal_id") or "")
                    seen_catalyst_ids.add(proposal_id)
                    project_status = str(proposal.get("project_status") or "")
                    records.append(
                        HistoryRecord(
                            current_proposal_id=current_proposal.proposal_id,
                            current_proposer_name=current_proposal.proposer_name,
                            source=match.source,
                            match_name=match.display_name,
                            match_score=match.score,
                            match_confidence=match.confidence,
                            historical_project_id=proposal_id,
                            historical_title=str(proposal.get("title") or ""),
                            historical_status=project_status,
                            funding_status=str(proposal.get("funding_status") or ""),
                            amount_ada=_amount_ada(proposal),
                            amount_original=_amount_original(proposal),
                            final_outputs=_final_outputs(proposal, milestones_by_proposal),
                            delivery_flags=_delivery_flags(proposal, milestones_by_proposal),
                            ongoing="yes" if project_status in ONGOING_PROJECT_STATUSES else "no",
                            source_url=_proposal_url(proposal),
                        )
                    )
            else:
                for project in tf1_projects_by_vendor.get(match.entity_id, []):
                    seen_tf1_ids.add(str(project.get("project_id") or ""))
                    status = str(project.get("status") or "")
                    amount_by_status = project.get("amount_by_milestone_status_ada")
                    flags = "No documented non-delivery signal in dataset."
                    if status in TF1_NEGATIVE_STATUSES:
                        status_amounts = json.dumps(amount_by_status, sort_keys=True)
                        flags = f"treasury_project_status={status}; {status_amounts}"
                    records.append(
                        HistoryRecord(
                            current_proposal_id=current_proposal.proposal_id,
                            current_proposer_name=current_proposal.proposer_name,
                            source=match.source,
                            match_name=match.display_name,
                            match_score=match.score,
                            match_confidence=match.confidence,
                            historical_project_id=str(project.get("project_id") or ""),
                            historical_title=str(project.get("title") or ""),
                            historical_status=status,
                            funding_status="contracted",
                            amount_ada=float(project.get("total_contract_ada") or 0),
                            amount_original=(
                                f"{float(project.get('total_contract_ada') or 0):,.2f} ADA"
                            ),
                            final_outputs=_tf1_outputs(project, tf1_milestones_by_project),
                            delivery_flags=flags,
                            ongoing="yes" if status in TF1_ONGOING_STATUSES else "no",
                            source_url=str(project.get("treasury_url") or ""),
                        )
                    )
        for reconciliation in tf1_reconciliation_records:
            if reconciliation.match_confidence == "low":
                continue
            tf1_project = tf1_projects_by_id.get(reconciliation.tf1_project_id)
            if not tf1_project or reconciliation.tf1_project_id in seen_tf1_ids:
                continue
            low_value_names = {
                "beneficiary listed above",
                "submission lead listed above",
            }
            identity_values = [
                value
                for value in _tf1_reconciliation_identity_values(reconciliation)
                if value and _normalize_name(value) not in low_value_names
            ]
            if not identity_values:
                continue
            scored = [
                (
                    max(
                        _name_score(current_proposal.proposer_name, value),
                        _name_in_text_score(current_proposal.proposer_name, value),
                    ),
                    value,
                )
                for value in identity_values
            ]
            score, match_name = max(scored, key=lambda item: item[0])
            if score < 0.74:
                continue
            if score < 1.0 and not _has_meaningful_name_overlap(
                current_proposal.proposer_name,
                match_name,
            ):
                continue
            status = str(tf1_project.get("status") or "")
            amount_by_status = tf1_project.get("amount_by_milestone_status_ada")
            flags = "No documented non-delivery signal in dataset."
            if status in TF1_NEGATIVE_STATUSES:
                status_amounts = json.dumps(amount_by_status, sort_keys=True)
                flags = f"treasury_project_status={status}; {status_amounts}"
            records.append(
                HistoryRecord(
                    current_proposal_id=current_proposal.proposal_id,
                    current_proposer_name=current_proposal.proposer_name,
                    source="Treasury Fund 1",
                    match_name=(
                        f"{match_name} via 2025 reconciliation "
                        f"({reconciliation.match_confidence}, {reconciliation.match_score:.2f})"
                    ),
                    match_score=score,
                    match_confidence=_confidence(score, high=0.92, medium=0.82),
                    historical_project_id=reconciliation.tf1_project_id,
                    historical_title=str(tf1_project.get("title") or ""),
                    historical_status=status,
                    funding_status="contracted",
                    amount_ada=float(tf1_project.get("total_contract_ada") or 0),
                    amount_original=f"{float(tf1_project.get('total_contract_ada') or 0):,.2f} ADA",
                    final_outputs=_tf1_outputs(tf1_project, tf1_milestones_by_project),
                    delivery_flags=flags,
                    ongoing="yes" if status in TF1_ONGOING_STATUSES else "no",
                    source_url=str(tf1_project.get("treasury_url") or ""),
                )
            )
            seen_tf1_ids.add(reconciliation.tf1_project_id)
        for proposal in catalyst_proposals:
            if proposal.get("funding_status") not in FUNDED_STATUSES:
                continue
            proposal_id = str(proposal.get("proposal_id") or "")
            if proposal_id in seen_catalyst_ids:
                continue
            score = _name_in_text_score(
                current_proposal.proposer_name,
                _text_for_proposal(proposal),
            )
            if score < 0.80:
                continue
            project_status = str(proposal.get("project_status") or "")
            records.append(
                HistoryRecord(
                    current_proposal_id=current_proposal.proposal_id,
                    current_proposer_name=current_proposal.proposer_name,
                    source="Project Catalyst",
                    match_name=f"{current_proposal.proposer_name} (proposal text mention)",
                    match_score=score,
                    match_confidence=_confidence(score, high=0.92, medium=0.82),
                    historical_project_id=proposal_id,
                    historical_title=str(proposal.get("title") or ""),
                    historical_status=project_status,
                    funding_status=str(proposal.get("funding_status") or ""),
                    amount_ada=_amount_ada(proposal),
                    amount_original=_amount_original(proposal),
                    final_outputs=_final_outputs(proposal, milestones_by_proposal),
                    delivery_flags=_delivery_flags(proposal, milestones_by_proposal),
                    ongoing="yes" if project_status in ONGOING_PROJECT_STATUSES else "no",
                    source_url=_proposal_url(proposal),
                )
            )
        for project in builderdao_projects:
            if project.get("isFunded") is not True:
                continue
            recipient = str(project.get("name") or "")
            score = _builderdao_match_score(current_proposal.proposer_name, recipient)
            if score < 0.74:
                continue
            if score < 1.0 and not _has_meaningful_name_overlap(
                current_proposal.proposer_name,
                recipient,
            ):
                continue
            amount = float(project.get("fundsRequested") or 0)
            round_number = int(project.get("round") or 0)
            records.append(
                HistoryRecord(
                    current_proposal_id=current_proposal.proposal_id,
                    current_proposer_name=current_proposal.proposer_name,
                    source="BuilderDAO downstream disbursement",
                    match_name=f"{recipient} via BuilderDAO KPI dashboard",
                    match_score=score,
                    match_confidence=_confidence(score, high=0.92, medium=0.82),
                    historical_project_id=_builderdao_project_id(project),
                    historical_title=f"BuilderDAO Round {round_number}: {recipient}",
                    historical_status="active",
                    funding_status="downstream_disbursement",
                    amount_ada=None,
                    amount_original=(
                        f"{amount:,.2f} ADA downstream; non-additive with "
                        f"{BUILDERDAO_PARENT_TF1_PROJECT_ID}"
                    ),
                    final_outputs=(
                        f"{_builderdao_counting_guidance()} KPI dashboard metrics: "
                        f"{_builderdao_metrics_summary(project)}"
                    ),
                    delivery_flags="No documented non-delivery signal in dataset.",
                    ongoing="yes",
                    source_url=BUILDERDAO_DASHBOARD_URL,
                )
            )
    records.sort(
        key=lambda r: (
            _normalize_name(r.current_proposer_name),
            r.source,
            -r.match_score,
            r.historical_project_id,
        )
    )
    return records


def _make_identity_bridge(
    current: Sequence[CurrentProposal],
    budget_2025_proposals: Sequence[dict[str, Any]],
) -> list[IdentityBridgeRecord]:
    records: list[IdentityBridgeRecord] = []
    for current_proposal in current:
        for proposal in budget_2025_proposals:
            identity_values = _budget_2025_identity_values(proposal)
            if not identity_values:
                continue
            scored = [
                (
                    max(
                        _name_score(current_proposal.proposer_name, value),
                        _name_in_text_score(current_proposal.proposer_name, value),
                    ),
                    value,
                )
                for value in identity_values
            ]
            score, match_name = max(scored, key=lambda item: item[0])
            if score < 0.74:
                continue
            if score < 1.0 and not _has_meaningful_name_overlap(
                current_proposal.proposer_name,
                match_name,
            ):
                continue
            owner = _budget_2025_owner(proposal)
            data = _budget_2025_data(proposal)
            records.append(
                IdentityBridgeRecord(
                    current_proposal_id=current_proposal.proposal_id,
                    current_title=current_proposal.title,
                    current_proposer_name=current_proposal.proposer_name,
                    budget_2025_proposal_id=str(data.get("id") or proposal.get("_id") or ""),
                    budget_2025_title=str(proposal.get("name") or data.get("name") or ""),
                    match_name=match_name,
                    match_score=score,
                    match_confidence=_confidence(score, high=0.92, medium=0.82),
                    company_name=str(owner.get("company_name") or ""),
                    group_name=str(owner.get("group_name") or ""),
                    social_handles=str(owner.get("social_handles") or ""),
                    company_domain=str(owner.get("company_domain_name") or ""),
                    public_champion=str(owner.get("proposal_public_champion") or ""),
                    submitted_on_behalf=str(owner.get("submited_on_behalf") or ""),
                    budget_2025_cost_ada=float(data.get("cost") or 0),
                    threshold_reached=str(proposal.get("thresholdReached") or False).lower(),
                    vote_summary=_budget_2025_vote_summary(proposal),
                    source_url=_budget_2025_source_url(proposal),
                )
            )
    records.sort(key=lambda r: (_normalize_name(r.current_proposer_name), -r.match_score))
    return records


def _build_tfidf_vectors(texts: Sequence[str]) -> list[dict[str, float]]:
    docs = [Counter(_tokenize(text)) for text in texts]
    df: Counter[str] = Counter()
    for doc in docs:
        df.update(doc.keys())
    total_docs = max(len(docs), 1)
    vectors: list[dict[str, float]] = []
    for doc in docs:
        vector: dict[str, float] = {}
        norm_sq = 0.0
        for token, count in doc.items():
            idf = math.log((1 + total_docs) / (1 + df[token])) + 1
            weight = (1 + math.log(count)) * idf
            vector[token] = weight
            norm_sq += weight * weight
        norm = math.sqrt(norm_sq) or 1.0
        vectors.append({token: weight / norm for token, weight in vector.items()})
    return vectors


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(weight * right.get(token, 0.0) for token, weight in left.items())


def _top_terms(left: str, right: str, limit: int = 8) -> str:
    overlap = set(_tokenize(left)) & set(_tokenize(right))
    return ", ".join(sorted(overlap)[:limit])


def _make_similarity(
    current: Sequence[CurrentProposal],
    catalyst_proposals: Sequence[dict[str, Any]],
    catalyst_milestones: Sequence[dict[str, Any]],
    tf1_projects: Sequence[dict[str, Any]],
    tf1_milestones: Sequence[dict[str, Any]],
    *,
    per_proposal_limit: int,
    min_similarity: float,
) -> list[SimilarityRecord]:
    completed_candidates: list[tuple[str, str, str, str, str, str]] = []
    milestones_by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for milestone in tf1_milestones:
        milestones_by_project[str(milestone.get("project_id") or "")].append(milestone)

    for proposal in catalyst_proposals:
        is_funded = proposal.get("funding_status") in FUNDED_STATUSES
        is_complete = proposal.get("project_status") in COMPLETED_PROJECT_STATUSES
        if is_funded and is_complete:
            completed_candidates.append(
                (
                    "Project Catalyst",
                    str(proposal.get("proposal_id") or ""),
                    str(proposal.get("title") or ""),
                    str(proposal.get("project_status") or ""),
                    _text_for_proposal(proposal),
                    _proposal_url(proposal),
                )
            )
    for project in tf1_projects:
        if project.get("status") == "complete":
            project_id = str(project.get("project_id") or "")
            completed_candidates.append(
                (
                    "Treasury Fund 1",
                    project_id,
                    str(project.get("title") or ""),
                    str(project.get("status") or ""),
                    _text_for_tf1_project(project, milestones_by_project.get(project_id, [])),
                    str(project.get("treasury_url") or ""),
                )
            )

    current_texts = [f"{p.title}\n{p.summary}" for p in current]
    candidate_texts = [candidate[4] for candidate in completed_candidates]
    vectors = _build_tfidf_vectors([*current_texts, *candidate_texts])
    current_vectors = vectors[: len(current_texts)]
    candidate_vectors = vectors[len(current_texts) :]

    records: list[SimilarityRecord] = []
    for idx, current_proposal in enumerate(current):
        scored: list[tuple[float, tuple[str, str, str, str, str, str], str]] = []
        for candidate_idx, candidate in enumerate(completed_candidates):
            score = _cosine(current_vectors[idx], candidate_vectors[candidate_idx])
            if score >= min_similarity:
                terms = _top_terms(current_texts[idx], candidate[4])
                scored.append((score, candidate, terms))
        scored.sort(key=lambda item: item[0], reverse=True)
        for score, candidate, terms in scored[:per_proposal_limit]:
            records.append(
                SimilarityRecord(
                    current_proposal_id=current_proposal.proposal_id,
                    current_title=current_proposal.title,
                    current_proposer_name=current_proposal.proposer_name,
                    source=candidate[0],
                    historical_project_id=candidate[1],
                    historical_title=candidate[2],
                    historical_status=candidate[3],
                    similarity=score,
                    confidence=_confidence(score, high=0.32, medium=0.20),
                    rationale=f"Shared terms: {terms}" if terms else "Sparse lexical overlap.",
                    source_url=candidate[5],
                )
            )
    records.sort(key=lambda r: (r.current_title.casefold(), -r.similarity))
    return records


def _write_csv(
    path: Path,
    rows: (
        Sequence[HistoryRecord]
        | Sequence[SimilarityRecord]
        | Sequence[IdentityBridgeRecord]
        | Sequence[TF1ReconciliationRecord]
        | Sequence[OnchainTreasuryReconciliationRecord]
        | Sequence[BuilderDAODisbursementRecord]
    ),
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    field_names = [field.name for field in fields(rows[0])]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=field_names)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in field_names})


def _summarize_history(
    records: Sequence[HistoryRecord],
    current: Sequence[CurrentProposal],
) -> dict[str, int]:
    proposers = {_normalize_name(p.proposer_name) for p in current}
    with_history = {_normalize_name(r.current_proposer_name) for r in records}
    return {
        "current_proposals": len(current),
        "current_unique_proposers": len(proposers),
        "proposers_with_prior_history": len(with_history),
        "history_records": len(records),
        "catalyst_history_records": sum(1 for r in records if r.source == "Project Catalyst"),
        "treasury_fund_1_history_records": sum(1 for r in records if r.source == "Treasury Fund 1"),
        "builderdao_downstream_history_records": sum(
            1 for r in records if r.source == "BuilderDAO downstream disbursement"
        ),
    }


def _write_history_md(
    path: Path,
    *,
    records: Sequence[HistoryRecord],
    current: Sequence[CurrentProposal],
    snapshot_fetched_at: str,
) -> None:
    by_proposer: dict[str, list[HistoryRecord]] = defaultdict(list)
    for record in records:
        by_proposer[record.current_proposer_name].append(record)
    lines = [
        "# Report 1: Treasury Fund 2 Proposer Funding History",
        "",
        f"Generated: {_utcnow_iso()}",
        f"Current Budget Process snapshot: {snapshot_fetched_at}",
        "",
        "Scope: the 69 live proposals from the Cardano Budget Process 2026 API. "
        "Prior history is matched against Project Catalyst and Treasury Fund 1.",
        "",
        "Delivery caveat: `failed/non-delivery signal` means a documented dataset signal "
        "such as cancelled/stalled Catalyst project status, rejected/stalled/withdrawn "
        "Catalyst milestones, or withdrawn/paused Treasury Fund 1 milestones. It is not "
        "a subjective performance judgment.",
        "",
        "Matching caveat: Project Catalyst proposer records in the interim archive are "
        "often anonymized. This report therefore uses direct proposer entity matches "
        "where possible, plus explicitly labeled proposal-text mentions for team names. "
        "Treasury Fund 1 proposer matches depend on named vendor records; address-only "
        "vendor records are not attributed to current teams.",
        "",
        "BuilderDAO caveat: BuilderDAO KPI dashboard rows are downstream recipient "
        "detail for the TF1 Cardano Builder DAO parent contract. They are shown with "
        "blank `amount_ada` and non-additive labels so TF1/on-chain parent funding is "
        "not counted twice.",
        "",
    ]
    summary = _summarize_history(records, current)
    lines.extend(
        [
            "## Summary",
            "",
            f"- Current proposals analyzed: {summary['current_proposals']}",
            f"- Unique proposer names analyzed: {summary['current_unique_proposers']}",
            f"- Proposers with matched prior history: {summary['proposers_with_prior_history']}",
            f"- Catalyst prior funding records: {summary['catalyst_history_records']}",
            "- Treasury Fund 1 prior funding records: "
            f"{summary['treasury_fund_1_history_records']}",
            "- BuilderDAO downstream detail records: "
            f"{summary['builderdao_downstream_history_records']}",
            "",
            "## Proposer Details",
            "",
        ]
    )
    for proposal in sorted(
        current,
        key=lambda p: (_normalize_name(p.proposer_name), p.title.casefold()),
    ):
        proposer_records = by_proposer.get(proposal.proposer_name, [])
        lines.extend(
            [
                f"### {proposal.proposer_name}",
                "",
                f"- Current proposal: {proposal.title}",
                f"- Current requested budget: {proposal.budget:,.2f} ADA",
            ]
        )
        if not proposer_records:
            lines.extend(["- Prior funded history found: none above matching threshold.", ""])
            continue
        total_ada = sum(r.amount_ada or 0 for r in proposer_records)
        ongoing = sum(1 for r in proposer_records if r.ongoing == "yes")
        flagged = sum(
            1
            for r in proposer_records
            if r.delivery_flags != "No documented non-delivery signal in dataset."
        )
        lines.extend(
            [
                f"- Matched prior records: {len(proposer_records)}",
                f"- Matched ADA-denominated total: {total_ada:,.2f} ADA",
                f"- Ongoing prior projects/contracts: {ongoing}",
                f"- Records with documented non-delivery signals: {flagged}",
                "",
            ]
        )
        for record in proposer_records:
            lines.extend(
                [
                    f"#### {record.source}: {record.historical_title}",
                    "",
                    "- Match: "
                    f"{record.match_name} ({record.match_confidence}, {record.match_score:.2f})",
                    f"- Amount: {record.amount_original}",
                    "- Status: "
                    f"{record.historical_status}; funding status: {record.funding_status}",
                    f"- Ongoing: {record.ongoing}",
                    f"- Failed/non-delivery signal: {record.delivery_flags}",
                    f"- Final documented outputs: {record.final_outputs}",
                    f"- Source: {record.source_url or 'not captured'}",
                    "",
                ]
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_similarity_md(
    path: Path,
    *,
    records: Sequence[SimilarityRecord],
    current: Sequence[CurrentProposal],
    snapshot_fetched_at: str,
) -> None:
    by_proposal: dict[str, list[SimilarityRecord]] = defaultdict(list)
    for record in records:
        by_proposal[record.current_proposal_id].append(record)
    lines = [
        "# Report 2: Treasury Fund 2 Similarity To Previously Completed Work",
        "",
        f"Generated: {_utcnow_iso()}",
        f"Current Budget Process snapshot: {snapshot_fetched_at}",
        "",
        "Method: lexical TF-IDF cosine similarity over current proposal title/summary "
        "against previously funded and completed Project Catalyst proposals plus "
        "completed Treasury Fund 1 projects. Similarity is a screening signal, not proof "
        "of duplication.",
        "",
        "Confidence bands: high >= 0.32, medium >= 0.20, low below 0.20. "
        "Rows below the configured minimum similarity threshold are omitted.",
        "",
        "## Proposal Details",
        "",
    ]
    for proposal in sorted(current, key=lambda p: p.title.casefold()):
        proposal_records = by_proposal.get(proposal.proposal_id, [])
        lines.extend(
            [
                f"### {proposal.title}",
                "",
                f"- Proposer: {proposal.proposer_name}",
                f"- Requested budget: {proposal.budget:,.2f} ADA",
            ]
        )
        if not proposal_records:
            lines.extend(["- Similar completed prior work found: none above threshold.", ""])
            continue
        for record in proposal_records:
            lines.extend(
                [
                    f"#### {record.source}: {record.historical_title}",
                    "",
                    f"- Similarity: {record.similarity:.3f} ({record.confidence})",
                    f"- Historical status: {record.historical_status}",
                    f"- Rationale: {record.rationale}",
                    f"- Source: {record.source_url or 'not captured'}",
                    "",
                ]
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_identity_bridge_md(
    path: Path,
    *,
    records: Sequence[IdentityBridgeRecord],
    current: Sequence[CurrentProposal],
    snapshot_fetched_at: str,
    budget_2025_fetched_at: str,
) -> None:
    by_proposer: dict[str, list[IdentityBridgeRecord]] = defaultdict(list)
    for record in records:
        by_proposer[record.current_proposer_name].append(record)
    lines = [
        "# Treasury Fund 2 Identity Bridge: 2025 Budget Reconciliation",
        "",
        f"Generated: {_utcnow_iso()}",
        f"Current Budget Process snapshot: {snapshot_fetched_at}",
        f"2025 Budget Reconciliation snapshot: {budget_2025_fetched_at or 'not available'}",
        "",
        "Purpose: connect 2026 Treasury Fund 2 proposer names to 2025 Budget "
        "Reconciliation owner metadata such as company name, domain, social handles, "
        "public champion, and vote threshold status. This is identity evidence only; "
        "it is not treated as proof of prior disbursement.",
        "",
        "## Summary",
        "",
        f"- Current proposals analyzed: {len(current)}",
        f"- Identity bridge records: {len(records)}",
        f"- Proposers with 2025 bridge evidence: {len(by_proposer)}",
        "",
        "## Bridge Details",
        "",
    ]
    for proposal in sorted(
        current,
        key=lambda p: (_normalize_name(p.proposer_name), p.title.casefold()),
    ):
        proposer_records = by_proposer.get(proposal.proposer_name, [])
        if not proposer_records:
            continue
        lines.extend(
            [
                f"### {proposal.proposer_name}",
                "",
                f"- Current proposal: {proposal.title}",
                f"- 2025 bridge records: {len(proposer_records)}",
                "",
            ]
        )
        for record in proposer_records:
            lines.extend(
                [
                    f"#### {record.budget_2025_title}",
                    "",
                    f"- Match: {record.match_name} "
                    f"({record.match_confidence}, {record.match_score:.2f})",
                    f"- Company: {record.company_name or 'not captured'}",
                    f"- Group: {record.group_name or 'not captured'}",
                    f"- Domain: {record.company_domain or 'not captured'}",
                    f"- Social handles: {record.social_handles or 'not captured'}",
                    f"- Public champion: {record.public_champion or 'not captured'}",
                    f"- 2025 requested budget: {record.budget_2025_cost_ada:,.2f} ADA",
                    f"- Threshold reached: {record.threshold_reached}",
                    f"- Vote summary: {record.vote_summary or 'not captured'}",
                    f"- Source: {record.source_url}",
                    "",
                ]
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_tf1_reconciliation_md(
    path: Path,
    *,
    records: Sequence[TF1ReconciliationRecord],
    tf1_projects: Sequence[dict[str, Any]],
    budget_2025_fetched_at: str,
) -> None:
    reconciled = {record.tf1_project_id for record in records}
    high = sum(1 for record in records if record.match_confidence == "high")
    medium = sum(1 for record in records if record.match_confidence == "medium")
    low = sum(1 for record in records if record.match_confidence == "low")
    lines = [
        "# Treasury Fund 1 To 2025 Ekklesia Reconciliation",
        "",
        f"Generated: {_utcnow_iso()}",
        f"2025 Budget Reconciliation snapshot: {budget_2025_fetched_at or 'not available'}",
        "",
        "Purpose: reconcile Treasury Fund 1 contract records from the Sundae Treasury "
        "site against the original 2025 Ekklesia budget-process proposal records. "
        "This supplies human-readable owner identity evidence for TF1 contracts whose "
        "treasury vendor field is only a payment address.",
        "",
        "Matching uses proposal-title similarity, requested/contracted ADA amount "
        "similarity, and owner metadata when available. Low-confidence rows are best "
        "candidates retained for manual review, not asserted identities. A matched "
        "Ekklesia proposal does not by itself prove milestone payment completion; "
        "payment state remains the TF1 milestone status from the treasury contract data.",
        "",
        "## Summary",
        "",
        f"- TF1 projects analyzed: {len(tf1_projects)}",
        f"- TF1 projects with 2025 Ekklesia candidate rows: {len(reconciled)}",
        f"- High-confidence reconciliations: {high}",
        f"- Medium-confidence reconciliations: {medium}",
        f"- Low-confidence reconciliations: {low}",
        "",
        "## Reconciliations",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"### {record.tf1_title}",
                "",
                f"- TF1 vendor label: {record.tf1_vendor_label}",
                f"- TF1 status: {record.tf1_status}",
                f"- TF1 contracted amount: {record.tf1_total_contract_ada:,.2f} ADA",
                f"- Ekklesia proposal: {record.budget_2025_title}",
                f"- Ekklesia requested amount: {record.budget_2025_cost_ada:,.2f} ADA",
                f"- Match: {record.match_confidence} ({record.match_score:.2f})",
                f"- Basis: {record.match_basis}",
                f"- Company: {record.company_name or 'not captured'}",
                f"- Group: {record.group_name or 'not captured'}",
                f"- Domain: {record.company_domain or 'not captured'}",
                f"- Social handles: {record.social_handles or 'not captured'}",
                f"- Public champion: {record.public_champion or 'not captured'}",
                f"- Threshold reached: {record.threshold_reached}",
                f"- Source: {record.source_url}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_onchain_treasury_reconciliation_md(
    path: Path,
    *,
    records: Sequence[OnchainTreasuryReconciliationRecord],
    onchain_fetched_at: str,
) -> None:
    overlap = [record for record in records if record.tf1_overlap == "yes"]
    independent = [record for record in records if record.tf1_overlap == "no"]
    high = sum(1 for record in overlap if record.match_confidence == "high")
    medium = sum(1 for record in overlap if record.match_confidence == "medium")
    matched_tf1_ids = {
        project_id
        for record in overlap
        for project_id in record.tf1_project_ids.split("; ")
        if project_id
    }
    lines = [
        "# On-chain Treasury Withdrawal Reconciliation",
        "",
        f"Generated: {_utcnow_iso()}",
        f"Koios TreasuryWithdrawals snapshot: {onchain_fetched_at or 'not available'}",
        "",
        "Purpose: identify which Cardano on-chain TreasuryWithdrawals governance actions "
        "overlap with Treasury Fund 1 records, so viewers can use the on-chain source "
        "without double-counting TF1 contract amounts.",
        "",
        "Counting policy: when an on-chain withdrawal overlaps TF1, count the on-chain "
        "row as the treasury action and use TF1 for contract and milestone details. Do "
        "not add the TF1 contract amount to the on-chain withdrawal amount. A negative "
        "amount delta usually means one TF1 contract is split across multiple on-chain "
        "withdrawal actions.",
        "",
        "## Summary",
        "",
        f"- On-chain TreasuryWithdrawals analyzed: {len(records)}",
        f"- On-chain withdrawals with TF1 overlap: {len(overlap)}",
        f"- On-chain withdrawals without TF1 overlap: {len(independent)}",
        f"- TF1 projects matched to on-chain withdrawals: {len(matched_tf1_ids)}",
        f"- High-confidence overlap rows: {high}",
        f"- Medium-confidence overlap rows: {medium}",
        "",
        "## Overlaps With Treasury Fund 1",
        "",
    ]
    for record in overlap:
        lines.extend(
            [
                f"### {record.onchain_title}",
                "",
                f"- On-chain status: {record.onchain_status}",
                f"- On-chain withdrawal amount: {record.onchain_total_withdrawal_ada:,.2f} ADA",
                f"- On-chain proposal id: {record.onchain_proposal_id}",
                f"- Proposed/enacted epochs: {record.proposed_epoch or 'not captured'} / "
                f"{record.enacted_epoch or 'not enacted'}",
                f"- TF1 project ids: {record.tf1_project_ids}",
                f"- TF1 titles: {record.tf1_titles}",
                f"- TF1 statuses: {record.tf1_statuses}",
                f"- TF1 contract total: {record.tf1_total_contract_ada:,.2f} ADA",
                f"- Amount delta (on-chain minus TF1): {record.amount_delta_ada:,.2f} ADA",
                f"- Match: {record.match_confidence} ({record.match_score:.2f})",
                f"- Basis: {record.match_basis}",
                f"- Counting guidance: {record.counting_guidance}",
                f"- Metadata: {record.meta_url or 'not captured'}",
                "",
            ]
        )
    lines.extend(["## No TF1 Overlap Found", ""])
    for record in independent:
        lines.extend(
            [
                f"### {record.onchain_title}",
                "",
                f"- On-chain status: {record.onchain_status}",
                f"- On-chain withdrawal amount: {record.onchain_total_withdrawal_ada:,.2f} ADA",
                f"- On-chain proposal id: {record.onchain_proposal_id}",
                f"- Proposed/enacted epochs: {record.proposed_epoch or 'not captured'} / "
                f"{record.enacted_epoch or 'not enacted'}",
                f"- Counting guidance: {record.counting_guidance}",
                f"- Metadata: {record.meta_url or 'not captured'}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_builderdao_disbursements_md(
    path: Path,
    *,
    records: Sequence[BuilderDAODisbursementRecord],
) -> None:
    total = sum(record.downstream_amount_ada for record in records)
    matched = [record for record in records if record.matched_tf2_proposer_names]
    lines = [
        "# BuilderDAO Downstream Disbursement Detail",
        "",
        f"Generated: {_utcnow_iso()}",
        f"Source dashboard: {BUILDERDAO_DASHBOARD_URL}",
        "",
        "Purpose: record BuilderDAO KPI dashboard recipient-level funding detail without "
        "double-counting the Treasury Fund 1 parent payment to Cardano Builder DAO.",
        "",
        "Counting policy: these rows are downstream attribution only. The treasury "
        f"amount is counted through parent TF1 project {BUILDERDAO_PARENT_TF1_PROJECT_ID}; "
        "do not add recipient amounts to TF1 or on-chain totals.",
        "",
        "## Summary",
        "",
        f"- Funded BuilderDAO recipient rows: {len(records)}",
        f"- Downstream amount shown by dashboard: {total:,.2f} ADA",
        f"- Recipient rows matching current TF2 proposer names: {len(matched)}",
        "",
        "## Disbursements",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"### Round {record.round}: {record.recipient_name}",
                "",
                f"- Downstream amount: {record.downstream_amount_ada:,.2f} ADA",
                f"- Parent TF1 project: {record.parent_tf1_project_id} - "
                f"{record.parent_tf1_title}",
                "- TF2 proposer match: "
                f"{record.matched_tf2_proposer_names or 'none in current TF2 snapshot'}",
                f"- KPI metrics: {record.metrics_summary}",
                f"- Proposal URL: {record.proposal_url or 'not captured'}",
                f"- Website: {record.website_url or 'not captured'}",
                f"- Counting guidance: {record.counting_guidance}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_reports(
    *,
    data_root: Path,
    report_root: Path,
    current_snapshot: Path,
    budget_2025_snapshot: Path,
    builderdao_snapshot: Path,
    per_proposal_limit: int,
    min_similarity: float,
) -> dict[str, object]:
    snapshot_fetched_at, current = _load_current(current_snapshot)
    budget_2025_fetched_at, budget_2025_proposals = _load_budget_2025(budget_2025_snapshot)
    builderdao_projects = _load_builderdao_projects(builderdao_snapshot)
    catalyst_proposals = _read_json_records(data_root / "consolidated" / "all_proposals.json")
    catalyst_proposers = _read_json_records(data_root / "consolidated" / "all_proposers.json")
    catalyst_milestones = _read_json_records(data_root / "consolidated" / "all_milestones.json")
    tf1_root = data_root / "historical" / "treasury-fund-01"
    tf1_projects = _read_json_records(tf1_root / "projects.json")
    tf1_vendors = _read_json_records(tf1_root / "vendors.json")
    tf1_milestones = _read_json_records(tf1_root / "milestones.json")
    tf1_reconciliation_records = _make_tf1_reconciliation(tf1_projects, budget_2025_proposals)
    onchain_root = data_root / "historical" / "cardano-treasury-withdrawals"
    onchain_withdrawals = _read_json_records(onchain_root / "withdrawals.json")
    onchain_meta = _read_json_dict(onchain_root / "_meta.json")
    onchain_reconciliation_records = _make_onchain_treasury_reconciliation(
        tf1_projects,
        onchain_withdrawals,
    )
    builderdao_disbursements = _make_builderdao_disbursements(
        builderdao_projects,
        current,
        tf1_projects,
    )

    history_records = _make_history(
        current,
        catalyst_proposals,
        catalyst_proposers,
        catalyst_milestones,
        tf1_projects,
        tf1_vendors,
        tf1_milestones,
        tf1_reconciliation_records,
        builderdao_projects,
    )
    similarity_records = _make_similarity(
        current,
        catalyst_proposals,
        catalyst_milestones,
        tf1_projects,
        tf1_milestones,
        per_proposal_limit=per_proposal_limit,
        min_similarity=min_similarity,
    )
    identity_bridge_records = _make_identity_bridge(current, budget_2025_proposals)

    report_root.mkdir(parents=True, exist_ok=True)
    _write_csv(report_root / "proposer-history.csv", history_records)
    _write_csv(report_root / "scope-similarity.csv", similarity_records)
    _write_csv(report_root / "identity-bridge-2025.csv", identity_bridge_records)
    _write_csv(report_root / "tf1-ekklesia-reconciliation.csv", tf1_reconciliation_records)
    _write_csv(
        report_root / "onchain-treasury-reconciliation.csv",
        onchain_reconciliation_records,
    )
    _write_csv(report_root / "builderdao-disbursements.csv", builderdao_disbursements)
    _write_history_md(
        report_root / "proposer-history.md",
        records=history_records,
        current=current,
        snapshot_fetched_at=snapshot_fetched_at,
    )
    _write_similarity_md(
        report_root / "scope-similarity.md",
        records=similarity_records,
        current=current,
        snapshot_fetched_at=snapshot_fetched_at,
    )
    _write_identity_bridge_md(
        report_root / "identity-bridge-2025.md",
        records=identity_bridge_records,
        current=current,
        snapshot_fetched_at=snapshot_fetched_at,
        budget_2025_fetched_at=budget_2025_fetched_at,
    )
    _write_tf1_reconciliation_md(
        report_root / "tf1-ekklesia-reconciliation.md",
        records=tf1_reconciliation_records,
        tf1_projects=tf1_projects,
        budget_2025_fetched_at=budget_2025_fetched_at,
    )
    _write_onchain_treasury_reconciliation_md(
        report_root / "onchain-treasury-reconciliation.md",
        records=onchain_reconciliation_records,
        onchain_fetched_at=str(onchain_meta.get("fetched_at") or ""),
    )
    _write_builderdao_disbursements_md(
        report_root / "builderdao-disbursements.md",
        records=builderdao_disbursements,
    )
    summary: dict[str, object] = {
        "generated_at": _utcnow_iso(),
        "current_snapshot": str(current_snapshot.relative_to(REPO_ROOT)),
        "current_snapshot_fetched_at": snapshot_fetched_at,
        "budget_2025_snapshot": str(budget_2025_snapshot.relative_to(REPO_ROOT)),
        "budget_2025_snapshot_fetched_at": budget_2025_fetched_at,
        "budget_2025_proposals": len(budget_2025_proposals),
        "builderdao_snapshot": str(builderdao_snapshot.relative_to(REPO_ROOT)),
        "builderdao_downstream_disbursements": len(builderdao_disbursements),
        "builderdao_downstream_total_ada_non_additive": sum(
            record.downstream_amount_ada for record in builderdao_disbursements
        ),
        "builderdao_tf2_matched_recipient_rows": sum(
            1 for record in builderdao_disbursements if record.matched_tf2_proposer_names
        ),
        **_summarize_history(history_records, current),
        "identity_bridge_2025_records": len(identity_bridge_records),
        "identity_bridge_2025_proposers": len(
            {_normalize_name(r.current_proposer_name) for r in identity_bridge_records}
        ),
        "tf1_ekklesia_reconciliation_records": len(tf1_reconciliation_records),
        "tf1_ekklesia_reconciliation_high_confidence": sum(
            1 for record in tf1_reconciliation_records if record.match_confidence == "high"
        ),
        "tf1_ekklesia_reconciliation_medium_confidence": sum(
            1 for record in tf1_reconciliation_records if record.match_confidence == "medium"
        ),
        "tf1_ekklesia_reconciliation_low_confidence": sum(
            1 for record in tf1_reconciliation_records if record.match_confidence == "low"
        ),
        "onchain_treasury_withdrawals": len(onchain_withdrawals),
        "onchain_treasury_reconciliation_records": len(onchain_reconciliation_records),
        "onchain_treasury_reconciliation_tf1_overlap_actions": sum(
            1 for record in onchain_reconciliation_records if record.tf1_overlap == "yes"
        ),
        "onchain_treasury_reconciliation_independent_actions": sum(
            1 for record in onchain_reconciliation_records if record.tf1_overlap == "no"
        ),
        "onchain_treasury_reconciliation_tf1_projects": len(
            {
                project_id
                for record in onchain_reconciliation_records
                for project_id in record.tf1_project_ids.split("; ")
                if project_id
            }
        ),
        "similarity_records": len(similarity_records),
        "similarity_min_threshold": min_similarity,
        "similarity_per_proposal_limit": per_proposal_limit,
    }
    _write_json(report_root / "_summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--current-snapshot", type=Path, default=CURRENT_SNAPSHOT)
    parser.add_argument("--budget-2025-snapshot", type=Path, default=BUDGET_2025_SNAPSHOT)
    parser.add_argument("--builderdao-snapshot", type=Path, default=BUILDERDAO_SNAPSHOT)
    parser.add_argument("--per-proposal-limit", type=int, default=5)
    parser.add_argument("--min-similarity", type=float, default=0.18)
    args = parser.parse_args(argv)
    try:
        summary = generate_reports(
            data_root=args.data_root,
            report_root=args.report_root,
            current_snapshot=args.current_snapshot,
            budget_2025_snapshot=args.budget_2025_snapshot,
            builderdao_snapshot=args.builderdao_snapshot,
            per_proposal_limit=args.per_proposal_limit,
            min_similarity=args.min_similarity,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps({"level": "ERROR", "msg": "fatal", "error": str(exc)}),
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"level": "INFO", "msg": "generated", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["generate_reports", "main"]
