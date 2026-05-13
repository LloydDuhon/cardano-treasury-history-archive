"""Catalyst Milestone Module HTML scraper.

Source:        https://milestones.projectcatalyst.io/projects/{id}
               https://milestones.projectcatalyst.io/projects/{id}/milestones/{n}
Coverage:      F9 pilot (large projects), F10-F15 mandatory
API:           None published; HTML scrape only

Phase 3 work:
  1. Enumerate funded proposal IDs for F9-F15 from the Lidonation snapshot.
     Project IDs encode the fund as a leading prefix (e.g., 1300187 = F13).
  2. Fetch /projects/{id} and each /projects/{id}/milestones/{n}; gzip-cache
     HTML under ../data/funds/fund-XX/_provenance/milestones/.
  3. Parse with selectolax: extract milestone count, statuses, evidence URLs,
     reviewer signoffs, close-out URLs.
  4. Output an intermediate milestones.json per fund.

Concurrency:   Conservative - single connection, MILESTONES_RPS from .env.

Status: NOT IMPLEMENTED (Phase 3). This module is a typed stub.
"""

from __future__ import annotations

from pathlib import Path


def scrape_project_pages(*, output_root: Path, fund: int) -> None:
    """Scrape Milestone Module pages for every funded proposal in a fund.

    Args:
        output_root: Path to the repo's data/ directory.
        fund: Fund number (9-15 expected; raises for earlier funds).

    Raises:
        NotImplementedError: Phase 3 implementation pending.
        ValueError: If `fund` < 9 (Milestone Module did not exist).
    """
    if fund < 9:
        raise ValueError(f"Milestone Module did not cover Fund {fund}; use other sources.")
    raise NotImplementedError("Phase 3.")
