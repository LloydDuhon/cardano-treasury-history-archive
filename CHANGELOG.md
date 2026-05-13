# Changelog

All notable changes to this dataset and pipeline will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning uses date-based snapshot tags (`snapshot-YYYY-MM-DD`) for data releases
and SemVer for pipeline code.

## [Unreleased]

### Added
- Phase 0 scaffolding: repo structure, dual license (MIT code / CC-BY-4.0 data),
  JSON Schemas for `proposal`, `proposer`, `milestone`, ADR-2026-05-13 documenting
  the multi-source capture strategy, ETL skeleton per `mellod-infra`
  `DEVELOPMENT_STANDARDS.md` (ruff, type hints, pinned deps, `.env.example`).
- `docs/CATALYST-HISTORY-CAPTURE-PLAN.md` — six-phase capture plan.
- `docs/PER_FUND_SOURCES.md` — per-fund decision matrix.
- `docs/DATA_QUALITY.md` — confidence-tier narrative.
- `docs/attributions.md` — upstream source attribution.
- `validate_against_schema.py` — working JSON Schema validator (the only
  ETL component implemented in Phase 0).

### Not yet implemented
- Fetchers (Phase 1+).
- Normalizers (Phase 6).
- GitHub Actions monthly refresh workflow (Phase 7).
- Any captured data under `data/`.
