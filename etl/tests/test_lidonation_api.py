"""Unit tests for fetchers/lidonation_api.py.

We test the polite client against respx-mocked HTTP, not the live API.
Live API behavior is documented in the module docstring and ADR notes.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from fetchers.lidonation_api import (
    API_BASE,
    FetcherConfig,
    LidonationClient,
    fetch_all_proposals,
    fetch_fund_titles,
)


def _make_client(tmp_path: Path) -> LidonationClient:
    """A client with high rps so tests don't wait for the throttle."""
    cfg = FetcherConfig(
        user_agent="test/1.0",
        rps=1000.0,
        data_root=tmp_path / "data",
    )
    return LidonationClient(cfg)


@respx.mock
def test_fetch_fund_titles_caches_atomically(tmp_path: Path, fund_titles_payload: bytes) -> None:
    respx.get(f"{API_BASE}/fund-titles").mock(
        return_value=httpx.Response(200, content=fund_titles_payload)
    )
    with _make_client(tmp_path) as client:
        target = fetch_fund_titles(output_root=tmp_path / "data", client=client)

    assert target.exists()
    assert target.read_bytes() == fund_titles_payload
    # Atomic-write tempfile is cleaned up
    assert list(target.parent.glob("*.tmp")) == []


@respx.mock
def test_fetch_fund_titles_skips_when_cached(tmp_path: Path, fund_titles_payload: bytes) -> None:
    target = tmp_path / "data" / "_raw" / "lidonation" / "fund-titles.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(fund_titles_payload)

    route = respx.get(f"{API_BASE}/fund-titles").mock(
        return_value=httpx.Response(200, content=b"SHOULD NOT BE CALLED")
    )
    with _make_client(tmp_path) as client:
        fetch_fund_titles(output_root=tmp_path / "data", client=client)
    assert route.call_count == 0
    assert target.read_bytes() == fund_titles_payload


@respx.mock
def test_smoke_sweep_first_two_pages(tmp_path: Path, proposals_page_payload: bytes) -> None:
    """A minimal end-to-end sweep that stops at max_pages=2."""
    # Force last_page to be > 2 so we know max_pages is doing the gating.
    page = json.loads(proposals_page_payload)
    page["last_page"] = 10
    page_bytes = json.dumps(page).encode()

    respx.get(f"{API_BASE}/proposals").mock(return_value=httpx.Response(200, content=page_bytes))

    with _make_client(tmp_path) as client:
        counters = fetch_all_proposals(
            output_root=tmp_path / "data",
            max_pages=2,
            client=client,
        )

    assert counters["fetched"] == 2
    assert counters["skipped"] == 0
    assert counters["total_pages_known"] == 10

    raw_dir = tmp_path / "data" / "_raw" / "lidonation"
    cached = sorted(raw_dir.glob("page-*.json.gz"))
    assert len(cached) == 2
    assert cached[0].name == "page-0001.json.gz"
    # Round-trip the gzip
    with gzip.open(cached[0], "rb") as fh:
        decoded: dict[str, Any] = json.loads(fh.read())
    assert decoded["last_page"] == 10
    assert "data" in decoded


@respx.mock
def test_sweep_is_idempotent_with_cache(tmp_path: Path, proposals_page_payload: bytes) -> None:
    page = json.loads(proposals_page_payload)
    page["last_page"] = 3
    page_bytes = json.dumps(page).encode()
    route = respx.get(f"{API_BASE}/proposals").mock(
        return_value=httpx.Response(200, content=page_bytes)
    )

    with _make_client(tmp_path) as client:
        first = fetch_all_proposals(output_root=tmp_path / "data", client=client)
    assert first["fetched"] == 3

    # Second run hits no HTTP (everything is cached).
    initial_calls = route.call_count
    with _make_client(tmp_path) as client:
        second = fetch_all_proposals(output_root=tmp_path / "data", client=client)
    assert second["fetched"] == 0
    assert second["skipped"] == 3
    assert route.call_count == initial_calls


@respx.mock
def test_retries_on_500_then_succeeds(tmp_path: Path, fund_titles_payload: bytes) -> None:
    """Polite retry policy must back off on 5xx and ultimately succeed."""
    route = respx.get(f"{API_BASE}/fund-titles").mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(500),
            httpx.Response(200, content=fund_titles_payload),
        ]
    )
    with _make_client(tmp_path) as client:
        target = fetch_fund_titles(output_root=tmp_path / "data", client=client)
    assert route.call_count == 3
    assert target.read_bytes() == fund_titles_payload


@respx.mock
def test_gives_up_after_repeated_5xx(tmp_path: Path) -> None:
    respx.get(f"{API_BASE}/fund-titles").mock(return_value=httpx.Response(503))
    with _make_client(tmp_path) as client, pytest.raises(RuntimeError):
        fetch_fund_titles(output_root=tmp_path / "data", client=client)


def test_lidonation_client_rejects_page_zero(tmp_path: Path) -> None:
    with _make_client(tmp_path) as client, pytest.raises(ValueError):
        client.fetch_proposals_page(0)
