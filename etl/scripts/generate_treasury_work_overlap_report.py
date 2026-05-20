"""Generate an AI-assisted prior-work overlap review for Treasury Fund 2.

The report has two stages:

1. Deterministic retrieval ranks historical Catalyst, TF1, on-chain treasury,
   and BuilderDAO records against each current TF2 proposal.
2. Optional OpenAI Responses API adjudication reviews the top candidates and
   estimates work-overlap percentage, funding relevance, and proposer relation.

Inputs:
    data/_raw/hydra_voting/cardano-budget-2026.json
    data/consolidated/all_proposals.json
    data/consolidated/all_proposers.json
    data/historical/treasury-fund-01/projects.json
    data/historical/treasury-fund-01/milestones.json
    data/historical/cardano-treasury-withdrawals/withdrawals.json
    data/_raw/builderdao_taptools/projects.json

Outputs:
    reports/treasury-fund-2/work-overlap-review-candidates.csv
    reports/treasury-fund-2/work-overlap-review-ai.jsonl
    reports/treasury-fund-2/work-overlap-review.csv
    reports/treasury-fund-2/work-overlap-review.md
    reports/treasury-fund-2/work-overlap-review-summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
DEFAULT_REPORT_ROOT = REPO_ROOT / "reports" / "treasury-fund-2"
CURRENT_SNAPSHOT = DEFAULT_DATA_ROOT / "_raw" / "hydra_voting" / "cardano-budget-2026.json"
BUILDERDAO_SNAPSHOT = DEFAULT_DATA_ROOT / "_raw" / "builderdao_taptools" / "projects.json"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
FUNDED_STATUSES = {"approved", "leftover"}
BUILDERDAO_PARENT_TF1_PROJECT_ID = "EMI-0004-25"
BUILDERDAO_SOURCE_URL = "https://cbdao.taptools.io/"
NO_AI_REVIEW = {
    "match_confidence": "not_reviewed",
    "work_overlap_percent": "",
    "overlap_type": "not_reviewed",
    "previously_proposed": "",
    "previously_funded_relevance": "not_reviewed",
    "same_or_related_proposer": "not_reviewed",
    "relationship_evidence": "AI review not run.",
    "overlap_evidence": "AI review not run.",
    "funding_evidence": "AI review not run.",
    "review_notes": "Run without --retrieval-only and with OPENAI_API_KEY to adjudicate.",
}
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
    "dao",
    "foundation",
    "group",
    "labs",
    "ltd",
    "network",
}


@dataclass(frozen=True)
class CurrentWork:
    current_proposal_id: str
    current_title: str
    current_proposer_name: str
    current_budget_ada: float
    current_status: str
    current_text: str


@dataclass(frozen=True)
class HistoricalWork:
    historical_source: str
    historical_project_id: str
    historical_title: str
    historical_status: str
    funding_status: str
    previously_funded: str
    amount_original: str
    historical_proposer_names: str
    historical_text: str
    source_url: str


@dataclass(frozen=True)
class CandidateRecord:
    current_proposal_id: str
    current_title: str
    current_proposer_name: str
    current_budget_ada: float
    historical_source: str
    historical_project_id: str
    historical_title: str
    historical_status: str
    funding_status: str
    previously_funded: str
    amount_original: str
    historical_proposer_names: str
    retrieval_rank: int
    retrieval_score: float
    body_similarity: float
    title_similarity: float
    keyphrase_overlap: float
    proposer_similarity: float
    shared_terms: str
    source_url: str


@dataclass(frozen=True)
class ReviewRecord:
    current_proposal_id: str
    current_title: str
    current_proposer_name: str
    current_budget_ada: float
    historical_source: str
    historical_project_id: str
    historical_title: str
    historical_status: str
    funding_status: str
    previously_funded: str
    amount_original: str
    historical_proposer_names: str
    retrieval_rank: int
    retrieval_score: float
    body_similarity: float
    title_similarity: float
    keyphrase_overlap: float
    proposer_similarity: float
    shared_terms: str
    match_confidence: str
    work_overlap_percent: int | str
    overlap_type: str
    previously_proposed: bool | str
    previously_funded_relevance: str
    same_or_related_proposer: str
    relationship_evidence: str
    overlap_evidence: str
    funding_evidence: str
    review_notes: str
    ai_model: str
    ai_reviewed_at: str
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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Sequence[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    field_names = [field.name for field in fields(rows[0])]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=field_names)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: getattr(row, name) for name in field_names})


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
    if "lido nation" in normalized:
        aliases.add("lido nation")
    if normalized == "no witness labs":
        aliases.add("nowitness labs")
    return {alias for alias in aliases if alias}


def _tokenize(value: str | None) -> list[str]:
    text = _strip_markdown_html(value or "").casefold()
    tokens = re.findall(r"[a-z0-9][a-z0-9-]{1,}", text)
    return [token for token in tokens if token not in STOPWORDS and len(token) > 2]


def _strip_markdown_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[#*_>`|~-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _join_text(parts: Iterable[Any]) -> str:
    values = [
        _strip_markdown_html(str(part))
        for part in parts
        if part is not None and str(part).strip()
    ]
    return "\n".join(values)


def _clip_text(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 24].rstrip() + "\n[... clipped ...]"


def _sequence_similarity(left: str, right: str) -> float:
    a = _normalize_name(left)
    b = _normalize_name(right)
    if not a or not b:
        return 0.0
    seq = SequenceMatcher(None, a, b).ratio()
    containment = 0.0
    if len(a) > 8 and a in b:
        containment = 0.95
    if len(b) > 8 and b in a:
        containment = 0.95
    return max(seq, containment, _token_jaccard(left, right))


def _token_jaccard(left: str, right: str) -> float:
    a = set(_tokenize(left))
    b = set(_tokenize(right))
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


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


def _proposer_score(current_name: str, historical_names: str, historical_text: str) -> float:
    names = [name.strip() for name in historical_names.split(";") if name.strip()]
    return max((_name_score(current_name, name) for name in names), default=0.0)


def _key_terms(value: str, limit: int = 30) -> set[str]:
    counts = Counter(_tokenize(value))
    generic = {
        "000",
        "2025",
        "2026",
        "ada",
        "also",
        "approved",
        "blockchain",
        "can",
        "community",
        "development",
        "ecosystem",
        "funding",
        "milestone",
        "new",
        "open",
        "support",
        "user",
        "users",
        "will",
        "work",
    }
    return {token for token, _ in counts.most_common(limit * 2) if token not in generic}


def _top_terms(left: str, right: str, limit: int = 10) -> str:
    generic = {
        "000",
        "2025",
        "2026",
        "ada",
        "also",
        "approved",
        "can",
        "community",
        "ecosystem",
        "new",
        "open",
        "users",
        "will",
    }
    overlap = sorted((set(_tokenize(left)) & set(_tokenize(right))) - generic)
    return ", ".join(overlap[:limit])


def _shared_term_text(left_tokens: set[str], right_tokens: set[str], limit: int = 10) -> str:
    generic = {
        "000",
        "2025",
        "2026",
        "ada",
        "also",
        "approved",
        "can",
        "community",
        "ecosystem",
        "new",
        "open",
        "users",
        "will",
    }
    return ", ".join(sorted((left_tokens & right_tokens) - generic)[:limit])


def _proposal_url(proposal: dict[str, Any]) -> str:
    links = proposal.get("links")
    links = links if isinstance(links, dict) else {}
    for key in (
        "lidonation_url",
        "projectcatalyst_io_url",
        "milestones_url",
        "catalyst_voices_url",
        "ideascale_url",
    ):
        value = links.get(key)
        if value:
            return str(value)
    return ""


def _amount_original(proposal: dict[str, Any]) -> str:
    amount = proposal.get("amount_received")
    if amount is None:
        amount = proposal.get("amount_requested")
    currency = proposal.get("currency") or "UNKNOWN"
    if amount is None:
        return f"unknown {currency}"
    return f"{float(amount):,.2f} {currency}"


def _load_current(snapshot_path: Path) -> list[CurrentWork]:
    snapshot = _read_json_dict(snapshot_path)
    response = snapshot.get("proposals_response")
    response = response if isinstance(response, dict) else {}
    proposals = response.get("data")
    if not isinstance(proposals, list):
        raise ValueError("Hydra voting snapshot missing proposals_response.data list")
    current: list[CurrentWork] = []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            continue
        metadata = proposal.get("metaData")
        metadata = metadata if isinstance(metadata, dict) else {}
        proposer = metadata.get("proposerDetails")
        proposer = proposer if isinstance(proposer, dict) else {}
        title = str(proposal.get("title") or "")
        summary = str(proposal.get("summary") or "")
        current.append(
            CurrentWork(
                current_proposal_id=str(proposal.get("_id") or ""),
                current_title=title,
                current_proposer_name=str(proposer.get("name") or ""),
                current_budget_ada=float(metadata.get("totalBudget") or 0),
                current_status=str(proposal.get("status") or ""),
                current_text=_join_text([title, summary]),
            )
        )
    return current


def _load_catalyst_candidates(
    proposals_path: Path,
    proposers_path: Path,
) -> list[HistoricalWork]:
    proposer_records = _read_json_records(proposers_path)
    proposer_names_by_id: dict[str, str] = {}
    for proposer in proposer_records:
        proposer_id = str(proposer.get("proposer_id") or "")
        name = str(proposer.get("display_name") or "")
        if proposer_id and name:
            proposer_names_by_id[proposer_id] = name

    works: list[HistoricalWork] = []
    for proposal in _read_json_records(proposals_path):
        proposer_names = [
            proposer_names_by_id.get(str(proposer_id), str(proposer_id))
            for proposer_id in proposal.get("proposer_ids") or []
        ]
        funding_status = str(proposal.get("funding_status") or "")
        funded = "yes" if funding_status in FUNDED_STATUSES else "no"
        title = str(proposal.get("title") or "")
        text = _join_text(
            [
                title,
                proposal.get("summary"),
                proposal.get("problem"),
                proposal.get("solution"),
                proposal.get("definition_of_success"),
                proposal.get("challenge"),
            ]
        )
        works.append(
            HistoricalWork(
                historical_source="Project Catalyst",
                historical_project_id=str(proposal.get("proposal_id") or ""),
                historical_title=title,
                historical_status=str(proposal.get("project_status") or ""),
                funding_status=funding_status,
                previously_funded=funded,
                amount_original=_amount_original(proposal),
                historical_proposer_names="; ".join(proposer_names),
                historical_text=text,
                source_url=_proposal_url(proposal),
            )
        )
    return works


def _load_tf1_candidates(root: Path) -> list[HistoricalWork]:
    projects = _read_json_records(root / "projects.json")
    milestones = _read_json_records(root / "milestones.json")
    milestones_by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for milestone in milestones:
        milestones_by_project[str(milestone.get("project_id") or "")].append(milestone)

    works: list[HistoricalWork] = []
    for project in projects:
        project_id = str(project.get("project_id") or "")
        milestone_parts: list[str] = []
        for milestone in milestones_by_project.get(project_id, []):
            milestone_parts.extend(
                [
                    milestone.get("title") or "",
                    milestone.get("description") or "",
                    milestone.get("acceptance_criteria") or "",
                ]
            )
        milestone_text = _join_text(milestone_parts)
        title = str(project.get("title") or "")
        amount = float(project.get("total_contract_ada") or 0)
        works.append(
            HistoricalWork(
                historical_source="Treasury Fund 1",
                historical_project_id=project_id,
                historical_title=title,
                historical_status=str(project.get("status") or ""),
                funding_status="contracted",
                previously_funded="yes",
                amount_original=f"{amount:,.2f} ADA",
                historical_proposer_names=str(project.get("vendor_label") or ""),
                historical_text=_join_text([title, project.get("description"), milestone_text]),
                source_url=str(project.get("treasury_url") or ""),
            )
        )
    return works


def _load_onchain_candidates(path: Path) -> list[HistoricalWork]:
    works: list[HistoricalWork] = []
    for withdrawal in _read_json_records(path):
        title = str(withdrawal.get("title") or "")
        amount = float(withdrawal.get("total_withdrawal_ada") or 0)
        works.append(
            HistoricalWork(
                historical_source="On-chain TreasuryWithdrawals",
                historical_project_id=str(
                    withdrawal.get("withdrawal_action_id") or withdrawal.get("proposal_id") or ""
                ),
                historical_title=title,
                historical_status=str(withdrawal.get("status") or ""),
                funding_status="withdrawal_action",
                previously_funded="yes",
                amount_original=f"{amount:,.2f} ADA",
                historical_proposer_names="",
                historical_text=_join_text(
                    [
                        title,
                        withdrawal.get("abstract"),
                        withdrawal.get("motivation"),
                        withdrawal.get("rationale"),
                    ]
                ),
                source_url=str(withdrawal.get("meta_url") or ""),
            )
        )
    return works


def _load_builderdao_candidates(path: Path) -> list[HistoricalWork]:
    if not path.exists():
        return []
    snapshot = _read_json_dict(path)
    projects = snapshot.get("data")
    if not isinstance(projects, list):
        raise ValueError("BuilderDAO snapshot missing data list")
    works: list[HistoricalWork] = []
    for project in projects:
        if not isinstance(project, dict) or project.get("isFunded") is not True:
            continue
        recipient = str(project.get("name") or "")
        amount = float(project.get("fundsRequested") or 0)
        metrics = project.get("metrics")
        metric_text = ""
        if isinstance(metrics, list):
            metric_text = _join_text(
                f"{m.get('label') or m.get('key')}: {m.get('value')} goal {m.get('goal')}"
                for m in metrics
                if isinstance(m, dict)
            )
        slug = str(project.get("slug") or _normalize_name(recipient).replace(" ", "-"))
        works.append(
            HistoricalWork(
                historical_source="BuilderDAO downstream disbursement",
                historical_project_id=f"builderdao-{slug}",
                historical_title=f"BuilderDAO Round {int(project.get('round') or 0)}: {recipient}",
                historical_status="active",
                funding_status="downstream_disbursement",
                previously_funded="non_additive",
                amount_original=(
                    f"{amount:,.2f} ADA downstream; non-additive with "
                    f"{BUILDERDAO_PARENT_TF1_PROJECT_ID}"
                ),
                historical_proposer_names=recipient,
                historical_text=_join_text(
                    [
                        recipient,
                        project.get("description"),
                        project.get("websiteURL"),
                        metric_text,
                    ]
                ),
                source_url=BUILDERDAO_SOURCE_URL,
            )
        )
    return works


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


def _retrieve_candidates(
    current: Sequence[CurrentWork],
    historical: Sequence[HistoricalWork],
    *,
    top_k: int,
) -> list[CandidateRecord]:
    vectors = _build_tfidf_vectors(
        [proposal.current_text for proposal in current]
        + [candidate.historical_text for candidate in historical]
    )
    current_vectors = vectors[: len(current)]
    historical_vectors = vectors[len(current) :]
    current_key_terms = [set(_key_terms(proposal.current_text)) for proposal in current]
    historical_key_terms = [set(_key_terms(candidate.historical_text)) for candidate in historical]
    current_tokens = [set(_tokenize(proposal.current_text)) for proposal in current]
    historical_tokens = [set(_tokenize(candidate.historical_text)) for candidate in historical]

    records: list[CandidateRecord] = []
    for current_idx, current_work in enumerate(current):
        prelim: list[tuple[float, int, float, float]] = []
        current_terms = current_key_terms[current_idx]
        current_token_set = current_tokens[current_idx]
        for candidate_idx, _candidate in enumerate(historical):
            body_similarity = _cosine(
                current_vectors[current_idx],
                historical_vectors[candidate_idx],
            )
            historical_terms = historical_key_terms[candidate_idx]
            keyphrase_overlap = (
                len(current_terms & historical_terms) / len(current_terms | historical_terms)
                if current_terms and historical_terms
                else 0.0
            )
            prelim_score = (body_similarity * 0.82) + (keyphrase_overlap * 0.18)
            prelim.append((prelim_score, candidate_idx, body_similarity, keyphrase_overlap))

        preselect_k = max(top_k * 20, 300)
        scored: list[tuple[float, HistoricalWork, float, float, float, float, str]] = []
        for _, candidate_idx, body_similarity, keyphrase_overlap in sorted(
            prelim,
            key=lambda item: item[0],
            reverse=True,
        )[:preselect_k]:
            candidate = historical[candidate_idx]
            title_similarity = _sequence_similarity(
                current_work.current_title,
                candidate.historical_title,
            )
            proposer_similarity = _proposer_score(
                current_work.current_proposer_name,
                candidate.historical_proposer_names,
                candidate.historical_text,
            )
            shared_terms = _shared_term_text(current_token_set, historical_tokens[candidate_idx])
            score = (
                (body_similarity * 0.52)
                + (title_similarity * 0.26)
                + (keyphrase_overlap * 0.14)
                + (proposer_similarity * 0.08)
            )
            scored.append(
                (
                    score,
                    candidate,
                    body_similarity,
                    title_similarity,
                    keyphrase_overlap,
                    proposer_similarity,
                    shared_terms,
                )
            )
        scored.sort(key=lambda item: item[0], reverse=True)
        for rank, item in enumerate(scored[:top_k], start=1):
            (
                score,
                candidate,
                body_similarity,
                title_similarity,
                keyphrase_overlap,
                proposer_similarity,
                shared_terms,
            ) = item
            records.append(
                CandidateRecord(
                    current_proposal_id=current_work.current_proposal_id,
                    current_title=current_work.current_title,
                    current_proposer_name=current_work.current_proposer_name,
                    current_budget_ada=current_work.current_budget_ada,
                    historical_source=candidate.historical_source,
                    historical_project_id=candidate.historical_project_id,
                    historical_title=candidate.historical_title,
                    historical_status=candidate.historical_status,
                    funding_status=candidate.funding_status,
                    previously_funded=candidate.previously_funded,
                    amount_original=candidate.amount_original,
                    historical_proposer_names=candidate.historical_proposer_names,
                    retrieval_rank=rank,
                    retrieval_score=score,
                    body_similarity=body_similarity,
                    title_similarity=title_similarity,
                    keyphrase_overlap=keyphrase_overlap,
                    proposer_similarity=proposer_similarity,
                    shared_terms=shared_terms,
                    source_url=candidate.source_url,
                )
            )
    return records


def _candidate_key(candidate: CandidateRecord) -> tuple[str, str, str]:
    return (
        candidate.current_proposal_id,
        candidate.historical_source,
        candidate.historical_project_id,
    )


def _history_by_key(historical: Sequence[HistoricalWork]) -> dict[tuple[str, str], HistoricalWork]:
    return {
        (work.historical_source, work.historical_project_id): work
        for work in historical
    }


def _current_by_id(current: Sequence[CurrentWork]) -> dict[str, CurrentWork]:
    return {work.current_proposal_id: work for work in current}


def _ai_schema() -> dict[str, Any]:
    return {
        "name": "work_overlap_review",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "match_confidence": {
                    "type": "string",
                    "enum": ["none", "low", "medium", "high"],
                },
                "work_overlap_percent": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                },
                "overlap_type": {
                    "type": "string",
                    "enum": [
                        "same_work",
                        "significant_partial",
                        "adjacent_related",
                        "generic_domain",
                        "no_match",
                    ],
                },
                "previously_proposed": {"type": "boolean"},
                "previously_funded_relevance": {
                    "type": "string",
                    "enum": ["none", "partial", "substantial", "full", "non_additive_detail"],
                },
                "same_or_related_proposer": {
                    "type": "string",
                    "enum": ["same", "related", "possible", "different", "unknown"],
                },
                "relationship_evidence": {"type": "string"},
                "overlap_evidence": {"type": "string"},
                "funding_evidence": {"type": "string"},
                "review_notes": {"type": "string"},
            },
            "required": [
                "match_confidence",
                "work_overlap_percent",
                "overlap_type",
                "previously_proposed",
                "previously_funded_relevance",
                "same_or_related_proposer",
                "relationship_evidence",
                "overlap_evidence",
                "funding_evidence",
                "review_notes",
            ],
        },
    }


def _ai_prompt(
    candidate: CandidateRecord,
    current_work: CurrentWork,
    historical_work: HistoricalWork,
) -> str:
    return (
        "You are reviewing Cardano treasury proposals for prior-work overlap.\n"
        "Decide whether the current proposal body of work was proposed before, "
        "whether previously funded work covers all or a significant portion of it, "
        "and whether the proposer appears to be the same or related.\n\n"
        "Use these definitions:\n"
        "- high confidence: same work or clearly substantial reuse, overlap >= 60%.\n"
        "- medium confidence: significant component reuse, overlap 30-59%.\n"
        "- low confidence: adjacent/weak overlap, overlap 10-29%.\n"
        "- none: no meaningful work overlap.\n"
        "- work_overlap_percent estimates the share of current work covered by the "
        "historical candidate, not textual similarity.\n"
        "- BuilderDAO downstream rows are non-additive funding detail.\n\n"
        "Retrieval signals are only hints. Base the final judgment on the text.\n\n"
        f"CURRENT PROPOSAL ID: {candidate.current_proposal_id}\n"
        f"CURRENT TITLE: {candidate.current_title}\n"
        f"CURRENT PROPOSER: {candidate.current_proposer_name}\n"
        f"CURRENT BUDGET ADA: {candidate.current_budget_ada:,.2f}\n"
        f"CURRENT TEXT:\n{_clip_text(current_work.current_text, 5000)}\n\n"
        f"HISTORICAL SOURCE: {candidate.historical_source}\n"
        f"HISTORICAL ID: {candidate.historical_project_id}\n"
        f"HISTORICAL TITLE: {candidate.historical_title}\n"
        f"HISTORICAL STATUS: {candidate.historical_status}\n"
        f"HISTORICAL FUNDING STATUS: {candidate.funding_status}\n"
        f"PREVIOUSLY FUNDED: {candidate.previously_funded}\n"
        f"AMOUNT: {candidate.amount_original}\n"
        f"HISTORICAL PROPOSER/RECIPIENT NAMES: {candidate.historical_proposer_names}\n"
        f"HISTORICAL TEXT:\n{_clip_text(historical_work.historical_text, 5000)}\n\n"
        "RETRIEVAL SIGNALS:\n"
        f"- rank: {candidate.retrieval_rank}\n"
        f"- score: {candidate.retrieval_score:.3f}\n"
        f"- body_similarity: {candidate.body_similarity:.3f}\n"
        f"- title_similarity: {candidate.title_similarity:.3f}\n"
        f"- keyphrase_overlap: {candidate.keyphrase_overlap:.3f}\n"
        f"- proposer_similarity: {candidate.proposer_similarity:.3f}\n"
        f"- shared_terms: {candidate.shared_terms}\n"
    )


def _validate_ai_payload(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("relationship_evidence", "overlap_evidence", "funding_evidence", "review_notes"):
        payload.setdefault(key, "")
    required = _ai_schema()["schema"]["required"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"AI review JSON missing required keys: {', '.join(missing)}")
    payload = {key: payload[key] for key in required}
    confidence_map = {
        "no": "none",
        "no match": "none",
        "low confidence": "low",
        "medium confidence": "medium",
        "high confidence": "high",
    }
    overlap_map = {
        "none": "no_match",
        "no overlap": "no_match",
        "no match": "no_match",
        "adjacent/weak overlap": "adjacent_related",
        "adjacent overlap": "adjacent_related",
        "substantial reuse": "same_work",
        "significant component reuse": "significant_partial",
    }
    funding_map = {
        "no": "none",
        "not funded": "none",
        "comprehensive": "full",
    }
    relationship_map = {
        True: "same",
        False: "different",
        "not related": "different",
        "no": "different",
        "yes": "same",
    }
    for key, mapping in (
        ("match_confidence", confidence_map),
        ("overlap_type", overlap_map),
        ("previously_funded_relevance", funding_map),
        ("same_or_related_proposer", relationship_map),
    ):
        value = payload[key]
        normalized = str(value).strip().casefold() if not isinstance(value, bool) else value
        payload[key] = mapping.get(normalized, payload[key])
    percent_text = str(payload["work_overlap_percent"])
    percent_match = re.search(r"\d+", percent_text)
    payload["work_overlap_percent"] = int(percent_match.group(0)) if percent_match else 0
    payload["work_overlap_percent"] = max(0, min(payload["work_overlap_percent"], 100))
    if payload["match_confidence"] not in {"none", "low", "medium", "high"}:
        if payload["work_overlap_percent"] >= 60:
            payload["match_confidence"] = "high"
        elif payload["work_overlap_percent"] >= 30:
            payload["match_confidence"] = "medium"
        elif payload["work_overlap_percent"] >= 10:
            payload["match_confidence"] = "low"
        else:
            payload["match_confidence"] = "none"
    if payload["overlap_type"] not in {
        "same_work",
        "significant_partial",
        "adjacent_related",
        "generic_domain",
        "no_match",
    }:
        payload["overlap_type"] = (
            "no_match" if payload["work_overlap_percent"] == 0 else "adjacent_related"
        )
    if payload["previously_funded_relevance"] not in {
        "none",
        "partial",
        "substantial",
        "full",
        "non_additive_detail",
    }:
        payload["previously_funded_relevance"] = "none"
    if payload["same_or_related_proposer"] not in {
        "same",
        "related",
        "possible",
        "different",
        "unknown",
    }:
        payload["same_or_related_proposer"] = "unknown"
    if isinstance(payload["previously_proposed"], str):
        payload["previously_proposed"] = payload["previously_proposed"].strip().casefold() in {
            "true",
            "yes",
            "1",
        }
    else:
        payload["previously_proposed"] = bool(payload["previously_proposed"])
    return payload


def _extract_json_text(value: str) -> dict[str, Any]:
    text = value.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def _extract_response_json(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("output_parsed"), dict):
        return payload["output_parsed"]
    output = payload.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if isinstance(part.get("parsed"), dict):
                    return part["parsed"]
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    return _extract_json_text(text)
    text = payload.get("output_text")
    if isinstance(text, str) and text.strip():
        return _extract_json_text(text)
    raise ValueError("OpenAI response did not include parseable JSON")


def _review_candidate_with_openai(
    client: Any,  # noqa: ANN401
    *,
    api_key: str,
    model: str,
    candidate: CandidateRecord,
    current_work: CurrentWork,
    historical_work: HistoricalWork,
    timeout_seconds: float,
    retries: int,
) -> dict[str, Any]:
    request_payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": (
                    "Return only the requested structured JSON. Be conservative: "
                    "do not treat generic domain similarity as funded overlap."
                ),
            },
            {"role": "user", "content": _ai_prompt(candidate, current_work, historical_work)},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                **_ai_schema(),
            }
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    for attempt in range(retries + 1):
        try:
            response = client.post(
                OPENAI_RESPONSES_URL,
                headers=headers,
                json=request_payload,
                timeout=timeout_seconds,
            )
            response.raise_for_status()
            return _validate_ai_payload(_extract_response_json(response.json()))
        except Exception as exc:
            if attempt >= retries:
                raise RuntimeError(
                    f"OpenAI review failed for {candidate.current_proposal_id} / "
                    f"{candidate.historical_project_id}: {exc}"
                ) from exc
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


class _StdlibResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            text = self.body.decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {self.status_code}: {text}")

    def json(self) -> dict[str, Any]:
        payload = json.loads(self.body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Expected HTTP response JSON object")
        return payload


class _StdlibHttpClient:
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> _StdlibResponse:
        request_headers = dict(headers or {})
        request_headers.setdefault("Content-Type", "application/json")
        data = None if json is None else __import__("json").dumps(json).encode("utf-8")
        request = urllib.request.Request(  # noqa: S310
            url,
            data=data,
            headers=request_headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                return _StdlibResponse(response.status, response.read())
        except urllib.error.HTTPError as exc:
            return _StdlibResponse(exc.code, exc.read())

    def close(self) -> None:
        return None


def _new_http_client() -> Any:  # noqa: ANN401
    try:
        import httpx
    except ImportError:
        return _StdlibHttpClient()
    return httpx.Client()


def _review_candidate_with_ollama(
    client: Any,  # noqa: ANN401
    *,
    base_url: str,
    model: str,
    candidate: CandidateRecord,
    current_work: CurrentWork,
    historical_work: HistoricalWork,
    timeout_seconds: float,
    retries: int,
) -> dict[str, Any]:
    request_payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "think": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only one valid JSON object matching the requested keys. "
                    "Do not include markdown, chain-of-thought, or commentary. Be conservative: "
                    "do not treat generic domain similarity as funded overlap."
                ),
            },
            {
                "role": "user",
                "content": (
                    _ai_prompt(candidate, current_work, historical_work)
                    + "\nReturn JSON with exactly these keys: "
                    + ", ".join(_ai_schema()["schema"]["required"])
                ),
            },
        ],
        "options": {
            "temperature": 0.1,
            "num_predict": 2000,
        },
    }
    url = base_url.rstrip("/") + "/api/chat"
    for attempt in range(retries + 1):
        try:
            response = client.post(url, json=request_payload, timeout=timeout_seconds)
            response.raise_for_status()
            payload = response.json()
            message = payload.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                raise ValueError("Ollama response did not include message.content")
            return _validate_ai_payload(_extract_json_text(message["content"]))
        except Exception as exc:
            if attempt >= retries:
                raise RuntimeError(
                    f"Ollama review failed for {candidate.current_proposal_id} / "
                    f"{candidate.historical_project_id}: {exc}"
                ) from exc
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def _load_existing_ai_reviews(path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    reviews: dict[tuple[str, str, str], dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            payload = json.loads(line)
            key = (
                str(payload.get("current_proposal_id") or ""),
                str(payload.get("historical_source") or ""),
                str(payload.get("historical_project_id") or ""),
            )
            reviews[key] = payload
    return reviews


def _append_ai_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def _review_candidates(
    candidates: Sequence[CandidateRecord],
    current: Sequence[CurrentWork],
    historical: Sequence[HistoricalWork],
    *,
    out_jsonl: Path,
    retrieval_only: bool,
    existing_ai_only: bool,
    ai_provider: str,
    model: str,
    api_key: str,
    ollama_url: str,
    timeout_seconds: float,
    retries: int,
    resume: bool,
) -> list[ReviewRecord]:
    current_lookup = _current_by_id(current)
    historical_lookup = _history_by_key(historical)
    existing = _load_existing_ai_reviews(out_jsonl) if resume else {}
    reviewed: list[ReviewRecord] = []
    client = None
    new_reviews = 0
    if not retrieval_only and not existing_ai_only:
        client = _new_http_client()
    try:
        total_candidates = len(candidates)
        for idx, candidate in enumerate(candidates, start=1):
            key = _candidate_key(candidate)
            current_work = current_lookup[candidate.current_proposal_id]
            historical_work = historical_lookup[
                (candidate.historical_source, candidate.historical_project_id)
            ]
            if retrieval_only:
                ai_payload = dict(NO_AI_REVIEW)
                ai_model = ""
                reviewed_at = ""
            elif key in existing:
                ai_payload = {
                    k: existing[key].get(k, "")
                    for k in NO_AI_REVIEW
                    if k in existing[key]
                }
                ai_model = str(existing[key].get("ai_model") or model)
                reviewed_at = str(existing[key].get("ai_reviewed_at") or "")
            elif existing_ai_only:
                ai_payload = dict(NO_AI_REVIEW)
                ai_model = ""
                reviewed_at = ""
            else:
                if client is None:
                    raise AssertionError("AI client missing outside retrieval-only mode")
                if ai_provider == "ollama":
                    ai_payload = _review_candidate_with_ollama(
                        client,
                        base_url=ollama_url,
                        model=model,
                        candidate=candidate,
                        current_work=current_work,
                        historical_work=historical_work,
                        timeout_seconds=timeout_seconds,
                        retries=retries,
                    )
                else:
                    ai_payload = _review_candidate_with_openai(
                        client,
                        api_key=api_key,
                        model=model,
                        candidate=candidate,
                        current_work=current_work,
                        historical_work=historical_work,
                        timeout_seconds=timeout_seconds,
                        retries=retries,
                    )
                ai_model = model
                reviewed_at = _utcnow_iso()
                new_reviews += 1
                _append_ai_jsonl(
                    out_jsonl,
                    {
                        **asdict(candidate),
                        **ai_payload,
                        "ai_model": ai_model,
                        "ai_reviewed_at": reviewed_at,
                    },
                )
                if idx % 25 == 0 or idx == total_candidates:
                    print(
                        json.dumps(
                            {
                                "level": "INFO",
                                "msg": "ai_review_progress",
                                "candidate_position": idx,
                                "candidate_pairs": total_candidates,
                                "new_reviews_in_this_run": new_reviews,
                            },
                            sort_keys=True,
                        ),
                        file=sys.stderr,
                    )
            reviewed.append(
                ReviewRecord(
                    **asdict(candidate),
                    match_confidence=ai_payload["match_confidence"],
                    work_overlap_percent=ai_payload["work_overlap_percent"],
                    overlap_type=ai_payload["overlap_type"],
                    previously_proposed=ai_payload["previously_proposed"],
                    previously_funded_relevance=ai_payload["previously_funded_relevance"],
                    same_or_related_proposer=ai_payload["same_or_related_proposer"],
                    relationship_evidence=ai_payload["relationship_evidence"],
                    overlap_evidence=ai_payload["overlap_evidence"],
                    funding_evidence=ai_payload["funding_evidence"],
                    review_notes=ai_payload["review_notes"],
                    ai_model=ai_model,
                    ai_reviewed_at=reviewed_at,
                )
            )
    finally:
        if client is not None:
            client.close()
    return reviewed


def _review_sort_key(record: ReviewRecord) -> tuple[int, int, float]:
    confidence_rank = {"high": 0, "medium": 1, "low": 2, "none": 3, "not_reviewed": 4}
    try:
        overlap = int(record.work_overlap_percent)
    except (TypeError, ValueError):
        overlap = -1
    return (confidence_rank.get(record.match_confidence, 5), -overlap, -record.retrieval_score)


def _include_in_triage(record: ReviewRecord, *, include_not_reviewed: bool) -> bool:
    if record.match_confidence == "not_reviewed":
        return include_not_reviewed
    if record.match_confidence in {"high", "medium"}:
        return True
    try:
        return record.match_confidence == "low" and int(record.work_overlap_percent) >= 35
    except (TypeError, ValueError):
        return False


def _write_markdown(
    path: Path,
    *,
    current: Sequence[CurrentWork],
    records: Sequence[ReviewRecord],
    retrieval_only: bool,
    existing_ai_only: bool,
    model: str,
    top_k: int,
) -> None:
    by_current: dict[str, list[ReviewRecord]] = defaultdict(list)
    for record in records:
        if _include_in_triage(record, include_not_reviewed=retrieval_only):
            by_current[record.current_proposal_id].append(record)
    if retrieval_only:
        mode_label = "retrieval only"
    elif existing_ai_only:
        mode_label = "existing AI/manual reviews applied"
    else:
        mode_label = "AI adjudicated"
    adjudication_counts = Counter(
        record.ai_model or "not_reviewed"
        for record in records
        if record.match_confidence != "not_reviewed" or record.ai_model
    )
    adjudication_lines = [
        f"- {model_name}: {count} candidate pairs"
        for model_name, count in sorted(adjudication_counts.items())
    ]
    if not adjudication_lines:
        adjudication_lines = ["- No AI or manual adjudications applied."]
    lines = [
        "# Treasury Fund 2 Prior Work Overlap Review",
        "",
        f"Generated: {_utcnow_iso()}",
        f"Mode: {mode_label}",
        "AI model: "
        f"{model if not retrieval_only and not existing_ai_only else 'mixed or not used'}",
        f"Retrieval shortlist depth: top {top_k} historical candidates per current proposal",
        "",
        "Purpose: screen the 69 current TF2 proposals for historically similar Catalyst, "
        "Treasury Fund 1, on-chain treasury, and BuilderDAO work. This is a triage report, "
        "not a final audit finding.",
        "",
        "Method: deterministic retrieval creates a top-candidate shortlist for each current "
        "proposal. Candidate-pair adjudication is then applied from the review JSONL. "
        "Manual console adjudications are human analyst judgments. Local AI screening rows "
        "are draft triage judgments produced by a workstation running Ollama with Qwen 3.5 "
        "4B; they require human review before being treated as final findings.",
        "",
        "Counting caveat: BuilderDAO downstream rows are non-additive detail and should "
        "not be added to the TF1/on-chain parent amount.",
        "",
        "## Adjudication Sources",
        "",
        *adjudication_lines,
        "",
        "## Summary",
        "",
        f"- Current proposals reviewed: {len(current)}",
        f"- Candidate pairs in CSV: {len(records)}",
        f"- Triage rows shown below: {sum(len(v) for v in by_current.values())}",
        "",
        "## Proposal Reviews",
        "",
    ]
    for proposal in sorted(current, key=lambda p: p.current_title.casefold()):
        proposal_records = sorted(
            by_current.get(proposal.current_proposal_id, []),
            key=_review_sort_key,
        )
        lines.extend(
            [
                f"### {proposal.current_title}",
                "",
                f"- Current proposer: {proposal.current_proposer_name}",
                f"- Current requested budget: {proposal.current_budget_ada:,.2f} ADA",
            ]
        )
        if not proposal_records:
            lines.extend(["- Triage matches: none.", ""])
            continue
        lines.extend([f"- Triage matches: {len(proposal_records)}", ""])
        for record in proposal_records:
            lines.extend(
                [
                    f"#### {record.historical_source}: {record.historical_title}",
                    "",
                    f"- Match confidence: {record.match_confidence}",
                    f"- Estimated current-work overlap: {record.work_overlap_percent}%",
                    f"- Overlap type: {record.overlap_type}",
                    f"- Previously proposed: {record.previously_proposed}",
                    "- Previously funded relevance: "
                    f"{record.previously_funded_relevance} "
                    f"({record.previously_funded}; {record.amount_original})",
                    f"- Proposer relationship: {record.same_or_related_proposer}",
                    "- Retrieval: "
                    f"rank {record.retrieval_rank}, score {record.retrieval_score:.3f}, "
                    f"shared terms: {record.shared_terms or 'none'}",
                    f"- Overlap evidence: {record.overlap_evidence}",
                    f"- Funding evidence: {record.funding_evidence}",
                    f"- Relationship evidence: {record.relationship_evidence}",
                    f"- Review notes: {record.review_notes}",
                    f"- Source: {record.source_url or 'not captured'}",
                    "",
                ]
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _load_all_historical(data_root: Path, builderdao_snapshot: Path) -> list[HistoricalWork]:
    return [
        *_load_catalyst_candidates(
            data_root / "consolidated" / "all_proposals.json",
            data_root / "consolidated" / "all_proposers.json",
        ),
        *_load_tf1_candidates(data_root / "historical" / "treasury-fund-01"),
        *_load_onchain_candidates(
            data_root / "historical" / "cardano-treasury-withdrawals" / "withdrawals.json"
        ),
        *_load_builderdao_candidates(builderdao_snapshot),
    ]


def _limit_current(
    current: list[CurrentWork],
    limit: int | None,
    offset: int = 0,
) -> list[CurrentWork]:
    current = current[offset:]
    if limit is None:
        return current
    return current[:limit]


def generate_report(
    *,
    data_root: Path,
    report_root: Path,
    current_snapshot: Path,
    builderdao_snapshot: Path,
    top_k: int,
    limit_current: int | None,
    current_offset: int,
    current_proposal_id: str | None,
    retrieval_only: bool,
    existing_ai_only: bool,
    ai_provider: str,
    model: str,
    api_key: str,
    ollama_url: str,
    timeout_seconds: float,
    retries: int,
    resume: bool,
) -> dict[str, Any]:
    if not retrieval_only and not existing_ai_only and ai_provider == "openai" and not api_key:
        raise ValueError("OPENAI_API_KEY is required unless --retrieval-only is used")
    current = _load_current(current_snapshot)
    historical = _load_all_historical(data_root, builderdao_snapshot)
    candidates = _retrieve_candidates(current, historical, top_k=top_k)
    if current_proposal_id:
        current = [
            proposal for proposal in current
            if proposal.current_proposal_id == current_proposal_id
        ]
        if not current:
            raise ValueError(f"Unknown current proposal id: {current_proposal_id}")
        candidates = [
            candidate for candidate in candidates
            if candidate.current_proposal_id == current_proposal_id
        ]
    else:
        current = _limit_current(current, limit_current, current_offset)
        current_ids = {proposal.current_proposal_id for proposal in current}
        candidates = [
            candidate for candidate in candidates
            if candidate.current_proposal_id in current_ids
        ]
    report_root.mkdir(parents=True, exist_ok=True)
    candidates_csv = report_root / "work-overlap-review-candidates.csv"
    ai_jsonl = report_root / "work-overlap-review-ai.jsonl"
    review_csv = report_root / "work-overlap-review.csv"
    review_md = report_root / "work-overlap-review.md"
    summary_json = report_root / "work-overlap-review-summary.json"

    _write_csv(candidates_csv, candidates)
    if retrieval_only and not ai_jsonl.exists():
        ai_jsonl.write_text("", encoding="utf-8")
    reviews = _review_candidates(
        candidates,
        current,
        historical,
        out_jsonl=ai_jsonl,
        retrieval_only=retrieval_only,
        existing_ai_only=existing_ai_only,
        ai_provider=ai_provider,
        model=model,
        api_key=api_key,
        ollama_url=ollama_url,
        timeout_seconds=timeout_seconds,
        retries=retries,
        resume=resume,
    )
    _write_csv(review_csv, reviews)
    _write_markdown(
        review_md,
        current=current,
        records=reviews,
        retrieval_only=retrieval_only,
        existing_ai_only=existing_ai_only,
        model=model,
        top_k=top_k,
    )
    confidence_counts = Counter(record.match_confidence for record in reviews)
    ai_model_counts = Counter(
        record.ai_model or "not_reviewed"
        for record in reviews
        if record.match_confidence != "not_reviewed" or record.ai_model
    )
    source_counts = Counter(work.historical_source for work in historical)
    summary = {
        "generated_at": _utcnow_iso(),
        "mode": (
            "retrieval_only"
            if retrieval_only
            else "existing_ai_applied"
            if existing_ai_only
            else "ai_adjudicated"
        ),
        "model": "" if retrieval_only or existing_ai_only else model,
        "current_proposals": len(current),
        "historical_candidates": len(historical),
        "historical_candidate_sources": dict(sorted(source_counts.items())),
        "top_k": top_k,
        "candidate_pairs": len(candidates),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "ai_model_counts": dict(sorted(ai_model_counts.items())),
        "outputs": {
            "candidates_csv": str(candidates_csv.relative_to(REPO_ROOT)),
            "ai_jsonl": str(ai_jsonl.relative_to(REPO_ROOT)),
            "review_csv": str(review_csv.relative_to(REPO_ROOT)),
            "review_md": str(review_md.relative_to(REPO_ROOT)),
            "summary_json": str(summary_json.relative_to(REPO_ROOT)),
        },
    }
    _write_json(summary_json, summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--current-snapshot", type=Path, default=CURRENT_SNAPSHOT)
    parser.add_argument("--builderdao-snapshot", type=Path, default=BUILDERDAO_SNAPSHOT)
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--limit-current", type=int)
    parser.add_argument(
        "--current-offset",
        type=int,
        default=0,
        help="Skip this many current proposals before applying --limit-current.",
    )
    parser.add_argument(
        "--current-proposal-id",
        help=(
            "Review one current proposal by id after retrieving candidates against "
            "the full current-proposal corpus."
        ),
    )
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument(
        "--apply-existing-ai",
        action="store_true",
        help="Merge existing JSONL adjudications without calling OpenAI.",
    )
    parser.add_argument("--ai-provider", choices=("openai", "ollama"), default="openai")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", DEFAULT_OLLAMA_URL))
    parser.add_argument("--timeout-seconds", type=float, default=90.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = generate_report(
            data_root=args.data_root,
            report_root=args.report_root,
            current_snapshot=args.current_snapshot,
            builderdao_snapshot=args.builderdao_snapshot,
            top_k=args.top_k,
            limit_current=args.limit_current,
            current_offset=args.current_offset,
            current_proposal_id=args.current_proposal_id,
            retrieval_only=args.retrieval_only,
            existing_ai_only=args.apply_existing_ai,
            ai_provider=args.ai_provider,
            model=args.model,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            ollama_url=args.ollama_url,
            timeout_seconds=args.timeout_seconds,
            retries=args.retries,
            resume=not args.no_resume,
        )
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(
            json.dumps({"level": "ERROR", "msg": "fatal", "error": str(exc)}),
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"level": "INFO", "msg": "generated", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["generate_report", "main"]
