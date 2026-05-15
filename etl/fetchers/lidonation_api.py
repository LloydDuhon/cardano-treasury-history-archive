"""Lidonation Catalyst Explorer API fetcher.

Source:        https://www.catalystexplorer.com/api/v1/*
Coverage:      Funds 2-15 (~11,528 proposals at survey time)
Auth:          None required
Rate limit:    Unpublished; we self-throttle via LIDONATION_RPS in .env

Probed live on 2026-05-14 after Darlington pointed us at the published API
docs. Findings:
  - The documented API is /api/v1/*, not the legacy /api/* endpoint.
  - /api/v1/proposals supports page, per_page (max 60), include, sort, and
    filter[fund_id]. We still do a flat sweep and split by fund client-side
    because one central cache is easier to replay and audit.
  - Total: 11,528 proposals across 193 pages at per_page=60 (snapshot
    2026-05-14).
  - Each proposal record carries `fund.id` (UUID) and `fund.title` ("Fund 10").
  - Include `campaign,fund,team` to preserve proposer/team data.

This fetcher writes raw page captures to a CENTRAL cache because pages mix
funds:
    data/_raw/lidonation/fund-titles.json
    data/_raw/lidonation/page-NNNN.json.gz

The normalizer (etl/normalizers/unify_proposals.py) demultiplexes those into
per-fund data/funds/fund-XX/proposals.json files.

CLI:
    python -m fetchers.lidonation_api              # full sweep, ~6 min
    python -m fetchers.lidonation_api --max-pages 10   # smoke test
    python -m fetchers.lidonation_api --start-page 200 # resume
    python -m fetchers.lidonation_api --force      # re-fetch cached pages

Idempotent: cached pages are skipped unless --force.
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
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

API_BASE = "https://www.catalystexplorer.com/api"
DEFAULT_USER_AGENT = (
    "catalyst-history-archive/0.1 " "(+https://github.com/lloydduhon/catalyst-history-archive)"
)
DEFAULT_RPS = 1.5
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"


# --------------------------------------------------------------------------- #
# Logging - structured JSON to stdout per DEVELOPMENT_STANDARDS section 3.1
# --------------------------------------------------------------------------- #


class JsonLogFormatter(logging.Formatter):
    """Minimal JSON formatter so logs are machine-parseable from line 1."""

    _STD_ATTRS = frozenset(
        {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for k, v in record.__dict__.items():
            if k in payload or k.startswith("_") or k in self._STD_ATTRS:
                continue
            payload[k] = v
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("lidonation_api")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


log = _configure_logging()


# --------------------------------------------------------------------------- #
# HTTP client with polite rate limit + retry
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FetcherConfig:
    """Tunables for one fetcher run. Loaded from .env via env vars."""

    user_agent: str = DEFAULT_USER_AGENT
    contact_email: str = ""
    rps: float = DEFAULT_RPS
    data_root: Path = DEFAULT_DATA_ROOT
    per_page: int = 60

    @classmethod
    def from_env(cls) -> FetcherConfig:
        return cls(
            user_agent=os.environ.get("HTTP_USER_AGENT", DEFAULT_USER_AGENT),
            contact_email=os.environ.get("HTTP_CONTACT_EMAIL", ""),
            rps=float(os.environ.get("LIDONATION_RPS", DEFAULT_RPS)),
            data_root=Path(os.environ.get("PROVENANCE_ROOT", str(DEFAULT_DATA_ROOT))),
            per_page=int(os.environ.get("LIDONATION_PER_PAGE", "60")),
        )


class _Throttle:
    """Simple monotonic-clock token-bucket: at most `rps` calls per second."""

    def __init__(self, rps: float) -> None:
        self._interval = 1.0 / max(rps, 0.01)
        self._next_allowed: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        if now < self._next_allowed:
            time.sleep(self._next_allowed - now)
        self._next_allowed = time.monotonic() + self._interval


def _retry_log(retry_state: RetryCallState) -> None:
    log.warning(
        "retry",
        extra={
            "attempt": retry_state.attempt_number,
            "wait_s": getattr(retry_state.next_action, "sleep", None),
            "exc": str(retry_state.outcome.exception()) if retry_state.outcome else None,
        },
    )


class LidonationClient:
    """Polite HTTP client for the Lidonation Catalyst Explorer API.

    Self-throttled, exponential-backoff on 429/5xx/network errors, identifiable
    User-Agent. Does not handle pagination - callers iterate page numbers.
    """

    def __init__(self, config: FetcherConfig) -> None:
        self._cfg = config
        self._throttle = _Throttle(config.rps)
        headers = {
            "User-Agent": config.user_agent,
            "Accept": "application/json",
        }
        if config.contact_email:
            headers["From"] = config.contact_email
        self._client = httpx.Client(
            base_url=API_BASE,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

    def __enter__(self) -> LidonationClient:
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
    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> bytes:
        self._throttle.wait()
        resp = self._client.get(path, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {path}")
        resp.raise_for_status()
        return resp.content

    def fetch_fund_titles(self) -> bytes:
        """Return raw JSON bytes from GET /api/v1/funds."""
        return self._get("/v1/funds", params={"per_page": 60})

    def fetch_proposals_page(self, page: int) -> bytes:
        """Return raw JSON bytes from GET /api/v1/proposals?page={page}."""
        if page < 1:
            raise ValueError(f"page must be >= 1, got {page}")
        return self._get(
            "/v1/proposals",
            params={
                "page": page,
                "per_page": min(max(self._cfg.per_page, 1), 60),
                "include": "campaign,fund,team",
            },
        )


# --------------------------------------------------------------------------- #
# Cache layout helpers
# --------------------------------------------------------------------------- #


def _raw_dir(data_root: Path) -> Path:
    return data_root / "_raw" / "lidonation"


def _fund_titles_path(data_root: Path) -> Path:
    return _raw_dir(data_root) / "fund-titles.json"


def _page_path(data_root: Path, page: int) -> Path:
    return _raw_dir(data_root) / f"page-{page:04d}.json.gz"


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, payload: bytes, *, gzip_compress: bool) -> None:
    """Write payload atomically (write to .tmp, fsync, rename)."""
    _ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = gzip.compress(payload, compresslevel=6) if gzip_compress else payload
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


# --------------------------------------------------------------------------- #
# Public fetch routines
# --------------------------------------------------------------------------- #


def fetch_fund_titles(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: LidonationClient | None = None,
) -> Path:
    """Fetch /api/fund-titles and cache it as data/_raw/lidonation/fund-titles.json.

    Args:
        output_root: Where data/ lives (defaults to repo's data/).
        force: Re-fetch even if a cached copy exists.
        client: Inject a client for testing; otherwise one is created.

    Returns:
        Path to the cached file.
    """
    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    target = _fund_titles_path(root)
    if target.exists() and not force:
        log.info("fund_titles.cached", extra={"path": str(target)})
        return target
    owns_client = client is None
    cli = client or LidonationClient(cfg)
    try:
        payload = cli.fetch_fund_titles()
    finally:
        if owns_client:
            cli.close()
    _atomic_write(target, payload, gzip_compress=False)
    log.info("fund_titles.fetched", extra={"path": str(target), "bytes": len(payload)})
    return target


def fetch_all_proposals(
    *,
    output_root: Path | None = None,
    max_pages: int | None = None,
    start_page: int = 1,
    force: bool = False,
    client: LidonationClient | None = None,
) -> dict[str, int]:
    """Walk /api/proposals?p=1..last_page, gzipping each page response.

    Args:
        output_root: Where data/ lives (defaults to repo's data/).
        max_pages: Stop after this many pages (counted from start_page).
                   None = walk to last_page reported by the server.
        start_page: First page to fetch (1-based).
        force: Re-fetch even if a cached copy exists.
        client: Inject a client for testing.

    Returns:
        Counters dict with keys: fetched, skipped, total_pages_known.
    """
    if start_page < 1:
        raise ValueError(f"start_page must be >= 1, got {start_page}")
    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    _ensure_dir(_raw_dir(root))

    owns_client = client is None
    cli = client or LidonationClient(cfg)
    counters = {"fetched": 0, "skipped": 0, "total_pages_known": 0}
    try:
        first_page = start_page
        page_path = _page_path(root, first_page)
        if page_path.exists() and not force:
            log.info("page.cached", extra={"page": first_page, "path": str(page_path)})
            with gzip.open(page_path, "rb") as fh:
                first_payload = fh.read()
            counters["skipped"] += 1
        else:
            first_payload = cli.fetch_proposals_page(first_page)
            _atomic_write(page_path, first_payload, gzip_compress=True)
            counters["fetched"] += 1
            log.info(
                "page.fetched",
                extra={"page": first_page, "bytes": len(first_payload)},
            )
        first_doc = json.loads(first_payload)
        meta = first_doc.get("meta") if isinstance(first_doc.get("meta"), dict) else {}
        last_page = int(meta.get("last_page") or first_doc.get("last_page", first_page))
        counters["total_pages_known"] = last_page

        end_page = last_page if max_pages is None else min(last_page, start_page + max_pages - 1)

        for page in range(start_page + 1, end_page + 1):
            page_path = _page_path(root, page)
            if page_path.exists() and not force:
                log.info("page.cached", extra={"page": page, "path": str(page_path)})
                counters["skipped"] += 1
                continue
            payload = cli.fetch_proposals_page(page)
            _atomic_write(page_path, payload, gzip_compress=True)
            counters["fetched"] += 1
            log.info(
                "page.fetched",
                extra={"page": page, "of": end_page, "bytes": len(payload)},
            )
    finally:
        if owns_client:
            cli.close()

    log.info("sweep.complete", extra=counters)
    return counters


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``python -m fetchers.lidonation_api ...``"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Override repo's data/ directory (defaults to ../data relative to etl/).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Stop after this many pages (counted from --start-page). Default: all.",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="First page to fetch (1-based). Default: 1.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch and overwrite cached pages.",
    )
    parser.add_argument(
        "--titles-only",
        action="store_true",
        help="Fetch only /api/fund-titles, skip the proposals sweep.",
    )
    args = parser.parse_args(argv)

    try:
        fetch_fund_titles(output_root=args.data_root, force=args.force)
        if args.titles_only:
            return 0
        fetch_all_proposals(
            output_root=args.data_root,
            max_pages=args.max_pages,
            start_page=args.start_page,
            force=args.force,
        )
    except (httpx.HTTPError, RuntimeError, OSError) as exc:
        log.error("fatal", extra={"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "API_BASE",
    "FetcherConfig",
    "LidonationClient",
    "fetch_all_proposals",
    "fetch_fund_titles",
    "main",
]
