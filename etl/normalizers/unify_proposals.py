"""Demultiplex Lidonation raw pages into per-fund proposals.json files.

Phase 1 scope only: read data/_raw/lidonation/page-*.json.gz, group records by
`fund.title` -> fund number, mint canonical proposal_ids, and write minimally
normalized records that satisfy proposal.schema.json (mandatory fields plus
the most useful optional fields).

Cross-source reconciliation against IOG voting-results PDFs is Phase 2;
proposer-entity reconciliation is Phase 6.

Output per fund (data/funds/fund-XX/):
    proposals.json     - normalized array, schema-conformant
    _meta.json         - sweep metadata (sources, fetched_at, coverage)

CLI:
    python -m normalizers.unify_proposals
    python -m normalizers.unify_proposals --fund 10
    python -m normalizers.unify_proposals --fund 10 --fund 11
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

# Constrained vocab from proposal.schema.json
VALID_FUNDING_STATUS = {
    "approved",
    "not_approved",
    "over_budget",
    "leftover",
    "withdrawn",
    "unknown",
}
VALID_PROJECT_STATUS = {
    "unfunded",
    "funded",
    "in_progress",
    "complete",
    "cancelled",
    "stalled",
    "unknown",
}
VALID_CURRENCY = {"ADA", "USD", "USDM", "UNKNOWN"}

# Map Lidonation `status` -> our project_status enum
_PROJECT_STATUS_MAP: dict[str, str] = {
    "unfunded": "unfunded",
    "funded": "funded",
    "in_progress": "in_progress",
    "in-progress": "in_progress",
    "inprogress": "in_progress",
    "complete": "complete",
    "completed": "complete",
    "cancelled": "cancelled",
    "stalled": "stalled",
}

# Map Lidonation `funding_status` -> our enum
_FUNDING_STATUS_MAP: dict[str, str] = {
    "approved": "approved",
    "funded": "approved",
    "not_approved": "not_approved",
    "not approved": "not_approved",
    "unfunded": "not_approved",
    "over_budget": "over_budget",
    "leftover": "leftover",
    "withdrawn": "withdrawn",
}


@dataclass(frozen=True)
class SnapshotContext:
    """Provenance metadata applied to every record produced in one run."""

    fetched_at: str
    source_label: str = "lidonation_api"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _coerce_fund_number(fund_title: str | None) -> int | None:
    """Extract integer fund number from e.g. 'Fund 10' / 'F10' / 'Fund10'."""
    if not fund_title:
        return None
    match = re.search(r"(\d+)", fund_title)
    return int(match.group(1)) if match else None


def _coerce_currency(raw: str | None) -> str:
    if not raw:
        return "UNKNOWN"
    upper = raw.strip().upper()
    return upper if upper in VALID_CURRENCY else "UNKNOWN"


def _coerce_funding_status(raw: str | None) -> str:
    if not raw:
        return "unknown"
    return _FUNDING_STATUS_MAP.get(raw.strip().lower(), "unknown")


def _coerce_project_status(raw: str | None) -> str:
    if not raw:
        return "unknown"
    return _PROJECT_STATUS_MAP.get(raw.strip().lower(), "unknown")


def _coerce_number(v: object) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _mint_proposal_id(fund: int, slug: str | None, *, fallback: str) -> str:
    base = slug or fallback
    base = slugify(base) or fallback
    return f"f{fund:02d}-{base}"


def _mint_proposer_id_basis(user: dict[str, Any]) -> str:
    """Stable basis string for proposer_id minting (hashed downstream in Phase 6)."""
    return str(user.get("id") or user.get("name") or "unknown")


def iter_pages(raw_dir: Path) -> Iterator[tuple[Path, dict[str, Any]]]:
    """Yield (path, parsed-page) for each cached lidonation page."""
    if not raw_dir.exists():
        return
    for p in sorted(raw_dir.glob("page-*.json.gz")):
        with gzip.open(p, "rb") as fh:
            yield p, json.loads(fh.read())


def normalize_record(
    rec: dict[str, Any],
    fund_number: int,
    page_relpath: str,
    ctx: SnapshotContext,
) -> dict[str, Any] | None:
    """Convert one raw Lidonation proposal into the canonical schema.

    Returns None if the record cannot be normalized (no fund, no title).
    """
    title = rec.get("title")
    if not title:
        return None

    slug = rec.get("slug")
    proposal_id = _mint_proposal_id(fund_number, slug, fallback=str(rec.get("id", "unknown")))

    users = rec.get("users") or []
    proposer_ids = [
        f"p-lido-{u.get('id') or _mint_proposer_id_basis(u)}" for u in users if isinstance(u, dict)
    ] or [f"p-lido-anonymous-f{fund_number:02d}-{slug or rec.get('id', 'unknown')}"]

    funding_status = _coerce_funding_status(rec.get("funding_status"))
    project_status = _coerce_project_status(rec.get("status"))

    # Schema's external_ids fields are not nullable; emit only known IDs.
    external_ids = {k: v for k, v in {"lidonation_uuid": rec.get("id")}.items() if v is not None}

    out: dict[str, Any] = {
        "proposal_id": proposal_id,
        "external_ids": external_ids,
        "fund": fund_number,
        "title": title,
        "slug": slug,
        "challenge": (rec.get("campaign") or {}).get("title"),
        "campaign_id": (rec.get("campaign") or {}).get("id"),
        "proposer_ids": proposer_ids,
        "amount_requested": _coerce_number(rec.get("amount_requested")),
        "amount_received": _coerce_number(rec.get("amount_received")),
        "currency": _coerce_currency(rec.get("currency")),
        "yes_votes": _coerce_number(rec.get("yes_votes_count")),
        "no_votes": _coerce_number(rec.get("no_votes_count")),
        "abstain_votes": _coerce_number(rec.get("abstain_votes_count")),
        "scores": {
            "alignment": _coerce_number(rec.get("alignment_score")),
            "feasibility": _coerce_number(rec.get("feasibility_score")),
            "auditability": _coerce_number(rec.get("auditability_score")),
            "overall": None,
        },
        "ranking_total": (
            int(rec["ranking_total"]) if isinstance(rec.get("ranking_total"), int) else None
        ),
        "funding_status": funding_status,
        "project_status": project_status,
        "funded_at": rec.get("funded_at"),
        "completed_at": None,
        "links": {
            "lidonation_url": rec.get("link"),
            "ideascale_url": rec.get("ideascale_link"),
            "projectcatalyst_io_url": rec.get("projectcatalyst_io_link"),
            "milestones_url": None,
            "catalyst_voices_url": None,
            "proposer_website": rec.get("website"),
            "github_repo": None,
        },
        "summary": rec.get("excerpt"),
        "problem": rec.get("problem"),
        "solution": rec.get("solution"),
        "definition_of_success": rec.get("definition_of_success"),
        "ai_summary": rec.get("ai_summary"),
        "milestone_count": None,
        "tags": [],
        "is_opensource": rec.get("opensource"),
        "sources": [
            {
                "source": ctx.source_label,
                "url": "https://www.catalystexplorer.com/api/proposals",
                "fetched_at": ctx.fetched_at,
                "provenance_path": page_relpath,
                "fields_provided": [
                    "title",
                    "slug",
                    "funding_status",
                    "project_status",
                    "amount_requested",
                    "amount_received",
                    "yes_votes",
                    "no_votes",
                    "abstain_votes",
                    "scores",
                    "proposer_ids",
                    "links",
                ],
            }
        ],
        "confidence": "medium",
        "field_confidence": None,
        "notes": None,
    }
    return out


def write_fund(
    data_root: Path,
    fund_number: int,
    records: list[dict[str, Any]],
    ctx: SnapshotContext,
) -> None:
    """Write proposals.json + _meta.json for one fund."""
    fund_dir = data_root / "funds" / f"fund-{fund_number:02d}"
    fund_dir.mkdir(parents=True, exist_ok=True)

    proposals_path = fund_dir / "proposals.json"
    with proposals_path.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")

    meta = {
        "fund": fund_number,
        "normalized_at": ctx.fetched_at,
        "record_count": len(records),
        "sources_used": [ctx.source_label],
        "phase": "phase-1",
        "phase_notes": (
            "Phase 1 ingestion from Lidonation /api/proposals only. Cross-source "
            "reconciliation against IOG voting-results PDFs is deferred to Phase 2; "
            "milestone data to Phase 3; proposer-entity dedup to Phase 6."
        ),
        "coverage_warnings": [
            "Vote counts are raw lovelace for older funds; units may vary by fund.",
            "Currency may be USD or ADA depending on fund.",
        ],
    }
    meta_path = fund_dir / "_meta.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def unify(
    *,
    data_root: Path | None = None,
    only_funds: list[int] | None = None,
) -> dict[int, int]:
    """Build per-fund proposals.json from the cached Lidonation pages.

    Args:
        data_root: Path to repo's data/.
        only_funds: If provided, write output only for these funds.

    Returns:
        Mapping of fund_number -> record_count.
    """
    root = data_root if data_root is not None else DEFAULT_DATA_ROOT
    raw_dir = root / "_raw" / "lidonation"
    ctx = SnapshotContext(fetched_at=_utcnow_iso())

    by_fund: dict[int, list[dict[str, Any]]] = defaultdict(list)
    seen_ids: dict[int, set[str]] = defaultdict(set)
    skipped_no_fund = 0
    pages_seen = 0

    for page_path, page in iter_pages(raw_dir):
        pages_seen += 1
        page_relpath = (
            str(page_path.relative_to(root.parent)) if page_path.is_absolute() else str(page_path)
        )
        for rec in page.get("data") or []:
            fund_info = rec.get("fund") or {}
            fund_number = _coerce_fund_number(fund_info.get("title"))
            if fund_number is None:
                skipped_no_fund += 1
                continue
            if only_funds and fund_number not in only_funds:
                continue
            norm = normalize_record(rec, fund_number, page_relpath, ctx)
            if norm is None:
                continue
            if norm["proposal_id"] in seen_ids[fund_number]:
                continue
            seen_ids[fund_number].add(norm["proposal_id"])
            by_fund[fund_number].append(norm)

    for fund_number, records in by_fund.items():
        records.sort(key=lambda r: r["proposal_id"])
        write_fund(root, fund_number, records, ctx)

    summary = {fund: len(recs) for fund, recs in by_fund.items()}
    print(
        json.dumps(
            {
                "pages_seen": pages_seen,
                "funds_written": sorted(summary.keys()),
                "records_per_fund": {str(k): v for k, v in sorted(summary.items())},
                "skipped_no_fund": skipped_no_fund,
            },
            indent=2,
        )
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Override repo's data/ directory (defaults to ../data relative to etl/).",
    )
    parser.add_argument(
        "--fund",
        type=int,
        action="append",
        default=None,
        help="Only normalize this fund. May be passed multiple times.",
    )
    args = parser.parse_args(argv)
    unify(data_root=args.data_root, only_funds=args.fund)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["normalize_record", "unify", "main", "SnapshotContext"]
