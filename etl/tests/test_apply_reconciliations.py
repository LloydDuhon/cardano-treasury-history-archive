"""Tests for normalizers/apply_reconciliations.py."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from normalizers.apply_reconciliations import _is_already_applied, apply_fund

REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSAL_SCHEMA = REPO_ROOT / "schemas" / "proposal.schema.json"


@pytest.fixture(scope="module")
def proposal_validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(PROPOSAL_SCHEMA.read_text()))


def _make_proposal(proposal_id: str, funding_status: str = "approved") -> dict[str, Any]:
    return {
        "proposal_id": proposal_id,
        "external_ids": {"lidonation_uuid": "abc-123"},
        "fund": 2,
        "title": "Test proposal",
        "slug": "test-proposal",
        "challenge": "Cat",
        "campaign_id": "x",
        "proposer_ids": ["p-lido-abc"],
        "amount_requested": 100.0,
        "amount_received": 100.0,
        "currency": "ADA",
        "yes_votes": 1.0,
        "no_votes": 0.0,
        "abstain_votes": 0.0,
        "scores": {
            "alignment": None,
            "feasibility": None,
            "auditability": None,
            "overall": None,
        },
        "ranking_total": None,
        "funding_status": funding_status,
        "project_status": "funded",
        "funded_at": None,
        "completed_at": None,
        "links": {
            "lidonation_url": None,
            "ideascale_url": None,
            "projectcatalyst_io_url": None,
            "milestones_url": None,
            "catalyst_voices_url": None,
            "proposer_website": None,
            "github_repo": None,
        },
        "summary": None,
        "problem": None,
        "solution": None,
        "definition_of_success": None,
        "ai_summary": None,
        "milestone_count": None,
        "tags": [],
        "is_opensource": None,
        "sources": [
            {
                "source": "lidonation_api",
                "url": "https://x.test/api",
                "fetched_at": "2026-05-13T00:00:00Z",
                "provenance_path": None,
                "fields_provided": ["funding_status"],
            }
        ],
        "confidence": "medium",
        "field_confidence": None,
        "notes": None,
    }


def _stage(
    tmp_path: Path,
    fund: int,
    proposals: list[dict[str, Any]],
    disagreements: list[dict[str, Any]],
) -> Path:
    fund_dir = tmp_path / "data" / "funds" / f"fund-{fund:02d}"
    fund_dir.mkdir(parents=True)
    (fund_dir / "proposals.json").write_text(json.dumps(proposals))
    (fund_dir / "_reconciliation.json").write_text(
        json.dumps(
            {
                "fund": fund,
                "reconciled_at": "2026-05-13T00:00:00Z",
                "sources": {
                    "primary": {"label": "lidonation_api", "path": "x"},
                    "secondary": {"label": "iohk_voting_results_pdf", "path": "y"},
                },
                "agreement_count": 0,
                "disagreements": disagreements,
                "unmatched_in_primary": [],
                "unmatched_in_secondary": [],
            }
        )
    )
    return tmp_path / "data"


def test_apply_flips_funding_status_when_secondary_wins(
    tmp_path: Path, proposal_validator: Draft202012Validator
) -> None:
    data_root = _stage(
        tmp_path,
        2,
        [_make_proposal("f02-x", funding_status="approved")],
        [
            {
                "primary_proposal_id": "f02-x",
                "matched_secondary_title": "Test proposal",
                "primary_funding_status": "approved",
                "secondary_funded_flag": False,
                "verdict": "secondary_wins",
                "note": None,
            }
        ],
    )
    counters = apply_fund(data_root=data_root, fund=2)
    assert counters["applied"] == 1

    updated = json.loads((data_root / "funds" / "fund-02" / "proposals.json").read_text())
    assert len(updated) == 1
    p = updated[0]
    assert p["funding_status"] == "not_approved"
    assert "RECONCILIATION" in (p["notes"] or "")
    assert "approved" in (p["notes"] or "")
    errors = list(proposal_validator.iter_errors(p))
    assert not errors, [(list(e.absolute_path), e.message) for e in errors]


def test_apply_marks_leftover_when_sponsored_by_leftovers_wins(tmp_path: Path) -> None:
    data_root = _stage(
        tmp_path,
        14,
        [_make_proposal("f14-x", funding_status="over_budget")],
        [
            {
                "primary_proposal_id": "f14-x",
                "matched_secondary_title": "Test proposal",
                "primary_funding_status": "over_budget",
                "secondary_funded_flag": True,
                "secondary_status": "FUNDED",
                "secondary_source_file": "fund-14-sponsored-by-leftovers.csv",
                "verdict": "secondary_wins",
                "note": None,
            }
        ],
    )

    counters = apply_fund(data_root=data_root, fund=14)

    assert counters["applied"] == 1
    updated = json.loads((data_root / "funds" / "fund-14" / "proposals.json").read_text())
    assert updated[0]["funding_status"] == "leftover"


def test_apply_is_idempotent(tmp_path: Path) -> None:
    data_root = _stage(
        tmp_path,
        3,
        [_make_proposal("f03-y", funding_status="approved")],
        [
            {
                "primary_proposal_id": "f03-y",
                "matched_secondary_title": "Test proposal",
                "primary_funding_status": "approved",
                "secondary_funded_flag": False,
                "verdict": "secondary_wins",
                "note": None,
            }
        ],
    )
    first = apply_fund(data_root=data_root, fund=3)
    second = apply_fund(data_root=data_root, fund=3)
    assert first["applied"] == 1
    assert second["applied"] == 0
    assert second["skipped_already_applied"] == 1


def test_apply_skips_non_secondary_wins_verdict(tmp_path: Path) -> None:
    data_root = _stage(
        tmp_path,
        4,
        [_make_proposal("f04-z")],
        [
            {
                "primary_proposal_id": "f04-z",
                "matched_secondary_title": "T",
                "primary_funding_status": "approved",
                "secondary_funded_flag": False,
                "verdict": "needs_human_review",
                "note": None,
            }
        ],
    )
    counters = apply_fund(data_root=data_root, fund=4)
    assert counters["applied"] == 0
    assert counters["skipped_non_verdict"] == 1


def test_apply_dry_run_does_not_write(tmp_path: Path) -> None:
    data_root = _stage(
        tmp_path,
        5,
        [_make_proposal("f05-a", funding_status="approved")],
        [
            {
                "primary_proposal_id": "f05-a",
                "matched_secondary_title": "T",
                "primary_funding_status": "approved",
                "secondary_funded_flag": False,
                "verdict": "secondary_wins",
                "note": None,
            }
        ],
    )
    counters = apply_fund(data_root=data_root, fund=5, dry_run=True)
    assert counters["applied"] == 1
    p = json.loads((data_root / "funds" / "fund-05" / "proposals.json").read_text())[0]
    # Funding status unchanged on disk because dry_run=True.
    assert p["funding_status"] == "approved"


def test_is_already_applied_recognizes_marker() -> None:
    p = _make_proposal("f02-q")
    assert not _is_already_applied(p)
    p["sources"].append(
        {
            "source": "iohk_voting_results_pdf",
            "url": None,
            "fetched_at": "2026-05-14T00:00:00Z",
            "provenance_path": None,
            "fields_provided": ["funding_status"],
        }
    )
    assert _is_already_applied(p)
