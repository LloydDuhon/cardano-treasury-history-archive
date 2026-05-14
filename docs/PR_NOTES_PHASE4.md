# Phase 4 PR Notes

Internal notes for the maintainer (Lloyd). Not part of the public docs.

## Branch and commit

Branch: `phase-4/fund-one-wayback` off `main`.

Suggested commit message:

```
Phase 4: Fund 1 Wayback Machine recovery

The Catalyst pilot has no canonical archive - cardano.ideascale.com
is auth-gated and JS-only today. The only viable path is the Internet
Archive.

- fetchers/ideascale_wayback.py rewritten as a two-stage Wayback
  fetcher: CDX query for /a/dtd/* in Sep 2020 - Jan 2021, then
  per-URL snapshot fetch via web.archive.org/web/<ts>id_/<url>.
  Conservative 0.5 rps, exponential backoff to 60s on 429, polite UA.
- normalizers/derive_fund_one.py parses archived IdeaScale HTML
  with BeautifulSoup4. Recovers title, proposer, description, ask.
  Emits data/funds/fund-01/proposals.json with funding_status="unknown"
  (no formal vote took place), project_status="unfunded",
  confidence="low" on every record. Notes field documents the F1
  pilot context.
- 16 new tests (suite total 67).
- Pinned deps: beautifulsoup4 4.12.3, soupsieve 2.6.

Refs: docs/CATALYST-HISTORY-CAPTURE-PLAN.md (Phase 4 - "heroic"),
ADR-2026-05-13.
```

## Local PowerShell flow

```powershell
cd $HOME\Documents\claude-work\repos\catalyst-history-archive
git checkout main; git pull
git checkout -b phase-4/fund-one-wayback

# Local preflight (Python 3.12)
cd etl
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt   # adds bs4 + soupsieve
ruff check .; ruff format --check .
python -m pytest                       # expect 67 passed
python -m mypy fetchers normalizers parsers validators
cd ..

# Phase 4 smoke
cd etl
python -m fetchers.ideascale_wayback --max-snapshots 5
python -m normalizers.derive_fund_one
type ..\data\funds\fund-01\proposals.json | python -m json.tool | Select-Object -First 50
python validators\validate_against_schema.py --fund 1
cd ..

# Commit and PR
git add etl docs CHANGELOG.md
# Decide whether to ship F1 smoke output in this PR:
# git add data\funds\fund-01\_provenance\ideascale_wayback data\funds\fund-01\proposals.json data\funds\fund-01\_meta.json
git commit -m "Phase 4: Fund 1 Wayback Machine recovery" -m "See docs/PR_NOTES_PHASE4.md."
git push -u origin phase-4/fund-one-wayback
gh pr create --base main --title "Phase 4: Fund 1 Wayback Machine recovery" --body-file docs/PR_NOTES_PHASE4.md
```

## Test plan before merge

| Step | Command | Expected |
|---|---|---|
| Unit tests | `python -m pytest` (from etl/) | 67 passed |
| Type check | `python -m mypy fetchers normalizers parsers validators` | no issues |
| Schema validator (empty data) | `python validators/validate_against_schema.py` | OK |
| Fetcher smoke | `python -m fetchers.ideascale_wayback --max-snapshots 5` | `cdx.json.gz` + 5 snapshot `.html.gz` files written |
| Normalizer smoke | `python -m normalizers.derive_fund_one` | `data/funds/fund-01/proposals.json` written with N records |
| Validator on output | `python validators/validate_against_schema.py --fund 1 --strict` | all records valid |

## Heroic caveats - read before merging

1. **Coverage is partial by design.** Wayback may have captured only a subset of the ~56 F1 proposals, and some snapshots will be JS-only/empty when parsed. Records with `title` recovered count as "good enough" for the archive. Records that come out title-less get a synthetic `untitled-<idea_id>` slug.
2. **All F1 records carry `confidence: low`.** This is the only fund where this is true by default. Don't sort F1 into research findings without an explicit disclaimer.
3. **`funding_status: "unknown"` is deliberate.** F1 had no formal vote; the program collected ideas but didn't fund any. `unknown` is the honest mapping. `not_approved` would imply a vote, which is wrong.
4. **`ideascale_url` is the archived URL** (the original cardano.ideascale.com URL), not the Wayback wrapper. The `sources[].url` carries the Wayback URL for replay.
5. **Wayback hits 429 easily.** The fetcher retries with exponential backoff up to 60 s, then gives up gracefully (snapshot fetcher returns None; the proposal is skipped). Re-running the fetcher resumes from where it left off because the cache is idempotent.

## What I left out (deliberate)

- **No F2-F5 manual-curation scaffolding.** That's a different category of work (humans writing notes against forum posts and IOG blog summaries). Tracked as a future phase, not a Phase 4 deliverable.
- **No `proposers.json` for F1.** Proposer-entity reconciliation lands in Phase 6; F1's parsed proposer names are kept on each proposal via `proposer_ids[]`.
- **No fallback when CDX itself 429s.** If Wayback CDX is unreachable, the fetcher raises after retries. That's acceptable; F1 sweep is a one-time operation that can be re-run later.
- **Sleep-then-retry isn't documented in the CLI.** Just re-run if you 429; the cache makes that safe.

