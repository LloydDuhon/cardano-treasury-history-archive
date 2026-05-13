"""Parse IOG-published catalyst-voting-results PDFs into structured rows.

These PDFs follow a consistent layout across funds F2-F9 (and onward), with
small variations:

    PROPOSALS   REQUESTED   USD value in ada   Funds remaining   STATUS
    <title>     $<ask_usd>  ADA <yes_votes>   ADA <remaining>   $<remaining_usd>  [Funded]

Funded rows carry a "Funded" trailing token; not-funded rows have an empty
trailing region (with a separate "Not Funded\n<reason>" block on subsequent
lines that we ignore for outcome purposes).

Validated on the Fund 2 PDF (78 proposals, 11 funded). Other funds may need
parser variants - we add per-fund handling when we hit them in Phase 2 sweeps.

Pure function: takes a Path, returns a list[ParsedRow] plus a summary dict.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TypedDict

import pdfplumber

ADA_SIGN = "₳"

# Matches one proposal row from the per-page table layout. Example:
#   "Create message signing standard $ 535.00 ADA 359,354,404 ADA 9,109,435 $ 199,465 Funded"
# (ADA glyph is U+20B3.)
_ROW_RE = re.compile(
    rf"^(.+?)\s+\$\s*([\d,\.]+)\s+{ADA_SIGN}\s*([\d,]+)\s+{ADA_SIGN}\s*([\d,]+)\s+\$\s*([\d,\.]+)\s*(.*)$"
)


class ParsedRow(TypedDict):
    """One proposal row extracted from a voting-results PDF."""

    title: str
    ask_usd: float
    yes_votes_ada: int
    remaining_ada: int
    remaining_usd: float
    funded: bool
    source_page: int


@dataclass(frozen=True)
class PdfParseSummary:
    """Aggregate metadata for one PDF parse."""

    page_count: int
    rows_matched: int
    funded_count: int


def _coerce_int(s: str) -> int:
    return int(s.replace(",", ""))


def _coerce_float(s: str) -> float:
    return float(s.replace(",", ""))


def iter_rows(pdf_path: Path) -> Iterator[ParsedRow]:
    """Yield parsed proposal rows from a voting-results PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for raw_line in text.split("\n"):
                line = raw_line.strip()
                if not line:
                    continue
                m = _ROW_RE.match(line)
                if not m:
                    continue
                title, ask, yes_ada, rem_ada, rem_usd, tail = m.groups()
                yield ParsedRow(
                    title=title.strip(),
                    ask_usd=_coerce_float(ask),
                    yes_votes_ada=_coerce_int(yes_ada),
                    remaining_ada=_coerce_int(rem_ada),
                    remaining_usd=_coerce_float(rem_usd),
                    funded=tail.strip().lower() == "funded",
                    source_page=page_idx + 1,
                )


def parse_voting_results_pdf(
    pdf_path: Path,
) -> tuple[list[ParsedRow], PdfParseSummary]:
    """Parse a voting-results PDF into a list of rows.

    Args:
        pdf_path: Path to a downloaded PDF.

    Returns:
        (rows, summary). `rows` is in document order with duplicates removed
        by (title, source_page).
    """
    rows: list[ParsedRow] = []
    seen: set[tuple[str, int]] = set()
    page_count = 0
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
    for r in iter_rows(pdf_path):
        key = (r["title"], r["source_page"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(r)
    summary = PdfParseSummary(
        page_count=page_count,
        rows_matched=len(rows),
        funded_count=sum(1 for r in rows if r["funded"]),
    )
    return rows, summary


def write_intermediate(
    rows: list[ParsedRow],
    summary: PdfParseSummary,
    *,
    fund: int,
    data_root: Path,
    source_url: str,
    pdf_relpath: str,
    parsed_at: str,
) -> Path:
    """Write the parsed PDF rows + summary to data/funds/fund-XX/_intermediate/iohk_winners.json.

    Returns the path to the written file.
    """
    fund_dir = data_root / "funds" / f"fund-{fund:02d}"
    intermediate_dir = fund_dir / "_intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    out_path = intermediate_dir / "iohk_winners.json"
    payload = {
        "fund": fund,
        "parsed_at": parsed_at,
        "source": {
            "label": "iohk_voting_results_pdf",
            "url": source_url,
            "provenance_path": pdf_relpath,
        },
        "summary": asdict(summary),
        "rows": list(rows),
    }
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return out_path


__all__ = [
    "ParsedRow",
    "PdfParseSummary",
    "iter_rows",
    "parse_voting_results_pdf",
    "write_intermediate",
]
