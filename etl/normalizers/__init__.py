"""Normalizers - convert raw provenance captures into the canonical schema.

Normalizers read from `../data/funds/fund-XX/_provenance/<source>/` and write
the validated `proposals.json` / `proposers.json` / `milestones.json` files
under the same fund directory.

Cross-source reconciliation produces `_reconciliation.json` flagging
disagreements between sources (e.g., Lidonation funding_status vs IOG PDF).

See ../docs/PER_FUND_SOURCES.md for the reconciliation policy.
"""
