# Per-Fund Source Decision Matrix

This document records, for each Catalyst fund, which upstream source we treat as authoritative for each field family. It is the operational complement to [ADR-2026-05-13](adr/ADR-2026-05-13-source-strategy.md).

**Source key:**

| Code | Source | URL pattern |
|---|---|---|
| `LIDO` | Lidonation Catalyst Explorer API | `catalystexplorer.com/api/v1/*` |
| `PCIO` | projectcatalyst.io fund page | `projectcatalyst.io/funds/{N}` |
| `PCIO_CSV` | projectcatalyst.io voting-results CSV link | `projectcatalyst.io/funds/{N}/voting-results` -> Google Sheets `gviz` CSV |
| `IOHK_PDF` | IOG-published voting-results PDF | `static.iohk.io/.../catalyst-voting-results-fund{N}.pdf` or Google Drive |
| `MILE` | Catalyst Milestone Module | `milestones.projectcatalyst.io/projects/{id}` |
| `IDSC_WB` | IdeaScale via Internet Archive | `web.archive.org/web/*/cardano.ideascale.com/*` |
| `IDSC_LIVE` | IdeaScale live (auth-gated) | `cardano.ideascale.com` |
| `FORUM` | Cardano Forum / IOG blog / community | various |
| `MANUAL` | Manual curation | n/a |

## Per-fund matrix

| Fund | Proposer + proposal | Win/Loss | Completion | Notes |
|------|---------------------|----------|------------|-------|
| F1   | `IOHK_PDF` + `IDSC_WB` | `IOHK_PDF` | n/a | One-page Fund 1 voting-results PDF is now the source of truth for the limited result table; Wayback remains useful only for proposal detail recovery. |
| F2   | `LIDO`              | `PCIO_CSV` + `IOHK_PDF` (`static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf`) | `PCIO` status flag + `FORUM` | 78 proposals / 11 funded / 9 completed per `PCIO`. |
| F3   | `LIDO`              | `PCIO_CSV` | `PCIO` status flag | 150 / 21 / 16. |
| F4   | `LIDO`              | `PCIO_CSV` | `PCIO` status flag + `MANUAL` | 277 / 51 / 40. |
| F5   | `LIDO`              | `PCIO_CSV` | `PCIO` status flag + Catalyst Swarm GitBook | 267 / 69 / 59. |
| F6   | `LIDO`              | `PCIO_CSV` | `PCIO` + Lidonation `cx_monthly_reports` (sparse) | 711 / 151 / 122. |
| F7   | `LIDO`              | `PCIO_CSV` | `LIDO` monthly_reports | 936 / 264 / 217. |
| F8   | `LIDO`              | `PCIO_CSV` | `LIDO` monthly_reports + proposer-hosted close-outs | 1134 / 367 / 306. |
| F9   | `LIDO`              | `PCIO_CSV` | `MILE` (pilot, large projects) + `LIDO` monthly | 1166 / 207 / 178. |
| F10  | `LIDO` + `PCIO`     | `PCIO_CSV` + `PCIO` PDF | **`MILE`** (mandatory) | First fully tracked fund. |
| F11  | `LIDO` + `PCIO`     | `PCIO_CSV`  | **`MILE`** | |
| F12  | `LIDO` + `PCIO`     | `PCIO_CSV`  | **`MILE`** | |
| F13  | `LIDO` + `PCIO`     | `PCIO_CSV`  | **`MILE`** | |
| F14  | `LIDO` (Catalyst Voices gateway deferred) | `PCIO_CSV` cached, parser blocked | **`MILE`** (in-flight) | Cached CSV export currently contains formula/reference rows; needs correct tab/export before reconciliation. |
| F15  | `LIDO`              | TBD (voting may be in progress) | `MILE` | Schema complete, completion data accruing. |

## Current Phase 2 Access Status

The interim snapshot now uses the staff-provided Fund 1 PDF plus official
Project Catalyst CSV artifacts where they parse cleanly. Artifact URLs, local
filenames, and remaining parser gaps are tracked in
`docs/IOG_RESULTS_ACCESS_TRACKER.md`.

Current state:
- F2-F14 official voting-results CSV links have been discovered from
  `projectcatalyst.io/funds/{N}/voting-results` and cached under
  `data/_raw/iohk-results/`.
- F1 voting-results PDF has been added under `data/_raw/iohk-pdfs/fund-01.pdf`
  and now drives `data/funds/fund-01/proposals.json`.
- F2-F13 CSVs parse into `_intermediate/iohk_winners.json` and reconciliation
  sidecars. Three funding-status disagreements have been applied per policy:
  F2 `Address Gap in SPO Education/Comms`, F4 `NFT-DAO NFT metadata standards`,
  and F8 `RootsWallet beta - Backup/Recovery`.
- F14 is cached but not reconciled because the default CSV export contains
  formula/reference rows rather than proposal result rows.
- The older F2 and F10 PDFs remain cached as legacy artifacts, but CSVs are now
  the preferred source for F2-F13 result reconciliation.

The final full snapshot should not claim complete IOG/CF reconciliation until
F14 has a parseable result export and the F7-F9 workbooks have been reviewed
for any additional required tabs.

## Reconciliation policy

When two sources disagree on the same field for the same proposal:

1. **Win/loss disagreement** between `LIDO.funding_status` and `IOHK_PDF` or `PCIO`: the IOG/CF artifact wins. `LIDO` value is preserved in `notes`, and a row is added to that fund's `_reconciliation.json`.
2. **Completion status disagreement** between `MILE` and `LIDO`: `MILE` wins for F10+. For F2–F9, prefer whichever source has a primary-evidence URL; if both do, prefer the more recent.
3. **Proposer identity disagreement**: never auto-merge. Add the other ID to `duplicate_candidates[]` on both records.
4. **Vote count disagreement**: prefer `IOHK_PDF` if it publishes raw tallies; otherwise `LIDO`. Flag both values in `notes`.

Reconciliation outcomes are reviewed by the maintainer (Lloyd) before being applied to the canonical dataset.
