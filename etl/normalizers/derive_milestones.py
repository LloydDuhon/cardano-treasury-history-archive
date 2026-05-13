"""Derive per-fund milestones.json from cached Milestone-Module Supabase data.

Inputs (from etl/fetchers/milestones_scraper.py):
    data/funds/fund-XX/_provenance/milestones_supabase/{funds,challenges,
        proposals,soms,poas,signoffs}.json.gz

Output:
    data/funds/fund-XX/milestones.json   (schema-conformant)

Rules:
  - Only `soms.current=true` rows enter the normalized output.
  - Per-milestone status is derived from PoA + signoff state.
  - PoA `content` is captured verbatim; embedded URLs are extracted into
    the milestone's `evidence[]` array.
  - The final milestone (highest `milestone` integer per proposal) is
    flagged `is_closeout=true`.

CLI:
    python -m normalizers.derive_milestones --fund 9
    python -m normalizers.derive_milestones                  # all available
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

# Milestone Module's Supabase fund_id -> real fund number.
SUPABASE_TO_FUND: dict[int, int] = {1: 9, 2: 10, 3: 11, 4: 12, 5: 13, 6: 14}

_URL_RE = re.compile(
    r"""(?:https?://[^\s<>"']+)|(?:www\.[^\s<>"']+)""",
    re.IGNORECASE,
)
_TRAILING_PUNCT = ".,;:!?)]}\"'"


def _utcnow_iso() -> str:
    # 3.10-compatible (timezone.utc rather than datetime.UTC alias).
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _read_table(prov_dir: Path, table: str) -> list[dict[str, Any]]:
    path = prov_dir / f"{table}.json.gz"
    if not path.exists():
        return []
    with gzip.open(path, "rb") as fh:
        data: list[dict[str, Any]] = json.loads(fh.read())
    return data


def _extract_urls(text: str | None) -> list[str]:
    """Return distinct URLs found in a markdown/plain blob."""
    if not text:
        return []
    seen: dict[str, None] = {}
    for m in _URL_RE.findall(text):
        url = m.rstrip(_TRAILING_PUNCT)
        if not url.lower().startswith(("http://", "https://")):
            url = "https://" + url.lstrip("/")
        if url not in seen:
            seen[url] = None
    return list(seen)


def _kind_for_url(url: str) -> str:
    """Best-effort classification for evidence URLs."""
    lower = url.lower()
    if "github.com" in lower:
        return "github_pr" if "/pull/" in lower or "/pr/" in lower else "github_repo"
    if lower.endswith(".pdf"):
        return "pdf"
    if any(host in lower for host in ("youtube.com", "youtu.be", "vimeo.com")):
        return "video"
    if "drive.google.com" in lower or "docs.google.com" in lower:
        return "demo"
    if "/blog/" in lower or lower.endswith((".md", ".rst")):
        return "blog_post"
    if lower.startswith("https://") and "/" not in lower[8:].rstrip("/"):
        return "website"
    return "other"


def _slug_from_proposal_url(url: str | None, fallback: str) -> str:
    if not url:
        return slugify(fallback) or "unknown"
    parts = [p for p in url.rstrip("/").split("/") if p]
    return slugify(parts[-1] if parts else fallback) or "unknown"


def _derive_status(
    som_id: int,
    poas_by_som: dict[int, list[dict[str, Any]]],
    signoffs_by_som: dict[int, list[dict[str, Any]]],
) -> str:
    """Map (PoA, signoff) state to the schema's milestone status enum."""
    has_signoff = bool(signoffs_by_som.get(som_id))
    current_poas = [p for p in poas_by_som.get(som_id, []) if p.get("current")]
    active_reviews = sum(int(p.get("active_reviews") or 0) for p in current_poas)
    if has_signoff:
        return "accepted"
    if active_reviews > 0:
        return "under_review"
    if current_poas:
        return "submitted"
    return "not_started"


def _normalize_currency(raw: str | None) -> str:
    if not raw:
        return "UNKNOWN"
    u = raw.strip().upper()
    return u if u in {"ADA", "USD", "USDM"} else "UNKNOWN"


