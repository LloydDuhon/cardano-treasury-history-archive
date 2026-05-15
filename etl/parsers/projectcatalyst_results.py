"""Parse official Project Catalyst voting-results artifacts.

The current `projectcatalyst.io/funds/{N}/voting-results` pages link to
Google Sheets. We cache those as CSV files under `data/_raw/iohk-results/`.
Fund 1 is different: Catalyst staff provided a one-page PDF, and the extracted
table text is good enough for outcome and rough amount fields.
"""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypedDict

import pdfplumber


class CatalystResultRow(TypedDict, total=False):
    """One row extracted from an official voting-results artifact."""

    title: str
    funded: bool
    status: str
    amount_requested: float | None
    currency: str | None
    yes_votes_ada: int | None
    no_votes_ada: int | None
    abstain_votes_ada: int | None
    vote_result_ada: int | None
    meets_approval_threshold: bool | None
    overall_score: float | None
    source_row: int
    source_file: str
    raw: dict[str, str]


@dataclass(frozen=True)
class CatalystResultSummary:
    """Aggregate metadata for one parsed artifact."""

    rows_matched: int
    funded_count: int
    source_kind: str


_FUND_ONE_ROW_RE = re.compile(
    r"^(?P<title>.+?)\s+"
    r"(?P<requested>[\d,]+)\s+"
    r"(?P<yes>[\d,]+)\s+"
    r"(?P<no>[\d,]+)\s+"
    r"\$\s*(?P<remaining>[\d,]+)\s+"
    r"(?P<status>NOT\s+FUNDE\s*D|FUNDE\s*D)$",
    flags=re.IGNORECASE,
)


