"""Catalyst Milestone Module fetcher (Supabase REST).

Source:        Supabase project hutbpqoulajxnzwykvrf.supabase.co
               (the backend powering https://milestones.projectcatalyst.io/)
Coverage:      Funds 9-14 (id=1..6 in Supabase). F9 was the pilot; F10
               onward mandatory for funded projects.
Auth:          Public anon key from milestones.projectcatalyst.io/env.js
               (intended for client-side use; baked into the SPA bundle).

Probed live on 2026-05-13:
  - The HTML page is a Vite SPA shell (<div id="app"></div>); no scrapable
    content. Data is loaded via XHR against Supabase REST.
  - The anon key is exposed in /env.js and designed for read-only access
    via Postgres row-level security.
  - Tables we read: funds, challenges, proposals, soms, poas, signoffs.
  - Schema notes:
      * `soms` (Statement of Milestones) is one row per milestone REVISION;
        filter `current=eq.true` for the live view, but we cache everything.
      * `poas` (Proof of Achievement) carries markdown content describing
        what was delivered, plus active_reviews counter.
      * `signoffs` link a som_id to a poa_id plus a reviewer user_id.

This module is named `milestones_scraper.py` for stable backward-compat with
the Phase 0 stub; despite the name, no HTML scraping is performed.

Outputs (gzipped JSON arrays, one per Supabase table per fund):
    data/funds/fund-XX/_provenance/milestones_supabase/
        funds.json.gz
        challenges.json.gz
        proposals.json.gz
        soms.json.gz
        poas.json.gz
        signoffs.json.gz

The normalizer `etl/normalizers/derive_milestones.py` reads these and emits
`data/funds/fund-XX/milestones.json` matching `schemas/milestone.schema.json`.

CLI:
    python -m fetchers.milestones_scraper --fund 9     # F9 smoke (~7 calls)
    python -m fetchers.milestones_scraper              # all F9-F14
    python -m fetchers.milestones_scraper --force      # re-fetch cached
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

from fetchers.lidonation_api import JsonLogFormatter

# These are PUBLIC values exposed in milestones.projectcatalyst.io/env.js
# for the SPA to use. Repeating them as defaults so the fetcher works without
# any environment configuration; .env can override.
DEFAULT_SUPABASE_URL = "https://hutbpqoulajxnzwykvrf.supabase.co"
DEFAULT_SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh1dGJwcW91bGFqeG56d3lrdnJmIiwic"
    "m9sZSI6ImFub24iLCJpYXQiOjE2ODI0NTU5NTAsImV4cCI6MTk5ODAzMTk1MH0."
    "ecs2bfAZzT0KwdsqrkAMpPWf0K1_pRvV1_4vK1_lCzI"
)
DEFAULT_USER_AGENT = (
    "cardano-treasury-history-archive/0.1 "
    "(+https://github.com/lloydduhon/cardano-treasury-history-archive)"
)
DEFAULT_RPS = 1.0
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
PAGE_SIZE = 1000
ID_FILTER_CHUNK_SIZE = 250

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

# Maps fund number (real-world: 9, 10, ...) to Supabase fund_id (1, 2, ...).
# Discovered by reading rest/v1/funds in May 2026.
FUND_TO_SUPABASE_ID: dict[int, int] = {
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 6,
}


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("milestones_supabase")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


log = _configure_logging()


@dataclass(frozen=True)
class MilestonesConfig:
    """Tunables for one milestone-module fetch run."""

    supabase_url: str = DEFAULT_SUPABASE_URL
    anon_key: str = DEFAULT_SUPABASE_ANON_KEY
    user_agent: str = DEFAULT_USER_AGENT
    rps: float = DEFAULT_RPS
    data_root: Path = DEFAULT_DATA_ROOT

    @classmethod
    def from_env(cls) -> MilestonesConfig:
        return cls(
            supabase_url=os.environ.get("MILESTONES_SUPABASE_URL", DEFAULT_SUPABASE_URL).rstrip(
                "/"
            ),
            anon_key=os.environ.get("MILESTONES_SUPABASE_ANON_KEY", DEFAULT_SUPABASE_ANON_KEY),
            user_agent=os.environ.get("HTTP_USER_AGENT", DEFAULT_USER_AGENT),
            rps=float(os.environ.get("MILESTONES_RPS", DEFAULT_RPS)),
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


class MilestonesSupabaseClient:
    """Polite Supabase REST client for the Milestone Module."""

    def __init__(self, config: MilestonesConfig) -> None:
        self._cfg = config
        self._throttle = _Throttle(config.rps)
        self._client = httpx.Client(
            base_url=config.supabase_url,
            headers={
                "User-Agent": config.user_agent,
                "apikey": config.anon_key,
                "Authorization": f"Bearer {config.anon_key}",
                "Accept": "application/json",
            },
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

    def __enter__(self) -> MilestonesSupabaseClient:
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
    def _get(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        self._throttle.wait()
        resp = self._client.get(path, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {path}")
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise RuntimeError(f"unexpected non-list response from {path}: {type(data).__name__}")
        return data

    def fetch_all(self, table: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Paginated GET against a Supabase table.

        Pages via offset+limit; stops when fewer than PAGE_SIZE rows return.
        """
        out: list[dict[str, Any]] = []
        offset = 0
        base_params = dict(params or {})
        while True:
            page_params = dict(base_params)
            page_params["limit"] = PAGE_SIZE
            page_params["offset"] = offset
            rows = self._get(f"/rest/v1/{table}", page_params)
            out.extend(rows)
            if len(rows) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
        log.info(
            "table.fetched",
            extra={"table": table, "rows": len(out), "params": dict(base_params)},
        )
        return out


