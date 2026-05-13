# etl/

Python pipeline that fetches Project Catalyst data from upstream sources, normalizes it into the canonical schema, validates it, and writes per-fund files under `../data/`.

This directory follows [`mellod-infra/docs/DEVELOPMENT_STANDARDS.md`](https://github.com/lloydduhon/mellod-infra/blob/main/docs/DEVELOPMENT_STANDARDS.md): Python N or N-1, `ruff` for lint/format/imports, pinned `requirements.txt`, type hints on public functions, `.env.example` indirection for secrets.

## Layout

```
etl/
├── pyproject.toml          # ruff + mypy configuration
├── requirements.txt        # pinned runtime dependencies
├── requirements-dev.txt    # pytest, respx, mypy, ruff
├── .env.example            # environment template
├── pytest.ini              # test discovery config
├── README.md               # you are here
├── fetchers/               # fetch raw data from each upstream
│   ├── lidonation_api.py
│   ├── projectcatalyst_funds.py
│   ├── milestones_scraper.py   (stub, Phase 3)
│   └── ideascale_wayback.py    (stub, Phase 4)
├── parsers/                # convert third-party formats to structured rows
│   └── iohk_pdf.py
├── normalizers/            # canonical schema producers
│   ├── unify_proposals.py
│   └── reconcile_winners.py
├── validators/             # quality gates
│   └── validate_against_schema.py
└── tests/                  # 33 tests across all of the above
    ├── conftest.py
    ├── fixtures/
    ├── test_lidonation_api.py
    ├── test_unify_proposals.py
    ├── test_projectcatalyst_funds.py
    ├── test_iohk_pdf_parser.py
    └── test_reconcile_winners.py
```

## Current status (Phase 2)

**Implemented:**

- `fetchers/lidonation_api.py` — Lidonation Catalyst Explorer API ingestion (Phase 1).
- `fetchers/projectcatalyst_funds.py` — projectcatalyst.io HTML + IOG voting-results PDF fetcher (Phase 2).
- `parsers/iohk_pdf.py` — pdfplumber-based voting-results PDF parser (Phase 2).
- `normalizers/unify_proposals.py` — per-fund demultiplex of the Lidonation cache (Phase 1).
- `normalizers/reconcile_winners.py` — diff-only sidecar against IOG PDFs (Phase 2).
- `validators/validate_against_schema.py` — JSON Schema gate over proposals, proposers, milestones, and `_reconciliation` files.
- `tests/` — 33 unit tests.

**Still stubbed** (raise `NotImplementedError`):

- `fetchers/milestones_scraper.py` (Phase 3)
- `fetchers/ideascale_wayback.py` (Phase 4)

## Setup

```bash
cd etl
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # then edit .env as needed
```

## Phased implementation plan

See [`../docs/CATALYST-HISTORY-CAPTURE-PLAN.md`](../docs/CATALYST-HISTORY-CAPTURE-PLAN.md). At a glance:

| Phase | Component | What |
|---|---|---|
| 1 | `fetchers/lidonation_api.py` + `normalizers/unify_proposals.py` | Paginated `/api/proposals` ingestion for F2–F15 |
| 2 | `fetchers/projectcatalyst_funds.py` + `parsers/iohk_pdf.py` + `normalizers/reconcile_winners.py` | Cross-verify winners against IOG PDFs |
| 3 | `fetchers/milestones_scraper.py` | F10–F15 milestone capture |
| 4 | `fetchers/ideascale_wayback.py` | F1 backfill from Internet Archive |
| 6 | `normalizers/*` | Apply reconciliations into canonical files; emit consolidated CSVs |

## Conventions every fetcher must honor

- Identify itself with `HTTP_USER_AGENT` from `.env`.
- Respect per-host rate limits from `.env`.
- Snapshot raw responses to `../data/_raw/<source>/` (centralized) or `../data/funds/fund-XX/_provenance/<source>/` (per-fund where the upstream supports fund scoping).
- Emit structured JSON logs to stdout (per `mellod-infra` DEVELOPMENT_STANDARDS § 3.1).
- Be idempotent — re-runs produce the same output for the same input.
- Never delete prior captures.

## Validate the dataset against schemas

```bash
python validators/validate_against_schema.py
```

Walks `../data/funds/*/{proposals,proposers,milestones,_reconciliation}.json` and validates every record. Exits non-zero on any failure. Always-on; safe with an empty dataset.

## Run the Phase 1 sweep

Smoke test (10 pages, ~10 seconds at 1.5 rps, ~240 proposals across ~8 funds):

```bash
cd etl
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

## Run the Phase 2 cross-check

Smoke against Fund 2 (downloads ~1.8 MB PDF, ~10 seconds total):

```bash
cd etl
python -m fetchers.projectcatalyst_funds --fund 2
# Parse the PDF into _intermediate/iohk_winners.json:
python -c "
from pathlib import Path
from datetime import datetime, timezone
from parsers.iohk_pdf import parse_voting_results_pdf, write_intermediate
rows, summary = parse_voting_results_pdf(Path('../data/_raw/iohk-pdfs/fund-02.pdf'))
write_intermediate(
    rows, summary,
    fund=2,
    data_root=Path('../data'),
    source_url='https://static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf',
    pdf_relpath='data/_raw/iohk-pdfs/fund-02.pdf',
    parsed_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
)
"
python -m normalizers.reconcile_winners --fund 2
cat ../data/funds/fund-02/_reconciliation.json
```

Full Phase 2 sweep (F2–F13, ~15 minutes wall once the parser is wired to a CLI runner):

```bash
python -m fetchers.projectcatalyst_funds        # downloads all PDFs + summaries
# Per-fund parse + reconcile (loop the one-liner above per fund), then:
python -m normalizers.reconcile_winners         # any fund with both inputs
```

A first-class `python -m parsers.iohk_pdf <fund>` CLI runner is a deliberate follow-up (see `docs/PR_NOTES_PHASE2.md`).

## Run the test suite

```bash
pip install -r requirements-dev.txt
python -m pytest                                    # 33 passed
python -m mypy fetchers normalizers parsers validators
```
