"""Tests for normalizers/derive_fund_one.py."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

import normalizers.derive_fund_one as derive_fund_one_module
from fetchers.ideascale_wayback import _snapshot_path
from normalizers.derive_fund_one import _extract_dtd_ids, derive, parse_snapshot

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "proposal.schema.json"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "wayback"


@pytest.fixture(scope="module")
def proposal_validator() -> Draft202012Validator:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return Draft202012Validator(json.load(fh))


def _stage_cache(data_root: Path) -> None:
    """Drop CDX + 2 snapshots into the per-fund provenance dir."""
    prov = data_root / "funds" / "fund-01" / "_provenance" / "ideascale_wayback"
    snap_dir = prov / "snapshots"
    snap_dir.mkdir(parents=True)
    (prov / "cdx.json.gz").write_bytes(gzip.compress((FIXTURE_DIR / "cdx.json").read_bytes()))
    rich = (FIXTURE_DIR / "sample-proposal.html").read_bytes()
    bare = (FIXTURE_DIR / "sample-bare-proposal.html").read_bytes()
    # Use the same filename scheme the fetcher produces, so cdx -> snapshot
    # matching works.
    p1 = _snapshot_path(data_root, "com,ideascale,cardano)/a/dtd/100001-1")
    p2 = _snapshot_path(data_root, "com,ideascale,cardano)/a/dtd/100002-1")
    p1.parent.mkdir(parents=True, exist_ok=True)
    p1.write_bytes(gzip.compress(rich))
    p2.write_bytes(gzip.compress(bare))


def test_extract_dtd_ids_parses_canonical_url() -> None:
    idea, campaign = _extract_dtd_ids("https://cardano.ideascale.com/a/dtd/100001-1")
    assert idea == "100001"
    assert campaign == "1"


def test_extract_dtd_ids_unmatched_returns_nones() -> None:
    assert _extract_dtd_ids("https://example.com/x") == (None, None)
    assert _extract_dtd_ids("") == (None, None)


def test_parse_snapshot_rich_html_extracts_all_fields() -> None:
    html = (FIXTURE_DIR / "sample-proposal.html").read_bytes()
    parsed = parse_snapshot(html)
    assert parsed["title"] == "Build a Cardano DEX"
    assert parsed["proposer_name"] == "Alice Catalyst"
    assert parsed["description"] and "decentralized exchange" in parsed["description"]
    assert parsed["ask_text"] and "50,000" in parsed["ask_text"]


def test_parse_snapshot_bare_html_falls_back_to_h1() -> None:
    html = (FIXTURE_DIR / "sample-bare-proposal.html").read_bytes()
    parsed = parse_snapshot(html)
    assert parsed["title"] == "Cardano Meetups Mexico"
    assert parsed["proposer_name"] is None
    assert parsed["description"] is None
    assert parsed["ask_text"] is None


def test_parse_snapshot_empty_html_returns_all_nones() -> None:
    parsed = parse_snapshot(b"")
    assert parsed == {"title": None, "proposer_name": None, "description": None, "ask_text": None}


def test_derive_emits_schema_conformant_records(
    tmp_path: Path, proposal_validator: Draft202012Validator
) -> None:
    data_root = tmp_path / "data"
    _stage_cache(data_root)
    count = derive(data_root=data_root)
    assert count == 2

    out_path = data_root / "funds" / "fund-01" / "proposals.json"
    records: list[dict[str, Any]] = json.loads(out_path.read_text())
    assert len(records) == 2

    for r in records:
        errors = list(proposal_validator.iter_errors(r))
        assert not errors, [(list(e.absolute_path), e.message) for e in errors]
        assert r["fund"] == 1
        assert r["funding_status"] == "unknown"
        assert r["project_status"] == "unfunded"
        assert r["confidence"] == "low"
        assert r["sources"][0]["source"] == "ideascale_wayback"


def test_derive_emits_meta_with_phase4_notes(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _stage_cache(data_root)
    derive(data_root=data_root)
    meta = json.loads((data_root / "funds" / "fund-01" / "_meta.json").read_text())
    assert meta["fund"] == 1
    assert meta["phase"] == "phase-4"
    assert "ideascale_wayback" in meta["sources_used"]
    assert "low" in meta["phase_notes"].lower() or "low" in str(meta).lower()


def test_derive_uses_fund_one_pdf_when_wayback_has_no_snapshots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, proposal_validator: Draft202012Validator
) -> None:
    data_root = tmp_path / "data"
    (data_root / "funds" / "fund-01" / "_provenance" / "ideascale_wayback").mkdir(parents=True)
    pdf_path = data_root / "_raw" / "iohk-pdfs" / "fund-01.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(b"%PDF-1.7\n")

    def fake_parse_fund_one_pdf(_pdf_path: Path) -> tuple[list[dict[str, Any]], Any]:
        summary = type("Summary", (), {"rows_matched": 2, "funded_count": 1})()
        return (
            [
                {
                    "title": "Alpha",
                    "funded": True,
                    "amount_requested": 10.0,
                    "currency": "USD",
                    "yes_votes_ada": 100,
                    "no_votes_ada": 1,
                    "source_row": 1,
                },
                {
                    "title": "Beta",
                    "funded": False,
                    "amount_requested": 20.0,
                    "currency": "USD",
                    "yes_votes_ada": 10,
                    "no_votes_ada": 50,
                    "source_row": 2,
                },
            ],
            summary,
        )

    monkeypatch.setattr(derive_fund_one_module, "parse_fund_one_pdf", fake_parse_fund_one_pdf)

    count = derive(data_root=data_root)

    assert count == 2
    records: list[dict[str, Any]] = json.loads(
        (data_root / "funds" / "fund-01" / "proposals.json").read_text()
    )
    assert {record["funding_status"] for record in records} == {"approved", "not_approved"}
    assert all(record["sources"][0]["source"] == "iohk_voting_results_pdf" for record in records)
    for record in records:
        errors = list(proposal_validator.iter_errors(record))
        assert not errors, [(list(e.absolute_path), e.message) for e in errors]


def test_derive_missing_cache_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        derive(data_root=tmp_path / "data")
