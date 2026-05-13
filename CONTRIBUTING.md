# Contributing

Thanks for considering a contribution. This repository is the source of truth for the dataset, so contributions land via pull request and never bypass review.

## What kinds of contributions are most useful

1. **Corrections** to existing records — wrong title, wrong proposer, wrong win/loss flag, wrong completion status. Cite a primary source in the PR.
2. **Filling in low-confidence fields** for F1–F5, where completion data is best-effort. Acceptable primary sources: IOG blog post, Cardano Forum thread (with author identity verifiable), proposer-published close-out report, Catalyst Swarm GitBook entry.
3. **Duplicate-proposer reconciliation.** If you identify that two `proposer_id` entries refer to the same entity, open a PR moving one into the other's `duplicate_candidates[]` and explain the evidence. We do not silently merge; the maintainer decides.
4. **New data sources.** If you find a source that fills a gap (especially for F1–F5 completion), propose a fetcher under `etl/fetchers/` and update `docs/PER_FUND_SOURCES.md` + an ADR.
5. **Schema improvements** — new fields with clear value. Schema changes require an ADR.

## Ground rules

- **Provenance is mandatory.** Every change to a data record must update its `sources[]` and `fetched_at`. Records without provenance will not be merged.
- **No silent overwrites.** If you change a field, the prior value must still be discoverable via git history; do not bulk-rewrite without a documented reason.
- **Confidence must be honest.** If you don't have a primary source, mark `confidence: low` and note why.
- **Closed enums** (`funding_status`, `project_status`, `milestone.status`, `source`) cannot be extended without an ADR.
- **Be polite to upstreams.** PRs that increase scrape pressure on Lidonation, IdeaScale, or the Milestone Module require explicit discussion.

## Workflow

1. Fork and branch from `main`.
2. Make changes. Keep PRs focused — one logical change per PR.
3. Run `ruff check etl/` and `python etl/validators/validate_against_schema.py` locally.
4. Open the PR with:
   - What changed and why
   - Which records are affected
   - Primary source(s) cited
5. CI will run linting and schema validation. Wait for review.

## Code style

Python code follows `mellod-infra/docs/DEVELOPMENT_STANDARDS.md`:

- Python N or N-1 (latest stable or one back)
- `ruff` for lint, format, and import sort (config in `etl/pyproject.toml`)
- Type hints required on public functions
- Dependencies pinned in `etl/requirements.txt`
- No secrets in committed code; use `etl/.env.example` for templates

## Questions

Open a GitHub Discussion (preferred) or file an issue tagged `question`.
