"""Apply per-fund _reconciliation.json to canonical proposals.json.

Per ADR-2026-05-13 section "Reconciliation policy":
  - On disagreement, the IOG/CF artifact wins.
  - The Lidonation value is preserved in the proposal's `notes` field.
  - A new `sources[]` entry with `source: iohk_voting_results_pdf` and
    `fields_provided: ["funding_status"]` records the override.

This applier is IDEMPOTENT: it detects when a reconciliation has already
been applied (by inspecting `sources[]` for the IOG-PDF marker) and skips
duplicates. Safe to re-run.

CLI:
    python -m normalizers.apply_reconciliations --fund 2
    python -m normalizers.apply_reconciliations                # all funds
    python -m normalizers.apply_reconciliations --dry-run      # show diff only
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

_SECONDARY_LABEL = "iohk_voting_results_pdf"
_APPLIED_FIELD = "funding_status"


def _utcnow_iso() -> str:
    # 3.10-compatible (timezone.utc rather than datetime.UTC alias).
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _is_already_applied(proposal: dict[str, Any]) -> bool:
    """Return True iff a prior run already wrote the IOG-PDF override marker."""
    for src in proposal.get("sources") or []:
        if src.get("source") != _SECONDARY_LABEL:
            continue
        fields = src.get("fields_provided") or []
        if _APPLIED_FIELD in fields:
            return True
    return False


def _apply_disagreement(
    proposal: dict[str, Any], disagreement: dict[str, Any], applied_at: str
) -> bool:
    """Apply one disagreement to the proposal in place. Returns True if applied."""
    if _is_already_applied(proposal):
        return False
    verdict = disagreement.get("verdict")
    if verdict != "secondary_wins":
        return False
    secondary_funded = bool(disagreement.get("secondary_funded_flag"))
    new_status = "approved" if secondary_funded else "not_approved"
    prior_status = proposal.get("funding_status", "unknown")
    proposal["funding_status"] = new_status

    note_prefix = (
        f"RECONCILIATION {applied_at}: funding_status changed from "
        f"'{prior_status}' (Lidonation) to '{new_status}' (IOG PDF). "
    )
    existing_notes = proposal.get("notes") or ""
    proposal["notes"] = (note_prefix + existing_notes).strip()

    # Append a sources[] entry recording the override.
    sources = list(proposal.get("sources") or [])
    sources.append(
        {
            "source": _SECONDARY_LABEL,
            "url": None,
            "fetched_at": applied_at,
            "provenance_path": None,
            "fields_provided": [_APPLIED_FIELD],
        }
    )
    proposal["sources"] = sources

    # Aggregate confidence: still "high" or "medium" overall, but flag this
    # specific field as "high" since IOG PDF is the canonical source.
    field_conf = dict(proposal.get("field_confidence") or {})
    field_conf["funding_status"] = "high"
    proposal["field_confidence"] = field_conf
    return True


def apply_fund(
    *,
    data_root: Path,
    fund: int,
    dry_run: bool = False,
) -> dict[str, int]:
    """Apply all disagreements from data/funds/fund-XX/_reconciliation.json.

    Returns a counters dict with keys: applied, skipped_already_applied,
    skipped_non_verdict, no_proposal_match.
    """
    fund_dir = data_root / "funds" / f"fund-{fund:02d}"
    reconciliation_path = fund_dir / "_reconciliation.json"
    proposals_path = fund_dir / "proposals.json"

    counters = {
        "applied": 0,
        "skipped_already_applied": 0,
        "skipped_non_verdict": 0,
        "no_proposal_match": 0,
    }
    if not reconciliation_path.exists():
        return counters
    if not proposals_path.exists():
        raise FileNotFoundError(
            f"reconciliation present but proposals missing for fund {fund}: {proposals_path}"
        )

    reconciliation: dict[str, Any] = json.loads(reconciliation_path.read_text())
    proposals: list[dict[str, Any]] = json.loads(proposals_path.read_text())
    proposals_by_id: dict[str, dict[str, Any]] = {
        p["proposal_id"]: p for p in proposals if "proposal_id" in p
    }
    applied_at = _utcnow_iso()

    for d in reconciliation.get("disagreements") or []:
        if d.get("verdict") != "secondary_wins":
            counters["skipped_non_verdict"] += 1
            continue
        pid = d.get("primary_proposal_id")
        proposal = proposals_by_id.get(pid or "")
        if proposal is None:
            counters["no_proposal_match"] += 1
            continue
        if _is_already_applied(proposal):
            counters["skipped_already_applied"] += 1
            continue
        applied = _apply_disagreement(proposal, d, applied_at)
        if applied:
            counters["applied"] += 1

    if not dry_run and counters["applied"] > 0:
        with proposals_path.open("w", encoding="utf-8") as fh:
            json.dump(proposals, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")

    print(json.dumps({"fund": fund, **counters, "dry_run": dry_run}, indent=2))
    return counters


def apply_all(*, data_root: Path, dry_run: bool = False) -> dict[int, dict[str, int]]:
    """Run apply_fund for every fund directory with a _reconciliation.json."""
    out: dict[int, dict[str, int]] = {}
    funds_dir = data_root / "funds"
    if not funds_dir.exists():
        return out
    for fund_dir in sorted(funds_dir.iterdir()):
        if not fund_dir.is_dir() or not fund_dir.name.startswith("fund-"):
            continue
        try:
            fund_n = int(fund_dir.name.split("-", 1)[1])
        except (IndexError, ValueError):
            continue
        if not (fund_dir / "_reconciliation.json").exists():
            continue
        out[fund_n] = apply_fund(data_root=data_root, fund=fund_n, dry_run=dry_run)
    return out


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None, help="Override data/ directory.")
    parser.add_argument(
        "--fund",
        type=int,
        action="append",
        default=None,
        help="Fund(s) to apply. Default: every fund with a _reconciliation.json.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing.",
    )
    args = parser.parse_args(argv)
    root = args.data_root if args.data_root is not None else DEFAULT_DATA_ROOT
    if args.fund:
        for n in args.fund:
            apply_fund(data_root=root, fund=n, dry_run=args.dry_run)
    else:
        apply_all(data_root=root, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["apply_all", "apply_fund", "main"]
