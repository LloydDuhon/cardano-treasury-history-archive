"""Normalize Koios on-chain TreasuryWithdrawals governance proposals."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
RAW_PATH = DEFAULT_DATA_ROOT / "_raw" / "koios_governance" / "treasury-withdrawal-proposals.json"
OUTPUT_DIR = DEFAULT_DATA_ROOT / "historical" / "cardano-treasury-withdrawals"
LOVELACE_PER_ADA = 1_000_000


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def _atomic_write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def _read_json(path: Path) -> JsonValue:
    return cast(JsonValue, json.loads(path.read_text(encoding="utf-8")))


def _block_time_iso(value: int | str | float | None) -> str:
    if value is None or value == "":
        return ""
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return ""
    return datetime.fromtimestamp(timestamp, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _proposal_status(row: dict[str, Any]) -> str:
    if row.get("enacted_epoch") is not None:
        return "enacted"
    if row.get("ratified_epoch") is not None:
        return "ratified"
    if row.get("expired_epoch") is not None:
        return "expired"
    if row.get("dropped_epoch") is not None:
        return "dropped"
    return "active"


def _metadata_body(row: dict[str, Any]) -> dict[str, Any]:
    meta_json = row.get("meta_json")
    if not isinstance(meta_json, dict):
        return {}
    body = meta_json.get("body")
    return body if isinstance(body, dict) else {}


def _withdrawals(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = row.get("withdrawal")
    if not isinstance(raw, list):
        return []
    withdrawals: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        amount_lovelace = int(item.get("amount") or 0)
        withdrawals.append(
            {
                "withdrawal_index": index,
                "stake_address": str(item.get("stake_address") or ""),
                "amount_lovelace": amount_lovelace,
                "amount_ada": amount_lovelace / LOVELACE_PER_ADA,
            }
        )
    return withdrawals


def _normalize_row(
    row: dict[str, Any],
    *,
    fetched_at: str,
    provenance_path: str,
) -> dict[str, Any]:
    body = _metadata_body(row)
    withdrawals = _withdrawals(row)
    total_lovelace = sum(int(withdrawal["amount_lovelace"]) for withdrawal in withdrawals)
    proposal_id = str(row.get("proposal_id") or "")
    proposal_tx_hash = str(row.get("proposal_tx_hash") or "")
    proposal_index = row.get("proposal_index")
    return {
        "withdrawal_action_id": proposal_id or f"{proposal_tx_hash}#{proposal_index}",
        "proposal_id": proposal_id,
        "proposal_tx_hash": proposal_tx_hash,
        "proposal_index": proposal_index,
        "proposal_type": str(row.get("proposal_type") or ""),
        "title": str(body.get("title") or ""),
        "abstract": str(body.get("abstract") or ""),
        "rationale": str(body.get("rationale") or ""),
        "motivation": str(body.get("motivation") or ""),
        "status": _proposal_status(row),
        "block_time": row.get("block_time"),
        "block_time_iso": _block_time_iso(row.get("block_time")),
        "proposed_epoch": row.get("proposed_epoch"),
        "ratified_epoch": row.get("ratified_epoch"),
        "enacted_epoch": row.get("enacted_epoch"),
        "dropped_epoch": row.get("dropped_epoch"),
        "expired_epoch": row.get("expired_epoch"),
        "expiration_epoch": row.get("expiration"),
        "deposit_lovelace": int(row.get("deposit") or 0),
        "return_address": str(row.get("return_address") or ""),
        "meta_url": str(row.get("meta_url") or ""),
        "meta_hash": str(row.get("meta_hash") or ""),
        "meta_is_valid": row.get("meta_is_valid"),
        "meta_comment": str(row.get("meta_comment") or ""),
        "total_withdrawal_lovelace": total_lovelace,
        "total_withdrawal_ada": total_lovelace / LOVELACE_PER_ADA,
        "withdrawal_count": len(withdrawals),
        "withdrawals": withdrawals,
        "sources": [
            {
                "source": "koios_governance_api",
                "url": "https://api.koios.rest/api/v1/proposal_list",
                "fetched_at": fetched_at,
                "provenance_path": provenance_path,
            }
        ],
        "confidence": "high",
    }


def normalize_onchain_treasury_withdrawals(
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
    raw_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, int]:
    """Normalize raw Koios TreasuryWithdrawals proposals."""

    source_path = raw_path or data_root / "_raw" / "koios_governance" / (
        "treasury-withdrawal-proposals.json"
    )
    target_dir = output_dir or data_root / "historical" / "cardano-treasury-withdrawals"
    raw = _read_json(source_path)
    if not isinstance(raw, dict):
        raise RuntimeError(f"{source_path} does not contain a JSON object")
    proposals = raw.get("proposals")
    if not isinstance(proposals, list):
        raise RuntimeError(f"{source_path} does not contain a proposals array")

    fetched_at = str(raw.get("fetched_at") or "")
    provenance_path = (
        str(source_path.relative_to(data_root))
        if source_path.is_relative_to(data_root)
        else str(source_path)
    )
    records = [
        _normalize_row(row, fetched_at=fetched_at, provenance_path=provenance_path)
        for row in proposals
        if isinstance(row, dict)
    ]
    records.sort(key=lambda r: (int(r.get("block_time") or 0), str(r.get("proposal_id") or "")))

    status_counts = Counter(str(record.get("status") or "") for record in records)
    total_lovelace = sum(int(record["total_withdrawal_lovelace"]) for record in records)
    meta = {
        "dataset": "cardano-treasury-withdrawals",
        "source": "koios_governance_api",
        "source_url": "https://api.koios.rest/api/v1/proposal_list",
        "raw_provenance_path": provenance_path,
        "fetched_at": fetched_at,
        "normalized_at": _utcnow_iso(),
        "records": len(records),
        "total_withdrawal_lovelace": total_lovelace,
        "total_withdrawal_ada": total_lovelace / LOVELACE_PER_ADA,
        "status_counts": dict(sorted(status_counts.items())),
        "notes": [
            "Rows are Conway-era on-chain governance actions of type TreasuryWithdrawals.",
            "This includes withdrawals that may overlap with TF1 and withdrawals outside "
            "Intersect budget processes.",
            "Amounts are requested withdrawal amounts from the governance proposal, not "
            "downstream vendor disbursements.",
        ],
    }

    _atomic_write_json(target_dir / "withdrawals.json", records)
    _atomic_write_json(target_dir / "_meta.json", meta)
    return {"withdrawal_actions": len(records)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--raw-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        counters = normalize_onchain_treasury_withdrawals(
            data_root=args.data_root,
            raw_path=args.raw_path,
            output_dir=args.output_dir,
        )
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"level": "ERROR", "msg": "fatal", "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({"level": "INFO", "msg": "normalized", **counters}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["normalize_onchain_treasury_withdrawals"]
