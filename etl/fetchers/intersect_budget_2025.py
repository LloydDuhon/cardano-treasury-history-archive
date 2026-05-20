"""Fetcher for the 2025 Cardano Budget Reconciliation Ekklesia API.

Source: https://2025budget.intersectmbo.org/
API:    https://2025budget.intersectmbo.org/api/v0

This captures the closed 2025 reconciliation ballot and its proposal owner
metadata. The owner fields are useful identity evidence when comparing 2025 and
2026 treasury proposers.
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

API_BASE = "https://2025budget.intersectmbo.org/api/v0"
DEFAULT_BALLOT_NAME = "2025 Cardano Budget Reconciliation"
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
    logger = logging.getLogger("intersect_budget_2025")
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


class IntersectBudget2025Client:
    """Small client for the public 2025 Ekklesia budget API."""

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
            follow_redirects=False,
        )

    def __enter__(self) -> IntersectBudget2025Client:
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
    def _get_json(self, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.get(path, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} on {path}")
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, dict):
            raise RuntimeError(f"API response from {path} was not an object")
        return payload

    def fetch_closed_ballots(self) -> dict[str, Any]:
        return self._get_json("/ballots", params={"status": "closed"})

    def fetch_ballot_proposals(self, ballot_id: str, *, limit: int = 100) -> dict[str, Any]:
        page = 1
        all_data: list[dict[str, Any]] = []
        pagination: dict[str, Any] = {}
        while True:
            payload = self._get_json(
                f"/ballots/{ballot_id}/proposals",
                params={
                    "page": page,
                    "limit": limit,
                    "direction": "asc",
                },
            )
            payload_data = payload.get("data")
            data = payload_data if isinstance(payload_data, list) else []
            all_data.extend(item for item in data if isinstance(item, dict))
            page_info = payload.get("pagination")
            pagination = page_info if isinstance(page_info, dict) else {}
            total_pages = int(pagination.get("totalPages") or page)
            if page >= total_pages:
                break
            page += 1
        return {"data": all_data, "pagination": pagination}


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _raw_dir(data_root: Path) -> Path:
    return data_root / "_raw" / "intersect_budget_2025"


def _snapshot_path(data_root: Path) -> Path:
    return _raw_dir(data_root) / "reconciliation.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def fetch_reconciliation_snapshot(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: IntersectBudget2025Client | None = None,
) -> Path:
    """Fetch and cache the closed 2025 reconciliation ballot plus proposals."""

    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    target = _snapshot_path(root)
    if target.exists() and not force:
        log.info("snapshot.cached", extra={"path": str(target)})
        return target

    owns_client = client is None
    cli = client or IntersectBudget2025Client(cfg)
    try:
        ballots = cli.fetch_closed_ballots()
        ballot_payload = ballots.get("data")
        ballot_data = ballot_payload if isinstance(ballot_payload, list) else []
        ballot = next(
            (
                item
                for item in ballot_data
                if isinstance(item, dict) and item.get("name") == DEFAULT_BALLOT_NAME
            ),
            None,
        )
        if not isinstance(ballot, dict):
            raise RuntimeError(f"ballot not found: {DEFAULT_BALLOT_NAME}")
        ballot_id = str(ballot.get("_id") or "")
        proposals = cli.fetch_ballot_proposals(ballot_id)
    finally:
        if owns_client:
            cli.close()

    snapshot = {
        "source": "intersect_budget_2025_api",
        "source_url": "https://2025budget.intersectmbo.org/",
        "api_url": API_BASE,
        "fetched_at": _utcnow_iso(),
        "ballot": ballot,
        "proposals_response": proposals,
    }
    _atomic_write_json(target, snapshot)
    proposal_data = proposals.get("data")
    proposal_count = len(proposal_data) if isinstance(proposal_data, list) else 0
    log.info("snapshot.fetched", extra={"path": str(target), "proposals": proposal_count})
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        fetch_reconciliation_snapshot(output_root=args.data_root, force=args.force)
    except (httpx.HTTPError, RuntimeError, OSError) as exc:
        log.error("fatal", extra={"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "API_BASE",
    "DEFAULT_BALLOT_NAME",
    "FetcherConfig",
    "IntersectBudget2025Client",
    "fetch_reconciliation_snapshot",
    "main",
]
