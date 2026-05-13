"""Tests for fetchers/milestones_scraper.py (Supabase REST flavour)."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import httpx
import pytest
import respx

from fetchers.milestones_scraper import (
    DEFAULT_SUPABASE_URL,
    FUND_TO_SUPABASE_ID,
    MilestonesConfig,
    MilestonesSupabaseClient,
    fetch_fund,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "milestones_supabase"


def _make_client(tmp_path: Path) -> MilestonesSupabaseClient:
    cfg = MilestonesConfig(
        supabase_url=DEFAULT_SUPABASE_URL,
        anon_key="test-anon-key",
        user_agent="test/1.0",
        rps=1000.0,
        data_root=tmp_path / "data",
    )
    return MilestonesSupabaseClient(cfg)


def _read_fixture(name: str) -> bytes:
    return (FIXTURE_DIR / name).read_bytes()


def test_fund_to_supabase_id_covers_f9_through_f14() -> None:
    assert set(FUND_TO_SUPABASE_ID) == {9, 10, 11, 12, 13, 14}
    assert FUND_TO_SUPABASE_ID[9] == 1


def test_fetch_fund_rejects_unsupported() -> None:
    with pytest.raises(ValueError):
        fetch_fund(2)


@respx.mock
def test_fetch_fund_caches_all_six_tables(tmp_path: Path) -> None:
    """End-to-end orchestrated fetch: 6 tables, gzipped cache, idempotent."""
    base = DEFAULT_SUPABASE_URL

    # Mock the six tables.
    respx.get(f"{base}/rest/v1/funds").mock(
        return_value=httpx.Response(200, content=_read_fixture("funds.json"))
    )
    respx.get(f"{base}/rest/v1/challenges").mock(
        return_value=httpx.Response(200, content=_read_fixture("challenges.json"))
    )
    respx.get(f"{base}/rest/v1/proposals").mock(
        return_value=httpx.Response(200, content=_read_fixture("proposals.json"))
    )
    respx.get(f"{base}/rest/v1/soms").mock(
        return_value=httpx.Response(200, content=_read_fixture("soms.json"))
    )
    respx.get(f"{base}/rest/v1/poas").mock(
        return_value=httpx.Response(200, content=_read_fixture("poas.json"))
    )
    respx.get(f"{base}/rest/v1/signoffs").mock(
        return_value=httpx.Response(200, content=_read_fixture("signoffs.json"))
    )

    with _make_client(tmp_path) as client:
        counters = fetch_fund(9, output_root=tmp_path / "data", client=client)

    prov = tmp_path / "data" / "funds" / "fund-09" / "_provenance" / "milestones_supabase"
    for table in ("funds", "challenges", "proposals", "soms", "poas", "signoffs"):
        path = prov / f"{table}.json.gz"
        assert path.exists(), f"{table}.json.gz missing"
        rows = json.loads(gzip.decompress(path.read_bytes()))
        assert isinstance(rows, list)
        assert counters[table] == len(rows)


@respx.mock
def test_fetch_fund_idempotent_skips_when_cached(tmp_path: Path) -> None:
    base = DEFAULT_SUPABASE_URL
    prov = tmp_path / "data" / "funds" / "fund-09" / "_provenance" / "milestones_supabase"
    prov.mkdir(parents=True)
    for table in ("funds", "challenges", "proposals", "soms", "poas", "signoffs"):
        gz_path = prov / f"{table}.json.gz"
        gz_path.write_bytes(gzip.compress(_read_fixture(f"{table}.json")))

    # Any call to upstream should fail the test.
    routes = [
        respx.get(f"{base}/rest/v1/{tbl}").mock(
            return_value=httpx.Response(500, content=b"should not be called")
        )
        for tbl in ("funds", "challenges", "proposals", "soms", "poas", "signoffs")
    ]

    with _make_client(tmp_path) as client:
        counters = fetch_fund(9, output_root=tmp_path / "data", client=client)
    assert all(r.call_count == 0 for r in routes)
    assert counters["proposals"] == 2


def test_default_anon_key_is_public_supabase_anon_role() -> None:
    """Sanity check: the bundled anon key claims the 'anon' role.

    The key is the one exposed in milestones.projectcatalyst.io/env.js -
    intended for client-side use. Decoding the JWT payload should show
    role=anon. We don't verify the signature.
    """
    import base64

    from fetchers.milestones_scraper import DEFAULT_SUPABASE_ANON_KEY

    payload_b64 = DEFAULT_SUPABASE_ANON_KEY.split(".")[1]
    # Add padding for base64 decode
    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded))
    assert payload.get("role") == "anon"
