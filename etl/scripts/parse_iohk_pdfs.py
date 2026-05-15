"""Phase 2 helper: parse one or all IOG voting-results PDFs into intermediates.

Replaces the awkward PowerShell-embedded Python one-liner. Reads the
projectcatalyst.io summary JSON (for the canonical URL) and the downloaded
PDF, then writes `data/funds/fund-XX/_intermediate/iohk_winners.json`.

Usage:
    python -m scripts.parse_iohk_pdfs --fund 2
    python -m scripts.parse_iohk_pdfs --fund 2 --fund 3 --fund 4
    python -m scripts.parse_iohk_pdfs                  # all F2-F13

This script does NOT fetch anything. Run
`python -m fetchers.projectcatalyst_funds` first to populate the cache.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from parsers.iohk_pdf import parse_voting_results_pdf, write_intermediate

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
DEFAULT_FUNDS: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def parse_fund(fund: int, data_root: Path) -> tuple[int, int] | None:
    """Return (rows_matched, funded_count) or None if inputs missing."""
    pdf = data_root / "_raw" / "iohk-pdfs" / f"fund-{fund:02d}.pdf"
    summary = data_root / "_raw" / "projectcatalyst_io" / f"funds-{fund:02d}.summary.json"
    if not pdf.exists():
        print(f"  f{fund}: SKIP (PDF not at {pdf})")
        return None
    if not summary.exists():
        print(f"  f{fund}: SKIP (summary not at {summary})")
        return None

    summary_doc = json.loads(summary.read_text(encoding="utf-8"))
    url = summary_doc.get("voting_results_url") or ""

    rows, parsed = parse_voting_results_pdf(pdf)
    rel_pdf = f"data/_raw/iohk-pdfs/fund-{fund:02d}.pdf"
    write_intermediate(
        rows,
        parsed,
        fund=fund,
        data_root=data_root,
        source_url=url,
        pdf_relpath=rel_pdf,
        parsed_at=_utcnow_iso(),
    )
    print(f"  f{fund}: {parsed.rows_matched} rows, {parsed.funded_count} funded")
    return parsed.rows_matched, parsed.funded_count


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Override data/ directory.",
    )
    parser.add_argument(
        "--fund",
        type=int,
        action="append",
        default=None,
        help="Fund(s) to parse. May be passed multiple times. Default: F2-F13.",
    )
    args = parser.parse_args(argv)
    root = args.data_root if args.data_root is not None else DEFAULT_DATA_ROOT
    funds = tuple(args.fund) if args.fund else DEFAULT_FUNDS
    total_ok = 0
    for n in funds:
        if parse_fund(n, root) is not None:
            total_ok += 1
    print(f"\nparsed {total_ok}/{len(funds)} funds")
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "parse_fund"]
