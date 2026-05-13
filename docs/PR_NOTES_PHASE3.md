# Phase 3 PR Notes

Internal notes for the maintainer (Lloyd). Not part of the public docs.

## Branch and commit

Branch: `phase-3/milestone-module-supabase` off `main`.

Suggested commit message:

```
Phase 3: Milestone Module ingestion via Supabase REST

The Milestone Module (milestones.projectcatalyst.io) is a Vite SPA
backed by Supabase, NOT an HTML site - the public anon key is
exposed in /env.js for client-side use. Pivot from HTML scrape
to Supabase REST is documented in ADR-2026-05-13 Implementation
Notes (Phase 3 appendix).

- fetchers/milestones_scraper.py rewritten as a Supabase REST
  fetcher. Same polite-client pattern (httpx + tenacity + 1 rps).
  Caches funds, challenges, proposals, soms, poas, signoffs per
  fund. Covers F9-F14 (1,146 funded proposals at survey time).
- normalizers/derive_milestones.py: filters soms.current=true,
  derives per-milestone status from PoA + signoff state,
  extracts evidence URLs from PoA markdown content, flags the
  final milestone as is_closeout. Writes per-fund milestones.json
  matching milestone.schema.json.
- 18 new tests (suite total 51); F9 trimmed fixtures (~70 KB).
- No new pip deps required.

Refs: docs/CATALYST-HISTORY-CAPTURE-PLAN.md, ADR-2026-05-13.
```

## Local PowerShell flow

```powershell
cd $HOME\Documents\claude-work\repos\catalyst-history-archive
git checkout main
git pull
git checkout -b phase-3/milestone-module-supabase

# Local preflight (Python 3.12)
cd etl
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
ruff check .; ruff format --check .
python -m pytest                      # expect 51 passed
python -m mypy fetchers normalizers parsers validators
cd ..

# Phase 3 smoke against Fund 9
cd etl
python -m fetchers.milestones_scraper --fund 9
python -m normalizers.derive_milestones --fund 9
type ..\data\funds\fund-09\milestones.json | python -m json.tool | Select-Object -First 50
python validators\validate_against_schema.py --fund 9
cd ..

# Stage and commit
git add etl docs CHANGELOG.md data\_raw\README.md
# Decide whether to ship the F9 smoke output in this PR:
# git add data\funds\fund-09\_provenance\milestones_supabase data\funds\fund-09\milestones.json
git status --short
git commit -m "Phase 3: Milestone Module ingestion via Supabase REST" -m "See docs/PR_NOTES_PHASE3.md and ADR-2026-05-13 Implementation Notes."

git push -u origin phase-3/milestone-module-supabase
gh pr create --base main --title "Phase 3: Milestone Module ingestion via Supabase REST" --body-file docs/PR_NOTES_PHASE3.md
```

## Test plan before merge

| Step | Command | Expected |
|---|---|---|
| Unit tests | `python -m pytest` (from etl/) | 51 passed |
| Type check | `python -m mypy fetchers normalizers parsers validators` | no issues |
| Schema validator | `python validators/validate_against_schema.py` | OK |
| Fetcher smoke | `python -m fetchers.milestones_scraper --fund 9` | 6 gz files under data/funds/fund-09/_provenance/milestones_supabase/ |
| Normalizer smoke | `python -m normalizers.derive_milestones --fund 9` | data/funds/fund-09/milestones.json written |
| Validator on output | `python validators/validate_against_schema.py --fund 9 --strict` | every milestone passes the schema |

## Why a Supabase key in the repo is OK

The anon key in `etl/fetchers/milestones_scraper.py` (also exposed in `.env.example`) is the **public** anon role JWT served by `milestones.projectcatalyst.io/env.js`. Supabase's anon key is designed for client-side use; the security boundary is Postgres row-level security policies on the Supabase side. We treat this key the same way we'd treat any unauthenticated public API endpoint - polite User-Agent, rate-limited, never written to (read-only by design). If the upstream rotates the key, override `MILESTONES_SUPABASE_ANON_KEY` in `.env`.

The unit test `test_default_anon_key_is_public_supabase_anon_role` decodes the JWT payload and asserts `role == "anon"` so we catch any accidental escalation.

## What I left out (deliberate)

- **No full F9-F14 sweep committed.** Phase 3 PR contains code + F9 smoke only.
- **No `derive_milestone_completion` correlation with Lidonation's proposers.completed_proposals_count.** That's Phase 6's job (cross-source enrichment).
- **rejected / stalled / withdrawn statuses are best-effort.** The Supabase tables don't expose explicit rejection signals; we fall back to `unknown` rather than guess. Phase 6 can layer in evidence from forum threads if needed.
- **No `delivery_target_date` derived from `starting_date + month_offset`.** I considered it but `month` in soms is a string and ambiguous (sometimes 1-based ordinal, sometimes literal calendar month). Setting it to None is safer; we can revisit with per-fund variants in a follow-up.
- **PoA `content` not stored in milestones.json.** Only the extracted URLs are. The raw content is preserved in the Supabase cache for replay or future enrichment.

## Known caveats

1. **Title encoding bug in some early F9 proposals.** I saw `500+ â‚łCommunity Sent to Conferences` in the raw API response — that's a mojibake of the ADA glyph ₳. We capture it verbatim; Phase 6 can clean it up.
2. **`milestones_qty` may not match actual `current` SoM count.** Some early proposals revised their SoM after starting; the qty reflects the latest plan. Tests assert per-proposal milestone counts stay within the maximum-known qty across the fixture, not that they equal `milestones_qty` exactly.
3. **Supabase pagination caps at 1000 rows by default.** Our `fetch_all` paginates beyond that via offset/limit. F10's `soms` table will likely exceed 1000 rows (revisions are bulky); the pagination loop handles it.

