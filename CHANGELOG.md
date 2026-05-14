# Changelog

All notable changes to this dataset and pipeline will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning uses date-based snapshot tags (`snapshot-YYYY-MM-DD`) for data releases
and SemVer for pipeline code.

## [Unreleased]

### Added (Phase 4 - Fund 1 Wayback recovery)
- `etl/fetchers/ideascale_wayback.py` - REWRITTEN. Two-stage fetcher:
  Wayback CDX query for `cardano.ideascale.com/a/dtd/*` in the F1
  window (Sept 2020 - Jan 2021), then per-URL snapshot download via
  `web.archive.org/web/<ts>id_/<url>`. Conservative 0.5 rps, big
  backoff on 429, identifiable UA. Cache under
  `data/funds/fund-01/_provenance/ideascale_wayback/`.
- `etl/normalizers/derive_fund_one.py` - BeautifulSoup4 parser for
  archived IdeaScale HTML. Recovers title / proposer / description /
  ask. Emits `data/funds/fund-01/proposals.json` matching
  `proposal.schema.json` with `funding_status: "unknown"` (F1 was the
  pilot, no formal voting occurred), `project_status: "unfunded"`,
  `confidence: "low"`.
- Test fixtures: handcrafted CDX response + rich/bare HTML samples.
- 16 new tests across `test_ideascale_wayback.py` and
  `test_derive_fund_one.py`; suite total now 67.
- `beautifulsoup4 4.12.3` + `soupsieve 2.6` pinned.

### Added (Phase 3 - Milestone Module Supabase ingestion)
- `etl/fetchers/milestones_scraper.py` - REWRITTEN. The Milestone Module
  is a Vite SPA backed by Supabase, not an HTML site; the SPA's public
  anon key is exposed in `/env.js`. We query Supabase REST directly
  against tables: funds, challenges, proposals, soms, poas, signoffs.
  No headless-browser / HTML scrape dep. Covers Funds 9-14
  (1,146 funded proposals at survey time).
- `etl/normalizers/derive_milestones.py` - reads the cached Supabase
  tables, filters `soms.current=true` for the normalized output (raw
  cache keeps all revisions), derives per-milestone `status` from
  PoA + signoff state, extracts evidence URLs from PoA markdown
  content, flags the final milestone as `is_closeout`. Writes
  `data/funds/fund-XX/milestones.json` matching
  `schemas/milestone.schema.json`.
- Test fixtures: trimmed real F9 Supabase responses for 2 proposals
  (~70 KB total across 6 tables).
- 18 new tests across `test_milestones_supabase.py` and
  `test_derive_milestones.py`; suite total now 51.
- ADR-2026-05-13 Implementation Notes appendix extended to record
  the Supabase-backed nature of the Milestone Module.

### Added (Phase 2 - IOG voting-results cross-check)
- `etl/parsers/iohk_pdf.py` - pdfplumber-based parser for the canonical
  IOG voting-results PDFs. Validated against Fund 2 (78 rows / 11 funded).
- `etl/fetchers/projectcatalyst_funds.py` - HTML scrape of /funds/N for
  the embedded `__NEXT_DATA__` JSON + PDF downloader handling
  static.iohk.io / Google Drive / inline patterns.
- `etl/normalizers/reconcile_winners.py` - diff-only sidecar that writes
  `data/funds/fund-XX/_reconciliation.json` listing per-record
  disagreements, unmatched primary, unmatched secondary. Never modifies
  `proposals.json` (corrections deferred to Phase 6).
- `schemas/reconciliation.schema.json` - canonical schema for the diff
  record. Now validated by `validate_against_schema.py`.
- Test fixtures: `etl/tests/fixtures/funds-2.html.gz` (45 KB) and
  `etl/tests/fixtures/iohk-pdfs/fund-02.pdf` (1.8 MB).
- 13 new tests across 3 modules; total suite now 33 tests.
- `pdfplumber 0.11.4` and `pypdf 5.0.1` pinned in `requirements.txt`.

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
