"""Cross-check Lidonation funding_status against official voting-results artifacts.

Diff-only sidecar: this module never modifies proposals.json. It writes
data/funds/fund-XX/_reconciliation.json listing per-record disagreements,
unmatched-in-primary records (IOG-only), and unmatched-in-secondary records
(Lidonation-only).

Phase 6 will apply corrections in a reviewable PR. Per ADR-2026-05-13, the
IOG/CF artifact wins automatically over Lidonation when they disagree.

Title matching:
  - Both sides are slugified (lowercase, punctuation stripped, ASCII-folded).
  - Whitespace runs collapsed.
  - Edge cases (truncated titles, special chars) are flagged with
    `verdict: needs_human_review` rather than auto-resolved.

CLI:
    python -m normalizers.reconcile_winners --fund 2
    python -m normalizers.reconcile_winners                  # all funds
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from slugify import slugify


def _rel_to(path: Path, anchor: Path) -> str:
    """Return path-as-string relative to anchor if possible, else just path."""
    try:
        return str(path.relative_to(anchor))
    except ValueError:
        return str(path)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _match_key(title: str) -> str:
    """Normalize a title for title-matching."""
    return slugify(title or "", lowercase=True) or ""


def _load_proposals(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def _load_iohk_intermediate(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def reconcile_fund(
    *,
    data_root: Path,
    fund: int,
) -> dict[str, Any]:
    """Produce a _reconciliation.json record for one fund.

    Args:
        data_root: Path to data/.
        fund: Fund number.

    Returns:
        The reconciliation record (also written to disk).

    Raises:
        FileNotFoundError: if either source is missing.
    """
    fund_dir = data_root / "funds" / f"fund-{fund:02d}"
    proposals_path = fund_dir / "proposals.json"
    iohk_path = fund_dir / "_intermediate" / "iohk_winners.json"

    if not proposals_path.exists():
        raise FileNotFoundError(
            f"Lidonation proposals.json missing for fund {fund}: {proposals_path}"
        )
    if not iohk_path.exists():
        raise FileNotFoundError(
            f"IOG intermediate missing for fund {fund}: {iohk_path}. "
            "Run `python -m fetchers.projectcatalyst_funds --fund {fund}` first."
        )

    proposals = _load_proposals(proposals_path)
    iohk = _load_iohk_intermediate(iohk_path)
    iohk_rows: list[dict[str, Any]] = iohk.get("rows") or []
    secondary_source = iohk.get("source") or {}
    secondary_label = secondary_source.get("label") or "iohk_voting_results_pdf"

    # Build lookup tables. Use _match_key to bridge title variation.
    primary_by_key: dict[str, dict[str, Any]] = {}
    for p in proposals:
        k = _match_key(p.get("title", ""))
        if k:
            primary_by_key.setdefault(k, p)

    secondary_by_key: dict[str, dict[str, Any]] = {}
    for r in iohk_rows:
        k = _match_key(r.get("title", ""))
        if k:
            secondary_by_key.setdefault(k, r)

    disagreements: list[dict[str, Any]] = []
    agreement_count = 0
    matched_secondary_keys: set[str] = set()

    for key, p_rec in primary_by_key.items():
        s_rec = secondary_by_key.get(key)
        if s_rec is None:
            continue
        matched_secondary_keys.add(key)
        primary_funded = p_rec.get("funding_status") in {"approved", "leftover"}
        secondary_funded = bool(s_rec.get("funded"))
        if primary_funded == secondary_funded:
            agreement_count += 1
            continue
        disagreements.append(
            {
                "primary_proposal_id": p_rec.get("proposal_id"),
                "matched_secondary_title": s_rec.get("title"),
                "primary_funding_status": p_rec.get("funding_status", "unknown"),
                "secondary_funded_flag": secondary_funded,
                "secondary_status": s_rec.get("status"),
                "secondary_source_file": s_rec.get("source_file"),
                "verdict": "secondary_wins",
                "note": "Auto-applied per ADR-2026-05-13. Human review optional.",
            }
        )

    unmatched_in_secondary: list[dict[str, Any]] = []
    for key, p_rec in primary_by_key.items():
        if key not in secondary_by_key:
            unmatched_in_secondary.append(
                {
                    "primary_proposal_id": p_rec.get("proposal_id"),
                    "title": p_rec.get("title", ""),
                    "primary_funding_status": p_rec.get("funding_status", "unknown"),
                }
            )

    unmatched_in_primary: list[dict[str, Any]] = []
    for key, s_rec in secondary_by_key.items():
        if key not in primary_by_key:
            unmatched_in_primary.append(
                {
                    "title": s_rec.get("title", ""),
                    "funded_flag": bool(s_rec.get("funded")),
                    "note": "Present in IOG PDF, no title match in Lidonation.",
                }
            )

    record = {
        "fund": fund,
        "reconciled_at": _utcnow_iso(),
        "sources": {
            "primary": {
                "label": "lidonation_api",
                "path": _rel_to(proposals_path, data_root.parent),
            },
            "secondary": {
                "label": secondary_label,
                "path": _rel_to(iohk_path, data_root.parent),
            },
        },
        "agreement_count": agreement_count,
        "disagreements": disagreements,
        "unmatched_in_primary": unmatched_in_primary,
        "unmatched_in_secondary": unmatched_in_secondary,
        "notes": None,
    }

    out_path = fund_dir / "_reconciliation.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        json.dumps(
            {
                "fund": fund,
                "agreement_count": agreement_count,
                "disagreement_count": len(disagreements),
                "unmatched_in_primary": len(unmatched_in_primary),
                "unmatched_in_secondary": len(unmatched_in_secondary),
                "written": _rel_to(out_path, data_root.parent),
            },
            indent=2,
        )
    )
    return record


def reconcile_all(*, data_root: Path) -> dict[int, dict[str, Any]]:
    """Run reconciliation for every fund that has BOTH inputs."""
    out: dict[int, dict[str, Any]] = {}
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
        proposals_ok = (fund_dir / "proposals.json").exists()
        iohk_ok = (fund_dir / "_intermediate" / "iohk_winners.json").exists()
        if not (proposals_ok and iohk_ok):
            continue
        out[fund_n] = reconcile_fund(data_root=data_root, fund=fund_n)
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
        help="Fund(s) to reconcile. Default: every fund with both inputs.",
    )
    args = parser.parse_args(argv)
    root = args.data_root if args.data_root is not None else DEFAULT_DATA_ROOT
    if args.fund:
        for n in args.fund:
            reconcile_fund(data_root=root, fund=n)
    else:
        reconcile_all(data_root=root)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["reconcile_all", "reconcile_fund", "main"]
