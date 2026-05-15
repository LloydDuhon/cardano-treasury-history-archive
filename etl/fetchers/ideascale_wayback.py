"""IdeaScale / Wayback Machine fetcher for Fund 1 backfill.

Source:        https://web.archive.org/cdx/search/cdx?url=cardano.ideascale.com/*
Coverage:      Fund 1 only (pilot, ~56 proposals, no funded winners).

This is the "heroic" fetcher: cardano.ideascale.com is a JS-rendered SPA
behind authentication today, so the only viable path for F1 data is the
Internet Archive's CDX index + snapshot fetch. Expect partial coverage,
imperfect titles, and `confidence: low` on every recovered record.

Two-stage fetch:
  1. CDX query for unique /a/dtd/* URLs in the F1 window (Sep 2020 - Jan 2021).
  2. For each unique URL, fetch the most recent successful HTML snapshot
     from https://web.archive.org/web/<timestamp>/<original>.

Outputs:
  data/funds/fund-01/_provenance/ideascale_wayback/cdx.json.gz
  data/funds/fund-01/_provenance/ideascale_wayback/snapshots/<urlkey>.html.gz

The normalizer `etl/normalizers/derive_fund_one.py` parses each snapshot
with BeautifulSoup and emits `data/funds/fund-01/proposals.json`.

Wayback is rate-sensitive. Default 0.5 rps, exponential backoff to 60s,
and we identify ourselves with a polite User-Agent. If you hit a 429,
just wait and re-run; cache makes the re-run idempotent.

CLI:
    python -m fetchers.ideascale_wayback --max-snapshots 5   # smoke
    python -m fetchers.ideascale_wayback                     # full F1 sweep
    python -m fetchers.ideascale_wayback --cdx-only          # just the index
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
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

from fetchers.lidonation_api import JsonLogFormatter

CDX_BASE = "https://web.archive.org/cdx/search/cdx"
WAYBACK_BASE = "https://web.archive.org/web"

# F1 window: pilot ran Sep 2020 - Dec 2020; we go to end of Jan 2021 for safety.
DEFAULT_FROM = "20200901"
DEFAULT_TO = "20210131"
DEFAULT_URL_PATTERN = "cardano.ideascale.com/a/dtd/*"

DEFAULT_USER_AGENT = (
    "cardano-treasury-history-archive/0.1 "
    "(+https://github.com/lloydduhon/cardano-treasury-history-archive)"
)
DEFAULT_RPS = 0.5
DEFAULT_TIMEOUT = httpx.Timeout(connect=15.0, read=60.0, write=10.0, pool=10.0)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("ideascale_wayback")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


log = _configure_logging()


@dataclass(frozen=True)
class WaybackConfig:
    """Tunables for one Wayback fetch run."""

    user_agent: str = DEFAULT_USER_AGENT
    rps: float = DEFAULT_RPS
    data_root: Path = DEFAULT_DATA_ROOT
    cdx_from: str = DEFAULT_FROM
    cdx_to: str = DEFAULT_TO
    url_pattern: str = DEFAULT_URL_PATTERN

    @classmethod
    def from_env(cls) -> WaybackConfig:
        return cls(
            user_agent=os.environ.get("HTTP_USER_AGENT", DEFAULT_USER_AGENT),
            rps=float(os.environ.get("WAYBACK_RPS", DEFAULT_RPS)),
            data_root=Path(os.environ.get("PROVENANCE_ROOT", str(DEFAULT_DATA_ROOT))),
        )


class _Throttle:
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


class WaybackClient:
    """Polite HTTP client for Wayback CDX + snapshot endpoints."""

    def __init__(self, config: WaybackConfig) -> None:
        self._cfg = config
        self._throttle = _Throttle(config.rps)
        self._client = httpx.Client(
            headers={"User-Agent": config.user_agent, "Accept": "*/*"},
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

    def __enter__(self) -> WaybackClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, RuntimeError)),
        wait=wait_exponential(multiplier=2.0, min=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
        before_sleep=_retry_log,
    )
    def get(self, url: str, params: dict[str, Any] | None = None) -> bytes:
        self._throttle.wait()
        resp = self._client.get(url, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {url}")
        resp.raise_for_status()
        return resp.content


# --------------------------------------------------------------------------- #
# Cache layout
# --------------------------------------------------------------------------- #


def _prov_dir(data_root: Path, fund: int = 1) -> Path:
    return data_root / "funds" / f"fund-{fund:02d}" / "_provenance" / "ideascale_wayback"


def _cdx_path(data_root: Path) -> Path:
    return _prov_dir(data_root) / "cdx.json.gz"


def _snapshot_path(data_root: Path, urlkey: str) -> Path:
    # urlkey can contain slashes/specials; hash-prefix for filesystem safety.
    digest = hashlib.sha1(urlkey.encode("utf-8"), usedforsecurity=False).hexdigest()[:16]
    safe = urlkey.replace("/", "_").replace(":", "_")[:80]
    return _prov_dir(data_root) / "snapshots" / f"{digest}-{safe}.html.gz"


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, payload: bytes, *, gzip_compress: bool) -> None:
    _ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = gzip.compress(payload, compresslevel=6) if gzip_compress else payload
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


# --------------------------------------------------------------------------- #
# CDX
# --------------------------------------------------------------------------- #


def parse_cdx(payload: bytes) -> list[dict[str, str]]:
    """Convert a Wayback CDX JSON response into a list of named dicts.

    The CDX response is `[header_row, ...data_rows]`. The header row contains
    column names. Most relevant columns: `urlkey`, `timestamp`, `original`,
    `statuscode`, `mimetype`.
    """
    data: list[list[str]] = json.loads(payload)
    if not data:
        return []
    header, rows = data[0], data[1:]
    out: list[dict[str, str]] = []
    for row in rows:
        out.append({header[i]: row[i] for i in range(min(len(header), len(row)))})
    return out


def fetch_cdx(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: WaybackClient | None = None,
) -> list[dict[str, str]]:
    """Query Wayback CDX for the F1 URL pattern and cache it.

    Returns the parsed CDX rows (one per snapshot).
    """
    cfg = WaybackConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    cdx_cache = _cdx_path(root)
    if cdx_cache.exists() and not force:
        log.info("cdx.cached", extra={"path": str(cdx_cache)})
        with gzip.open(cdx_cache, "rb") as fh:
            raw = fh.read()
        return parse_cdx(raw)

    params: dict[str, Any] = {
        "url": cfg.url_pattern,
        "from": cfg.cdx_from,
        "to": cfg.cdx_to,
        "output": "json",
        "filter": ["statuscode:200", "mimetype:text/html"],
        "collapse": "original",
    }
    owns = client is None
    cli = client or WaybackClient(cfg)
    try:
        payload = cli.get(CDX_BASE, params=params)
    finally:
        if owns:
            cli.close()
    _atomic_write(cdx_cache, payload, gzip_compress=True)
    log.info("cdx.fetched", extra={"bytes": len(payload), "path": str(cdx_cache)})
    return parse_cdx(payload)


def _pick_latest_per_url(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Return one row per original URL: the latest successful snapshot."""
    by_url: dict[str, dict[str, str]] = {}
    for row in rows:
        original = row.get("original")
        if not original:
            continue
        existing = by_url.get(original)
        if existing is None or row.get("timestamp", "") > existing.get("timestamp", ""):
            by_url[original] = row
    return list(by_url.values())


