"""Unit tests for normalizers/unify_proposals.py."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from normalizers.unify_proposals import (
    SnapshotContext,
    _coerce_fund_number,
    _coerce_funding_status,
    _coerce_project_status,
    _mint_proposal_id,
    normalize_record,
    unify,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "proposal.schema.json"


@pytest.fixture(scope="module")
def proposal_validator() -> Draft202012Validator:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    return Draft202012Validator(schema)


def test_coerce_fund_number_handles_common_titles() -> None:
    assert _coerce_fund_number("Fund 10") == 10
    assert _coerce_fund_number("Fund10") == 10
    assert _coerce_fund_number("F2") == 2
    assert _coerce_fund_number(None) is None
    assert _coerce_fund_number("") is None
    assert _coerce_fund_number("Fund Catalyst") is None


def test_coerce_funding_status_maps_unfunded_to_not_approved() -> None:
    assert _coerce_funding_status("approved") == "approved"
    assert _coerce_funding_status("not_approved") == "not_approved"
    assert _coerce_funding_status("unfunded") == "not_approved"
    assert _coerce_funding_status("funded") == "approved"
    assert _coerce_funding_status("nonsense") == "unknown"
    assert _coerce_funding_status(None) == "unknown"


def test_coerce_project_status_normalizes_hyphenation() -> None:
    assert _coerce_project_status("in_progress") == "in_progress"
    assert _coerce_project_status("in-progress") == "in_progress"
    assert _coerce_project_status("completed") == "complete"
    assert _coerce_project_status("anything-else") == "unknown"


def test_mint_proposal_id_format_is_stable() -> None:
    assert _mint_proposal_id(10, "decentralize-impact", fallback="x") == "f10-decentralize-impact"
    assert _mint_proposal_id(2, None, fallback="abc-123") == "f02-abc-123"
    # Underscores become hyphens via slugify
    assert _mint_proposal_id(10, "smart_contracts", fallback="x") == "f10-smart-contracts"


def test_normalize_record_real_fixture_passes_schema(
    proposals_page_dict: dict[str, object],
    proposal_validator: Draft202012Validator,
) -> None:
    data = proposals_page_dict.get("data") or []
    assert data, "fixture must contain at least one record"
    ctx = SnapshotContext(fetched_at="2026-05-13T12:00:00Z")
    for raw in data:
        assert isinstance(raw, dict)
        fund_title = (raw.get("fund") or {}).get("title")
        fund_n = _coerce_fund_number(fund_title)
        assert fund_n is not None, f"fixture record missing fund: {raw.get('id')}"
        norm = normalize_record(raw, fund_n, "data/_raw/lidonation/page-0001.json.gz", ctx)
        assert norm is not None
        # Should validate against proposal.schema.json
        errors = list(proposal_validator.iter_errors(norm))
        assert not errors, [(list(e.absolute_path), e.message) for e in errors]
        # Mandatory fields populated
        assert norm["fund"] == fund_n
        assert norm["proposal_id"].startswith(f"f{fund_n:02d}-")
        assert norm["funding_status"] in {
            "approved",
            "not_approved",
            "over_budget",
            "leftover",
            "withdrawn",
            "unknown",
        }
        assert norm["project_status"] in {
            "unfunded",
            "funded",
            "in_progress",
            "complete",
            "cancelled",
            "stalled",
            "unknown",
        }
        assert norm["sources"]
        assert norm["sources"][0]["source"] == "lidonation_api"


def test_unify_end_to_end_writes_perfund_files(
    tmp_path: Path,
    proposals_page_payload: bytes,
    proposal_validator: Draft202012Validator,
) -> None:
    """Feed one cached page through `unify` and assert outputs are well-formed."""
    data_root = tmp_path / "data"
    raw_dir = data_root / "_raw" / "lidonation"
    raw_dir.mkdir(parents=True)
    (raw_dir / "page-0001.json.gz").write_bytes(gzip.compress(proposals_page_payload))

    summary = unify(data_root=data_root)
    assert summary, "expected at least one fund to be written"

    for fund_n, count in summary.items():
        fund_dir = data_root / "funds" / f"fund-{fund_n:02d}"
        proposals_path = fund_dir / "proposals.json"
        meta_path = fund_dir / "_meta.json"
        assert proposals_path.exists()
        assert meta_path.exists()

        records = json.loads(proposals_path.read_text())
        assert isinstance(records, list)
        assert len(records) == count
        for r in records:
            errors = list(proposal_validator.iter_errors(r))
            assert not errors, [(list(e.absolute_path), e.message) for e in errors]

        meta = json.loads(meta_path.read_text())
        assert meta["fund"] == fund_n
        assert meta["record_count"] == count
        assert "lidonation_api" in meta["sources_used"]


def test_unify_only_funds_filter(
    tmp_path: Path,
    proposals_page_payload: bytes,
) -> None:
    """only_funds=[N] writes at most fund-N/, never any other fund."""
    data_root = tmp_path / "data"
    raw_dir = data_root / "_raw" / "lidonation"
    raw_dir.mkdir(parents=True)
    (raw_dir / "page-0001.json.gz").write_bytes(gzip.compress(proposals_page_payload))

    # Pick a fund that exists in the fixture (page 1 mixes ~8 funds).
    summary = unify(data_root=data_root, only_funds=[4])
    funds_dir = data_root / "funds"
    if funds_dir.exists():
        fund_dirs = list(funds_dir.iterdir())
        assert all(d.name == "fund-04" for d in fund_dirs)
    # If F4 was in the page we should have something; if not, summary is empty.
    if 4 in summary:
        assert summary[4] > 0
