"""Fetchers - pull raw data from upstream Catalyst sources.

Every fetcher must:
  - Identify itself via HTTP_USER_AGENT from .env.
  - Respect per-host rate limits from .env.
  - Snapshot raw responses under ../data/funds/fund-XX/_provenance/<source>/.
  - Emit structured JSON logs to stdout.
  - Be idempotent (re-runs produce the same provenance for the same input).
  - Never delete prior captures.

See ../docs/CATALYST-HISTORY-CAPTURE-PLAN.md for the per-phase implementation
plan and ../docs/adr/ADR-2026-05-13-source-strategy.md for the source-selection
decision record.
"""