def derive_fund(
    *,
    data_root: Path,
    fund: int,
) -> int:
    """Build data/funds/fund-XX/milestones.json from cached Supabase data.

    Returns the number of milestone records written.
    """
    prov = data_root / "funds" / f"fund-{fund:02d}" / "_provenance" / "milestones_supabase"
    if not prov.exists():
        raise FileNotFoundError(
            f"No Supabase cache for fund {fund} at {prov}. "
            f"Run `python -m fetchers.milestones_scraper --fund {fund}` first."
        )

    proposals = _read_table(prov, "proposals")
    soms = _read_table(prov, "soms")
    poas = _read_table(prov, "poas")
    signoffs = _read_table(prov, "signoffs")

    if not proposals:
        return 0

    proposals_by_id: dict[int, dict[str, Any]] = {p["id"]: p for p in proposals}

    # Group SoMs by proposal (current only)
    soms_by_proposal: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for s in soms:
        if s.get("current"):
            soms_by_proposal[s["proposal_id"]].append(s)

    # PoAs grouped by som_id
    poas_by_som: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for p in poas:
        som_id = p.get("som_id")
        if som_id is not None:
            poas_by_som[som_id].append(p)

    signoffs_by_som: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for so in signoffs:
        som_id = so.get("som_id")
        if som_id is not None:
            signoffs_by_som[som_id].append(so)

    snapshot_at = _utcnow_iso()
    out_records: list[dict[str, Any]] = []

    for proposal_id, current_soms in sorted(soms_by_proposal.items()):
        proposal = proposals_by_id.get(proposal_id)
        if proposal is None:
            continue
        slug = _slug_from_proposal_url(proposal.get("url"), proposal.get("title") or "p")
        canonical_proposal_id = f"f{fund:02d}-{slug}"
        currency = _normalize_currency(proposal.get("currency"))
        ordered = sorted(current_soms, key=lambda s: int(s.get("milestone") or 0))
        if not ordered:
            continue
        max_milestone = max(int(s.get("milestone") or 0) for s in ordered)

        for som in ordered:
            milestone_n = int(som.get("milestone") or 0)
            if milestone_n <= 0:
                continue
            som_id = som["id"]
            status = _derive_status(som_id, poas_by_som, signoffs_by_som)

            # Evidence: aggregate URLs found in PoA content (current PoAs only).
            evidence: list[dict[str, Any]] = []
            for poa in poas_by_som.get(som_id, []):
                if not poa.get("current"):
                    continue
                for url in _extract_urls(poa.get("content")):
                    evidence.append({"url": url, "kind": _kind_for_url(url), "description": None})

            delivered_at: str | None = None
            sos = signoffs_by_som.get(som_id) or []
            if sos:
                # Use the most recent signoff's created_at.
                latest = max(sos, key=lambda x: x.get("created_at") or "")
                delivered_at = latest.get("created_at")

            record: dict[str, Any] = {
                "milestone_id": f"{canonical_proposal_id}-m{milestone_n:02d}",
                "proposal_id": canonical_proposal_id,
                "external_ids": {
                    "milestones_projectcatalyst_io_id": str(proposal.get("project_id") or "")
                    or None,
                    "lidonation_schedule_id": None,
                },
                "milestone_number": milestone_n,
                "title": som.get("title"),
                "description": som.get("outputs"),
                "budget": som.get("cost"),
                "currency": currency,
                "delivery_target_date": None,
                "delivered_at": delivered_at,
                "status": status,
                "acceptance_criteria": som.get("success_criteria"),
                "is_closeout": milestone_n == max_milestone,
                "evidence": evidence,
                "reviewer_signoffs": [
                    {
                        "reviewer_id": (so.get("user_id") or "")[:60] or None,
                        "decision": "accepted",
                        "decided_at": so.get("created_at"),
                        "comment": None,
                    }
                    for so in sos
                ],
                "closeout_report_url": None,
                "closeout_video_url": None,
                "sources": [
                    {
                        "source": "milestones_projectcatalyst_io",
                        "url": (
                            f"https://milestones.projectcatalyst.io/projects/"
                            f"{proposal.get('project_id', '')}"
                            f"/milestones/{milestone_n}"
                        ),
                        "fetched_at": snapshot_at,
                        "provenance_path": (
                            f"data/funds/fund-{fund:02d}/_provenance/"
                            f"milestones_supabase/soms.json.gz"
                        ),
                    }
                ],
                "confidence": "high",
                "notes": None,
            }

            # If this is the closeout and any evidence URL looks like a video,
            # capture it as the closeout_video_url for convenience.
            if record["is_closeout"]:
                for e in evidence:
                    if e["kind"] == "video" and record["closeout_video_url"] is None:
                        record["closeout_video_url"] = e["url"]
                    if e["kind"] == "pdf" and record["closeout_report_url"] is None:
                        record["closeout_report_url"] = e["url"]

            out_records.append(record)

    out_records.sort(key=lambda r: (r["proposal_id"], r["milestone_number"]))

    out_path = data_root / "funds" / f"fund-{fund:02d}" / "milestones.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(out_records, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")

    print(
        json.dumps(
            {
                "fund": fund,
                "milestone_count": len(out_records),
                "proposals_with_milestones": len(soms_by_proposal),
                "written": str(out_path.relative_to(data_root.parent))
                if data_root.parent in out_path.parents
                else str(out_path),
            },
            indent=2,
        )
    )
    return len(out_records)


def derive_all(*, data_root: Path) -> dict[int, int]:
    """Run derivation for every fund with a Supabase cache."""
    out: dict[int, int] = {}
    funds_dir = data_root / "funds"
    if not funds_dir.exists():
        return out
    for fund_dir in sorted(funds_dir.iterdir()):
        if not fund_dir.is_dir() or not fund_dir.name.startswith("fund-"):
            continue
        try:
            fund_n = int(fund_dir.name.split("-", 1)[1])
        except (IndexError, ValueError):
            continue
        prov = fund_dir / "_provenance" / "milestones_supabase"
        if not prov.exists():
            continue
        out[fund_n] = derive_fund(data_root=data_root, fund=fund_n)
    return out


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None, help="Override data/ directory.")
    parser.add_argument(
        "--fund",
        type=int,
        action="append",
        default=None,
        help="Fund(s) to derive (9-14). Default: every fund with a cache.",
    )
    args = parser.parse_args(argv)
    root = args.data_root if args.data_root is not None else DEFAULT_DATA_ROOT
    if args.fund:
        for n in args.fund:
            derive_fund(data_root=root, fund=n)
    else:
        derive_all(data_root=root)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["derive_all", "derive_fund", "main", "SUPABASE_TO_FUND"]
