"""projectcatalyst.io fund pages and IOG voting-results PDF fetcher.

Source:        https://projectcatalyst.io/funds/{N}
Coverage:      Funds 2-13 PDFs are the canonical IOG winner artifact;
               F10-F15 also have inline voting-results pages.

Probed live on 2026-05-13:
  - HTML pages embed a <script id="__NEXT_DATA__"> JSON blob with the
    authoritative `votingResultsUrl`, `numProposalsFunded`, `fundName`,
    `challenges[]`, and other counts at `props.pageProps.data.fund`.
  - F2 PDF lives at static.iohk.io; F3-F9 at Google Drive
    (/file/d/{id}/view); F10+ inline at projectcatalyst.io.

Outputs:
  data/_raw/projectcatalyst_io/funds-NN.html.gz   (raw HTML)
  data/_raw/projectcatalyst_io/funds-NN.json      (extracted next.js summary)
  data/_raw/iohk-pdfs/fund-NN.pdf                 (downloaded artifact)

CLI:
    python -m fetchers.projectcatalyst_funds --fund 2
    python -m fetchers.projectcatalyst_funds                  # all funds
    python -m fetchers.projectcatalyst_funds --metadata-only  # skip PDFs
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Reuse the JSON log formatter from the Lidonation fetcher.
from fetchers.lidonation_api import JsonLogFormatter

BASE_URL = "https://projectcatalyst.io"
DEFAULT_USER_AGENT = (
    "catalyst-history-archive/0.1 " "(+https://github.com/lloydduhon/catalyst-history-archive)"
)
DEFAULT_RPS = 2.0
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

# Funds for which a voting-results artifact is expected.
KNOWN_FUNDS_WITH_RESULTS: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)

# Google Drive file URL pattern: https://drive.google.com/file/d/<ID>/view
_GDRIVE_FILE_RE = re.compile(r"drive\.google\.com/file/d/([A-Za-z0-9_\-]+)")


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("projectcatalyst_funds")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


log = _configure_logging()


@dataclass(frozen=True)
class FundFetcherConfig:
    """Tunables for a fund-page fetch run."""

    user_agent: str = DEFAULT_USER_AGENT
    rps: float = DEFAULT_RPS
    data_root: Path = DEFAULT_DATA_ROOT

    @classmethod
    def from_env(cls) -> FundFetcherConfig:
        return cls(
            user_agent=os.environ.get("HTTP_USER_AGENT", DEFAULT_USER_AGENT),
            rps=float(os.environ.get("PROJECTCATALYST_IO_RPS", DEFAULT_RPS)),
            data_root=Path(os.environ.get("PROVENANCE_ROOT", str(DEFAULT_DATA_ROOT))),
        )


class _Throttle:
    """At most `rps` calls per second."""

    def __init__(self, rps: float) -> None:
        self._interval = 1.0 / max(rps, 0.01)
        self._next: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        if now < self._next:
            time.sleep(self._next - now)
        self._next = time.monotonic() + self._interval


def _retry_log(rs: RetryCallState) -> None:
    log.warning(
        "retry",
        extra={
            "attempt": rs.attempt_number,
            "wait_s": getattr(rs.next_action, "sleep", None),
            "exc": str(rs.outcome.exception()) if rs.outcome else None,
        },
    )


# --------------------------------------------------------------------------- #
# HTML extraction
# --------------------------------------------------------------------------- #


_NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL)


class NextDataError(ValueError):
    """Raised when the __NEXT_DATA__ blob is missing or unparseable."""


def extract_next_data(html: bytes | str) -> dict[str, Any]:
    """Pull the JSON blob from `<script id="__NEXT_DATA__">`."""
    text = html.decode("utf-8") if isinstance(html, bytes) else html
    m = _NEXT_DATA_RE.search(text)
    if not m:
        raise NextDataError("__NEXT_DATA__ script tag not found")
    try:
        parsed: dict[str, Any] = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        raise NextDataError(f"could not parse __NEXT_DATA__ JSON: {exc}") from exc
    return parsed


def extract_fund_summary(html: bytes | str) -> dict[str, Any]:
    """Distill the per-fund summary the Phase 2 reconciler needs.

    Returns a dict with `fund`, `fund_name`, `proposals_count`,
    `funded_count`, `voting_results_url`, `currency`, plus the raw
    `fund_object` for further inspection.
    """
    blob = extract_next_data(html)
    fund_obj = blob.get("props", {}).get("pageProps", {}).get("data", {}).get("fund")
    if not isinstance(fund_obj, dict):
        raise NextDataError("expected props.pageProps.data.fund to be a dict")

    fund_name = fund_obj.get("fundName") or ""
    fund_id = fund_obj.get("fundId")
    try:
        fund_number = int(fund_id) if fund_id is not None else None
    except (TypeError, ValueError):
        fund_number = None
    if fund_number is None:
        m = re.search(r"(\d+)", fund_name)
        fund_number = int(m.group(1)) if m else None

    challenges = fund_obj.get("challenges") or []
    proposals_count = sum(ch.get("totalProjects") or 0 for ch in challenges if isinstance(ch, dict))
    funded_count = fund_obj.get("numProposalsFunded")

    return {
        "fund": fund_number,
        "fund_name": fund_name,
        "proposals_count": proposals_count,
        "funded_count": funded_count,
        "voting_results_url": fund_obj.get("votingResultsUrl") or None,
        "currency": fund_obj.get("currency"),
        "raw_fund_object": fund_obj,
    }


# --------------------------------------------------------------------------- #
# Google Drive URL handling
# --------------------------------------------------------------------------- #


def gdrive_direct_url(view_url: str) -> str | None:
    """Convert a /file/d/{id}/view URL to a direct-download URL.

    Returns None if the URL is not a Google Drive file URL.
    """
    m = _GDRIVE_FILE_RE.search(view_url)
    if not m:
        return None
    file_id = m.group(1)
    return f"https://drive.google.com/uc?export=download&id={file_id}"


# --------------------------------------------------------------------------- #
# Cache layout
# --------------------------------------------------------------------------- #


def _funds_html_path(data_root: Path, fund: int) -> Path:
    return data_root / "_raw" / "projectcatalyst_io" / f"funds-{fund:02d}.html.gz"


def _funds_summary_path(data_root: Path, fund: int) -> Path:
    return data_root / "_raw" / "projectcatalyst_io" / f"funds-{fund:02d}.summary.json"


def _pdf_path(data_root: Path, fund: int) -> Path:
    return data_root / "_raw" / "iohk-pdfs" / f"fund-{fund:02d}.pdf"


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, payload: bytes, *, gzip_compress: bool = False) -> None:
    _ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = gzip.compress(payload, compresslevel=6) if gzip_compress else payload
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


# --------------------------------------------------------------------------- #
# HTTP client
# --------------------------------------------------------------------------- #


class FundPageClient:
    """Polite HTTP client for projectcatalyst.io HTML and IOG/Drive PDF downloads."""

    def __init__(self, config: FundFetcherConfig) -> None:
        self._cfg = config
        self._throttle = _Throttle(config.rps)
        self._client = httpx.Client(
            headers={
                "User-Agent": config.user_agent,
                "Accept": "*/*",
            },
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

    def __enter__(self) -> FundPageClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, RuntimeError)),
        wait=wait_exponential(multiplier=1.5, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
        before_sleep=_retry_log,
    )
    def get_bytes(self, url: str) -> bytes:
        """GET a URL, returning raw response bytes. Retries on transient errors."""
        self._throttle.wait()
        resp = self._client.get(url)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {url}")
        resp.raise_for_status()
        return resp.content


# --------------------------------------------------------------------------- #
# Public fetch routines
# --------------------------------------------------------------------------- #


def fetch_fund_landing(
    fund: int,
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: FundPageClient | None = None,
) -> dict[str, Any]:
    """Fetch /funds/{N} HTML, cache it gzipped, extract and write summary JSON.

    Args:
        fund: Fund number.
        output_root: Path to data/. Defaults to repo's data/.
        force: Re-fetch even when cached.
        client: Inject a client for tests.

    Returns:
        The fund summary dict (also written to disk).
    """
    cfg = FundFetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    html_path = _funds_html_path(root, fund)
    summary_path = _funds_summary_path(root, fund)

    owns = client is None
    cli = client or FundPageClient(cfg)
    try:
        if html_path.exists() and not force:
            log.info("html.cached", extra={"fund": fund, "path": str(html_path)})
            with gzip.open(html_path, "rb") as fh:
                html_bytes = fh.read()
        else:
            url = f"{BASE_URL}/funds/{fund}"
            html_bytes = cli.get_bytes(url)
            _atomic_write(html_path, html_bytes, gzip_compress=True)
            log.info(
                "html.fetched",
                extra={"fund": fund, "url": url, "bytes": len(html_bytes)},
            )
    finally:
        if owns:
            cli.close()

    summary = extract_fund_summary(html_bytes)
    _ensure_dir(summary_path.parent)
    with summary_path.open("w", encoding="utf-8") as fh:
        # Strip the raw_fund_object from the on-disk summary to keep it tidy;
        # full HTML is in the .html.gz neighbor for replay.
        compact = {k: v for k, v in summary.items() if k != "raw_fund_object"}
        json.dump(compact, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    log.info(
        "summary.written",
        extra={"fund": fund, "path": str(summary_path), "summary": compact},
    )
    return summary


def download_voting_results_pdf(
    fund: int,
    voting_results_url: str,
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: FundPageClient | None = None,
) -> Path:
    """Download the canonical voting-results artifact for one fund.

    Handles three URL patterns:
      - static.iohk.io direct PDF (F2)
      - drive.google.com /file/d/{id}/view (F3-F9)
      - projectcatalyst.io inline PDF (F10+)
    """
    cfg = FundFetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    pdf_path = _pdf_path(root, fund)
    if pdf_path.exists() and not force:
        log.info("pdf.cached", extra={"fund": fund, "path": str(pdf_path)})
        return pdf_path

    url = voting_results_url
    gd = gdrive_direct_url(url)
    if gd:
        url = gd
        log.info("pdf.gdrive.translated", extra={"fund": fund, "url": url})

    owns = client is None
    cli = client or FundPageClient(cfg)
    try:
        payload = cli.get_bytes(url)
        if not payload.startswith(b"%PDF"):
            # Google Drive sometimes returns an HTML confirm page for >100MB files.
            preview = payload[:200].decode("utf-8", errors="replace")
            raise RuntimeError(f"fund {fund}: response is not a PDF (first 200 bytes: {preview!r})")
        _atomic_write(pdf_path, payload)
        log.info(
            "pdf.fetched",
            extra={"fund": fund, "url": url, "bytes": len(payload)},
        )
    finally:
        if owns:
            cli.close()
    return pdf_path


def fetch_fund(
    fund: int,
    *,
    output_root: Path | None = None,
    metadata_only: bool = False,
    force: bool = False,
    client: FundPageClient | None = None,
) -> dict[str, Any]:
    """Convenience: landing + PDF in one call.

    Returns the summary dict (with an added `pdf_path` entry if a PDF was
    downloaded).
    """
    summary = fetch_fund_landing(fund, output_root=output_root, force=force, client=client)
    if metadata_only:
        return summary
    voting_url = summary.get("voting_results_url")
    if not voting_url:
        log.info("pdf.skipped.no_url", extra={"fund": fund})
        return summary
    pdf_path = download_voting_results_pdf(
        fund, voting_url, output_root=output_root, force=force, client=client
    )
    summary["pdf_path"] = str(pdf_path)
    return summary


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None, help="Override data/ directory.")
    parser.add_argument(
        "--fund",
        type=int,
        action="append",
        default=None,
        help="Fund number(s) to fetch. May be passed multiple times. Default: F2-F13.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Fetch only the HTML and summary; skip PDF downloads.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch even if a cached copy exists.",
    )
    args = parser.parse_args(argv)

    funds = tuple(args.fund) if args.fund else KNOWN_FUNDS_WITH_RESULTS
    cfg = FundFetcherConfig.from_env()
    try:
        with FundPageClient(cfg) as client:
            for n in funds:
                fetch_fund(
                    n,
                    output_root=args.data_root,
                    metadata_only=args.metadata_only,
                    force=args.force,
                    client=client,
                )
    except (httpx.HTTPError, RuntimeError, OSError) as exc:
        log.error("fatal", extra={"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "BASE_URL",
    "FundFetcherConfig",
    "FundPageClient",
    "KNOWN_FUNDS_WITH_RESULTS",
    "NextDataError",
    "download_voting_results_pdf",
    "extract_fund_summary",
    "extract_next_data",
    "fetch_fund",
    "fetch_fund_landing",
    "gdrive_direct_url",
    "main",
]