def _clean_header(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _value(row: dict[str, str], *names: str) -> str:
    by_clean = {_clean_header(k): v for k, v in row.items()}
    for name in names:
        got = by_clean.get(_clean_header(name))
        if got is not None:
            return got.strip()
    return ""


def _money_or_number(value: str) -> float | None:
    cleaned = (
        (value or "")
        .replace("₳", "")
        .replace("$", "")
        .replace(",", "")
        .replace("#REF!", "")
        .strip()
    )
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _ada_int(value: str) -> int | None:
    parsed = _money_or_number(value)
    if parsed is None:
        return None
    return int(parsed)


def _bool_yes(value: str) -> bool | None:
    cleaned = (value or "").strip().lower()
    if cleaned == "yes":
        return True
    if cleaned == "no":
        return False
    return None


def _funded_from_status(value: str) -> bool:
    return (
        "funded" in (value or "").strip().lower()
        and "not funded" not in (value or "").strip().lower()
    )


def _requested_field(row: dict[str, str]) -> tuple[float | None, str | None]:
    usd = _value(row, "Requested $", "REQUESTED $")
    if usd:
        return _money_or_number(usd), "USD"
    ada = _value(row, "Requested Ada")
    if ada:
        return _money_or_number(ada), "ADA"
    return None, None


def iter_csv_rows(
    csv_path: Path,
    *,
    default_status: str | None = None,
) -> Iterator[CatalystResultRow]:
    """Yield parsed rows from a cached official Catalyst CSV."""
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row_index, row in enumerate(reader, start=2):
            title = _value(row, "Proposal")
            status = _value(row, "Status", "STATUS") or (default_status or "")
            if not title or not status or status == "#REF!":
                continue
            amount_requested, currency = _requested_field(row)
            result_row: CatalystResultRow = {
                "title": title,
                "funded": _funded_from_status(status),
                "status": status,
                "amount_requested": amount_requested,
                "currency": currency,
                "yes_votes_ada": _ada_int(_value(row, "Yes", "YES")),
                "no_votes_ada": _ada_int(_value(row, "No", "NO")),
                "abstain_votes_ada": _ada_int(_value(row, "Abstain")),
                "vote_result_ada": _ada_int(_value(row, "Result")),
                "meets_approval_threshold": _bool_yes(_value(row, "Meets approval threshold")),
                "overall_score": _money_or_number(_value(row, "Overall score")),
                "source_row": row_index,
                "source_file": csv_path.name,
                "raw": dict(row),
            }
            yield result_row


def parse_csv_results(
    csv_path: Path,
    *,
    default_status: str | None = None,
) -> tuple[list[CatalystResultRow], CatalystResultSummary]:
    """Parse a cached official Catalyst CSV into normalized result rows."""
    rows = list(iter_csv_rows(csv_path, default_status=default_status))
    summary = CatalystResultSummary(
        rows_matched=len(rows),
        funded_count=sum(1 for row in rows if row["funded"]),
        source_kind="projectcatalyst_voting_results_csv",
    )
    return rows, summary


def _result_priority(row: CatalystResultRow) -> tuple[int, int]:
    """Rank duplicate rows from a multi-tab result workbook.

    Fund 14's `Sponsored by leftovers` tab repeats proposals from their primary
    challenge tab. A `FUNDED` leftovers row is the final official result and
    should override the earlier over-budget row. Non-funded leftovers rows are
    explanatory and should not replace the primary challenge result.
    """
    source_file = row.get("source_file", "")
    if row["funded"] and "sponsored-by-leftovers" in source_file:
        return (2, 0)
    if "sponsored-by-leftovers" in source_file:
        return (0, 0)
    if row.get("status") == "WITHDRAWN":
        return (1, 0)
    return (1, 1)


def parse_csv_result_files(
    csv_paths: Iterable[Path | tuple[Path, str | None]],
) -> tuple[list[CatalystResultRow], CatalystResultSummary]:
    """Parse and merge multiple CSV tabs from a single official result workbook."""
    by_title: dict[str, CatalystResultRow] = {}
    for item in csv_paths:
        if isinstance(item, tuple):
            csv_path, default_status = item
        else:
            csv_path, default_status = item, None
        for row in iter_csv_rows(csv_path, default_status=default_status):
            title = row["title"]
            existing = by_title.get(title)
            if existing is None or _result_priority(row) > _result_priority(existing):
                by_title[title] = row
    rows = sorted(
        by_title.values(),
        key=lambda row: (row.get("source_file", ""), row["source_row"]),
    )
    summary = CatalystResultSummary(
        rows_matched=len(rows),
        funded_count=sum(1 for row in rows if row["funded"]),
        source_kind="projectcatalyst_voting_results_csv",
    )
    return rows, summary


def iter_fund_one_pdf_rows(pdf_path: Path) -> Iterator[CatalystResultRow]:
    """Yield Fund 1 rows from the staff-provided voting-results PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        source_row = 0
        pending: CatalystResultRow | None = None
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            in_table = False
            for raw_line in text.splitlines():
                line = " ".join(raw_line.split())
                if not line:
                    continue
                if "P R O P O SA LS" in line:
                    in_table = True
                    continue
                if not in_table:
                    continue
                m = _FUND_ONE_ROW_RE.match(line)
                if not m:
                    if pending is not None and line.startswith("(") and line.endswith(")"):
                        pending["title"] = f"{pending['title']} {line}"
                    continue
                if pending is not None:
                    yield pending
                source_row += 1
                status = " ".join(m.group("status").upper().split()).replace("FUNDE D", "FUNDED")
                pending = {
                    "title": m.group("title").strip(),
                    "funded": status == "FUNDED",
                    "status": status,
                    "amount_requested": _money_or_number(m.group("requested")),
                    "currency": "USD",
                    "yes_votes_ada": _ada_int(m.group("yes")),
                    "no_votes_ada": _ada_int(m.group("no")),
                    "abstain_votes_ada": None,
                    "vote_result_ada": None,
                    "meets_approval_threshold": None,
                    "overall_score": None,
                    "source_row": source_row,
                    "source_file": pdf_path.name,
                    "raw": {
                        "line": line,
                        "funds_remaining_usd": m.group("remaining"),
                    },
                }
        if pending is not None:
            yield pending


def parse_fund_one_pdf(
    pdf_path: Path,
) -> tuple[list[CatalystResultRow], CatalystResultSummary]:
    """Parse the staff-provided Fund 1 PDF into normalized result rows."""
    rows = list(iter_fund_one_pdf_rows(pdf_path))
    summary = CatalystResultSummary(
        rows_matched=len(rows),
        funded_count=sum(1 for row in rows if row["funded"]),
        source_kind="fund1_voting_results_pdf",
    )
    return rows, summary


def write_intermediate(
    rows: Iterable[CatalystResultRow],
    summary: CatalystResultSummary,
    *,
    fund: int,
    data_root: Path,
    source_label: str,
    source_url: str | None,
    provenance_path: str,
    parsed_at: str,
) -> Path:
    """Write parsed official result rows to fund _intermediate/iohk_winners.json."""
    fund_dir = data_root / "funds" / f"fund-{fund:02d}"
    intermediate_dir = fund_dir / "_intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    out_path = intermediate_dir / "iohk_winners.json"
    payload: dict[str, Any] = {
        "fund": fund,
        "parsed_at": parsed_at,
        "source": {
            "label": source_label,
            "url": source_url,
            "provenance_path": provenance_path,
        },
        "summary": asdict(summary),
        "rows": list(rows),
    }
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return out_path


__all__ = [
    "CatalystResultRow",
    "CatalystResultSummary",
    "iter_csv_rows",
    "iter_fund_one_pdf_rows",
    "parse_csv_result_files",
    "parse_csv_results",
    "parse_fund_one_pdf",
    "write_intermediate",
]
