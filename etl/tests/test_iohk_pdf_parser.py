"""Tests for parsers/iohk_pdf.py against the real F2 voting-results PDF."""

from __future__ import annotations

from pathlib import Path

import pytest

from parsers.iohk_pdf import parse_voting_results_pdf

FIXTURE_PDF = Path(__file__).resolve().parent / "fixtures" / "iohk-pdfs" / "fund-02.pdf"


@pytest.mark.skipif(not FIXTURE_PDF.exists(), reason="F2 PDF fixture missing")
def test_parse_f2_pdf_counts_match_canonical() -> None:
    """The F2 PDF should yield 78 rows, 11 of which are funded."""
    rows, summary = parse_voting_results_pdf(FIXTURE_PDF)
    assert summary.rows_matched == 78
    assert summary.funded_count == 11
    assert summary.page_count == 5
    assert len(rows) == 78


@pytest.mark.skipif(not FIXTURE_PDF.exists(), reason="F2 PDF fixture missing")
def test_parse_f2_pdf_first_funded_row_shape() -> None:
    """First funded row should be the 'Create message signing standard' proposal."""
    rows, _ = parse_voting_results_pdf(FIXTURE_PDF)
    first_funded = next(r for r in rows if r["funded"])
    assert first_funded["title"] == "Create message signing standard"
    assert first_funded["ask_usd"] == 535.0
    assert first_funded["yes_votes_ada"] == 359_354_404
    assert first_funded["remaining_ada"] == 9_109_435
    assert first_funded["remaining_usd"] == 199_465.0


@pytest.mark.skipif(not FIXTURE_PDF.exists(), reason="F2 PDF fixture missing")
def test_parse_f2_pdf_funded_titles() -> None:
    """All 11 F2 winners are present and unique."""
    rows, _ = parse_voting_results_pdf(FIXTURE_PDF)
    funded_titles = {r["title"] for r in rows if r["funded"]}
    assert len(funded_titles) == 11
    # Spot check a couple of well-known F2 winners.
    assert "Liqwid:Cardano DeFi Lending Markets" in funded_titles
    assert "Cardano Starter Kits + APIs" in funded_titles


@pytest.mark.skipif(not FIXTURE_PDF.exists(), reason="F2 PDF fixture missing")
def test_parse_f2_pdf_rows_have_source_page() -> None:
    """Every row should carry a 1-based source_page reference."""
    rows, _ = parse_voting_results_pdf(FIXTURE_PDF)
    for r in rows:
        assert 1 <= r["source_page"] <= 5
