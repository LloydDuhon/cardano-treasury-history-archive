"""Hydra Voting API fetcher for Cardano Budget 2026 proposals.

Source: https://hydra-voting.intersectmbo.org/votes/cardano-budget-2026
API:    https://hydra-voting.intersectmbo.org/api/v0

This captures the current 2026 Cardano Budget Process proposal list used as
the Treasury Fund 2 comparison set in report generation.
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

API_BASE = "https://hydra-voting.intersectmbo.org/api/v0"
DEFAULT_VOTE_SLUG = "cardano-budget-2026"
DEFAULT_USER_AGENT = (
    "catalyst-history-archive/0.1 (+https://github.com/lloydduhon/catalyst-history-archive)"
)
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
    logger = logging.getLogger("hydra_voting")
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


class HydraVotingClient:
    """Small client for the public Intersect Hydra Voting API."""

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

    def __enter__(self) -> HydraVotingClient:
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

    def fetch_vote(self, slug: str) -> dict[str, Any]:
        payload = self._get_json("/votes/", params={"slug": slug})
        votes = payload.get("data") if isinstance(payload.get("data"), list) else []
        if not votes:
            raise RuntimeError(f"vote not found for slug {slug}")
        vote = votes[0]
        if not isinstance(vote, dict):
            raise RuntimeError(f"vote payload for slug {slug} was not an object")
        return vote

    def fetch_live_proposals(self, vote_id: str) -> dict[str, Any]:
        return self._get_json(
            "/proposals",
            params={
                "vote": vote_id,
                "page": 1,
                "limit": 100,
                "sort": "submittedAt",
                "direction": "desc",
                "status": "live",
            },
        )


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _raw_dir(data_root: Path) -> Path:
    return data_root / "_raw" / "hydra_voting"


def _snapshot_path(data_root: Path, slug: str) -> Path:
    return _raw_dir(data_root) / f"{slug}.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def fetch_vote_snapshot(
    *,
    output_root: Path | None = None,
    vote_slug: str = DEFAULT_VOTE_SLUG,
    force: bool = False,
    client: HydraVotingClient | None = None,
) -> Path:
    """Fetch and cache a vote plus its live proposal list."""

    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    target = _snapshot_path(root, vote_slug)
    if target.exists() and not force:
        log.info("snapshot.cached", extra={"path": str(target)})
        return target

    owns_client = client is None
    cli = client or HydraVotingClient(cfg)
    try:
        vote = cli.fetch_vote(vote_slug)
        vote_id = str(vote.get("_id") or "")
        proposals = cli.fetch_live_proposals(vote_id)
    finally:
        if owns_client:
            cli.close()

    snapshot = {
        "source": "hydra_voting_api",
        "source_url": f"https://hydra-voting.intersectmbo.org/votes/{vote_slug}",
        "api_url": API_BASE,
        "fetched_at": _utcnow_iso(),
        "vote_slug": vote_slug,
        "vote": vote,
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
    parser.add_argument("--vote-slug", default=DEFAULT_VOTE_SLUG)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        fetch_vote_snapshot(
            output_root=args.data_root,
            vote_slug=args.vote_slug,
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
    "DEFAULT_VOTE_SLUG",
    "FetcherConfig",
    "HydraVotingClient",
    "fetch_vote_snapshot",
    "main",
]
