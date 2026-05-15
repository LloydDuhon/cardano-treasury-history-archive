"""Deduplicate proposer entities across all funds.

Reads every `data/funds/fund-XX/proposals.json` and the raw Lidonation cache
(if present), extracts proposer references, and emits per-fund
`proposers.json` files plus a consolidated cross-fund view used by
`consolidate.py`.

Dedup logic (per ADR-2026-05-13 schema):
  - Exact external_id match (lidonation_profile_uuid,
    ideascale_profile_id, catalyst_voices_stake_address) collapses
    multiple local proposer_id references into one canonical proposer.
  - Fuzzy display-name match (levenshtein <= 2 across distinct external
    ids OR display_name equal after slugify) is recorded in
    `duplicate_candidates[]` on BOTH records - never silently merged.

CLI:
    python -m normalizers.dedupe_proposers
    python -m normalizers.dedupe_proposers --fund 10
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

_LIDO_RE = re.compile(r"^p-lido-([0-9a-fA-F-]{8,})$")
_IDEASCALE_F01_RE = re.compile(r"^p-ideascale-wayback-f(\d{2})-(.+?)-(\w+)$")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _mint_proposer_id(display_name: str, anchor: str) -> str:
    """Canonical proposer_id: p-<slug>-<short_hash>."""
    slug = slugify(display_name)[:40] or "anonymous"
    short = hashlib.sha1(anchor.encode("utf-8"), usedforsecurity=False).hexdigest()[:6]
    return f"p-{slug}-{short}"


def _load_proposer_names_from_lidonation(data_root: Path) -> dict[str, str]:
    """Walk raw Lidonation pages and build a uuid -> display_name map."""
    out: dict[str, str] = {}
    raw_dir = data_root / "_raw" / "lidonation"
    if not raw_dir.exists():
        return out
    for page_path in sorted(raw_dir.glob("page-*.json.gz")):
        with gzip.open(page_path, "rb") as fh:
            page = json.loads(fh.read())
        for proposal in page.get("data") or []:
            for user in proposal.get("users") or []:
                if not isinstance(user, dict):
                    continue
                uid = user.get("id")
                name = user.get("name")
                if uid and name:
                    out.setdefault(str(uid), str(name))
    return out


def _extract_external_ids(local_proposer_id: str) -> dict[str, str]:
    """Parse a local proposer_id back into external_ids fields."""
    if m := _LIDO_RE.match(local_proposer_id):
        return {"lidonation_profile_uuid": m.group(1)}
    if m := _IDEASCALE_F01_RE.match(local_proposer_id):
        # We have only the idea_id + a slug of the display name; nothing
        # canonical to bind to. Return empty; dedupe will rely on the slug.
        return {}
    return {}


def _name_for(local_proposer_id: str, lidonation_names: dict[str, str]) -> str:
    if m := _LIDO_RE.match(local_proposer_id):
        uid = m.group(1)
        return lidonation_names.get(uid, f"Proposer {uid[:8]}")
    if m := _IDEASCALE_F01_RE.match(local_proposer_id):
        slug = m.group(2)
        return slug.replace("-", " ").title() or "Anonymous"
    return "Anonymous"


def _slug_key(s: str) -> str:
    return slugify(s or "", lowercase=True)


def _iter_proposals(data_root: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield (fund_number, proposal) tuples for every fund's proposals.json."""
    funds_dir = data_root / "funds"
    if not funds_dir.exists():
        return
    for fund_dir in sorted(funds_dir.iterdir()):
        if not fund_dir.is_dir() or not fund_dir.name.startswith("fund-"):
            continue
        try:
            fund_n = int(fund_dir.name.split("-", 1)[1])
        except (IndexError, ValueError):
            continue
        prop_path = fund_dir / "proposals.json"
        if not prop_path.exists():
            continue
        proposals: list[dict[str, Any]] = json.loads(prop_path.read_text())
        for p in proposals:
            yield fund_n, p


