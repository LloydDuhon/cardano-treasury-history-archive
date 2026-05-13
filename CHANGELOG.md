# Changelog

All notable changes to this dataset and pipeline will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning uses date-based snapshot tags (`snapshot-YYYY-MM-DD`) for data releases
and SemVer for pipeline code.

## [Unreleased]

### Added (Phase 1 - Lidonation ingestion)
- `etl/fetchers/lidonation_api.py` - polite paginated fetcher for the
  Catalyst Explorer API. 1.5 rps default, exponential backoff, identifiable
  UA, atomic writes, gzip caching to `data/_raw/lidonation/page-NNNN.json.gz`.
  CLI: `python -m fetchers.lidonation_api [--max-pages N] [--start-page N]
  [--force] [--titles-only]`.
- `etl/normalizers/unify_proposals.py` - demultiplexes the flat-sweep raw
  cache into per-fund `data/funds/fund-XX/proposals.json` (schema-conformant)
  + `_meta.json` (sweep metadata).
- Test suite (14 tests): `etl/tests/` with respx-mocked HTTP, real fixture
  from the live API, schema-conformance assertion, idempotency check, retry
  policy check.
- `etl/requirements-dev.txt` - pytest 8.3, respx 0.21, mypy 1.13, ruff 0.6.
- `.github/workflows/tests.yml` - pytest + mypy (strict) jobs on PR.
- `etl/pytest.ini` - test discovery config.
- ADR-2026-05-13 "Implementation Notes" appendix documenting the live-API
  findings (broken fund filter, mixed-fund pages, central cache strategy).

### Added (Phase 0 - scaffolding)
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
