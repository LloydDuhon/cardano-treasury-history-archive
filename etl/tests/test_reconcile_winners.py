"""Tests for normalizers/reconcile_winners.py."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from normalizers.reconcile_winners import reconcile_fund

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "reconciliation.schema.json"


@pytest.fixture(scope="module")
def reconciliation_validator() -> Draft202012Validator:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return Draft202012Validator(json.load(fh))


def _write_inputs(
    data_root: Path,
    fund: int,
    lidonation: list[dict[str, Any]],
    iohk_rows: list[dict[str, Any]],
) -> None:
    fund_dir = data_root / "funds" / f"fund-{fund:02d}"
    intermediate = fund_dir / "_intermediate"
    intermediate.mkdir(parents=True)
    (fund_dir / "proposals.json").write_text(json.dumps(lidonation), encoding="utf-8")
    (intermediate / "iohk_winners.json").write_text(
        json.dumps(
            {
                "fund": fund,
                "parsed_at": "2026-05-13T00:00:00Z",
                "source": {
                    "label": "iohk_voting_results_pdf",
                    "url": "https://x/y.pdf",
                    "provenance_path": "data/_raw/iohk-pdfs/fund-02.pdf",
                },
                "summary": {
                    "page_count": 5,
                    "rows_matched": len(iohk_rows),
                    "funded_count": sum(1 for r in iohk_rows if r["funded"]),
                },
                "rows": iohk_rows,
            }
        ),
        encoding="utf-8",
    )


def _mk_lido(proposal_id: str, title: str, funding_status: str) -> dict[str, Any]:
    return {"proposal_id": proposal_id, "title": title, "funding_status": funding_status}


def _mk_iohk(title: str, funded: bool) -> dict[str, Any]:
    return {
        "title": title,
        "ask_usd": 1.0,
        "yes_votes_ada": 1,
        "remaining_ada": 1,
        "remaining_usd": 1.0,
        "funded": funded,
        "source_page": 2,
    }


def test_full_agreement_emits_no_disagreements(
    tmp_path: Path, reconciliation_validator: Draft202012Validator
) -> None:
    data_root = tmp_path / "data"
    _write_inputs(
        data_root,
        2,
        [
            _mk_lido("f02-a", "Alpha proposal", "approved"),
            _mk_lido("f02-b", "Beta proposal", "not_approved"),
        ],
        [
            _mk_iohk("Alpha proposal", True),
            _mk_iohk("Beta proposal", False),
        ],
    )
    record = reconcile_fund(data_root=data_root, fund=2)
    assert record["agreement_count"] == 2
    assert record["disagreements"] == []
    assert record["unmatched_in_primary"] == []
    assert record["unmatched_in_secondary"] == []
    errors = list(reconciliation_validator.iter_errors(record))
    assert not errors


def test_disagreement_flags_secondary_wins(
    tmp_path: Path, reconciliation_validator: Draft202012Validator
) -> None:
    data_root = tmp_path / "data"
    _write_inputs(
        data_root,
        3,
        [_mk_lido("f03-a", "Disputed", "approved")],
        [_mk_iohk("Disputed", False)],
    )
    record = reconcile_fund(data_root=data_root, fund=3)
    assert record["agreement_count"] == 0
    assert len(record["disagreements"]) == 1
    d = record["disagreements"][0]
    assert d["primary_proposal_id"] == "f03-a"
    assert d["primary_funding_status"] == "approved"
    assert d["secondary_funded_flag"] is False
    assert d["verdict"] == "secondary_wins"
    errors = list(reconciliation_validator.iter_errors(record))
    assert not errors


def test_unmatched_records_appear_in_both_buckets(
    tmp_path: Path, reconciliation_validator: Draft202012Validator
) -> None:
    data_root = tmp_path / "data"
    _write_inputs(
        data_root,
        4,
        [
            _mk_lido("f04-only", "Only in Lidonation", "not_approved"),
            _mk_lido("f04-both", "Both", "approved"),
        ],
        [
            _mk_iohk("Both", True),
            _mk_iohk("Only in IOG PDF", True),
        ],
    )
    record = reconcile_fund(data_root=data_root, fund=4)
    assert record["agreement_count"] == 1
    assert len(record["unmatched_in_primary"]) == 1
    assert record["unmatched_in_primary"][0]["title"] == "Only in IOG PDF"
    assert len(record["unmatched_in_secondary"]) == 1
    assert record["unmatched_in_secondary"][0]["title"] == "Only in Lidonation"
    errors = list(reconciliation_validator.iter_errors(record))
    assert not errors


def test_title_matching_is_punctuation_insensitive(tmp_path: Path) -> None:
    """Trailing colons, extra spaces, casing should not break the match."""
    data_root = tmp_path / "data"
    _write_inputs(
        data_root,
        5,
        [_mk_lido("f05-a", "Liqwid: Cardano DeFi Lending Markets", "approved")],
        [_mk_iohk("Liqwid:Cardano DeFi Lending Markets", True)],
    )
    record = reconcile_fund(data_root=data_root, fund=5)
    assert record["agreement_count"] == 1
    assert record["disagreements"] == []


def test_missing_input_raises(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    with pytest.raises(FileNotFoundError):
        reconcile_fund(data_root=data_root, fund=99)
