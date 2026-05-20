"""Sundae Treasury GraphQL fetcher.

Source:   https://treasury.sundae.fi
API:      https://api.treasury.sundae.fi/graphql
Coverage: Intersect Treasury Contracts 1, used here as Treasury Fund 1 history.
Auth:     None required.

This fetcher captures the public GraphQL project listing used by the Sundae
Treasury site. The normalizer in ``etl/normalizers/sundae_treasury.py`` turns
the raw capture into a report-ready historical funding dataset.

CLI:
    python -m fetchers.sundae_treasury
    python -m fetchers.sundae_treasury --force
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

API_BASE = "https://api.treasury.sundae.fi/graphql"
TREASURY_FUND_1_INSTANCE_ID = "9e65e4ed7d6fd86fc4827d2b45da6d2c601fb920e8bfd794b8ecc619"
DEFAULT_USER_AGENT = "cardano-treasury-history-archive/0.1 (+https://github.com/lloydduhon/cardano-treasury-history-archive)"
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

PROJECTS_QUERY = """
query fetchInstanceProjectsForArchive($Instance: String!) {
  instanceById(ID: $Instance) {
    identifier
    label
    description
    projects {
      identifier
      label
      description
      otherIdentifiers
      vendor {
        label
      }
      milestones {
        identifier
        label
        description
        acceptanceCriteria
        status
        value {
          assetId
          quantity
        }
        maturation {
          format
          unixMilli
        }
      }
    }
  }
}
"""


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
    logger = logging.getLogger("sundae_treasury")
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


class SundaeTreasuryClient:
    """Small GraphQL client for the public Sundae Treasury API."""

    def __init__(self, config: FetcherConfig) -> None:
        headers = {
            "User-Agent": config.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if config.contact_email:
            headers["From"] = config.contact_email
        self._client = httpx.Client(
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=False,
        )

    def __enter__(self) -> SundaeTreasuryClient:
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
    def query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.post(API_BASE, json={"query": query, "variables": variables})
        if resp.status_code == 429 or resp.status_code >= 500:
            raise RuntimeError(f"upstream {resp.status_code} from Sundae Treasury GraphQL")
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("errors"):
            raise RuntimeError(f"GraphQL errors: {payload['errors']}")
        if not isinstance(payload, dict):
            raise RuntimeError("GraphQL response was not an object")
        return payload

    def fetch_treasury_fund_1_projects(self) -> dict[str, Any]:
        return self.query(PROJECTS_QUERY, {"Instance": TREASURY_FUND_1_INSTANCE_ID})


def _raw_dir(data_root: Path) -> Path:
    return data_root / "_raw" / "sundae_treasury"


def _projects_path(data_root: Path) -> Path:
    return _raw_dir(data_root) / "treasury-fund-01-projects.json"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def fetch_treasury_fund_1_projects(
    *,
    output_root: Path | None = None,
    force: bool = False,
    client: SundaeTreasuryClient | None = None,
) -> Path:
    """Fetch and cache the Treasury Fund 1 project listing."""

    cfg = FetcherConfig.from_env()
    root = output_root if output_root is not None else cfg.data_root
    target = _projects_path(root)
    if target.exists() and not force:
        log.info("projects.cached", extra={"path": str(target)})
        return target

    owns_client = client is None
    cli = client or SundaeTreasuryClient(cfg)
    try:
        payload = cli.fetch_treasury_fund_1_projects()
    finally:
        if owns_client:
            cli.close()

    archive_payload = {
        "source": "sundae_treasury_graphql",
        "source_url": API_BASE,
        "fetched_at": _utcnow_iso(),
        "instance_id": TREASURY_FUND_1_INSTANCE_ID,
        "query": PROJECTS_QUERY.strip(),
        "response": payload,
    }
    _atomic_write_json(target, archive_payload)
    project_count = len(
        payload.get("data", {}).get("instanceById", {}).get("projects", [])
        if isinstance(payload.get("data"), dict)
        else []
    )
    log.info("projects.fetched", extra={"path": str(target), "projects": project_count})
    return target


def main(argv: list[str] | None = None) -> int:
    """Entry point: ``python -m fetchers.sundae_treasury``."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Override repo's data/ directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch and overwrite cached response.",
    )
    args = parser.parse_args(argv)

    try:
        fetch_treasury_fund_1_projects(output_root=args.data_root, force=args.force)
    except (httpx.HTTPError, RuntimeError, OSError) as exc:
        log.error("fatal", extra={"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "API_BASE",
    "PROJECTS_QUERY",
    "TREASURY_FUND_1_INSTANCE_ID",
    "FetcherConfig",
    "SundaeTreasuryClient",
    "fetch_treasury_fund_1_projects",
    "main",
]
