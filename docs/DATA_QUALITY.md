# Data Quality

This document is a brutally honest description of what this dataset is good for and where its limits are. If you are about to publish a finding based on this data, read this first.

## Confidence tiers

Every record carries a `confidence` field with one of:

- **`high`** — Authoritative source captured and machine-verified. Field values trace to a primary artifact (IOG PDF, Milestone Module page, Lidonation API response). Multiple sources agree, or the single source is canonical.
- **`medium`** — Authoritative source for the core record exists, but at least one secondary field is inferred, reconciled across sources, or carried over from a previous snapshot without re-verification.
- **`low`** — Best-effort reconstruction from secondary or fragmentary sources. Expect inaccuracy. Useful as a starting point for further investigation; not appropriate to cite uncritically.

Per-field overrides live in each record's optional `field_confidence` object.

## What this dataset is good for

- Counting proposals per fund, per challenge, per proposer
- Identifying funded vs not-funded outcomes from Lidonation v1 for Funds 2–15,
  with IOG/CF voting-results reconciliation still pending for several funds
- Tracking milestone completion for Funds 10–15
- Analyzing proposer behavior across funds (with caveats about duplicate identity — see below)
- Reviewing AI summaries, scores, and votes where Lidonation has them
- Reproducing source artifacts via the `_provenance/` directory

## What this dataset is NOT good for (yet)

- **Confidently answering "did Fund 2–5 projects finish?"** Per-project completion data for these funds is essentially missing in any structured source. We default to `confidence: low` here and explain why in the `sources[]` array for those records.
- **Identifying every proposer-entity duplicate.** We do not silently merge near-duplicates. Two records that look like the same person/team will both exist with cross-references in `duplicate_candidates[]` until a human reviews.
- **On-chain voting-power analysis.** Deferred to a future sibling repository. CIP-15/36 registrations are not in this schema.
- **Real-time data.** Snapshots are taken on a monthly cadence; expect lag of up to ~30 days for in-flight funds.
- **Catalyst Voices native data.** Until `api.projectcatalyst.io/api/v1/health/ready` returns 200, F14+ data comes from Lidonation's mirror, not the upstream system of record.
- **Final IOG/CF voting-results reconciliation.** The interim dataset includes
  Lidonation v1 funding outcomes for F2-F15, but the independent IOG/CF
  voting-results artifacts are not fully available yet. See
  `docs/IOG_RESULTS_ACCESS_TRACKER.md`.

## Known systematic limitations

### Interim snapshot status
The current working snapshot is intentionally interim. It validates against the
schemas and contains complete Lidonation v1 proposal coverage for F2-F15 plus
Milestone Module data for F9-F14, but it is not the final "full snapshot"
because Phase 2 voting-results reconciliation is incomplete.

Current validated counts from the interim run:
- `all_proposals.json`: 11,528 records
- `all_proposers.json`: 9,818 records
- `all_milestones.json`: 5,039 records
- 15 fund directories present
- Schema validation: 37 files across 15 funds

The Lidonation API changed from the legacy `/api/*` surface to the documented
`/api/v1/*` surface. The old endpoint returned only eight funds in the captured
sweep; `/api/v1/proposals` with `include=campaign,fund,team` returns every
F2-F15 fund covered by Catalyst Explorer.

### Fund 1
~56 pilot proposals, no funded winners. Recovered from Internet Archive Wayback snapshots of `cardano.ideascale.com`. Coverage may be incomplete. All F1 records carry `confidence: low` by default; some fields may be missing entirely.

The current Wayback CDX query returned an empty result, so the interim generated
dataset has no recovered Fund 1 proposal records. Fund 1 remains a separate
low-confidence recovery task.

### IOG/CF voting-results artifacts
Phase 2 is only partially complete. `fund-02.pdf` is downloaded and parsed.
`fund-10.pdf` is downloaded, but the current parser returns 0 rows because the
layout differs from the Fund 2 PDF. F3-F9 Drive/bit.ly artifacts are permission
blocked from CLI, and F11-F13 Google Sheets exports return 401 from CLI. These
blocked artifacts are tracked in `docs/IOG_RESULTS_ACCESS_TRACKER.md`.

### Funds 2–5 completion data
There was no canonical close-out tracker for these funds. The IOG-published count of "Completed" proposals exists in aggregate (e.g., F2 reports 9 of 11 completed), but per-proposal evidence is scattered across:
- A now-frozen Google Sheet ("Catalyst Funded Reporting", marked CLOSED)
- IOG blog posts (narrative summaries, not structured)
- Proposer-hosted close-out pages
- Forum threads with verifiable authorship

These records carry `field_confidence.project_status: low`. The aggregate count from `projectcatalyst.io/funds/{N}?status=Completed` is used as a coarse boolean, but specific evidence is often unavailable.

### Funds 6–9 completion data
Better than F2–F5 but still partial. Lidonation's `cx_monthly_reports` table covers a subset, especially from F7 forward. Expect `field_confidence.project_status: medium` for most records.

### Vote count units
Lidonation `yes_votes_count` returns different units across funds — raw lovelace for older funds, normalized ADA for some, raw counts elsewhere. Each record's `sources[]` entry includes a `fields_provided` array indicating which fields came from which source so you can disambiguate.

### Currency
Funds increasingly mix ADA / USD / USDM denominations. `amount_requested.currency` is always populated; do not assume ADA.

### Proposer identity
- Some proposers use different display names across funds. We attempt reconciliation via `external_ids.ideascale_profile_id`, `lidonation_profile_uuid`, and `catalyst_voices_stake_address` where any of these match.
- When only the display name matches, we do NOT auto-merge — the proposers exist as separate records with mutual `duplicate_candidates[]` references.
- "Team" proposals are recorded under a single `proposer_id` with `team_members[]`; individual team members are not extracted as separate proposer entities.

## How to report a data quality issue

Open an issue or pull request. Include:

1. The affected `proposal_id`, `proposer_id`, or `milestone_id`.
2. What you observed in the dataset vs. what you believe is correct.
3. A primary-source URL (not "Twitter says").
4. Whether the fix is straightforward or requires schema/ADR discussion.

The maintainer reviews and merges. Nothing in `data/` is overwritten silently; every change is a git commit you can audit.
