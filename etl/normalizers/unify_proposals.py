"""Unify per-fund proposal records across sources into the canonical schema.

Reads:   ../data/funds/fund-XX/_provenance/*/ (raw captures)
Writes:  ../data/funds/fund-XX/proposals.json + proposals.csv
         ../data/funds/fund-XX/proposers.json + proposers.csv
         ../data/funds/fund-XX/_meta.json

Status: NOT IMPLEMENTED (Phase 6). This module is a typed stub.
"""

from __future__ import annotations

from pathlib import Path


def unify_fund(*, data_root: Path, fund: int) -> None:
    """Produce canonical proposals.json/csv + proposers.json/csv for one fund.

    Args:
        data_root: Path to the repo's data/ directory.
        fund: Fund number.

    Raises:
        NotImplementedError: Phase 6 implementation pending.
    """
    raise NotImplementedError("Phase 6.")


def unify_all() -> None:
    """Run unification for every fund directory present under data/funds/."""
    raise NotImplementedError("Phase 6.")
