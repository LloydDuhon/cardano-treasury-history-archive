# Per-Fund Source Decision Matrix

This document records, for each Catalyst fund, which upstream source we treat as authoritative for each field family. It is the operational complement to [ADR-2026-05-13](adr/ADR-2026-05-13-source-strategy.md).

**Source key:**

| Code | Source | URL pattern |
|---|---|---|
| `LIDO` | Lidonation Catalyst Explorer API | `catalystexplorer.com/api/*` |
| `PCIO` | projectcatalyst.io fund page | `projectcatalyst.io/funds/{N}` |
| `IOHK_PDF` | IOG-published voting-results PDF | `static.iohk.io/.../catalyst-voting-results-fund{N}.pdf` or Google Drive |
| `MILE` | Catalyst Milestone Module | `milestones.projectcatalyst.io/projects/{id}` |
| `IDSC_WB` | IdeaScale via Internet Archive | `web.archive.org/web/*/cardano.ideascale.com/*` |
| `IDSC_LIVE` | IdeaScale live (auth-gated) | `cardano.ideascale.com` |
| `FORUM` | Cardano Forum / IOG blog / community | various |
| `MANUAL` | Manual curation | n/a |

## Per-fund matrix

| Fund | Proposer + proposal | Win/Loss | Completion | Notes |
|------|---------------------|----------|------------|-------|
| F1   | `IDSC_WB`           | n/a (pilot, no funded winners) | n/a | ~56 proposals; Wayback CDX is the only practical path. |
| F2   | `LIDO`              | `IOHK_PDF` (`static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf`) | `PCIO` status flag + `FORUM` | 78 proposals / 11 funded / 9 completed per `PCIO`. |
| F3   | `LIDO`              | `IOHK_PDF` (Google Drive) | `PCIO` status flag | 150 / 21 / 16. |
| F4   | `LIDO`              | `IOHK_PDF` (Google Drive) | `PCIO` status flag + `MANUAL` | 277 / 51 / 40. |
| F5   | `LIDO`              | `IOHK_PDF` (Google Drive) | `PCIO` status flag + Catalyst Swarm GitBook | 267 / 69 / 59. |
| F6   | `LIDO`              | `IOHK_PDF` (Google Drive) | `PCIO` + Lidonation `cx_monthly_reports` (sparse) | 711 / 151 / 122. |
| F7   | `LIDO`              | `IOHK_PDF` (`bit.ly/3HJNhuX`) | `LIDO` monthly_reports | 936 / 264 / 217. |
| F8   | `LIDO`              | `IOHK_PDF` (Google Drive) | `LIDO` monthly_reports + proposer-hosted close-outs | 1134 / 367 / 306. |
| F9   | `LIDO`              | `IOHK_PDF` (`bit.ly/Fund9_Results`) | `MILE` (pilot, large projects) + `LIDO` monthly | 1166 / 207 / 178. |
| F10  | `LIDO` + `PCIO`     | `PCIO` (`fund10-voting-results.pdf`) | **`MILE`** (mandatory) | First fully tracked fund. |
| F11  | `LIDO` + `PCIO`     | `PCIO`  | **`MILE`** | |
| F12  | `LIDO` + `PCIO`     | `PCIO`  | **`MILE`** | |
| F13  | `LIDO` + `PCIO`     | `PCIO`  | **`MILE`** | |
| F14  | `LIDO` (Catalyst Voices gateway deferred) | `PCIO` | **`MILE`** (in-flight) | Catalyst Voices is upstream system of record once gateway stabilizes. |
| F15  | `LIDO`              | TBD (voting may be in progress) | `MILE` | Schema complete, completion data accruing. |

## Reconciliation policy

When two sources disagree on the same field for the same proposal:

1. **Win/loss disagreement** between `LIDO.funding_status` and `IOHK_PDF` or `PCIO`: the IOG/CF artifact wins. `LIDO` value is preserved in `notes`, and a row is added to that fund's `_reconciliation.json`.
2. **Completion status disagreement** between `MILE` and `LIDO`: `MILE` wins for F10+. For F2–F9, prefer whichever source has a primary-evidence URL; if both do, prefer the more recent.
3. **Proposer identity disagreement**: never auto-merge. Add the other ID to `duplicate_candidates[]` on both records.
4. **Vote count disagreement**: prefer `IOHK_PDF` if it publishes raw tallies; otherwise `LIDO`. Flag both values in `notes`.

Reconciliation outcomes are reviewed by the maintainer (Lloyd) before being applied to the canonical dataset.
