"""Tests for parsers/projectcatalyst_results.py."""

from __future__ import annotations

from pathlib import Path

from parsers.projectcatalyst_results import parse_csv_results, parse_fund_one_pdf

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_parse_csv_results_handles_early_usd_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "fund-02.csv"
    csv_path.write_text(
        "\n".join(
            [
                "Proposal,Yes,No,Result,Meets approval threshold,Requested $,Status",
                "Alpha,₳10,₳2,₳8,YES,$123.00,FUNDED",
                "Beta,₳1,₳9,₳-8,NO,$456.00,NOT FUNDED",
                ",,,,,#REF!,#REF!",
            ]
        ),
        encoding="utf-8",
    )

    rows, summary = parse_csv_results(csv_path)

    assert summary.rows_matched == 2
    assert summary.funded_count == 1
    assert rows[0]["title"] == "Alpha"
    assert rows[0]["amount_requested"] == 123.0
    assert rows[0]["currency"] == "USD"
    assert rows[0]["funded"] is True
    assert rows[1]["funded"] is False


def test_parse_csv_results_handles_later_ada_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "fund-10.csv"
    csv_path.write_text(
        "\n".join(
            [
                "Proposal,Votes cast,Yes,Abstain,Meets approval threshold,Requested Ada,Status",
                "Gamma,10,₳100,₳7,YES,₳42,FUNDED",
            ]
        ),
        encoding="utf-8",
    )

    rows, summary = parse_csv_results(csv_path)

    assert summary.rows_matched == 1
    assert summary.funded_count == 1
    assert rows[0]["amount_requested"] == 42.0
    assert rows[0]["currency"] == "ADA"
    assert rows[0]["yes_votes_ada"] == 100
    assert rows[0]["abstain_votes_ada"] == 7


def test_parse_fund_one_pdf_extracts_staff_provided_result_table() -> None:
    pdf_path = REPO_ROOT / "data" / "_raw" / "iohk-pdfs" / "fund-01.pdf"
    rows, summary = parse_fund_one_pdf(pdf_path)

    assert summary.rows_matched == 45
    assert summary.funded_count == 8
    assert rows[0]["title"] == "Open Source Experiential Learning"
    assert rows[0]["funded"] is True
    assert rows[-1]["title"] == "FOX Rewards"
    assert rows[-1]["funded"] is False
