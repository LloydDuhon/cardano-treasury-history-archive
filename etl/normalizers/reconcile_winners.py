"""Cross-check Lidonation funding_status against IOG voting-results PDFs.

For each fund where both sources exist, emit a per-fund _reconciliation.json
listing proposals whose `funding_status` differs between the two sources.

Policy (from ../docs/PER_FUND_SOURCES.md):
  - On disagreement, the IOG/CF artifact wins.
  - The Lidonation value is preserved in the proposal's `notes` field.
  - All reconciliation outcomes are reviewed by the maintainer before being
    applied to the canonical dataset.

Status: NOT IMPLEMENTED (Phase 2). This module is a typed stub.
"""

from __future__ import annotations

from pathlib import Path


def reconcile_fund(*, data_root: Path, fund: int) -> None:
    """Compare Lidonation vs IOG winners for one fund; emit _reconciliation.json."""
    raise NotImplementedError("Phase 2.")
