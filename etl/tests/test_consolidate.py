"""Tests for normalizers/consolidate.py."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from normalizers.consolidate import (
    MILESTONE_CSV_COLS,
    PROPOSAL_CSV_COLS,
    PROPOSER_CSV_COLS,
    _flatten_milestone,
    _flatten_proposal,
    _flatten_proposer,
    consolidate,
)


def _full_proposal(proposal_id: str, fund: int) -> dict[str, Any]:
    return {
        "proposal_id": proposal_id,
        "fund": fund,
        "title": "T",
        "slug": "t",
        "challenge": "c",
        "proposer_ids": ["p-lido-x", "p-lido-y"],
        "amount_requested": 100.0,
        "amount_received": 100.0,
        "currency": "ADA",
        "yes_votes": 50.0,
        "no_votes": 1.0,
        "abstain_votes": 0.0,
        "scores": {"alignment": 4.0, "feasibility": 3.5, "auditability": 4.5, "overall": 4.0},
        "ranking_total": 1,
        "funding_status": "approved",
        "project_status": "complete",
        "funded_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-06-01T00:00:00Z",
        "links": {
            "lidonation_url": "https://lido/p",
            "ideascale_url": None,
            "projectcatalyst_io_url": None,
            "milestones_url": None,
            "catalyst_voices_url": None,
            "proposer_website": None,
            "github_repo": None,
        },
        "milestone_count": 4,
        "is_opensource": True,
        "confidence": "high",
        "ai_summary": "summary",
        "sources": [],
    }


def test_flatten_proposal_extracts_expected_columns() -> None:
    row = _flatten_proposal(_full_proposal("f10-a", 10))
    assert set(PROPOSAL_CSV_COLS) >= set(row.keys())
    assert row["proposer_ids"] == "p-lido-x;p-lido-y"
    assert row["score_feasibility"] == 3.5
    assert row["lidonation_url"] == "https://lido/p"


def test_flatten_proposer_flattens_externals_and_rollups() -> None:
    rec = {
        "proposer_id": "p-x",
        "display_name": "X",
        "entity_type": "individual",
        "external_ids": {"lidonation_profile_uuid": "abc"},
        "rollups": {
            "total_proposals": 3,
            "total_funded": 2,
            "first_fund": 9,
            "last_fund": 12,
        },
        "socials": {"twitter": "@x"},
        "confidence": "medium",
        "duplicate_candidates": ["p-y"],
    }
    row = _flatten_proposer(rec)
    assert row["lidonation_profile_uuid"] == "abc"
    assert row["total_proposals"] == 3
    assert row["duplicate_candidates_count"] == 1
    assert row["twitter"] == "@x"
    assert set(PROPOSER_CSV_COLS) >= set(row.keys())


def test_flatten_milestone_counts_lists() -> None:
    rec = {
        "milestone_id": "f10-a-m01",
        "proposal_id": "f10-a",
        "milestone_number": 1,
        "evidence": [{"url": "x", "kind": "github_repo"}],
        "reviewer_signoffs": [{"decision": "accepted"}, {"decision": "accepted"}],
        "confidence": "high",
        "is_closeout": False,
    }
    row = _flatten_milestone(rec)
    assert row["evidence_count"] == 1
    assert row["signoff_count"] == 2
    assert set(MILESTONE_CSV_COLS) >= set(row.keys())


def test_consolidate_end_to_end_writes_csvs_and_jsons(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    # Two funds with one proposal each
    for fund_n in (10, 11):
        d = data_root / "funds" / f"fund-{fund_n:02d}"
        d.mkdir(parents=True)
        (d / "proposals.json").write_text(json.dumps([_full_proposal(f"f{fund_n:02d}-a", fund_n)]))
        (d / "proposers.json").write_text(
            json.dumps(
                [
                    {
                        "proposer_id": f"p-x-{fund_n}",
                        "display_name": "X",
                        "external_ids": {},
                        "rollups": {"total_proposals": 1},
                        "socials": {},
                        "confidence": "medium",
                        "duplicate_candidates": [],
                        "proposal_ids": [f"f{fund_n:02d}-a"],
                    }
                ]
            )
        )
    counters = consolidate(data_root=data_root)
    assert counters["proposals"] == 2
    assert counters["proposers"] == 2

    out = data_root / "consolidated"
    assert (out / "all_proposals.csv").exists()
    assert (out / "all_proposals.json").exists()
    assert (out / "all_proposers.csv").exists()
    assert (out / "schema.md").exists()

    # CSV round-trips
    with (out / "all_proposals.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert {r["fund"] for r in rows} == {"10", "11"}


def test_consolidate_empty_data_writes_empty_files(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    (data_root / "funds").mkdir(parents=True)
    counters = consolidate(data_root=data_root)
    assert counters == {"proposals": 0, "proposers": 0, "milestones": 0}
    out = data_root / "consolidated"
    # empty arrays + valid CSVs (header only)
    assert json.loads((out / "all_proposals.json").read_text()) == []
