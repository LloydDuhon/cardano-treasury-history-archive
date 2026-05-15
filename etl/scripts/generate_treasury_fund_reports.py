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

Outputs:
    reports/treasury-fund-2/proposer-history.md
    reports/treasury-fund-2/proposer-history.csv
    reports/treasury-fund-2/scope-similarity.md
    reports/treasury-fund-2/scope-similarity.csv
    reports/treasury-fund-2/identity-bridge-2025.csv
    reports/treasury-fund-2/identity-bridge-2025.md
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


def _match_entities(
    current_name: str,
    catalyst_proposers: Sequence[dict[str, Any]],
    tf1_vendors: Sequence[dict[str, Any]],
) -> list[NameMatch]:
    matches: list[NameMatch] = []
    for proposer in catalyst_proposers:
        name = str(proposer.get("display_name") or "")
        if _normalize_name(name) in {"anonymous", "unknown"}:
            continue
        score = _name_score(current_name, name)
        if score >= 0.74:
            matches.append(
                NameMatch(
                    source="Project Catalyst",
                    entity_id=str(proposer.get("proposer_id") or ""),
                    display_name=name,
                    score=score,
                    confidence=_confidence(score, high=0.92, medium=0.82),
                )
            )
    for vendor in tf1_vendors:
        name = str(vendor.get("display_name") or "")
        score = _name_score(current_name, name)
        if score >= 0.74:
            matches.append(
                NameMatch(
                    source="Treasury Fund 1",
                    entity_id=str(vendor.get("vendor_id") or ""),
                    display_name=name,
                    score=score,
                    confidence=_confidence(score, high=0.92, medium=0.82),
                )
            )
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


def _make_history(
    current: Sequence[CurrentProposal],
    catalyst_proposals: Sequence[dict[str, Any]],
    catalyst_proposers: Sequence[dict[str, Any]],
    catalyst_milestones: Sequence[dict[str, Any]],
    tf1_projects: Sequence[dict[str, Any]],
    tf1_vendors: Sequence[dict[str, Any]],
    tf1_milestones: Sequence[dict[str, Any]],
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

    records: list[HistoryRecord] = []
    for current_proposal in current:
        seen_catalyst_ids: set[str] = set()
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
    rows: Sequence[HistoryRecord] | Sequence[SimilarityRecord] | Sequence[IdentityBridgeRecord],
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


def generate_reports(
    *,
    data_root: Path,
    report_root: Path,
    current_snapshot: Path,
    budget_2025_snapshot: Path,
    per_proposal_limit: int,
    min_similarity: float,
) -> dict[str, object]:
    snapshot_fetched_at, current = _load_current(current_snapshot)
    budget_2025_fetched_at, budget_2025_proposals = _load_budget_2025(budget_2025_snapshot)
    catalyst_proposals = _read_json_records(data_root / "consolidated" / "all_proposals.json")
    catalyst_proposers = _read_json_records(data_root / "consolidated" / "all_proposers.json")
    catalyst_milestones = _read_json_records(data_root / "consolidated" / "all_milestones.json")
    tf1_root = data_root / "historical" / "treasury-fund-01"
    tf1_projects = _read_json_records(tf1_root / "projects.json")
    tf1_vendors = _read_json_records(tf1_root / "vendors.json")
    tf1_milestones = _read_json_records(tf1_root / "milestones.json")

    history_records = _make_history(
        current,
        catalyst_proposals,
        catalyst_proposers,
        catalyst_milestones,
        tf1_projects,
        tf1_vendors,
        tf1_milestones,
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
    summary: dict[str, object] = {
        "generated_at": _utcnow_iso(),
        "current_snapshot": str(current_snapshot.relative_to(REPO_ROOT)),
        "current_snapshot_fetched_at": snapshot_fetched_at,
        "budget_2025_snapshot": str(budget_2025_snapshot.relative_to(REPO_ROOT)),
        "budget_2025_snapshot_fetched_at": budget_2025_fetched_at,
        "budget_2025_proposals": len(budget_2025_proposals),
        **_summarize_history(history_records, current),
        "identity_bridge_2025_records": len(identity_bridge_records),
        "identity_bridge_2025_proposers": len(
            {_normalize_name(r.current_proposer_name) for r in identity_bridge_records}
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
    parser.add_argument("--per-proposal-limit", type=int, default=5)
    parser.add_argument("--min-similarity", type=float, default=0.18)
    args = parser.parse_args(argv)
    try:
        summary = generate_reports(
            data_root=args.data_root,
            report_root=args.report_root,
            current_snapshot=args.current_snapshot,
            budget_2025_snapshot=args.budget_2025_snapshot,
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
