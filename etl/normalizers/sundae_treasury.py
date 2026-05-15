"""Normalize Sundae Treasury Fund 1 captures into historical funding files.

Input:
    data/_raw/sundae_treasury/treasury-fund-01-projects.json

Outputs:
    data/historical/treasury-fund-01/_meta.json
    data/historical/treasury-fund-01/projects.json
    data/historical/treasury-fund-01/vendors.json
    data/historical/treasury-fund-01/milestones.json

These files are intentionally separate from the Catalyst proposal schema. They
represent on-chain treasury contracts and milestone payment states, not Catalyst
votes. Reports can join them to current proposers by normalized vendor/proposer
name and by the vendor label when it is a stake address.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"
RAW_RELATIVE_PATH = "data/_raw/sundae_treasury/treasury-fund-01-projects.json"
SOURCE_URL = "https://api.treasury.sundae.fi/graphql"
TREASURY_SITE_URL = "https://treasury.sundae.fi"
JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned or "unknown"


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]


def _vendor_id(label: str) -> str:
    normalized = _normalize_name(label)
    return f"tf1-vendor-{_slugify(normalized)[:60]}-{_short_hash(label)}"


def _normalize_name(value: str | None) -> str:
    if not value:
        return "unknown"
    collapsed = re.sub(r"\s+", " ", value).strip()
    return collapsed


def _lovelace_to_ada(quantity: str | int | float | None) -> float:
    if quantity is None:
        return 0.0
    return int(quantity) / 1_000_000


def _sum_ada(values: list[dict[str, Any]]) -> float:
    total = 0.0
    for value in values:
        if value.get("assetId") == "ada.lovelace":
            total += _lovelace_to_ada(value.get("quantity"))
    return total


def _project_status(status_counts: Counter[str]) -> str:
    if not status_counts:
        return "unknown"
    total = sum(status_counts.values())
    if status_counts.get("Withdrawn", 0) == total:
        return "withdrawn"
    if status_counts.get("Matured", 0) == total:
        return "complete"
    if status_counts.get("Paused", 0):
        return "paused"
    if status_counts.get("Active", 0):
        return "active"
    return "mixed"


def _read_raw(raw_path: Path) -> dict[str, Any]:
    with raw_path.open("r", encoding="utf-8") as fh:
        payload: dict[str, Any] = json.load(fh)
    return payload


def _write_json(path: Path, payload: JsonValue) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def _source_entry(raw_path: Path, fetched_at: str) -> dict[str, Any]:
    return {
        "source": "sundae_treasury_graphql",
        "url": SOURCE_URL,
        "fetched_at": fetched_at,
        "provenance_path": str(raw_path),
    }


def normalize_treasury_fund_1(
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
    raw_path: Path | None = None,
) -> dict[str, int]:
    """Normalize raw Treasury Fund 1 GraphQL data into historical funding files."""

    raw = raw_path or data_root / "_raw" / "sundae_treasury" / "treasury-fund-01-projects.json"
    payload = _read_raw(raw)
    fetched_at = str(payload.get("fetched_at") or _utcnow_iso())
    response_obj = payload.get("response")
    response: dict[str, Any] = response_obj if isinstance(response_obj, dict) else {}
    data_obj = response.get("data")
    data: dict[str, Any] = data_obj if isinstance(data_obj, dict) else {}
    instance = data.get("instanceById", {})
    if not isinstance(instance, dict):
        raise ValueError("Raw Sundae Treasury response missing data.instanceById")
    projects_in = instance.get("projects") or []
    if not isinstance(projects_in, list):
        raise ValueError("Raw Sundae Treasury response projects field is not a list")

    provenance_path = raw.relative_to(REPO_ROOT) if raw.is_relative_to(REPO_ROOT) else raw
    source = _source_entry(provenance_path, fetched_at)
    instance_id = str(instance.get("identifier") or payload.get("instance_id") or "")
    instance_label = str(instance.get("label") or "Intersect Treasury Contracts 1")

    projects: list[dict[str, Any]] = []
    milestones: list[dict[str, Any]] = []
    vendor_projects: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for project in projects_in:
        if not isinstance(project, dict):
            continue
        project_id = str(project.get("identifier") or "")
        vendor_label = _normalize_name((project.get("vendor") or {}).get("label"))
        vendor_id = _vendor_id(vendor_label)
        project_milestones = project.get("milestones") or []
        status_counts: Counter[str] = Counter()
        amount_by_status: defaultdict[str, float] = defaultdict(float)
        total_contract_ada = 0.0

        for idx, milestone in enumerate(project_milestones, start=1):
            if not isinstance(milestone, dict):
                continue
            status = str(milestone.get("status") or "Unknown")
            values = milestone.get("value") or []
            milestone_ada = _sum_ada(values if isinstance(values, list) else [])
            status_counts[status] += 1
            amount_by_status[status] += milestone_ada
            total_contract_ada += milestone_ada
            milestone_id = str(milestone.get("identifier") or f"m-{idx}")
            milestones.append(
                {
                    "milestone_id": f"tf1-{project_id}-{milestone_id}",
                    "project_id": project_id,
                    "milestone_number": idx,
                    "source_milestone_id": milestone_id,
                    "title": milestone.get("label") or None,
                    "description": milestone.get("description") or None,
                    "acceptance_criteria": milestone.get("acceptanceCriteria") or None,
                    "status": status,
                    "amount_ada": milestone_ada,
                    "maturation_at": (milestone.get("maturation") or {}).get("format"),
                    "sources": [source],
                    "confidence": "high",
                }
            )

        project_record = {
            "project_id": project_id,
            "source_project_id": project_id,
            "instance_id": instance_id,
            "instance_label": instance_label,
            "title": project.get("label") or project_id,
            "description": project.get("description") or None,
            "other_identifiers": project.get("otherIdentifiers") or [],
            "vendor_id": vendor_id,
            "vendor_label": vendor_label,
            "status": _project_status(status_counts),
            "milestone_count": sum(status_counts.values()),
            "milestone_status_counts": dict(sorted(status_counts.items())),
            "total_contract_ada": total_contract_ada,
            "amount_by_milestone_status_ada": dict(sorted(amount_by_status.items())),
            "treasury_url": f"{TREASURY_SITE_URL}/budgets/{instance_id}/project/{project_id}",
            "sources": [source],
            "confidence": "high",
        }
        projects.append(project_record)
        vendor_projects[vendor_id].append(project_record)

    vendors = []
    for vendor_id, vendor_project_records in sorted(vendor_projects.items()):
        first = vendor_project_records[0]
        status_counts = Counter(p["status"] for p in vendor_project_records)
        vendors.append(
            {
                "vendor_id": vendor_id,
                "display_name": first["vendor_label"],
                "normalized_name": _normalize_name(first["vendor_label"]).casefold(),
                "source_system": "sundae_treasury",
                "source_instance": "treasury-fund-01",
                "project_ids": [p["project_id"] for p in vendor_project_records],
                "total_projects": len(vendor_project_records),
                "total_contract_ada": sum(
                    float(p["total_contract_ada"]) for p in vendor_project_records
                ),
                "project_status_counts": dict(sorted(status_counts.items())),
                "sources": [source],
                "confidence": "high",
            }
        )

    output_dir = data_root / "historical" / "treasury-fund-01"
    meta = {
        "dataset": "treasury-fund-01",
        "title": "Treasury Fund 1 - Intersect Treasury Contracts 1",
        "description": (
            "Historical funding dataset from the Sundae Treasury public GraphQL API. "
            "Use alongside Catalyst history when reporting whether current proposers "
            "have prior Catalyst or Treasury Fund 1 funding history."
        ),
        "source_url": TREASURY_SITE_URL,
        "api_url": SOURCE_URL,
        "instance_id": instance_id,
        "instance_label": instance_label,
        "raw_provenance_path": str(provenance_path),
        "fetched_at": fetched_at,
        "normalized_at": _utcnow_iso(),
        "project_count": len(projects),
        "vendor_count": len(vendors),
        "milestone_count": len(milestones),
        "notes": [
            "total_contract_ada is the sum of milestone values exposed by the treasury contract.",
            (
                "amount_by_milestone_status_ada preserves whether milestones are Withdrawn, "
                "Paused, Active, or Matured."
            ),
            (
                "Reports should distinguish contracted/allocated funding from Matured "
                "milestone amounts."
            ),
        ],
    }

    _write_json(output_dir / "_meta.json", meta)
    _write_json(output_dir / "projects.json", projects)
    _write_json(output_dir / "vendors.json", vendors)
    _write_json(output_dir / "milestones.json", milestones)

    return {
        "projects": len(projects),
        "vendors": len(vendors),
        "milestones": len(milestones),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=None,
        help="Override the raw Sundae Treasury capture path.",
    )
    args = parser.parse_args(argv)

    try:
        counters = normalize_treasury_fund_1(data_root=args.data_root, raw_path=args.raw_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps({"level": "ERROR", "msg": "fatal", "error": str(exc)}),
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"level": "INFO", "msg": "normalized", **counters}))
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["normalize_treasury_fund_1", "main"]
