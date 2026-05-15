"""Tests for parsers/projectcatalyst_results.py."""

from __future__ import annotations

from pathlib import Path

from parsers.projectcatalyst_results import (
    parse_csv_result_files,
    parse_csv_results,
    parse_fund_one_pdf,
)

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


def test_parse_csv_result_files_merges_fund14_leftovers_override(tmp_path: Path) -> None:
    main = tmp_path / "fund-14-cardano-open-developers.csv"
    main.write_text(
        "\n".join(
            [
                (
                    "Proposal,Votes cast,Yes,Abstain,Meets approval threshold,"
                    "Requested Ada,Status,Reason for not funded status"
                ),
                "Alpha,10,₳100,₳1,YES,₳42,NOT FUNDED,Over Budget",
                "Beta,11,₳110,₳2,YES,₳43,NOT FUNDED,Over Budget",
            ]
        ),
        encoding="utf-8",
    )
    leftovers = tmp_path / "fund-14-sponsored-by-leftovers.csv"
    leftovers.write_text(
        "\n".join(
            [
                (
                    "2 funded?,Category,Proposal,Votes cast,Yes,Abstain,"
                    "Meets approval threshold,Requested Ada,Status,"
                    "Reason for not funded status"
                ),
                "yes,dev,Alpha,10,₳100,₳1,YES,₳42,FUNDED,",
                (
                    "no,dev,Beta,11,₳110,₳2,YES,₳43,"
                    '"Does not meet ""sponsored by leftovers"" requirements.",'
                ),
            ]
        ),
        encoding="utf-8",
    )
    withdrawn = tmp_path / "fund-14-withdrawn.csv"
    withdrawn.write_text(
        "\n".join(
            [
                "Challenge,Proposer,Proposal,Votes cast,Yes,Abstain,Requested Ada",
                "Cardano Use Cases,Mynth,Gamma,211,₳131879,₳30,₳450000",
            ]
        ),
        encoding="utf-8",
    )

    rows, summary = parse_csv_result_files([main, leftovers, (withdrawn, "WITHDRAWN")])

    by_title = {row["title"]: row for row in rows}
    assert summary.rows_matched == 3
    assert summary.funded_count == 1
    assert by_title["Alpha"]["funded"] is True
    assert by_title["Alpha"]["source_file"] == leftovers.name
    assert by_title["Beta"]["funded"] is False
    assert by_title["Beta"]["source_file"] == main.name
    assert by_title["Gamma"]["status"] == "WITHDRAWN"


def test_parse_fund_one_pdf_extracts_staff_provided_result_table() -> None:
    pdf_path = REPO_ROOT / "data" / "_raw" / "iohk-pdfs" / "fund-01.pdf"
    rows, summary = parse_fund_one_pdf(pdf_path)

    assert summary.rows_matched == 45
    assert summary.funded_count == 8
    assert rows[0]["title"] == "Open Source Experiential Learning"
    assert rows[0]["funded"] is True
    assert rows[-1]["title"] == "FOX Rewards"
    assert rows[-1]["funded"] is False
