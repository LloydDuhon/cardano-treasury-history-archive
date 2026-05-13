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

## Current status (Phase 0)

Only the validator is implemented. All fetchers and normalizers are stubs that raise `NotImplementedError`. This is intentional — Phase 0 is scaffolding only; Phase 1+ implementations follow ADR-approved per-source plans.

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