# --------------------------------------------------------------------------- #
# Cache layout
# --------------------------------------------------------------------------- #


def _prov_dir(data_root: Path, fund: int) -> Path:
    return data_root / "funds" / f"fund-{fund:02d}" / "_provenance" / "milestones_supabase"


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _atomic_write_gz(path: Path, payload: bytes) -> None:
    _ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = gzip.compress(payload, compresslevel=6)
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def _cache_path(data_root: Path, fund: int, table: str) -> Path:
    return _prov_dir(data_root, fund) / f"{table}.json.gz"


def _read_cache(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    with gzip.open(path, "rb") as fh:
        data = json.loads(fh.read())
    if not isinstance(data, list):
        raise RuntimeError(f"cache file is not a JSON array: {path}")
    return data


def _write_cache(path: Path, rows: list[dict[str, Any]]) -> None:
    _atomic_write_gz(path, json.dumps(rows, ensure_ascii=False).encode("utf-8"))


def _chunks(values: list[str], size: int = ID_FILTER_CHUNK_SIZE) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


# --------------------------------------------------------------------------- #
# Public fetch routines
# --------------------------------------------------------------------------- #


def fetch_fund(
    fund: int,
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: MilestonesSupabaseClient | None = None,
) -> dict[str, int]:
    """Fetch and cache every Supabase table needed to derive one fund's milestones.

    Args:
        fund: Real-world fund number (9, 10, ..., 14).
        output_root: Path to data/ (defaults to repo's data/).
        force: Re-fetch even when cached.
        client: Inject for tests.

    Returns:
        Counters dict mapping table_name -> row_count.

    Raises:
        ValueError: if `fund` is outside FUND_TO_SUPABASE_ID coverage.
    """
    if fund not in FUND_TO_SUPABASE_ID:
        raise ValueError(
            f"Fund {fund} is not covered by the Milestone Module "
            f"(supported: {sorted(FUND_TO_SUPABASE_ID)})"
        )
    cfg = MilestonesConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    sb_fund_id = FUND_TO_SUPABASE_ID[fund]

    owns = client is None
    cli = client or MilestonesSupabaseClient(cfg)
    counters: dict[str, int] = {}

    def _fetch_or_cache(table: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        cache = _cache_path(root, fund, table)
        if cache.exists() and not force:
            cached = _read_cache(cache)
            assert cached is not None
            log.info("table.cached", extra={"table": table, "rows": len(cached)})
            counters[table] = len(cached)
            return cached
        rows = cli.fetch_all(table, params)
        _write_cache(cache, rows)
        counters[table] = len(rows)
        return rows

    def _fetch_signoffs_or_cache(som_ids: list[str]) -> list[dict[str, Any]]:
        table = "signoffs"
        cache = _cache_path(root, fund, table)
        if cache.exists() and not force:
            cached = _read_cache(cache)
            assert cached is not None
            log.info("table.cached", extra={"table": table, "rows": len(cached)})
            counters[table] = len(cached)
            return cached
        rows: list[dict[str, Any]] = []
        for chunk in _chunks(som_ids):
            som_filter = f"in.({','.join(chunk)})"
            rows.extend(cli.fetch_all(table, {"som_id": som_filter}))
        _write_cache(cache, rows)
        counters[table] = len(rows)
        return rows

    try:
        # 1. funds (small but useful for the join map)
        _fetch_or_cache("funds", {"id": f"eq.{sb_fund_id}"})

        # 2. challenges in this fund
        challenges = _fetch_or_cache("challenges", {"fund_id": f"eq.{sb_fund_id}"})
        challenge_ids = [str(c["id"]) for c in challenges]
        if not challenge_ids:
            log.warning("no_challenges", extra={"fund": fund})
            return counters
        ch_filter = f"in.({','.join(challenge_ids)})"

        # 3. proposals in those challenges
        proposals = _fetch_or_cache("proposals", {"challenge_id": ch_filter})
        proposal_ids = [str(p["id"]) for p in proposals]
        if not proposal_ids:
            log.warning("no_proposals", extra={"fund": fund})
            return counters
        pid_filter = f"in.({','.join(proposal_ids)})"

        # 4. soms (all revisions; normalizer filters current=true)
        soms = _fetch_or_cache("soms", {"proposal_id": pid_filter})

        # 5. poas
        _fetch_or_cache("poas", {"proposal_id": pid_filter})

        # 6. signoffs (joined via som_id)
        som_ids = [str(s["id"]) for s in soms]
        if som_ids:
            _fetch_signoffs_or_cache(som_ids)
        else:
            counters["signoffs"] = 0
    finally:
        if owns:
            cli.close()

    log.info("fund.complete", extra={"fund": fund, "counters": counters})
    return counters


def fetch_all_funds(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: MilestonesSupabaseClient | None = None,
) -> dict[int, dict[str, int]]:
    """Fetch every covered fund (F9-F14)."""
    out: dict[int, dict[str, int]] = {}
    for fund in sorted(FUND_TO_SUPABASE_ID):
        out[fund] = fetch_fund(fund, output_root=output_root, force=force, client=client)
    return out


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
        help="Fund(s) to fetch (9-14). Default: all.",
    )
    parser.add_argument("--force", action="store_true", help="Re-fetch cached tables.")
    args = parser.parse_args(argv)

    cfg = MilestonesConfig.from_env()
    funds = tuple(args.fund) if args.fund else tuple(sorted(FUND_TO_SUPABASE_ID))
    try:
        with MilestonesSupabaseClient(cfg) as client:
            for n in funds:
                fetch_fund(n, output_root=args.data_root, force=args.force, client=client)
    except (httpx.HTTPError, RuntimeError, OSError, ValueError) as exc:
        log.error("fatal", extra={"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "DEFAULT_SUPABASE_ANON_KEY",
    "DEFAULT_SUPABASE_URL",
    "FUND_TO_SUPABASE_ID",
    "MilestonesConfig",
    "MilestonesSupabaseClient",
    "fetch_all_funds",
    "fetch_fund",
    "main",
]
