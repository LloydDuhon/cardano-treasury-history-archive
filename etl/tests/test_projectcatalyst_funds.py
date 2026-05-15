"""Tests for fetchers/projectcatalyst_funds.py."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import httpx
import pytest
import respx

from fetchers.projectcatalyst_funds import (
    BASE_URL,
    FUND_14_RESULT_TABS,
    FundFetcherConfig,
    FundPageClient,
    NextDataError,
    download_voting_results_csv,
    download_voting_results_pdf,
    extract_fund_summary,
    extract_next_data,
    extract_voting_results_sheet_url,
    fetch_fund_csv,
    fetch_fund_landing,
    fetch_voting_results_page,
    gdrive_direct_url,
    google_sheet_csv_url,
    google_sheet_csv_url_for_gid,
)

FIXTURE_HTML = Path(__file__).resolve().parent / "fixtures" / "funds-2.html.gz"


def _make_client(tmp_path: Path) -> FundPageClient:
    cfg = FundFetcherConfig(user_agent="test/1.0", rps=1000.0, data_root=tmp_path / "data")
    return FundPageClient(cfg)


def test_extract_next_data_from_fixture() -> None:
    html = gzip.decompress(FIXTURE_HTML.read_bytes())
    blob = extract_next_data(html)
    assert "props" in blob


def test_extract_fund_summary_from_fixture() -> None:
    html = gzip.decompress(FIXTURE_HTML.read_bytes())
    summary = extract_fund_summary(html)
    assert summary["fund"] == 2
    assert summary["fund_name"] == "Fund2"
    assert summary["funded_count"] == 11
    assert summary["voting_results_url"] == (
        "https://static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf"
    )


def test_extract_next_data_missing_script() -> None:
    with pytest.raises(NextDataError):
        extract_next_data(b"<html><body>no next data here</body></html>")


def test_extract_next_data_unparseable() -> None:
    with pytest.raises(NextDataError):
        extract_next_data(b'<script id="__NEXT_DATA__" type="application/json">{not json}</script>')


def test_gdrive_direct_url_translation() -> None:
    view = "https://drive.google.com/file/d/13h5JFtwqyylMUNMoRGXQZ-FJEM4bznOJ/view"
    direct = gdrive_direct_url(view)
    assert direct == (
        "https://drive.google.com/uc?export=download&id=" "13h5JFtwqyylMUNMoRGXQZ-FJEM4bznOJ"
    )


def test_gdrive_direct_url_non_gdrive_returns_none() -> None:
    assert gdrive_direct_url("https://static.iohk.io/x.pdf") is None
    assert gdrive_direct_url("") is None


def test_google_sheet_csv_url_translation() -> None:
    url = "https://docs.google.com/spreadsheets/d/abc_123/edit?gid=987#gid=987"
    assert google_sheet_csv_url(url) == (
        "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=987"
    )


def test_google_sheet_csv_url_uses_fragment_gid() -> None:
    url = "https://docs.google.com/spreadsheets/d/abc_123/edit#gid=654"
    assert google_sheet_csv_url(url) == (
        "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=654"
    )


def test_google_sheet_csv_url_defaults_to_gid_zero() -> None:
    url = "https://docs.google.com/spreadsheets/d/abc_123/edit"
    assert google_sheet_csv_url(url) == (
        "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=0"
    )


def test_google_sheet_csv_url_for_gid() -> None:
    url = "https://docs.google.com/spreadsheets/d/abc_123/edit"
    assert google_sheet_csv_url_for_gid(url, "42") == (
        "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=42"
    )


def test_extract_voting_results_sheet_url() -> None:
    html = b"""
    <html>
      <a href="https://docs.google.com/spreadsheets/d/abc_123/edit?gid=987">CSV file here</a>
    </html>
    """
    assert extract_voting_results_sheet_url(html) == (
        "https://docs.google.com/spreadsheets/d/abc_123/edit?gid=987"
    )


@respx.mock
def test_fetch_fund_landing_caches_atomically(tmp_path: Path) -> None:
    html_bytes = gzip.decompress(FIXTURE_HTML.read_bytes())
    respx.get(f"{BASE_URL}/funds/2").mock(return_value=httpx.Response(200, content=html_bytes))
    with _make_client(tmp_path) as client:
        summary = fetch_fund_landing(2, output_root=tmp_path / "data", client=client)
    assert summary["fund"] == 2
    assert summary["funded_count"] == 11

    cached_html = tmp_path / "data" / "_raw" / "projectcatalyst_io" / "funds-02.html.gz"
    cached_summary = tmp_path / "data" / "_raw" / "projectcatalyst_io" / "funds-02.summary.json"
    assert cached_html.exists()
    assert cached_summary.exists()
    parsed = json.loads(cached_summary.read_text())
    assert parsed["fund"] == 2
    assert "raw_fund_object" not in parsed  # stripped from on-disk summary


@respx.mock
def test_fetch_fund_landing_skips_when_cached(tmp_path: Path) -> None:
    html_bytes = gzip.decompress(FIXTURE_HTML.read_bytes())
    cached = tmp_path / "data" / "_raw" / "projectcatalyst_io" / "funds-02.html.gz"
    cached.parent.mkdir(parents=True)
    cached.write_bytes(gzip.compress(html_bytes))

    route = respx.get(f"{BASE_URL}/funds/2").mock(
        return_value=httpx.Response(200, content=b"SHOULD NOT BE CALLED")
    )
    with _make_client(tmp_path) as client:
        fetch_fund_landing(2, output_root=tmp_path / "data", client=client)
    assert route.call_count == 0


@respx.mock
def test_download_voting_results_pdf_static_iohk(tmp_path: Path) -> None:
    pdf_bytes = b"%PDF-1.7\n" + b"\x00" * 100
    url = "https://static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf"
    respx.get(url).mock(return_value=httpx.Response(200, content=pdf_bytes))
    with _make_client(tmp_path) as client:
        path = download_voting_results_pdf(2, url, output_root=tmp_path / "data", client=client)
    assert path.exists()
    assert path.read_bytes() == pdf_bytes


@respx.mock
def test_download_voting_results_pdf_follows_gdrive_confirm_href(tmp_path: Path) -> None:
    pdf_bytes = b"%PDF-1.7\n" + b"\x00" * 100
    url = "https://drive.google.com/file/d/abcdef/view"
    direct = "https://drive.google.com/uc?export=download&id=abcdef"
    confirm = "https://drive.google.com/uc?export=download&confirm=t&id=abcdef"
    respx.get(direct).mock(
        return_value=httpx.Response(
            200,
            content=(
                b'<html><a href="/uc?export=download&amp;confirm=t&amp;id=abcdef">'
                b"download</a></html>"
            ),
        )
    )
    respx.get(confirm).mock(return_value=httpx.Response(200, content=pdf_bytes))

    with _make_client(tmp_path) as client:
        path = download_voting_results_pdf(3, url, output_root=tmp_path / "data", client=client)

    assert path.exists()
    assert path.read_bytes() == pdf_bytes


@respx.mock
def test_download_voting_results_pdf_follows_gdrive_confirm_form(tmp_path: Path) -> None:
    pdf_bytes = b"%PDF-1.7\n" + b"\x00" * 100
    url = "https://drive.google.com/file/d/abcdef/view"
    direct = "https://drive.google.com/uc?export=download&id=abcdef"
    confirm = (
        "https://drive.usercontent.google.com/download"
        "?id=abcdef&export=download&confirm=t&uuid=123"
    )
    respx.get(direct).mock(
        return_value=httpx.Response(
            200,
            content=(
                b'<html><form action="https://drive.usercontent.google.com/download">'
                b'<input name="id" value="abcdef">'
                b'<input name="export" value="download">'
                b'<input name="confirm" value="t">'
                b'<input name="uuid" value="123">'
                b"</form></html>"
            ),
        )
    )
    respx.get(confirm).mock(return_value=httpx.Response(200, content=pdf_bytes))

    with _make_client(tmp_path) as client:
        path = download_voting_results_pdf(3, url, output_root=tmp_path / "data", client=client)

    assert path.exists()
    assert path.read_bytes() == pdf_bytes


@respx.mock
def test_download_voting_results_pdf_rejects_non_pdf(tmp_path: Path) -> None:
    """Google Drive hard-block pages without confirm controls are rejected."""
    url = "https://drive.google.com/file/d/abcdef/view"
    direct = "https://drive.google.com/uc?export=download&id=abcdef"
    respx.get(direct).mock(
        return_value=httpx.Response(200, content=b"<html>confirm download?</html>")
    )
    with _make_client(tmp_path) as client, pytest.raises(RuntimeError):
        download_voting_results_pdf(99, url, output_root=tmp_path / "data", client=client)


@respx.mock
def test_fetch_voting_results_page_discovers_sheet(tmp_path: Path) -> None:
    html = b"""
    <html>
      <a href="https://docs.google.com/spreadsheets/d/abc_123/edit#gid=654">CSV file here</a>
    </html>
    """
    respx.get(f"{BASE_URL}/funds/2/voting-results").mock(
        return_value=httpx.Response(200, content=html)
    )

    with _make_client(tmp_path) as client:
        summary = fetch_voting_results_page(2, output_root=tmp_path / "data", client=client)

    assert summary["sheet_url"] == "https://docs.google.com/spreadsheets/d/abc_123/edit#gid=654"
    assert summary["csv_url"] == (
        "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=654"
    )
    assert (tmp_path / "data" / "_raw" / "projectcatalyst_io" / "results-02.html.gz").exists()
    assert (tmp_path / "data" / "_raw" / "projectcatalyst_io" / "results-02.summary.json").exists()


@respx.mock
def test_download_voting_results_csv(tmp_path: Path) -> None:
    csv_bytes = b"Proposal,Yes,No\nExample,1,0\n"
    url = "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=654"
    respx.get(url).mock(return_value=httpx.Response(200, content=csv_bytes))

    with _make_client(tmp_path) as client:
        path = download_voting_results_csv(2, url, output_root=tmp_path / "data", client=client)

    assert path.exists()
    assert path.read_bytes() == csv_bytes


@respx.mock
def test_fetch_fund_csv_fetches_page_and_csv(tmp_path: Path) -> None:
    html = b"""
    <html>
      <a href="https://docs.google.com/spreadsheets/d/abc_123/edit?gid=654">CSV file here</a>
    </html>
    """
    csv_bytes = b"Proposal,Yes,No\nExample,1,0\n"
    csv_url = "https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid=654"
    respx.get(f"{BASE_URL}/funds/2/voting-results").mock(
        return_value=httpx.Response(200, content=html)
    )
    respx.get(csv_url).mock(return_value=httpx.Response(200, content=csv_bytes))

    with _make_client(tmp_path) as client:
        summary = fetch_fund_csv(2, output_root=tmp_path / "data", client=client)

    assert summary["csv_path"].endswith("data/_raw/iohk-results/fund-02.csv")
    assert (tmp_path / "data" / "_raw" / "iohk-results" / "fund-02.csv").exists()


@respx.mock
def test_fetch_fund_csv_fetches_fund14_multi_tab_csvs(tmp_path: Path) -> None:
    sheet_url = "https://docs.google.com/spreadsheets/d/abc_123"
    html = f"""
    <html>
      <a href="{sheet_url}">CSV file here</a>
    </html>
    """.encode()
    respx.get(f"{BASE_URL}/funds/14/voting-results").mock(
        return_value=httpx.Response(200, content=html)
    )
    for gid, _filename in FUND_14_RESULT_TABS:
        csv_url = f"https://docs.google.com/spreadsheets/d/abc_123/gviz/tq?tqx=out:csv&gid={gid}"
        respx.get(csv_url).mock(
            return_value=httpx.Response(200, content=b"Proposal,Status\nExample,FUNDED\n")
        )

    with _make_client(tmp_path) as client:
        summary = fetch_fund_csv(14, output_root=tmp_path / "data", client=client)

    assert len(summary["csv_paths"]) == len(FUND_14_RESULT_TABS)
    for _gid, filename in FUND_14_RESULT_TABS:
        assert (tmp_path / "data" / "_raw" / "iohk-results" / filename).exists()
