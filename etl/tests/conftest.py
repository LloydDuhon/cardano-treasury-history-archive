"""Pytest fixtures shared across the etl test suite."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fund_titles_payload() -> bytes:
    """Raw bytes of /api/fund-titles, captured live on 2026-05-13."""
    return (FIXTURE_DIR / "fund-titles.json").read_bytes()


@pytest.fixture
def proposals_page_payload() -> bytes:
    """Raw bytes of /api/proposals?p=1, trimmed to 3 records for size."""
    return (FIXTURE_DIR / "proposals-page-1.json").read_bytes()


@pytest.fixture
def proposals_page_dict(proposals_page_payload: bytes) -> dict[str, object]:
    """Parsed dict form of the proposals page fixture."""
    return json.loads(proposals_page_payload)
