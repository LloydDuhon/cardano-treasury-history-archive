"""Koios governance fetcher for on-chain Cardano treasury withdrawals.

Source: https://api.koios.rest/api/v1/proposal_list
Docs:   https://github.com/cardano-community/koios-artifacts
Auth:   None required for public tier.

This captures Conway-era on-chain governance actions of type
``TreasuryWithdrawals``. These are the Cardano treasury withdrawal actions
recorded on-chain, which may overlap with Intersect Treasury Fund 1 and may
also include independent withdrawals outside the TF1/TF2 process.

CLI:
    python -m fetchers.koios_governance
    python -m fetchers.koios_governance --force
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

API_BASE = "https://api.koios.rest/api/v1"
PROPOSAL_LIST_PATH = "/proposal_list"
DEFAULT_USER_AGENT = "cardano-treasury-history-archive/0.1 (+https://github.com/lloydduhon/cardano-treasury-history-archive)"
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"


class JsonLogFormatter(logging.Formatter):
    """Minimal JSON formatter so fetch logs are machine-readable."""

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
    logger = logging.getLogger("koios_governance")
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
    """Tunables for one fetcher run."""

    user_agent: str = DEFAULT_USER_AGENT
    contact_email: str = ""
    data_root: Path = DEFAULT_DATA_ROOT

    @classmethod
    def from_env(cls) -> FetcherConfig:
        return cls(
            user_agent=os.environ.get("HTTP_USER_AGENT", DEFAULT_USER_AGENT),
            contact_email=os.environ.get("HTTP_CONTACT_EMAIL", ""),
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


class KoiosGovernanceClient:
    """Small client for the public Koios governance API."""

    def __init__(self, config: FetcherConfig) -> None:
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

    def __enter__(self) -> KoiosGovernanceClient:
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
    def _get_json(self, path: str, *, params: dict[str, Any]) -> list[dict[str, Any]]:
        resp = self._client.get(path, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {path}")
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, list):
            raise RuntimeError(f"API response from {path} was not an array")
        if not all(isinstance(item, dict) for item in payload):
            raise RuntimeError(f"API response from {path} contained non-object rows")
        return payload

    def fetch_treasury_withdrawal_proposals(self) -> list[dict[str, Any]]:
        return self._get_json(
            PROPOSAL_LIST_PATH,
            params={"proposal_type": "eq.TreasuryWithdrawals"},
        )


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _raw_dir(data_root: Path) -> Path:
    return data_root / "_raw" / "koios_governance"


def _snapshot_path(data_root: Path) -> Path:
    return _raw_dir(data_root) / "treasury-withdrawal-proposals.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def fetch_treasury_withdrawal_snapshot(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: KoiosGovernanceClient | None = None,
) -> Path:
    """Fetch and cache on-chain TreasuryWithdrawals governance proposals."""

    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    target = _snapshot_path(root)
    if target.exists() and not force:
        log.info("snapshot.cached", extra={"path": str(target)})
        return target

    owns_client = client is None
    cli = client or KoiosGovernanceClient(cfg)
    try:
        proposals = cli.fetch_treasury_withdrawal_proposals()
    finally:
        if owns_client:
            cli.close()

    snapshot = {
        "source": "koios_governance_api",
        "source_url": "https://api.koios.rest/api/v1/proposal_list",
        "api_url": API_BASE,
        "fetched_at": _utcnow_iso(),
        "query": {"proposal_type": "eq.TreasuryWithdrawals"},
        "proposals": proposals,
    }
    _atomic_write_json(target, snapshot)
    log.info("snapshot.fetched", extra={"path": str(target), "proposals": len(proposals)})
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        fetch_treasury_withdrawal_snapshot(
            output_root=args.data_root,
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
    "KoiosGovernanceClient",
    "fetch_treasury_withdrawal_snapshot",
    "main",
]
