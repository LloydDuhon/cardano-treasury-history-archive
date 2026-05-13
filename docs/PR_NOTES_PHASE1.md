# Phase 1 PR Notes

Internal notes for the maintainer (Lloyd). Not part of the public documentation
- delete or git-rm this file before tagging a public release.

## Branch and commit

Suggested branch: `phase-1/lidonation-ingestion`.

Suggested commit message:

```
Phase 1: Lidonation Catalyst Explorer API ingestion

- fetchers/lidonation_api.py: polite paginated client (httpx + tenacity)
  with 1.5 rps default, exponential backoff, identifiable UA, atomic
  writes, gzip caching. Idempotent (--force to re-fetch).
- normalizers/unify_proposals.py: demultiplexes flat /api/proposals
  sweep into per-fund proposals.json that satisfy proposal.schema.json.
- Test suite (14 tests) under etl/tests/: respx-mocked HTTP, real
  fixture from the live API, schema-conformance assertion, idempotency
  check, retry policy check.
- .github/workflows/tests.yml: pytest + mypy strict jobs on PR.
- ADR-2026-05-13 Implementation Notes appendix documenting the
  broken-server-side-filter finding and central _raw/ cache strategy.
- requirements: pinned httpx 0.27, tenacity 9.0, python-slugify 8.0.
- Per-fund directories under data/funds/ are NOT created yet -
  they appear on first sweep.

Refs: docs/CATALYST-HISTORY-CAPTURE-PLAN.md (Phase 1)
```

## Local PowerShell flow

```powershell
cd $HOME\Documents\claude-work\repos\catalyst-history-archive

# 0) (If you haven't already pushed Phase 0)
#    Follow the Phase 0 instructions first.

# 1) Branch + stage
git checkout -b phase-1/lidonation-ingestion
git status --short
git diff --stat

# 2) Optional local preflight (Python 3.12)
cd etl
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
python -m pytest                       # expect: 14 passed
python -m mypy fetchers normalizers validators  # strict
cd ..

# 3) Smoke sweep (10 pages, ~10 seconds at 1.5 rps)
cd etl
python -m fetchers.lidonation_api --max-pages 10
python -m normalizers.unify_proposals
python validators\validate_against_schema.py  # expect: OK
ls ..\data\funds                         # see which funds got records
cd ..

# 4) Commit (excluding /data/_raw/* until you're happy)
git add etl schemas docs .github CHANGELOG.md data/README.md data/_raw/README.md
# Only commit the raw cache once you've eyeballed it
# git add data/_raw data/funds
git status --short
git commit -F docs/PR_NOTES_PHASE1.md  # or paste the message above

# 5) Push and open PR
git push -u origin phase-1/lidonation-ingestion
gh pr create --base main --head phase-1/lidonation-ingestion \
   --title "Phase 1: Lidonation Catalyst Explorer API ingestion" \
   --body "See docs/PR_NOTES_PHASE1.md and docs/CATALYST-HISTORY-CAPTURE-PLAN.md"
```

## Test plan to run before merge

| Step | Command | Expected |
|------|---------|----------|
| Unit tests | `python -m pytest` (from etl/) | 14 passed |
| Type check | `python -m mypy fetchers normalizers validators` | no issues |
| Schema validator (empty data) | `python validators/validate_against_schema.py` | "OK" / exit 0 |
| Smoke fetch | `python -m fetchers.lidonation_api --max-pages 10` | 10 page-NNNN.json.gz files in data/_raw/lidonation/ |
| Smoke normalize | `python -m normalizers.unify_proposals` | several data/funds/fund-XX/proposals.json + _meta.json files |
| Schema validator (after normalize) | `python validators/validate_against_schema.py` | OK across all populated funds |

## What I left out (deliberate, deferred to follow-up PRs)

- **No full 475-page sweep committed.** The Phase 1 PR contains code + 10-page
  smoke output only. Run the full sweep on `main` after Phase 1 lands.
- **`/api/campaigns`, `/api/ideascale-profiles`, `/api/groups` not consumed yet.**
  These will enrich proposer data in a Phase 1b follow-up once the proposal
  shape is validated.
- **No proposer.json or proposers.csv written.** Proposer-entity reconciliation
  is Phase 6 work; for now `proposer_ids` on each proposal record carry the
  basis for it.
- **No CSV outputs.** Phase 6 produces the consolidated CSVs.
- **GitHub Actions `refresh-data.yml` still disabled.** Re-enable it (uncomment
  the `schedule:` block + remove `if: false`) only after the first full sweep
  is in the repo on `main`.

## Cleanup before push

I left two probe-marker files in the repo root during sandbox debugging:

- `_marker.txt` (64 bytes)
- `_marker2.py` (small Python file)

They're harmless but shouldn't ship. Delete them before the PR:

```powershell
Remove-Item .\_marker.txt, .\_marker2.py -ErrorAction SilentlyContinue
```

## Known sandbox-only caveats

Two things that will trip you ONLY in the local sandbox environment, not on
your Windows machine or in CI:

1. **Python 3.10 doesn't support `datetime.UTC` import** (3.11+). Our code
   uses the 3.10-compatible `timezone.utc` idiom with a `# noqa: UP017` so
   ruff stays happy under our py312 target. Works on both.
2. **pytest tmp_path cleanup recursion** on the WSL/Windows mount. Local
   PowerShell pytest writes to `C:\Users\<you>\AppData\Local\Temp` and is
   unaffected.

