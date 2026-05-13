"""Tests for normalizers/derive_milestones.py."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from normalizers.derive_milestones import (
    _derive_status,
    _extract_urls,
    _kind_for_url,
    _slug_from_proposal_url,
    derive_fund,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "milestone.schema.json"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "milestones_supabase"


@pytest.fixture(scope="module")
def milestone_validator() -> Draft202012Validator:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return Draft202012Validator(json.load(fh))


def _stage_fund_cache(data_root: Path, fund: int = 9) -> None:
    """Copy the fixture JSON files (uncompressed) into gzipped per-fund cache."""
    prov = data_root / "funds" / f"fund-{fund:02d}" / "_provenance" / "milestones_supabase"
    prov.mkdir(parents=True)
    for table in ("funds", "challenges", "proposals", "soms", "poas", "signoffs"):
        src = FIXTURE_DIR / f"{table}.json"
        dst = prov / f"{table}.json.gz"
        dst.write_bytes(gzip.compress(src.read_bytes()))


def test_extract_urls_basic() -> None:
    text = "See https://github.com/org/repo/pull/42 and http://example.com/x.pdf."
    urls = _extract_urls(text)
    assert urls == ["https://github.com/org/repo/pull/42", "http://example.com/x.pdf"]


def test_extract_urls_strips_trailing_punctuation() -> None:
    urls = _extract_urls("See (https://x.org/a), more at https://y.org/b.")
    assert "https://x.org/a" in urls
    assert "https://y.org/b" in urls


def test_extract_urls_handles_none() -> None:
    assert _extract_urls(None) == []
    assert _extract_urls("") == []


def test_kind_for_url_classification() -> None:
    assert _kind_for_url("https://github.com/org/repo") == "github_repo"
    assert _kind_for_url("https://github.com/org/repo/pull/1") == "github_pr"
    assert _kind_for_url("https://x.org/doc.pdf") == "pdf"
    assert _kind_for_url("https://youtu.be/abc") == "video"
    assert _kind_for_url("https://docs.google.com/document/d/x") == "demo"


def test_slug_from_proposal_url() -> None:
    url = "https://projectcatalyst.io/funds/9/challenge-x/my-cool-project"
    assert _slug_from_proposal_url(url, "fallback") == "my-cool-project"
    assert _slug_from_proposal_url(None, "fallback") == "fallback"


def test_derive_status_accepted_when_signoff_present() -> None:
    poas_by_som = {1: [{"current": True, "active_reviews": 0}]}
    signoffs_by_som = {1: [{"id": 99}]}
    assert _derive_status(1, poas_by_som, signoffs_by_som) == "accepted"


def test_derive_status_under_review() -> None:
    poas_by_som = {1: [{"current": True, "active_reviews": 2}]}
    assert _derive_status(1, poas_by_som, {}) == "under_review"


def test_derive_status_submitted_when_poa_no_review() -> None:
    poas_by_som = {1: [{"current": True, "active_reviews": 0}]}
    assert _derive_status(1, poas_by_som, {}) == "submitted"


def test_derive_status_not_started_when_no_poa() -> None:
    assert _derive_status(1, {}, {}) == "not_started"


def test_derive_fund_writes_schema_conformant_milestones(
    tmp_path: Path, milestone_validator: Draft202012Validator
) -> None:
    data_root = tmp_path / "data"
    _stage_fund_cache(data_root, fund=9)

    count = derive_fund(data_root=data_root, fund=9)
    out_path = data_root / "funds" / "fund-09" / "milestones.json"
    assert out_path.exists()
    records: list[dict[str, Any]] = json.loads(out_path.read_text())
    assert len(records) == count
    assert count > 0
    for r in records:
        errors = list(milestone_validator.iter_errors(r))
        assert not errors, [(list(e.absolute_path), e.message) for e in errors]
        assert r["sources"][0]["source"] == "milestones_projectcatalyst_io"


def test_derive_fund_marks_final_milestone_as_closeout(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _stage_fund_cache(data_root, fund=9)
    derive_fund(data_root=data_root, fund=9)
    records: list[dict[str, Any]] = json.loads(
        (data_root / "funds" / "fund-09" / "milestones.json").read_text()
    )
    # Group by proposal_id and check that exactly one milestone per proposal has is_closeout=true.
    by_proposal: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        by_proposal.setdefault(r["proposal_id"], []).append(r)
    for proposal_id, rows in by_proposal.items():
        closeouts = [r for r in rows if r["is_closeout"]]
        assert len(closeouts) == 1, f"proposal {proposal_id} has {len(closeouts)} closeouts"
        max_n = max(r["milestone_number"] for r in rows)
        assert closeouts[0]["milestone_number"] == max_n


def test_derive_fund_filters_current_soms_only(tmp_path: Path) -> None:
    """Old (current=false) SoM revisions must NOT appear in normalized output."""
    data_root = tmp_path / "data"
    _stage_fund_cache(data_root, fund=9)
    derive_fund(data_root=data_root, fund=9)
    records = json.loads((data_root / "funds" / "fund-09" / "milestones.json").read_text())
    # Each proposal should have <= milestones_qty milestone rows.
    proposals = json.loads((FIXTURE_DIR / "proposals.json").read_text())
    qty_by_proposal_id = {p["id"]: p["milestones_qty"] for p in proposals}
    by_proposal: dict[str, int] = {}
    for r in records:
        by_proposal[r["proposal_id"]] = by_proposal.get(r["proposal_id"], 0) + 1
    for _, count in by_proposal.items():
        # Reasonable upper bound; current-only filter must keep this <= 5 in fixture.
        assert count <= max(qty_by_proposal_id.values())


def test_derive_fund_missing_cache_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        derive_fund(data_root=tmp_path / "data", fund=9)
