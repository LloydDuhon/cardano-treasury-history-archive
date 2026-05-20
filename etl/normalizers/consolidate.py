"""Consolidate per-fund data into data/consolidated/ outputs.

Emits, from existing data/funds/fund-XX/{proposals,proposers,milestones}.json:
    data/consolidated/
        all_proposals.csv     # ~25 columns, spreadsheet-friendly
        all_proposals.json    # full fidelity
        all_proposers.csv     # narrow columns, deduped across funds
        all_proposers.json    # full fidelity
        all_milestones.csv    # narrow, F9+ where data exists
        all_milestones.json   # full fidelity
        schema.md             # column reference

CSVs are LOSSY by design (nested objects flatten / collapse to JSON strings
for arrays). Full-fidelity JSON is the authoritative consolidated form.

This module assumes apply_reconciliations.py and dedupe_proposers.py have
already run. The validator (`validate_against_schema.py`) catches any
record that drifts from its schema.

CLI:
    python -m normalizers.consolidate
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

# ----------------------------- column schemas ---------------------------- #

PROPOSAL_CSV_COLS: list[str] = [
    "proposal_id",
    "fund",
    "title",
    "slug",
    "challenge",
    "proposer_ids",
    "amount_requested",
    "amount_received",
    "currency",
    "yes_votes",
    "no_votes",
    "abstain_votes",
    "score_alignment",
    "score_feasibility",
    "score_auditability",
    "ranking_total",
    "funding_status",
    "project_status",
    "funded_at",
    "completed_at",
    "lidonation_url",
    "ideascale_url",
    "projectcatalyst_io_url",
    "milestones_url",
    "milestone_count",
    "is_opensource",
    "confidence",
    "ai_summary",
]

PROPOSER_CSV_COLS: list[str] = [
    "proposer_id",
    "display_name",
    "entity_type",
    "ideascale_profile_id",
    "lidonation_profile_uuid",
    "catalyst_voices_stake_address",
    "total_proposals",
    "total_funded",
    "total_completed",
    "total_cancelled",
    "total_in_progress",
    "total_requested_ada",
    "total_received_ada",
    "first_fund",
    "last_fund",
    "confidence",
    "duplicate_candidates_count",
    "twitter",
    "github",
    "website",
]

MILESTONE_CSV_COLS: list[str] = [
    "milestone_id",
    "proposal_id",
    "milestone_number",
    "title",
    "budget",
    "currency",
    "status",
    "is_closeout",
    "delivered_at",
    "evidence_count",
    "signoff_count",
    "closeout_video_url",
    "closeout_report_url",
    "confidence",
]


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _iter_fund_files(data_root: Path, filename: str) -> Iterable[tuple[int, Path]]:
    """Yield (fund_number, file_path) for every fund directory."""
    funds_dir = data_root / "funds"
    if not funds_dir.exists():
        return
    for fund_dir in sorted(funds_dir.iterdir()):
        if not fund_dir.is_dir() or not fund_dir.name.startswith("fund-"):
            continue
        try:
            fund_n = int(fund_dir.name.split("-", 1)[1])
        except (IndexError, ValueError):
            continue
        path = fund_dir / filename
        if path.exists():
            yield fund_n, path


def _flatten_proposal(p: dict[str, Any]) -> dict[str, Any]:
    scores = p.get("scores") or {}
    links = p.get("links") or {}
    return {
        "proposal_id": p.get("proposal_id"),
        "fund": p.get("fund"),
        "title": p.get("title"),
        "slug": p.get("slug"),
        "challenge": p.get("challenge"),
        "proposer_ids": ";".join(p.get("proposer_ids") or []),
        "amount_requested": p.get("amount_requested"),
        "amount_received": p.get("amount_received"),
        "currency": p.get("currency"),
        "yes_votes": p.get("yes_votes"),
        "no_votes": p.get("no_votes"),
        "abstain_votes": p.get("abstain_votes"),
        "score_alignment": scores.get("alignment"),
        "score_feasibility": scores.get("feasibility"),
        "score_auditability": scores.get("auditability"),
        "ranking_total": p.get("ranking_total"),
        "funding_status": p.get("funding_status"),
        "project_status": p.get("project_status"),
        "funded_at": p.get("funded_at"),
        "completed_at": p.get("completed_at"),
        "lidonation_url": links.get("lidonation_url"),
        "ideascale_url": links.get("ideascale_url"),
        "projectcatalyst_io_url": links.get("projectcatalyst_io_url"),
        "milestones_url": links.get("milestones_url"),
        "milestone_count": p.get("milestone_count"),
        "is_opensource": p.get("is_opensource"),
        "confidence": p.get("confidence"),
        "ai_summary": p.get("ai_summary"),
    }


def _flatten_proposer(r: dict[str, Any]) -> dict[str, Any]:
    ext = r.get("external_ids") or {}
    ru = r.get("rollups") or {}
    socials = r.get("socials") or {}
    return {
        "proposer_id": r.get("proposer_id"),
        "display_name": r.get("display_name"),
        "entity_type": r.get("entity_type"),
        "ideascale_profile_id": ext.get("ideascale_profile_id"),
        "lidonation_profile_uuid": ext.get("lidonation_profile_uuid"),
        "catalyst_voices_stake_address": ext.get("catalyst_voices_stake_address"),
        "total_proposals": ru.get("total_proposals"),
        "total_funded": ru.get("total_funded"),
        "total_completed": ru.get("total_completed"),
        "total_cancelled": ru.get("total_cancelled"),
        "total_in_progress": ru.get("total_in_progress"),
        "total_requested_ada": ru.get("total_requested_ada"),
        "total_received_ada": ru.get("total_received_ada"),
        "first_fund": ru.get("first_fund"),
        "last_fund": ru.get("last_fund"),
        "confidence": r.get("confidence"),
        "duplicate_candidates_count": len(r.get("duplicate_candidates") or []),
        "twitter": socials.get("twitter"),
        "github": socials.get("github"),
        "website": socials.get("website"),
    }


def _flatten_milestone(m: dict[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": m.get("milestone_id"),
        "proposal_id": m.get("proposal_id"),
        "milestone_number": m.get("milestone_number"),
        "title": m.get("title"),
        "budget": m.get("budget"),
        "currency": m.get("currency"),
        "status": m.get("status"),
        "is_closeout": m.get("is_closeout"),
        "delivered_at": m.get("delivered_at"),
        "evidence_count": len(m.get("evidence") or []),
        "signoff_count": len(m.get("reviewer_signoffs") or []),
        "closeout_video_url": m.get("closeout_video_url"),
        "closeout_report_url": m.get("closeout_report_url"),
        "confidence": m.get("confidence"),
    }


def _write_csv(path: Path, cols: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")


def _gather(data_root: Path, filename: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, path in _iter_fund_files(data_root, filename):
        rows.extend(json.loads(path.read_text(encoding="utf-8")))
    return rows


def consolidate(*, data_root: Path | None = None) -> dict[str, int]:
    """Produce data/consolidated/* files."""
    root = data_root if data_root is not None else DEFAULT_DATA_ROOT
    out_dir = root / "consolidated"

    proposals = _gather(root, "proposals.json")
    proposers = _gather(root, "proposers.json")
    milestones = _gather(root, "milestones.json")

    _write_json(out_dir / "all_proposals.json", proposals)
    _write_json(out_dir / "all_proposers.json", proposers)
    _write_json(out_dir / "all_milestones.json", milestones)
    _write_csv(
        out_dir / "all_proposals.csv",
        PROPOSAL_CSV_COLS,
        [_flatten_proposal(p) for p in proposals],
    )
    _write_csv(
        out_dir / "all_proposers.csv",
        PROPOSER_CSV_COLS,
        [_flatten_proposer(p) for p in proposers],
    )
    _write_csv(
        out_dir / "all_milestones.csv",
        MILESTONE_CSV_COLS,
        [_flatten_milestone(m) for m in milestones],
    )
    _write_schema_md(out_dir / "schema.md")

    counters = {
        "proposals": len(proposals),
        "proposers": len(proposers),
        "milestones": len(milestones),
    }
    print(json.dumps({"consolidated_at": _utcnow_iso(), **counters}, indent=2))
    return counters


def _write_schema_md(path: Path) -> None:
    """Describe the consolidated CSV columns."""
    body = """# Consolidated CSV column reference

All files under `data/consolidated/` are derived from the per-fund
`data/funds/fund-XX/*.json` files. The JSON form (`all_*.json`) carries
full schema fidelity; the CSV form is intentionally narrowed to ~25 columns
for spreadsheet ergonomics.

## `all_proposals.csv`

| Column | Source | Notes |
|---|---|---|
| `proposal_id` | mint(`f{fund:02d}-{slug}`) | canonical key |
| `fund` | int 1-15 | |
| `title` | proposal.title | |
| `slug` | proposal.slug | URL-safe |
| `challenge` | proposal.challenge | category/campaign |
| `proposer_ids` | `;`-joined list | join with `all_proposers.csv` via `external_ids` |
| `amount_requested` / `amount_received` | numbers | currency in next col |
| `currency` | `ADA` / `USD` / `USDM` / `UNKNOWN` | |
| `yes_votes` / `no_votes` / `abstain_votes` | numbers | units vary per fund |
| `score_*` | flattened from `scores.*` | review scores where available |
| `ranking_total` | int | position within fund/challenge |
| `funding_status` | enum | post-reconciliation: IOG-canonical |
| `project_status` | enum | unfunded/funded/in_progress/complete/cancelled/stalled/unknown
| `funded_at` / `completed_at` | ISO 8601 | |
| `*_url` | flattened from `links.*` | one column per known source link |
| `milestone_count` | derived | from F10+ Milestone Module |
| `is_opensource` | boolean | |
| `confidence` | enum `high` / `medium` / `low` | |
| `ai_summary` | string or null | Lidonation-attributed |

Lossy: `sources[]`, `field_confidence`, `external_ids`, the full `links` map,
and `notes` are in `all_proposals.json` but not the CSV.

## `all_proposers.csv`

| Column | Notes |
|---|---|
| `proposer_id` | canonical, deduped across funds |
| `display_name` | best-known name |
| `entity_type` | individual / team / organization / unknown |
| `*_profile_id`, `lidonation_profile_uuid`, `catalyst_voices_stake_address` | external ids |
| `total_*` | rollup counts across all funds |
| `total_requested_*` / `total_received_*` | numbers; denomination-mixed across funds
| `first_fund` / `last_fund` | int |
| `confidence` | enum |
| `duplicate_candidates_count` | int; >0 means the entity may collide with others |
| `twitter` / `github` / `website` | flattened socials |

## `all_milestones.csv`

| Column | Notes |
|---|---|
| `milestone_id` | format `{proposal_id}-m{NN}` |
| `proposal_id` | back-reference |
| `milestone_number` | 1-based |
| `budget` | per-milestone budget in `currency` |
| `status` | enum |
| `is_closeout` | boolean; final milestone |
| `delivered_at` | ISO 8601 |
| `evidence_count` / `signoff_count` | int |
| `closeout_*_url` | when present |
| `confidence` | |

## Caveats

- F1 proposal result rows come from the staff-provided voting-results PDF.
  Funding status is high confidence; proposal-detail fields are limited.
- F2-F5 completion data is best-effort; expect `project_status: unknown` for
  many records.
- Vote-count units vary per fund (raw lovelace vs normalized count). See
  per-fund `_meta.json` for source notes.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None)
    args = parser.parse_args(argv)
    consolidate(data_root=args.data_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["consolidate", "main"]