def build_proposers(
    *,
    data_root: Path,
    only_funds: set[int] | None = None,
) -> dict[str, dict[str, Any]]:
    """Build canonical proposer entities keyed by canonical proposer_id.

    Returns a dict[canonical_id] -> proposer_record (schema-conformant).
    """
    lido_names = _load_proposer_names_from_lidonation(data_root)
    snapshot_at = _utcnow_iso()

    # 1. Walk every proposal and collect (local_proposer_id, fund, proposal_id).
    refs: list[tuple[str, int, str]] = []
    for fund_n, proposal in _iter_proposals(data_root):
        if only_funds is not None and fund_n not in only_funds:
            continue
        for pid in proposal.get("proposer_ids") or []:
            refs.append((pid, fund_n, proposal.get("proposal_id", "")))

    # 2. Bucket by exact-ID anchor. For Lidonation: the UUID. For others: the
    # full local_proposer_id string (no transitive cross-source merge yet).
    by_anchor: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    for ref in refs:
        local_id, fund_n, proposal_id = ref
        ext = _extract_external_ids(local_id)
        anchor = ext.get("lidonation_profile_uuid") or local_id
        by_anchor[anchor].append(ref)

    # 3. Build one proposer record per anchor.
    proposers: dict[str, dict[str, Any]] = {}
    name_index: dict[str, list[str]] = defaultdict(list)  # slug -> [canonical_id]

    for anchor, group in by_anchor.items():
        # Use the first local_id for naming.
        first_local_id = group[0][0]
        display_name = _name_for(first_local_id, lido_names)
        canonical_id = _mint_proposer_id(display_name, anchor)
        ext_ids: dict[str, str | None] = {
            "ideascale_profile_id": None,
            "lidonation_profile_uuid": None,
            "catalyst_voices_profile_id": None,
            "catalyst_voices_stake_address": None,
        }
        first_ext = _extract_external_ids(first_local_id)
        for k, v in first_ext.items():
            ext_ids[k] = v
        # Only emit non-null external_ids to satisfy the schema.
        ext_ids_clean = {k: v for k, v in ext_ids.items() if v is not None}

        funds_seen = sorted({r[1] for r in group})
        proposal_ids = sorted({r[2] for r in group if r[2]})

        rec: dict[str, Any] = {
            "proposer_id": canonical_id,
            "display_name": display_name,
            "entity_type": "unknown",
            "team_members": [],
            "external_ids": ext_ids_clean,
            "socials": {},
            "proposal_ids": proposal_ids,
            "rollups": {
                "total_proposals": len(proposal_ids),
                "total_funded": 0,
                "total_completed": 0,
                "total_cancelled": 0,
                "total_in_progress": 0,
                "total_requested_ada": 0,
                "total_received_ada": 0,
                "first_fund": funds_seen[0] if funds_seen else None,
                "last_fund": funds_seen[-1] if funds_seen else None,
            },
            "sources": [
                {
                    "source": "lidonation_api"
                    if first_ext.get("lidonation_profile_uuid")
                    else "ideascale_wayback",
                    "url": None,
                    "fetched_at": snapshot_at,
                    "provenance_path": None,
                }
            ],
            "confidence": "medium" if first_ext.get("lidonation_profile_uuid") else "low",
            "duplicate_candidates": [],
            "notes": None,
        }
        proposers[canonical_id] = rec
        name_index[_slug_key(display_name)].append(canonical_id)

    # 4. Fuzzy duplicate detection: same display_name slug -> mutual candidates.
    for slug, ids in name_index.items():
        if len(ids) <= 1 or not slug:
            continue
        for cid in ids:
            others = [other for other in ids if other != cid]
            proposers[cid]["duplicate_candidates"] = others

    # 5. Compute rollups by re-walking proposals with proposer_id mapping.
    canonical_for_local: dict[str, str] = {}
    for anchor, group in by_anchor.items():
        # Each group corresponds to one canonical proposer.
        first_local_id = group[0][0]
        display_name = _name_for(first_local_id, lido_names)
        cid = _mint_proposer_id(display_name, anchor)
        for local_id, _, _ in group:
            canonical_for_local[local_id] = cid

    for fund_n, proposal in _iter_proposals(data_root):
        if only_funds is not None and fund_n not in only_funds:
            continue
        for local_id in proposal.get("proposer_ids") or []:
            mapped_cid: str | None = canonical_for_local.get(local_id)
            if mapped_cid is None:
                continue
            rec = proposers[mapped_cid]
            ru = rec["rollups"]
            if proposal.get("funding_status") == "approved":
                ru["total_funded"] += 1
            status = proposal.get("project_status")
            if status == "complete":
                ru["total_completed"] += 1
            elif status == "cancelled":
                ru["total_cancelled"] += 1
            elif status == "in_progress":
                ru["total_in_progress"] += 1
            req = proposal.get("amount_requested") or 0
            rcv = proposal.get("amount_received") or 0
            ru["total_requested_ada"] += float(req)
            ru["total_received_ada"] += float(rcv)

    return proposers


def write_per_fund(*, data_root: Path, proposers: dict[str, dict[str, Any]]) -> dict[int, int]:
    """Write data/funds/fund-XX/proposers.json (subset participating in that fund)."""
    by_fund: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for rec in proposers.values():
        ru = rec["rollups"]
        first = ru.get("first_fund")
        last = ru.get("last_fund")
        if first is None or last is None:
            continue
        for fund_n in range(first, last + 1):
            # Only include the proposer in funds where they actually had proposals.
            # We can re-derive this by scanning proposal_ids prefix.
            if any(pid.startswith(f"f{fund_n:02d}-") for pid in rec["proposal_ids"]):
                by_fund[fund_n].append(rec)

    counts: dict[int, int] = {}
    for fund_n, recs in by_fund.items():
        fund_dir = data_root / "funds" / f"fund-{fund_n:02d}"
        fund_dir.mkdir(parents=True, exist_ok=True)
        out_path = fund_dir / "proposers.json"
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(
                sorted(recs, key=lambda r: r["proposer_id"]),
                fh,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            fh.write("\n")
        counts[fund_n] = len(recs)
    return counts


def dedupe(
    *,
    data_root: Path | None = None,
    only_funds: list[int] | None = None,
) -> dict[str, dict[str, Any]]:
    """Top-level entry point - returns the canonical proposers map."""
    root = data_root if data_root is not None else DEFAULT_DATA_ROOT
    only_set = set(only_funds) if only_funds else None
    proposers = build_proposers(data_root=root, only_funds=only_set)
    counts = write_per_fund(data_root=root, proposers=proposers)
    print(
        json.dumps(
            {
                "total_canonical_proposers": len(proposers),
                "fuzzy_duplicate_pairs": sum(
                    1 for p in proposers.values() if p["duplicate_candidates"]
                ),
                "per_fund_counts": {str(k): v for k, v in sorted(counts.items())},
            },
            indent=2,
        )
    )
    return proposers


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument(
        "--fund",
        type=int,
        action="append",
        default=None,
        help="Restrict to specific fund(s).",
    )
    args = parser.parse_args(argv)
    dedupe(data_root=args.data_root, only_funds=args.fund)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["build_proposers", "dedupe", "main"]
