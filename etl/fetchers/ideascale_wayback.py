"""IdeaScale / Wayback Machine fetcher for Fund 1 backfill.

Source:        https://web.archive.org/cdx/search/cdx?url=cardano.ideascale.com/*
Coverage:      Fund 1 (pilot, ~56 proposals - no funded winners)
               Optionally F2-F9 for cross-verification only

Phase 4 work:
  1. Query Wayback CDX for all snapshots of cardano.ideascale.com proposal
     pages in the Fund 1 window (Sept-Dec 2020).
  2. Deduplicate to one canonical snapshot per proposal URL.
  3. Fetch each archived HTML page; preserve under
     ../data/funds/fund-01/_provenance/ideascale-wayback/.
  4. Parse with BeautifulSoup to extract title, proposer, ask amount,
     description; emit intermediate JSON.

Rate limit:    Wayback is rate-sensitive - WAYBACK_RPS=0.5 by default.
               Expect partial coverage; some proposals may have no snapshot.

Status: NOT IMPLEMENTED (Phase 4 - 'heroic'). This module is a typed stub.
"""

from __future__ import annotations

from pathlib import Path


def fetch_fund_one_snapshots(*, output_root: Path) -> None:
    """Recover Fund 1 proposal pages from the Internet Archive.

    Args:
        output_root: Path to the repo's data/ directory.

    Raises:
        NotImplementedError: Phase 4 implementation pending.
    """
    raise NotImplementedError("Phase 4 - heroic; fragile by design.")
