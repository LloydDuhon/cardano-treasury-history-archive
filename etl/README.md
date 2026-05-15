# etl/

Python pipeline that fetches Project Catalyst data from upstream sources, normalizes it into the canonical schema, validates it, and writes per-fund files under `../data/`.

This directory follows [`mellod-infra/docs/DEVELOPMENT_STANDARDS.md`](https://github.com/lloydduhon/mellod-infra/blob/main/docs/DEVELOPMENT_STANDARDS.md): Python N or N-1, `ruff` for lint/format/imports, pinned `requirements.txt`, type hints on public functions, `.env.example` indirection for secrets.

## Layout

```
etl/
├── pyproject.toml           # ruff + mypy configuration
├── requirements.txt         # pinned runtime deps
├── requirements-dev.txt     # pytest, respx, mypy, ruff
├── .env.example
├── pytest.ini
├── README.md                # you are here
├── fetchers/
│   ├── lidonation_api.py            # Phase 1
│   ├── projectcatalyst_funds.py     # Phase 2
│   ├── milestones_scraper.py        # Phase 3 (Supabase REST)
│   └── ideascale_wayback.py         # Phase 4 (Wayback CDX)
├── parsers/
│   └── iohk_pdf.py                  # Phase 2
├── normalizers/
│   ├── unify_proposals.py           # Phase 1
│   ├── reconcile_winners.py         # Phase 2
│   ├── derive_milestones.py         # Phase 3
│   ├── derive_fund_one.py           # Phase 4
│   ├── apply_reconciliations.py     # Phase 6
│   ├── dedupe_proposers.py          # Phase 6
│   └── consolidate.py               # Phase 6
├── validators/
│   └── validate_against_schema.py
└── tests/                           # 84 tests
```

## Current status (Phase 6)

**Implemented:**

- `fetchers/lidonation_api.py` (Phase 1).
- `fetchers/projectcatalyst_funds.py` + `parsers/iohk_pdf.py` (Phase 2).
- `fetchers/milestones_scraper.py` (Phase 3, Supabase REST).
- `fetchers/ideascale_wayback.py` (Phase 4, Wayback CDX + snapshot fetch).
- `normalizers/unify_proposals.py` (Phase 1).
- `normalizers/reconcile_winners.py` (Phase 2).
- `normalizers/derive_milestones.py` (Phase 3).
- `normalizers/derive_fund_one.py` (Phase 4, BS4-parsed IdeaScale snapshots).
- `validators/validate_against_schema.py` covers `proposals`, `proposers`, `milestones`, and `_reconciliation`.
- **84 unit tests** across the suite.

**Still stubbed:** none. All four fetchers and all consolidation normalizers are real.

## Setup

```bash
cd etl
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit as needed
```

## Conventions every fetcher must honor

- Identify itself with `HTTP_USER_AGENT` from `.env`.
- Respect per-host rate limits from `.env`.
- Cache raw responses; never delete prior captures.
- Emit structured JSON logs to stdout.
- Be idempotent — re-runs produce the same output for the same input.

## Validate the dataset against schemas

```bash
python validators/validate_against_schema.py
```

Always-on; safe with an empty dataset.

## Phase 1 — Lidonation Catalyst Explorer API

Smoke (10 pages, ~10 s):

```bash
python -m fetchers.lidonation_api --max-pages 10
python -m normalizers.unify_proposals
```

Full sweep (~6 min):

```bash
python -m fetchers.lidonation_api
python -m normalizers.unify_proposals
```

## Phase 2 — IOG voting-results PDF cross-check

Smoke against Fund 2:

```bash
python -m fetchers.projectcatalyst_funds --fund 2
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
```

## Phase 3 — Milestone Module (Supabase REST)

Smoke against Fund 9 (66 proposals, ~7 endpoint calls):

```bash
python -m fetchers.milestones_scraper --fund 9
python -m normalizers.derive_milestones --fund 9
type ..\data\funds\fund-09\milestones.json | python -m json.tool | head -50
python validators\validate_against_schema.py --fund 9
```

Full sweep (Funds 9–14):

```bash
python -m fetchers.milestones_scraper
python -m normalizers.derive_milestones
```

## Run the test suite

```bash
pip install -r requirements-dev.txt
python -m pytest                                  # 84 passed
python -m mypy fetchers normalizers parsers validators
```

## Phase 4 — Fund 1 Wayback recovery

The Catalyst pilot's only paper trail is the Internet Archive. Wayback is
rate-sensitive; if you hit 429, wait and re-run (cache makes it idempotent).

Smoke (5 snapshots, ~1 min):

```bash
python -m fetchers.ideascale_wayback --max-snapshots 5
python -m normalizers.derive_fund_one
type ..\data\funds\fund-01\proposals.json | python -m json.tool | Select-Object -First 50
python validators\validate_against_schema.py --fund 1
```

Full F1 sweep (~56 unique URLs at 0.5 rps = ~3 minutes wall):

```bash
python -m fetchers.ideascale_wayback           # CDX index + all snapshots
python -m normalizers.derive_fund_one          # emits proposals.json
```

Expect imperfect recovery. Every record carries `confidence: low` and
`funding_status: "unknown"` (F1 was the pilot — no formal vote).

## Phase 6 — Consolidation pipeline

Phase 6 is the "fold everything into one canonical surface" step. Run after
all four data sweeps (Phases 1-4) have run and produced their per-fund
artifacts.

```bash
cd etl
# (assume phases 1-4 cache + per-fund JSON are already in data/funds/)

# 1) Apply IOG-PDF reconciliations (idempotent - safe to re-run)
python -m normalizers.apply_reconciliations

# 2) Dedupe proposers across all funds
python -m normalizers.dedupe_proposers

# 3) Emit consolidated CSVs + JSON + schema.md
python -m normalizers.consolidate

# 4) Final validation gate
python validators\validate_against_schema.py --strict
```

Outputs land in `data/consolidated/`:
- `all_proposals.csv` (~25 columns) + `all_proposals.json` (full fidelity)
- `all_proposers.csv` + `all_proposers.json`
- `all_milestones.csv` + `all_milestones.json`
- `schema.md` (auto-generated column reference)

`apply_reconciliations.py` is idempotent (re-runs detect the IOG-PDF
override marker in `sources[]` and skip already-applied changes), so it's
safe to wire into a scheduled refresh.
