"""Validate every per-fund data file against its JSON Schema.

Walks ../data/funds/*/proposals.json, proposers.json, milestones.json and
validates each record against the matching schema under ../schemas/.

Exit code:
    0  - every record valid
    1  - at least one record invalid (full report printed to stdout)
    2  - schema or data file missing where expected

Usage:
    python etl/validators/validate_against_schema.py
    python etl/validators/validate_against_schema.py --fund 10
    python etl/validators/validate_against_schema.py --strict   # fail on missing files

This is the only ETL component implemented in Phase 0. It is intentionally
small, dependency-light (jsonschema only), and runs in CI on every PR.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "schemas"
DATA_DIR = REPO_ROOT / "data" / "funds"

SCHEMA_FILES: dict[str, str] = {
    "proposals.json": "proposal.schema.json",
    "proposers.json": "proposer.schema.json",
    "milestones.json": "milestone.schema.json",
}


@dataclass(frozen=True)
class Failure:
    """One schema-validation failure."""

    file_path: Path
    record_index: int
    record_id: str | None
    error_path: str
    message: str


def load_schema(schema_path: Path) -> Draft202012Validator:
    """Load and compile a JSON Schema validator."""
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def iter_records(data_path: Path) -> Iterable[tuple[int, dict[str, object]]]:
    """Yield (index, record) pairs from a JSON array file.

    Tolerates an empty file or a file containing `[]`.
    """
    with data_path.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, list):
        raise ValueError(f"{data_path} must contain a JSON array, got {type(payload).__name__}")
    for idx, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValueError(f"{data_path}[{idx}] is not an object")
        yield idx, record


def validate_file(
    data_path: Path,
    validator: Draft202012Validator,
    id_field: str,
) -> list[Failure]:
    """Validate every record in `data_path` against `validator`."""
    failures: list[Failure] = []
    for idx, record in iter_records(data_path):
        record_id = record.get(id_field)
        record_id_str = record_id if isinstance(record_id, str) else None
        for err in validator.iter_errors(record):
            failures.append(
                Failure(
                    file_path=data_path,
                    record_index=idx,
                    record_id=record_id_str,
                    error_path="/".join(str(p) for p in err.absolute_path) or "<root>",
                    message=err.message,
                )
            )
    return failures


def id_field_for(filename: str) -> str:
    """Return the canonical id field name for each data file type."""
    return {
        "proposals.json": "proposal_id",
        "proposers.json": "proposer_id",
        "milestones.json": "milestone_id",
    }[filename]


def discover_funds(only_fund: int | None) -> list[Path]:
    """Return the fund directories to validate."""
    if not DATA_DIR.exists():
        return []
    if only_fund is not None:
        fund_dir = DATA_DIR / f"fund-{only_fund:02d}"
        return [fund_dir] if fund_dir.is_dir() else []
    return sorted(p for p in DATA_DIR.iterdir() if p.is_dir())


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fund", type=int, default=None, help="Validate only this fund number.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing expected data files as failures (default: skip silently).",
    )
    args = parser.parse_args(argv)

    if not SCHEMA_DIR.is_dir():
        print(f"FATAL: schema directory missing at {SCHEMA_DIR}", file=sys.stderr)
        return 2

    validators = {
        filename: load_schema(SCHEMA_DIR / schema_filename)
        for filename, schema_filename in SCHEMA_FILES.items()
    }

    fund_dirs = discover_funds(args.fund)
    if not fund_dirs:
        print("No fund directories under data/funds/ - nothing to validate. (Phase 0 expected.)")
        return 0

    all_failures: list[Failure] = []
    files_checked = 0

    for fund_dir in fund_dirs:
        for filename, validator in validators.items():
            data_path = fund_dir / filename
            if not data_path.exists():
                if args.strict:
                    print(f"MISSING {data_path}", file=sys.stderr)
                    all_failures.append(
                        Failure(
                            file_path=data_path,
                            record_index=-1,
                            record_id=None,
                            error_path="<file>",
                            message="expected data file missing under --strict",
                        )
                    )
                continue
            files_checked += 1
            try:
                failures = validate_file(data_path, validator, id_field_for(filename))
            except (json.JSONDecodeError, ValueError) as exc:
                all_failures.append(
                    Failure(
                        file_path=data_path,
                        record_index=-1,
                        record_id=None,
                        error_path="<file>",
                        message=f"could not parse: {exc}",
                    )
                )
                continue
            all_failures.extend(failures)

    if all_failures:
        print(f"FAILED: {len(all_failures)} validation error(s) in {files_checked} file(s)")
        for f in all_failures:
            rid = f" ({f.record_id})" if f.record_id else ""
            print(
                f"  {f.file_path.relative_to(REPO_ROOT)} "
                f"[{f.record_index}]{rid} @ {f.error_path}: {f.message}"
            )
        return 1

    print(f"OK: validated {files_checked} file(s) across {len(fund_dirs)} fund(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# Re-export ValidationError so test code can `from validators... import ValidationError`.
__all__ = ["Failure", "ValidationError", "main"]
