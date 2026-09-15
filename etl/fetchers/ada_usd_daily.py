"""Fetch historical ADA/USD daily market data.

Source: https://min-api.cryptocompare.com/data/v2/histoday
Docs:   https://min-api.cryptocompare.com/documentation
Auth:   None required for the public endpoint used here.

The normalized dataset is intended for USD-denominated Catalyst records where
we need a defensible ADA-equivalent estimate. It is market price data, not proof
of the actual ADA paid in a disbursement transaction.

CLI:
    python -m fetchers.ada_usd_daily
    python -m fetchers.ada_usd_daily --force
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
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

API_BASE = "https://min-api.cryptocompare.com"
HISTODAY_PATH = "/data/v2/histoday"
DEFAULT_USER_AGENT = (
    "cardano-treasury-history-archive/0.1 "
    "(+https://github.com/lloydduhon/cardano-treasury-history-archive)"
)
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("ada_usd_daily")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


log = _configure_logging()


@dataclass(frozen=True)
class FetcherConfig:
    """Tunables for one ADA/USD historical price fetch."""

    user_agent: str = DEFAULT_USER_AGENT
    data_root: Path = DEFAULT_DATA_ROOT

    @classmethod
    def from_env(cls) -> FetcherConfig:
        return cls(
            user_agent=os.environ.get("HTTP_USER_AGENT", DEFAULT_USER_AGENT),
            data_root=Path(os.environ.get("PROVENANCE_ROOT", str(DEFAULT_DATA_ROOT))),
        )


def _retry_log(retry_state: RetryCallState) -> None:
    log.warning(
        "retry",
        extra={
            "attempt": retry_state.attempt_number,
            "wait_s": getattr(retry_state.next_action, "sleep", None),
            "exc": str(retry_state.outcome.exception()) if retry_state.outcome else None,
        },
    )


class CcdataMarketClient:
    """Small client for CCData/CryptoCompare market-history endpoints."""

    def __init__(self, config: FetcherConfig) -> None:
        self._client = httpx.Client(
            base_url=API_BASE,
            headers={
                "User-Agent": config.user_agent,
                "Accept": "application/json",
            },
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

    def __enter__(self) -> CcdataMarketClient:
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
    def fetch_ada_usd_all_daily(self) -> dict[str, Any]:
        resp = self._client.get(
            HISTODAY_PATH,
            params={
                "fsym": "ADA",
                "tsym": "USD",
                "allData": "true",
                "extraParams": "cardano-treasury-history-archive",
            },
        )
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {HISTODAY_PATH}")
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, dict):
            raise RuntimeError("CCData histoday response was not a JSON object")
        if payload.get("Response") != "Success":
            raise RuntimeError(f"CCData histoday response was not successful: {payload!r}")
        data = payload.get("Data")
        if not isinstance(data, dict) or not isinstance(data.get("Data"), list):
            raise RuntimeError("CCData histoday response did not include Data.Data rows")
        return payload


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _snapshot_path(data_root: Path) -> Path:
    return data_root / "_raw" / "ccdata" / "ada-usd-histoday-all.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def fetch_ada_usd_daily_snapshot(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: CcdataMarketClient | None = None,
) -> Path:
    """Fetch and cache full ADA/USD daily market history from CCData."""

    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    target = _snapshot_path(root)
    if target.exists() and not force:
        log.info("snapshot.cached", extra={"path": str(target)})
        return target

    owns_client = client is None
    cli = client or CcdataMarketClient(cfg)
    try:
        payload = cli.fetch_ada_usd_all_daily()
    finally:
        if owns_client:
            cli.close()

    rows = payload.get("Data", {}).get("Data", [])
    snapshot = {
        "source": "ccdata_cryptocompare_histoday",
        "source_url": "https://min-api.cryptocompare.com/data/v2/histoday",
        "api_url": API_BASE,
        "fetched_at": _utcnow_iso(),
        "query": {
            "fsym": "ADA",
            "tsym": "USD",
            "allData": True,
            "extraParams": "cardano-treasury-history-archive",
        },
        "response": payload,
    }
    _atomic_write_json(target, snapshot)
    log.info("snapshot.fetched", extra={"path": str(target), "rows": len(rows)})
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        fetch_ada_usd_daily_snapshot(output_root=args.data_root, force=args.force)
    except (httpx.HTTPError, RuntimeError, OSError) as exc:
        log.error("fatal", extra={"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "API_BASE",
    "CcdataMarketClient",
    "FetcherConfig",
    "fetch_ada_usd_daily_snapshot",
    "main",
]
