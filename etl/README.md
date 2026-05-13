# etl/

Python pipeline that fetches Project Catalyst data from upstream sources, normalizes it into the canonical schema, validates it, and writes per-fund files under `../data/`.

This directory follows [`mellod-infra/docs/DEVELOPMENT_STANDARDS.md`](https://github.com/lloydduhon/mellod-infra/blob/main/docs/DEVELOPMENT_STANDARDS.md): Python N or N-1, `ruff` for lint/format/imports, pinned `requirements.txt`, type hints on public functions, `.env.example` indirection for secrets.

## Layout

```
etl/
├── pyproject.toml          # ruff + mypy configuration
├── requirements.txt        # pinned dependencies
├── .env.example            # environment template
├── README.md               # you are here
├── fetchers/               # fetch raw data from each upstream
│   ├── lidonation_api.py
│   ├── projectcatalyst_funds.py
│   ├── milestones_scraper.py
│   └── ideascale_wayback.py
├── normalizers/            # convert raw captures → canonical schema
│   ├── unify_proposals.py
│   └── reconcile_winners.py
└── validators/             # quality gates
    └── validate_against_schema.py
```

## Current status (Phase 1)

**Implemented:**

- `fetchers/lidonation_api.py` — Lidonation Catalyst Explorer API ingestion.
- `normalizers/unify_proposals.py` — per-fund demultiplex of the Lidonation cache.
- `validators/validate_against_schema.py` — JSON Schema gate.
- `tests/` — 14 unit tests (respx-mocked HTTP, fixture-driven normalizer checks).

**Still stubbed** (raise `NotImplementedError`):

- `fetchers/projectcatalyst_funds.py` (Phase 2)
- `fetchers/milestones_scraper.py` (Phase 3)
- `fetchers/ideascale_wayback.py` (Phase 4)
- `normalizers/reconcile_winners.py` (Phase 2)

## Setup

```bash
cd etl
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # then edit .env as needed
```

## Validate the dataset against schemas

The only thing you can run today:

```bash
python validators/validate_against_schema.py
```

It walks `../data/funds/*/proposals.json`, `../data/funds/*/proposers.json` (when present), and `../data/funds/*/milestones.json` (when present), validates each record against the matching schema, and exits non-zero on any failure.

## Phased implementation plan

See [`../docs/CATALYST-HISTORY-CAPTURE-PLAN.md`](../docs/CATALYST-HISTORY-CAPTURE-PLAN.md). At a glance:

| Phase | Component | What |
|---|---|---|
| 1 | `fetchers/lidonation_api.py` | Paginated `/api/proposals` ingestion for F2–F15 |
| 2 | `fetchers/projectcatalyst_funds.py` + PDF parsing | Authoritative winner cross-check |
| 3 | `fetchers/milestones_scraper.py` | F10–F15 milestone capture |
| 4 | `fetchers/ideascale_wayback.py` | F1 backfill from Internet Archive |
| 6 | `normalizers/*` | Cross-source merge into canonical files |

Each fetcher must:

- Identify itself with `HTTP_USER_AGENT` from `.env`
- Respect per-host rate limits from `.env`
- Snapshot raw responses to `../data/funds/fund-XX/_provenance/<source>/`
- Emit structured JSON logs to stdout (per DEVELOPMENT_STANDARDS § 3.1)
- Be idempotent — re-runs produce the same output for the same input
- Never delete prior captures

## Run the Phase 1 sweep

The smoke test (10 pages, ~10 seconds at 1.5 rps, ~240 proposals across ~8 funds):

```bash
cd etl
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m fetchers.lidonation_api --max-pages 10
python -m normalizers.unify_proposals
ls ../data/funds/
```

Full sweep (~6 minutes wall, all 475 pages, ~11,385 proposals):

```bash
python -m fetchers.lidonation_api
python -m normalizers.unify_proposals
```

Resume an interrupted sweep:

```bash
python -m fetchers.lidonation_api --start-page 312
```

Re-fetch a specific cached page (e.g., after upstream correction):

```bash
python -m fetchers.lidonation_api --start-page 47 --max-pages 1 --force
python -m normalizers.unify_proposals    # re-derive per-fund output
```

## Run the test suite

```bash
pip install -r requirements-dev.txt
python -m pytest
python -m mypy fetchers normalizers validators
```
