"""Parse cached official Catalyst voting-results artifacts into intermediates.

Inputs:
    data/_raw/iohk-pdfs/fund-01.pdf
    data/_raw/iohk-results/fund-02.csv ... fund-14.csv
    data/_raw/projectcatalyst_io/results-02.summary.json ...

Output:
    data/funds/fund-XX/_intermediate/iohk_winners.json

This script does not fetch network resources. Run
`python -m fetchers.projectcatalyst_funds --csv-only` first to populate the
CSV cache.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from parsers.projectcatalyst_results import (
    parse_csv_result_files,
    parse_csv_results,
    parse_fund_one_pdf,
    write_intermediate,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
DEFAULT_FUNDS: tuple[int, ...] = tuple(range(1, 15))
FUND_14_CSV_TABS: tuple[tuple[str, str | None], ...] = (
    ("fund-14-cardano-use-cases-partners-products.csv", None),
    ("fund-14-cardano-use-cases-concept.csv", None),
    ("fund-14-cardano-open-developers.csv", None),
    ("fund-14-cardano-open-ecosystem.csv", None),
    ("fund-14-sponsored-by-leftovers.csv", None),
    ("fund-14-withdrawn.csv", "WITHDRAWN"),
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _summary_url(summary_path: Path) -> str | None:
    if not summary_path.exists():
        return None
    doc = json.loads(summary_path.read_text(encoding="utf-8"))
    return doc.get("voting_results_page_url") or doc.get("csv_url")


def parse_fund(fund: int, data_root: Path) -> tuple[int, int] | None:
    """Parse one fund artifact. Return (rows_matched, funded_count), or None."""
    parsed_at = _utcnow_iso()
    if fund == 1:
        pdf_path = data_root / "_raw" / "iohk-pdfs" / "fund-01.pdf"
        if not pdf_path.exists():
            print(f"  f{fund}: SKIP (PDF not at {pdf_path})")
            return None
        rows, summary = parse_fund_one_pdf(pdf_path)
        write_intermediate(
            rows,
            summary,
            fund=fund,
            data_root=data_root,
            source_label="iohk_voting_results_pdf",
            source_url=None,
            provenance_path="data/_raw/iohk-pdfs/fund-01.pdf",
            parsed_at=parsed_at,
        )
        print(f"  f{fund}: {summary.rows_matched} rows, {summary.funded_count} funded")
        return summary.rows_matched, summary.funded_count

    if fund == 14:
        tab_paths = [
            (data_root / "_raw" / "iohk-results" / filename, default_status)
            for filename, default_status in FUND_14_CSV_TABS
        ]
        missing = [path for path, _ in tab_paths if not path.exists()]
        if missing:
            print(f"  f{fund}: SKIP (missing tab CSVs: {', '.join(str(p) for p in missing)})")
            return None
        rows, summary = parse_csv_result_files(tab_paths)
        source_url = _summary_url(
            data_root / "_raw" / "projectcatalyst_io" / f"results-{fund:02d}.summary.json"
        )
        write_intermediate(
            rows,
            summary,
            fund=fund,
            data_root=data_root,
            source_label="projectcatalyst_io",
            source_url=source_url,
            provenance_path="data/_raw/iohk-results/fund-14-*.csv",
            parsed_at=parsed_at,
        )
        print(f"  f{fund}: {summary.rows_matched} rows, {summary.funded_count} funded")
        return summary.rows_matched, summary.funded_count

    csv_path = data_root / "_raw" / "iohk-results" / f"fund-{fund:02d}.csv"
    if not csv_path.exists():
        print(f"  f{fund}: SKIP (CSV not at {csv_path})")
        return None
    rows, summary = parse_csv_results(csv_path)
    if summary.rows_matched == 0:
        print(f"  f{fund}: SKIP (CSV parsed 0 result rows from {csv_path})")
        return None
    source_url = _summary_url(
        data_root / "_raw" / "projectcatalyst_io" / f"results-{fund:02d}.summary.json"
    )
    write_intermediate(
        rows,
        summary,
        fund=fund,
        data_root=data_root,
        source_label="projectcatalyst_io",
        source_url=source_url,
        provenance_path=f"data/_raw/iohk-results/fund-{fund:02d}.csv",
        parsed_at=parsed_at,
    )
    print(f"  f{fund}: {summary.rows_matched} rows, {summary.funded_count} funded")
    return summary.rows_matched, summary.funded_count


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
        help="Fund(s) to parse. May be passed multiple times. Default: F1-F14.",
    )
    args = parser.parse_args(argv)
    root = args.data_root if args.data_root is not None else DEFAULT_DATA_ROOT
    funds = tuple(args.fund) if args.fund else DEFAULT_FUNDS
    total_ok = 0
    for fund in funds:
        if parse_fund(fund, root) is not None:
            total_ok += 1
    print(f"\nparsed {total_ok}/{len(funds)} funds")
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "parse_fund"]
