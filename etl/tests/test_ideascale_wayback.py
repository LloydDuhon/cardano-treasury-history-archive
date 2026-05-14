"""Tests for fetchers/ideascale_wayback.py."""

from __future__ import annotations

import gzip
from pathlib import Path

import httpx
import respx

from fetchers.ideascale_wayback import (
    CDX_BASE,
    WaybackClient,
    WaybackConfig,
    _pick_latest_per_url,
    fetch_cdx,
    fetch_fund_one_snapshots,
    fetch_snapshot,
    parse_cdx,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "wayback"


def _make_client(tmp_path: Path) -> WaybackClient:
    cfg = WaybackConfig(
        user_agent="test/1.0",
        rps=1000.0,
        data_root=tmp_path / "data",
    )
    return WaybackClient(cfg)


def _cdx_payload() -> bytes:
    return (FIXTURE_DIR / "cdx.json").read_bytes()


def test_parse_cdx_returns_named_dicts() -> None:
    rows = parse_cdx(_cdx_payload())
    assert len(rows) == 3
    first = rows[0]
    assert first["urlkey"] == "com,ideascale,cardano)/a/dtd/100001-1"
    assert first["timestamp"] == "20201015120000"
    assert first["statuscode"] == "200"


def test_parse_cdx_empty_returns_empty_list() -> None:
    assert parse_cdx(b"[]") == []


def test_pick_latest_per_url_keeps_newest() -> None:
    rows = [
        {"urlkey": "k1", "timestamp": "20201001120000", "original": "https://x/1"},
        {"urlkey": "k1", "timestamp": "20210101120000", "original": "https://x/1"},  # newer
        {"urlkey": "k2", "timestamp": "20201001120000", "original": "https://x/2"},
    ]
    out = sorted(_pick_latest_per_url(rows), key=lambda r: r["original"])
    assert len(out) == 2
    assert out[0]["timestamp"] == "20210101120000"


@respx.mock
def test_fetch_cdx_caches_atomically(tmp_path: Path) -> None:
    respx.get(CDX_BASE).mock(return_value=httpx.Response(200, content=_cdx_payload()))
    with _make_client(tmp_path) as client:
        rows = fetch_cdx(output_root=tmp_path / "data", client=client)
    assert len(rows) == 3
    cache = (
        tmp_path
        / "data"
        / "funds"
        / "fund-01"
        / "_provenance"
        / "ideascale_wayback"
        / "cdx.json.gz"
    )
    assert cache.exists()
    # cache round-trips
    payload = gzip.decompress(cache.read_bytes())
    re_parsed = parse_cdx(payload)
    assert len(re_parsed) == 3


@respx.mock
def test_fetch_cdx_skips_when_cached(tmp_path: Path) -> None:
    cache = (
        tmp_path
        / "data"
        / "funds"
        / "fund-01"
        / "_provenance"
        / "ideascale_wayback"
        / "cdx.json.gz"
    )
    cache.parent.mkdir(parents=True)
    cache.write_bytes(gzip.compress(_cdx_payload()))
    route = respx.get(CDX_BASE).mock(
        return_value=httpx.Response(500, content=b"should-not-be-called")
    )
    with _make_client(tmp_path) as client:
        rows = fetch_cdx(output_root=tmp_path / "data", client=client)
    assert route.call_count == 0
    assert len(rows) == 3


@respx.mock
def test_fetch_snapshot_caches_html(tmp_path: Path) -> None:
    html = (FIXTURE_DIR / "sample-proposal.html").read_bytes()
    cdx_row = {
        "urlkey": "com,ideascale,cardano)/a/dtd/100001-1",
        "timestamp": "20201015120000",
        "original": "https://cardano.ideascale.com/a/dtd/100001-1",
    }
    expected_wb_url = (
        "https://web.archive.org/web/20201015120000id_/"
        "https://cardano.ideascale.com/a/dtd/100001-1"
    )
    respx.get(expected_wb_url).mock(return_value=httpx.Response(200, content=html))
    with _make_client(tmp_path) as client:
        path = fetch_snapshot(cdx_row, output_root=tmp_path / "data", client=client)
    assert path is not None
    assert path.exists()
    decoded = gzip.decompress(path.read_bytes())
    assert b"Build a Cardano DEX" in decoded


@respx.mock
def test_fetch_snapshot_returns_none_on_persistent_5xx(tmp_path: Path) -> None:
    cdx_row = {
        "urlkey": "k1",
        "timestamp": "20201015120000",
        "original": "https://cardano.ideascale.com/a/dtd/100001-1",
    }
    respx.get(
        "https://web.archive.org/web/20201015120000id_/"
        "https://cardano.ideascale.com/a/dtd/100001-1"
    ).mock(return_value=httpx.Response(503))
    with _make_client(tmp_path) as client:
        path = fetch_snapshot(cdx_row, output_root=tmp_path / "data", client=client)
    assert path is None


@respx.mock
def test_fetch_fund_one_max_snapshots_caps_count(tmp_path: Path) -> None:
    respx.get(CDX_BASE).mock(return_value=httpx.Response(200, content=_cdx_payload()))
    html = (FIXTURE_DIR / "sample-bare-proposal.html").read_bytes()
    respx.get(url__regex=r"https://web\.archive\.org/web/.*").mock(
        return_value=httpx.Response(200, content=html)
    )
    with _make_client(tmp_path) as client:
        counters = fetch_fund_one_snapshots(
            output_root=tmp_path / "data", max_snapshots=2, client=client
        )
    assert counters["unique_urls"] == 3
    assert counters["snapshots_fetched"] == 2
