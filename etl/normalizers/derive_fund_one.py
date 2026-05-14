"""Parse archived IdeaScale snapshots into Fund 1 proposals.json.

Inputs (from etl/fetchers/ideascale_wayback.py):
    data/funds/fund-01/_provenance/ideascale_wayback/cdx.json.gz
    data/funds/fund-01/_provenance/ideascale_wayback/snapshots/*.html.gz

Output:
    data/funds/fund-01/proposals.json     (schema-conformant, confidence: low)
    data/funds/fund-01/_meta.json

F1 was the Catalyst pilot. No proposals received funding
(`numProposalsFunded: 0` per projectcatalyst.io). We record every recovered
proposal with `funding_status: "unknown"` (no vote was actually held) and
`confidence: low`. Fields that the archived HTML doesn't expose (votes,
amounts, scores) are left null.

CLI:
    python -m normalizers.derive_fund_one
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = REPO_ROOT / "data"

# IdeaScale URL pattern: /a/dtd/<idea_id>-<campaign_id>
_DTD_RE = re.compile(r"/a/dtd/(\d+)-(\d+)")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017


def _read_cdx(prov_dir: Path) -> list[dict[str, str]]:
    cdx_path = prov_dir / "cdx.json.gz"
    if not cdx_path.exists():
        return []
    with gzip.open(cdx_path, "rb") as fh:
        data = json.loads(fh.read())
    if not data:
        return []
    header, rows = data[0], data[1:]
    return [{header[i]: r[i] for i in range(min(len(header), len(r)))} for r in rows]


def _read_snapshot(path: Path) -> bytes:
    with gzip.open(path, "rb") as fh:
        return fh.read()


def _extract_dtd_ids(url: str) -> tuple[str | None, str | None]:
    """Pull (idea_id, campaign_id) from an IdeaScale /a/dtd/{idea}-{campaign} URL."""
    m = _DTD_RE.search(url or "")
    if not m:
        return None, None
    return m.group(1), m.group(2)


def parse_snapshot(html: bytes | str) -> dict[str, Any]:
    """Best-effort parse of an archived IdeaScale proposal page.

    Returns a dict with keys: `title`, `proposer_name`, `description`,
    `ask_text`. Missing fields are None. We're tolerant - the archived HTML
    may be partial, JS-only, or wrapped by Wayback. This parser is the
    contract; do not change the keys without updating callers.
    """
    if not html:
        return {"title": None, "proposer_name": None, "description": None, "ask_text": None}
    soup = BeautifulSoup(html, "html.parser")

    title = _first_text(
        soup.select_one("h1.idea-title"),
        soup.select_one("h1"),
        (soup.select_one("meta[property='og:title']"), "content"),
        soup.find("title"),
    )

    proposer_name = _first_text(
        soup.select_one(".idea-author .name"),
        soup.select_one(".author-name"),
        soup.select_one(".profile-name"),
        (soup.select_one("[data-author-name]"), "data-author-name"),
    )

    description = _first_text(
        soup.select_one(".idea-description"),
        soup.select_one("[itemprop='description']"),
        (soup.select_one("meta[name='description']"), "content"),
    )

    ask_text = _first_text(
        soup.select_one(".idea-funding"),
        soup.select_one(".budget"),
        (soup.select_one("[data-budget]"), "data-budget"),
    )

    return {
        "title": _clean(title),
        "proposer_name": _clean(proposer_name),
        "description": _clean(description),
        "ask_text": _clean(ask_text),
    }


def _first_text(*candidates: object) -> str | None:
    """Return the first non-empty text/attr value from a list of bs4 results.

    Each candidate is either a Tag (use .get_text()) or a 2-tuple
    (Tag, attr) which reads the named attribute. We accept positional
    args in either shape for compactness.
    """
    for c in candidates:
        if c is None:
            continue
        if isinstance(c, tuple) and len(c) == 2:
            tag, attr = c
            if tag is not None and hasattr(tag, "get"):
                val: Any = tag.get(attr)
                if val:
                    text: str = str(val).strip()
                    if text:
                        return text
            continue
        if hasattr(c, "get_text"):
            got: Any = c.get_text(strip=True)
            if got:
                return str(got)
    return None


def _clean(s: str | None) -> str | None:
    if not s:
        return None
    cleaned = " ".join(s.split())
    return cleaned or None


def _snapshot_paths(prov_dir: Path) -> Iterator[Path]:
    snap_dir = prov_dir / "snapshots"
    if not snap_dir.exists():
        return
    yield from sorted(snap_dir.glob("*.html.gz"))


def derive(*, data_root: Path | None = None) -> int:
    """Build data/funds/fund-01/proposals.json from cached Wayback snapshots.

    Returns the number of proposal records written.
    """
    root = data_root if data_root is not None else DEFAULT_DATA_ROOT
    prov = root / "funds" / "fund-01" / "_provenance" / "ideascale_wayback"
    if not prov.exists():
        raise FileNotFoundError(
            f"No Wayback cache at {prov}. Run " "`python -m fetchers.ideascale_wayback` first."
        )

    cdx_rows = _read_cdx(prov)
    by_urlkey: dict[str, dict[str, str]] = {r["urlkey"]: r for r in cdx_rows if "urlkey" in r}

    snapshot_at = _utcnow_iso()
    out: list[dict[str, Any]] = []
    seen_proposal_ids: set[str] = set()

    for snap_path in _snapshot_paths(prov):
        html = _read_snapshot(snap_path)
        parsed = parse_snapshot(html)

        # Recover the original URL from the matching CDX row by digest prefix
        # in the filename. snapshot filename pattern: <16hexhash>-<safekey>.html.gz
        prefix = snap_path.name.split("-", 1)[0]
        cdx_row: dict[str, str] | None = None
        for row in cdx_rows:
            urlkey = row.get("urlkey", "")
            if (
                urlkey
                and urlkey.startswith(("com,", "org,", ""))
                and _digest_for_urlkey(urlkey) == prefix
            ):
                cdx_row = row
                break
        original = (cdx_row or {}).get("original", "")
        timestamp = (cdx_row or {}).get("timestamp", "")
        idea_id, campaign_id = _extract_dtd_ids(original)

        # Mint proposal_id. Slugify title if present; otherwise fall back to idea_id.
        title = parsed["title"] or f"untitled-{idea_id or 'unknown'}"
        slug = slugify(title)[:80] or (idea_id or "unknown")
        proposal_id = f"f01-{slug}"
        if proposal_id in seen_proposal_ids:
            # rare collision; suffix with idea_id
            proposal_id = f"{proposal_id}-{idea_id or 'x'}"
        seen_proposal_ids.add(proposal_id)

        record: dict[str, Any] = {
            "proposal_id": proposal_id,
            "external_ids": {k: v for k, v in {"ideascale_id": idea_id}.items() if v is not None},
            "fund": 1,
            "title": parsed["title"] or title,
            "slug": slug or None,
            "challenge": campaign_id,  # F1 campaigns are not named in the archive
            "campaign_id": campaign_id,
            "proposer_ids": [
                f"p-ideascale-wayback-f01-{slugify(parsed['proposer_name'])}-{idea_id or 'x'}"
                if parsed["proposer_name"]
                else f"p-ideascale-wayback-f01-anonymous-{idea_id or 'x'}"
            ],
            "amount_requested": None,
            "amount_received": 0,
            "currency": "UNKNOWN",
            "yes_votes": None,
            "no_votes": None,
            "abstain_votes": None,
            "scores": None,
            "ranking_total": None,
            "funding_status": "unknown",
            "project_status": "unfunded",
            "funded_at": None,
            "completed_at": None,
            "links": {
                "lidonation_url": None,
                "ideascale_url": original or None,
                "projectcatalyst_io_url": None,
                "milestones_url": None,
                "catalyst_voices_url": None,
                "proposer_website": None,
                "github_repo": None,
            },
            "summary": parsed["description"],
            "problem": None,
            "solution": None,
            "definition_of_success": None,
            "ai_summary": None,
            "milestone_count": None,
            "tags": [],
            "is_opensource": None,
            "sources": [
                {
                    "source": "ideascale_wayback",
                    "url": (
                        f"https://web.archive.org/web/{timestamp}/{original}"
                        if timestamp and original
                        else None
                    ),
                    "fetched_at": snapshot_at,
                    "provenance_path": (
                        f"data/funds/fund-01/_provenance/ideascale_wayback/"
                        f"snapshots/{snap_path.name}"
                    ),
                    "fields_provided": [
                        k
                        for k in ("title", "summary")
                        if parsed.get(k) or parsed.get("description")
                    ],
                }
            ],
            "confidence": "low",
            "field_confidence": None,
            "notes": (
                "Fund 1 pilot. No formal voting took place; funding_status "
                "recorded as 'unknown'. Title and proposer recovered from "
                "Internet Archive snapshot; expect imperfect coverage."
            ),
        }
        out.append(record)

    out.sort(key=lambda r: r["proposal_id"])

    fund_dir = root / "funds" / "fund-01"
    fund_dir.mkdir(parents=True, exist_ok=True)
    proposals_path = fund_dir / "proposals.json"
    with proposals_path.open("w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")

    meta = {
        "fund": 1,
        "normalized_at": snapshot_at,
        "record_count": len(out),
        "sources_used": ["ideascale_wayback"],
        "phase": "phase-4",
        "phase_notes": (
            "Fund 1 was the Catalyst pilot. No formal voting outcome existed; "
            "funding_status is 'unknown' for every record. Titles and proposers "
            "are best-effort recovery from Internet Archive snapshots. Records "
            "carry confidence: low. There is no canonical complete list - expect "
            "10-20% records to be missing or have incomplete fields."
        ),
        "coverage_warnings": [
            "Vote counts and ask amounts are usually null (not in archived HTML).",
            "Proposer name may be 'anonymous' when the archived page hid it.",
            "Description may include Wayback Machine UI fragments if snapshot is wrapped.",
        ],
    }
    meta_path = fund_dir / "_meta.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        json.dumps(
            {
                "fund": 1,
                "records": len(out),
                "snapshots_seen": len(list(_snapshot_paths(prov))),
                "cdx_rows_known": len(by_urlkey),
            },
            indent=2,
        )
    )
    return len(out)


def _digest_for_urlkey(urlkey: str) -> str:
    """Match the same digest scheme used by the fetcher when naming files."""
    import hashlib

    return hashlib.sha1(urlkey.encode("utf-8"), usedforsecurity=False).hexdigest()[:16]


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=None, help="Override data/ directory.")
    args = parser.parse_args(argv)
    derive(data_root=args.data_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["derive", "main", "parse_snapshot"]
