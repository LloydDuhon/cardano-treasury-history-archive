# Phase 6 PR Notes

Internal notes for the maintainer (Lloyd). Not part of the public docs.

## Branch and commit

Branch: `phase-6/consolidation` off `main`.

Suggested commit message:

```
Phase 6: cross-source consolidation pipeline

Adds the three normalizers that fold the four phases' per-fund outputs
into canonical, cross-fund datasets:

- normalizers/apply_reconciliations.py - idempotent applier of
  per-fund _reconciliation.json. Per ADR-2026-05-13, when
  verdict=secondary_wins, funding_status is updated to the IOG-PDF
  value, the original Lidonation value is preserved in notes, and
  a sources[] entry marks the override. Re-runs are no-ops.
- normalizers/dedupe_proposers.py - cross-fund proposer dedupe.
  Exact-ID merge on lidonation_profile_uuid; fuzzy name matches go
  into duplicate_candidates[] for human review (per schema, never
  silent merge).
- normalizers/consolidate.py - emits data/consolidated/* CSVs (narrow,
  ~25 cols) and JSON (full fidelity) plus an auto-generated schema.md.

17 new tests, mypy strict happy, suite total 84.

Refs: docs/CATALYST-HISTORY-CAPTURE-PLAN.md (Phase 6), ADR-2026-05-13.
```

## Local PowerShell flow

```powershell
cd $HOME\Documents\claude-work\repos\catalyst-history-archive
git checkout main; git pull
git checkout -b phase-6/consolidation

# Local preflight (Python 3.12)
cd etl
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt       # adds pandas + numpy
ruff check .; ruff format --check .
python -m pytest                           # expect 84 passed
python -m mypy fetchers normalizers parsers validators
cd ..

# Commit + PR. No smoke output to ship - the pipeline is code-only until
# the four data sweeps run.
git add etl docs CHANGELOG.md
git status --short
git commit -m "Phase 6: cross-source consolidation pipeline" -m "See docs/PR_NOTES_PHASE6.md."
git push -u origin phase-6/consolidation
gh pr create --base main --title "Phase 6: cross-source consolidation pipeline" --body-file docs/PR_NOTES_PHASE6.md
```

## Test plan before merge

| Step | Command | Expected |
|---|---|---|
| Unit tests | `python -m pytest` (from etl/) | 84 passed |
| Type check | `python -m mypy fetchers normalizers parsers validators` | no issues |
| Schema validator | `python validators/validate_against_schema.py` | OK |

## After merge - the full pipeline (one-time, on your machine)

Once Phase 6 is in main, you can run the entire archive build end-to-end:

```powershell
cd etl
.venv\Scripts\Activate.ps1

# Phase 1: Lidonation full sweep (~6 min)
python -m fetchers.lidonation_api
python -m normalizers.unify_proposals

# Phase 2: IOG PDFs for F2-F13 (~15 min including Google Drive)
python -m fetchers.projectcatalyst_funds
# (per-fund parser one-liner from the Phase 2 PR notes, loop F2-F13)
python -m normalizers.reconcile_winners

# Phase 3: Milestone Module (~1 min)
python -m fetchers.milestones_scraper
python -m normalizers.derive_milestones

# Phase 4: Fund 1 Wayback (~3 min, may 429)
python -m fetchers.ideascale_wayback
python -m normalizers.derive_fund_one

# Phase 6: fold it all together
python -m normalizers.apply_reconciliations
python -m normalizers.dedupe_proposers
python -m normalizers.consolidate
python validators\validate_against_schema.py --strict

cd ..
git checkout -b snapshot/2026-05-XX
git add data\
git status --short    # eyeball before committing 11K+ proposals
git commit -m "snapshot 2026-05-XX: first full sweep"
git push
gh pr create --base main --title "Data snapshot 2026-05-XX (first full sweep)"
```

When that PR merges, tag a release: `gh release create snapshot-2026-05-XX --notes "First full Catalyst history snapshot."`

## Key design choices baked in

1. **Reconciliation is idempotent.** A re-run of `apply_reconciliations`
   detects the IOG-PDF marker in `sources[]` and skips proposals it has
   already touched. Safe under a monthly refresh.
2. **Proposer dedupe is name-driven where possible.** The dedup module
   walks `data/_raw/lidonation/page-*.json.gz` for display names. If the
   raw cache is missing (e.g., you only have F4 data), proposer
   display names fall back to "Proposer {short_uuid}".
3. **Fuzzy duplicate_candidates is mutual.** If proposer A's `duplicate_candidates[]`
   includes B, then B's includes A. Human review collapses or rejects.
4. **CSV intentionally lossy.** Nested objects don't survive to CSV. Use
   the matching `.json` file for full schema fidelity.

## What I left out (deliberate)

- **No tagged release in this PR.** Tagging follows the first full data
  sweep, which itself follows this PR's merge.
- **No `data/consolidated/*` files in this PR.** Code only - no data
  artifacts. They land when the sweep runs.
- **No pandas usage in the implementation.** Pandas is pinned but Phase 6
  uses stdlib csv + json. Pandas is reserved for any future heavier
  cross-source analysis script.
- **No Phase 5 (on-chain CIP-15/36).** Deferred per earlier decision; a
  separate `catalyst-voting-power-archive` repo is the natural home.
- **No DATA_QUALITY.md row-count refresh.** Will happen post-sweep, when
  there are real counts to commit.

