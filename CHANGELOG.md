# Changelog

All notable changes to this dataset and pipeline will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning uses date-based snapshot tags (`snapshot-YYYY-MM-DD`) for data releases
and SemVer for pipeline code.

## [Unreleased]

### Added (TF2 static viewer)
- `site/` - static Treasury Fund 2 history explorer with graph, ledger, flow,
  proposal detail, and proposer detail views over the current archive data.
- `etl/scripts/generate_treasury_dashboard_data.py` - regenerates
  `site/data.js` and `site/data.json` from the Hydra Voting snapshot and TF2
  report CSVs.
- `.github/workflows/pages.yml` - publishes `site/` to GitHub Pages.

### Added (TF2 figures)
- `etl/scripts/generate_treasury_fund_figures.py` - reproducible figure
  generator for the Treasury Fund 2 proposer-history reports. Writes four
  PNGs, a self-contained HTML dashboard, and an underlying
  `figures-data.csv` to `reports/treasury-fund-2/figures/`. Initial
  audience: Cardano Budget Committee at Intersect; intended to circulate
  to the broader Cardano audience after approval.
- `reports/treasury-fund-2/figures/README.md` - methodology, sources,
  caveats, and "known issues" log (notably the MLabs LTD / MLabsLTD
  entity-resolution duplicate, which is merged at the display layer
  only).
- Pinned `matplotlib==3.10.8` for the figure generator.

### Changed (Interim 2026-05-15)
- Migrated the Lidonation fetcher from the legacy `/api/*` surface to the
  documented `/api/v1/*` API after the Catalyst Explorer maintainer pointed us
  at the current docs. The interim sweep now covers F2-F15 with 11,528 proposal
  records and zero no-fund skips.
- Added v1 `team` proposer normalization and proposal-ID collision preservation
  for duplicate slugs.
- Added Google Drive confirm-link/form handling to the voting-results downloader.
  Several historical artifacts remain permission blocked, so the final IOG/CF
  reconciliation is tracked separately in `docs/IOG_RESULTS_ACCESS_TRACKER.md`.
- Chunked Milestone Module Supabase `signoffs` fetches to avoid oversized
  `in.(...)` filters.
- Current validation gate: 86 tests, mypy clean, ruff clean, schema validation
  clean for the interim generated snapshot.

### Added (Docs)
- `docs/IOG_RESULTS_ACCESS_TRACKER.md` documents the missing IOG/CF artifacts,
  their source URLs, expected local filenames, and remaining parser work.

### Added (Phase 6 - Cross-source consolidation)
- `etl/normalizers/apply_reconciliations.py` - idempotent applier of
  per-fund `_reconciliation.json` into canonical `proposals.json`.
  Per ADR-2026-05-13: when verdict=secondary_wins, funding_status is
  updated to the IOG-PDF value, the original Lidonation value is
  preserved verbatim in `notes`, and a new `sources[]` entry with
  source=`iohk_voting_results_pdf` and fields_provided=["funding_status"]
  records the override. Re-runs are no-ops.
- `etl/normalizers/dedupe_proposers.py` - cross-fund proposer dedupe.
  Exact-ID merge on `lidonation_profile_uuid` collapses references
  across funds; fuzzy display-name matches populate
  `duplicate_candidates[]` mutually on both records (never silent
  merge). Walks raw Lidonation cache to recover display names. Emits
  per-fund `proposers.json` matching the proposer schema.
- `etl/normalizers/consolidate.py` - emits `data/consolidated/`:
  `all_proposals.{csv,json}`, `all_proposers.{csv,json}`,
  `all_milestones.{csv,json}`, plus an auto-generated `schema.md`
  describing CSV columns. CSV is intentionally narrow (~25 columns);
  full schema fidelity preserved in JSON.
- 17 new tests across 3 modules; suite total 84.
- Pinned: pandas 2.2.3 (transitive numpy 2.1.3).

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
- GitHub Actions monthly refresh workflow (Phase 7).
- Final IOG/CF voting-results reconciliation for F3-F13 pending source access
  and parser support.
