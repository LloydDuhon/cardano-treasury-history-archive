"""Normalize historical ADA/USD daily market data from CCData."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
RAW_PATH = DEFAULT_DATA_ROOT / "_raw" / "ccdata" / "ada-usd-histoday-all.json"
OUTPUT_DIR = DEFAULT_DATA_ROOT / "historical" / "ada-usd-daily"

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _atomic_write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def _atomic_write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    columns = [
        "date",
        "timestamp",
        "open_usd",
        "high_usd",
        "low_usd",
        "close_usd",
        "volume_ada",
        "volume_usd",
        "conversion_type",
        "conversion_symbol",
    ]
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def _read_json(path: Path) -> JsonValue:
    return cast(JsonValue, json.loads(path.read_text(encoding="utf-8")))


def _date_from_timestamp(value: int | str | float | None) -> str:
    if value is None or value == "":
        return ""
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return ""
    return datetime.fromtimestamp(timestamp, tz=UTC).strftime("%Y-%m-%d")


def _number(row: dict[str, Any], key: str) -> float:
    try:
        return float(row.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def _normalize_price_row(row: dict[str, Any]) -> dict[str, Any]:
    timestamp = int(row.get("time") or 0)
    return {
        "date": _date_from_timestamp(timestamp),
        "timestamp": timestamp,
        "open_usd": _number(row, "open"),
        "high_usd": _number(row, "high"),
        "low_usd": _number(row, "low"),
        "close_usd": _number(row, "close"),
        "volume_ada": _number(row, "volumefrom"),
        "volume_usd": _number(row, "volumeto"),
        "conversion_type": str(row.get("conversionType") or ""),
        "conversion_symbol": str(row.get("conversionSymbol") or ""),
    }


def _valid_market_row(row: dict[str, Any]) -> bool:
    return int(row.get("time") or 0) > 0 and _number(row, "close") > 0


def normalize_ada_usd_daily(
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
    raw_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, int]:
    """Normalize raw CCData ADA/USD daily OHLCV rows to JSON and CSV."""

    source_path = raw_path or data_root / "_raw" / "ccdata" / "ada-usd-histoday-all.json"
    target_dir = output_dir or data_root / "historical" / "ada-usd-daily"
    raw = _read_json(source_path)
    if not isinstance(raw, dict):
        raise RuntimeError(f"{source_path} does not contain a JSON object")
    response = raw.get("response")
    if not isinstance(response, dict):
        raise RuntimeError(f"{source_path} does not contain a response object")
    data = response.get("Data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{source_path} response does not contain Data object")
    raw_rows = data.get("Data")
    if not isinstance(raw_rows, list):
        raise RuntimeError(f"{source_path} response does not contain Data.Data rows")

    records = [
        _normalize_price_row(row)
        for row in raw_rows
        if isinstance(row, dict) and _valid_market_row(row)
    ]
    records.sort(key=lambda row: (str(row.get("date") or ""), int(row.get("timestamp") or 0)))

    provenance_path = (
        str(source_path.relative_to(data_root))
        if source_path.is_relative_to(data_root)
        else str(source_path)
    )
    meta = {
        "dataset": "ada-usd-daily",
        "source": "ccdata_cryptocompare_histoday",
        "source_url": "https://min-api.cryptocompare.com/data/v2/histoday",
        "docs_url": "https://min-api.cryptocompare.com/documentation",
        "raw_provenance_path": provenance_path,
        "fetched_at": str(raw.get("fetched_at") or ""),
        "normalized_at": _utcnow_iso(),
        "records": len(records),
        "raw_rows": len(raw_rows),
        "dropped_rows": len(raw_rows) - len(records),
        "first_date": records[0]["date"] if records else None,
        "last_date": records[-1]["date"] if records else None,
        "quote_currency": "USD",
        "base_currency": "ADA",
        "price_fields": ["open_usd", "high_usd", "low_usd", "close_usd"],
        "notes": [
            "Daily OHLCV market data for ADA quoted in USD.",
            "Rows with close_usd <= 0 are excluded from normalized outputs; CCData's allData "
            "response includes zero-filled pre-market rows before ADA traded.",
            "Use close_usd on the selected policy date for reproducible USD-to-ADA estimates.",
            "This dataset estimates historical ADA equivalents; it does not prove actual "
            "disbursement transaction amounts.",
            "CoinGecko public API full-range access was unavailable during implementation "
            "because public requests were limited to the trailing 365 days.",
        ],
    }

    _atomic_write_json(target_dir / "prices.json", records)
    _atomic_write_csv(target_dir / "prices.csv", records)
    _atomic_write_json(target_dir / "_meta.json", meta)
    return {"price_rows": len(records), "dropped_rows": len(raw_rows) - len(records)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--raw-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        counters = normalize_ada_usd_daily(
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


__all__ = [
    "OUTPUT_DIR",
    "RAW_PATH",
    "main",
    "normalize_ada_usd_daily",
]
