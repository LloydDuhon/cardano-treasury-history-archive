"""Lidonation Catalyst Explorer API fetcher.

Source:        https://www.catalystexplorer.com/api/*
Coverage:      Funds 2-15 (~11,385 proposals at survey time, paginated 24/page)
Auth:          None required
Rate limit:    Unpublished; we self-throttle via LIDONATION_RPS in .env

Endpoints we plan to consume in Phase 1:
  GET /api/proposals?p={page}                    - paginated proposals list
  GET /api/fund-titles                           - fund taxonomy
  GET /api/campaigns                             - challenge/campaign taxonomy
  GET /api/ideascale-profiles                    - proposer profile data
  GET /api/catalyst-profiles                     - Catalyst Voices proposer data
  GET /api/groups                                - proposer team groupings
  GET /api/tags                                  - proposal tags

Provenance:
  Raw paginated responses are gzipped and written to
  ../data/funds/fund-XX/_provenance/lidonation/page-{NNN}.json.gz

Status: NOT IMPLEMENTED (Phase 1). This module is a typed stub.
"""

from __future__ import annotations

from pathlib import Path


def fetch_all_proposals(*, output_root: Path) -> None:
    """Fetch every proposal across every fund from the Lidonation API.

    Args:
        output_root: Path to the repo's data/ directory.

    Raises:
        NotImplementedError: Phase 1 implementation pending.
    """
    raise NotImplementedError(
        "Phase 1 - implement after ADR sign-off and Lidonation rate-limit confirmation."
    )


def fetch_fund_titles(*, output_root: Path) -> None:
    """Fetch the canonical fund taxonomy from /api/fund-titles."""
    raise NotImplementedError("Phase 1.")


def fetch_campaigns(*, output_root: Path) -> None:
    """Fetch challenge/campaign taxonomy from /api/campaigns."""
    raise NotImplementedError("Phase 1.")