# --------------------------------------------------------------------------- #
# Snapshot fetching
# --------------------------------------------------------------------------- #


def fetch_snapshot(
    cdx_row: dict[str, str],
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: WaybackClient | None = None,
) -> Path | None:
    """Fetch one Wayback snapshot's HTML and cache it.

    Returns the cache path. Returns None if the snapshot can't be retrieved.
    """
    cfg = WaybackConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    urlkey = cdx_row.get("urlkey") or cdx_row.get("original", "")
    if not urlkey:
        return None
    cache = _snapshot_path(root, urlkey)
    if cache.exists() and not force:
        log.info("snapshot.cached", extra={"path": str(cache)})
        return cache

    timestamp = cdx_row.get("timestamp", "")
    original = cdx_row.get("original", "")
    if not timestamp or not original:
        return None
    # Use `id_` (identifier with raw flag) to skip Wayback's HTML wrapper.
    wb_url = f"{WAYBACK_BASE}/{timestamp}id_/{original}"

    owns = client is None
    cli = client or WaybackClient(cfg)
    try:
        payload = cli.get(wb_url)
    except (httpx.HTTPError, RuntimeError) as exc:
        log.warning(
            "snapshot.failed",
            extra={"url": wb_url, "error": str(exc), "type": type(exc).__name__},
        )
        return None
    finally:
        if owns:
            cli.close()
    _atomic_write(cache, payload, gzip_compress=True)
    log.info(
        "snapshot.fetched",
        extra={"urlkey": urlkey, "timestamp": timestamp, "bytes": len(payload)},
    )
    return cache


