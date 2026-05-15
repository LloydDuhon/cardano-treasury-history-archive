# Consolidated CSV column reference

All files under `data/consolidated/` are derived from the per-fund
`data/funds/fund-XX/*.json` files. The JSON form (`all_*.json`) carries
full schema fidelity; the CSV form is intentionally narrowed to ~25 columns
for spreadsheet ergonomics.

## `all_proposals.csv`

| Column | Source | Notes |
|---|---|---|
| `proposal_id` | mint(`f{fund:02d}-{slug}`) | canonical key |
| `fund` | int 1-15 | |
| `title` | proposal.title | |
| `slug` | proposal.slug | URL-safe |
| `challenge` | proposal.challenge | category/campaign |
| `proposer_ids` | `;`-joined list | join with `all_proposers.csv` via `external_ids` |
| `amount_requested` / `amount_received` | numbers | currency in next col |
| `currency` | `ADA` / `USD` / `USDM` / `UNKNOWN` | |
| `yes_votes` / `no_votes` / `abstain_votes` | numbers | units vary per fund |
| `score_*` | flattened from `scores.*` | review scores where available |
| `ranking_total` | int | position within fund/challenge |
| `funding_status` | enum | post-reconciliation: IOG-canonical |
| `project_status` | enum | unfunded/funded/in_progress/complete/cancelled/stalled/unknown
| `funded_at` / `completed_at` | ISO 8601 | |
| `*_url` | flattened from `links.*` | one column per known source link |
| `milestone_count` | derived | from F10+ Milestone Module |
| `is_opensource` | boolean | |
| `confidence` | enum `high` / `medium` / `low` | |
| `ai_summary` | string or null | Lidonation-attributed |

Lossy: `sources[]`, `field_confidence`, `external_ids`, the full `links` map,
and `notes` are in `all_proposals.json` but not the CSV.

## `all_proposers.csv`

| Column | Notes |
|---|---|
| `proposer_id` | canonical, deduped across funds |
| `display_name` | best-known name |
| `entity_type` | individual / team / organization / unknown |
| `*_profile_id`, `lidonation_profile_uuid`, `catalyst_voices_stake_address` | external ids |
| `total_*` | rollup counts across all funds |
| `total_requested_*` / `total_received_*` | numbers; denomination-mixed across funds
| `first_fund` / `last_fund` | int |
| `confidence` | enum |
| `duplicate_candidates_count` | int; >0 means the entity may collide with others |
| `twitter` / `github` / `website` | flattened socials |

## `all_milestones.csv`

| Column | Notes |
|---|---|
| `milestone_id` | format `{proposal_id}-m{NN}` |
| `proposal_id` | back-reference |
| `milestone_number` | 1-based |
| `budget` | per-milestone budget in `currency` |
| `status` | enum |
| `is_closeout` | boolean; final milestone |
| `delivered_at` | ISO 8601 |
| `evidence_count` / `signoff_count` | int |
| `closeout_*_url` | when present |
| `confidence` | |

## Caveats

- F1 proposal result rows come from the staff-provided voting-results PDF.
  Funding status is high confidence; proposal-detail fields are limited.
- F2-F5 completion data is best-effort; expect `project_status: unknown` for
  many records.
- Vote-count units vary per fund (raw lovelace vs normalized count). See
  per-fund `_meta.json` for source notes.
