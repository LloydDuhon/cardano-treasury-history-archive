"""Tests for normalizers/dedupe_proposers.py."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from normalizers.dedupe_proposers import (
    _extract_external_ids,
    _mint_proposer_id,
    build_proposers,
    dedupe,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSER_SCHEMA = REPO_ROOT / "schemas" / "proposer.schema.json"


@pytest.fixture(scope="module")
def proposer_validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(PROPOSER_SCHEMA.read_text()))


def _stub_proposal(proposal_id: str, fund: int, proposer_ids: list[str]) -> dict[str, Any]:
    return {
        "proposal_id": proposal_id,
        "fund": fund,
        "title": proposal_id,
        "proposer_ids": proposer_ids,
        "amount_requested": 100,
        "amount_received": 100,
        "currency": "ADA",
        "funding_status": "approved",
        "project_status": "funded",
        "links": {},
        "sources": [],
        "confidence": "medium",
    }


def _stage_two_funds_same_proposer(tmp_path: Path) -> Path:
    """Same Lidonation UUID used in F10 and F11 -> should collapse to one proposer."""
    data_root = tmp_path / "data"
    for fund_n, proposal_id in [(10, "f10-a"), (11, "f11-b")]:
        d = data_root / "funds" / f"fund-{fund_n:02d}"
        d.mkdir(parents=True)
        (d / "proposals.json").write_text(
            json.dumps(
                [
                    _stub_proposal(
                        proposal_id, fund_n, ["p-lido-9a2cc727-a9d2-482a-ab55-5dfccc14988e"]
                    )
                ]
            )
        )
    return data_root


def test_extract_external_ids_recognizes_lidonation_pattern() -> None:
    ext = _extract_external_ids("p-lido-9a2cc727-a9d2-482a-ab55-5dfccc14988e")
    assert ext == {"lidonation_profile_uuid": "9a2cc727-a9d2-482a-ab55-5dfccc14988e"}


def test_extract_external_ids_returns_empty_for_unknown_pattern() -> None:
    assert _extract_external_ids("p-arbitrary") == {}


def test_mint_proposer_id_is_stable_for_same_anchor() -> None:
    a = _mint_proposer_id("Marc-Andre", "anchor-1")
    b = _mint_proposer_id("Marc-Andre", "anchor-1")
    c = _mint_proposer_id("Marc-Andre", "anchor-2")
    assert a == b
    assert a != c


def test_build_proposers_collapses_same_uuid_across_funds(tmp_path: Path) -> None:
    data_root = _stage_two_funds_same_proposer(tmp_path)
    proposers = build_proposers(data_root=data_root)
    assert len(proposers) == 1
    rec = next(iter(proposers.values()))
    assert rec["external_ids"]["lidonation_profile_uuid"].startswith("9a2cc727")
    assert sorted(rec["proposal_ids"]) == ["f10-a", "f11-b"]
    assert rec["rollups"]["first_fund"] == 10
    assert rec["rollups"]["last_fund"] == 11
    assert rec["rollups"]["total_proposals"] == 2
    assert rec["rollups"]["total_funded"] == 2


def test_build_proposers_keeps_distinct_uuids_separate(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    d = data_root / "funds" / "fund-10"
    d.mkdir(parents=True)
    (d / "proposals.json").write_text(
        json.dumps(
            [
                _stub_proposal("f10-a", 10, ["p-lido-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"]),
                _stub_proposal("f10-b", 10, ["p-lido-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]),
            ]
        )
    )
    proposers = build_proposers(data_root=data_root)
    assert len(proposers) == 2


def test_dedupe_writes_per_fund_files_validating_schema(
    tmp_path: Path, proposer_validator: Draft202012Validator
) -> None:
    data_root = _stage_two_funds_same_proposer(tmp_path)
    dedupe(data_root=data_root)
    for fund_n in (10, 11):
        path = data_root / "funds" / f"fund-{fund_n:02d}" / "proposers.json"
        assert path.exists()
        records = json.loads(path.read_text())
        assert len(records) == 1
        for r in records:
            errors = list(proposer_validator.iter_errors(r))
            assert not errors, [(list(e.absolute_path), e.message) for e in errors]


def test_dedupe_records_fuzzy_candidates_when_display_names_match(
    tmp_path: Path,
) -> None:
    """Two distinct UUIDs with identical display name should mutually populate
    duplicate_candidates[]. We need names in the raw cache to test this."""
    data_root = tmp_path / "data"
    d = data_root / "funds" / "fund-10"
    d.mkdir(parents=True)
    (d / "proposals.json").write_text(
        json.dumps(
            [
                _stub_proposal("f10-a", 10, ["p-lido-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"]),
                _stub_proposal("f10-b", 10, ["p-lido-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]),
            ]
        )
    )
    raw = data_root / "_raw" / "lidonation"
    raw.mkdir(parents=True)
    (raw / "page-0001.json.gz").write_bytes(
        gzip.compress(
            json.dumps(
                {
                    "data": [
                        {
                            "users": [
                                {
                                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                    "name": "Marc Brochu",
                                }
                            ]
                        },
                        {
                            "users": [
                                {
                                    "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                                    "name": "Marc Brochu",
                                }
                            ]
                        },
                    ]
                }
            ).encode()
        )
    )
    proposers = dedupe(data_root=data_root)
    # Both should have the other in duplicate_candidates
    records = list(proposers.values())
    assert len(records) == 2
    for r in records:
        assert len(r["duplicate_candidates"]) == 1