def fetch_fund_one_snapshots(
    *,
    output_root: Path | None = None,
    max_snapshots: int | None = None,
    force: bool = False,
    client: WaybackClient | None = None,
) -> dict[str, int]:
    """Two-stage fetch: CDX index + per-URL snapshot.

    Args:
        output_root: Path to data/. Defaults to repo's data/.
        max_snapshots: Cap on snapshot fetches for smoke tests.
        force: Re-fetch CDX and snapshots even if cached.
        client: Inject for tests.

    Returns:
        Counters dict.
    """
    cfg = WaybackConfig.from_env()
    owns = client is None
    cli = client or WaybackClient(cfg)
    counters = {"cdx_rows": 0, "unique_urls": 0, "snapshots_fetched": 0, "snapshots_skipped": 0}
    try:
        rows = fetch_cdx(output_root=output_root, force=force, client=cli)
        counters["cdx_rows"] = len(rows)
        unique = _pick_latest_per_url(rows)
        counters["unique_urls"] = len(unique)
        if max_snapshots is not None:
            unique = unique[:max_snapshots]
        for row in unique:
            existed_before = _snapshot_path(
                output_root or cfg.data_root, row.get("urlkey") or row.get("original", "")
            ).exists()
            path = fetch_snapshot(row, output_root=output_root, force=force, client=cli)
            if path is None:
                continue
            if existed_before and not force:
                counters["snapshots_skipped"] += 1
            else:
                counters["snapshots_fetched"] += 1
    finally:
        if owns:
            cli.close()

    log.info("sweep.complete", extra=counters)
    return counters


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``python -m fetchers.ideascale_wayback ...``"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None, help="Override data/ directory.")
    parser.add_argument(
        "--max-snapshots",
        type=int,
        default=None,
        help="Cap on per-URL snapshot fetches. None = all unique URLs.",
    )
    parser.add_argument(
        "--cdx-only",
        action="store_true",
        help="Fetch and cache only the CDX index; skip snapshot fetches.",
    )
    parser.add_argument("--force", action="store_true", help="Re-fetch cached files.")
    args = parser.parse_args(argv)

    try:
        with WaybackClient(WaybackConfig.from_env()) as client:
            if args.cdx_only:
                fetch_cdx(output_root=args.data_root, force=args.force, client=client)
            else:
                fetch_fund_one_snapshots(
                    output_root=args.data_root,
                    max_snapshots=args.max_snapshots,
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
    "CDX_BASE",
    "WAYBACK_BASE",
    "WaybackClient",
    "WaybackConfig",
    "fetch_cdx",
    "fetch_fund_one_snapshots",
    "fetch_snapshot",
    "main",
    "parse_cdx",
]
