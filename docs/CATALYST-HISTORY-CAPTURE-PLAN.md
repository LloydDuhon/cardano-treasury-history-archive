# Project Catalyst Historical Data Capture — Plan

**Author:** Lloyd Duhon (with Claude research)
**Date:** 2026-05-13
**Status:** Draft for review — no code written yet
**Owner:** Lloyd
**Scope:** Capture proposer, proposal, win/loss, and completion data for every Project Catalyst fund (Fund 1 → Fund 15), as a GitHub-resident research dataset.

---

## 1. Executive Summary

Project Catalyst data is **fragmented** across at least eight sources spanning four eras (Pilot / IdeaScale / Jörmungandr / Catalyst Voices). No single source covers everything cleanly. Here is the honest landscape as of May 13, 2026:

| Source | What it gives us | Status |
|---|---|---|
| **Lidonation Catalyst Explorer API** (`catalystexplorer.com/api/*`) | 11,385 proposals, F2–F15, rich fields incl. proposer, votes, funding status, AI summary. Apache-2.0 codebase. **No auth.** | **Working. Primary source for F2–F15 proposer/proposal data.** |
| `projectcatalyst.io/funds/{N}/voting-results` | Canonical IOG winner artifacts for F2–F13 (PDFs on `static.iohk.io` / Google Drive) plus per-fund counts | **Working. Primary source for authoritative win/loss.** |
| `milestones.projectcatalyst.io` | Authoritative milestone-level completion data, F10–F15 | **Live; HTML scrape only — no public API.** |
| `cardano-foundation/catalyst-voices` | Future system of record, Fund 14+; signed-document model | **API design exists; public deployed gateway returns HTTP 500 today.** Defer. |
| Lidonation legacy API (`lidonation.com/api/catalyst-explorer/*`) | Older REST surface | **Broken** (UUID-vs-bigint mismatch). Schema reference only. |
| `cardano.ideascale.com` | F1–F9 proposal pages (original source) | SPA, REST API gated. **Wayback CDX scrape is the only practical path. Required for F1.** |
| On-chain CIP-15 / CIP-36 (label 61284) via Koios / Blockfrost / db-sync | Voter eligibility and voting power per fund (NOT proposal outcomes) | Working but **does not answer "who won"** — votes were cast off-chain on Jörmungandr/Hydra. Useful sidecar dataset only. |
| `catalyst-fund-archive-tool` / `catalyst-toolbox` / `catalyst-core` event-db dumps | Jörmungandr-era raw tally recomputation | Heavy machinery, useful only for audit/verification. |

**The dataset will be heterogeneous in confidence.** F10–F15 will be excellent end-to-end. F6–F9 will be good for proposals and win/loss, partial for completion. F2–F5 will be good for the proposal list and win/loss, but completion data will be best-effort with low confidence. F1 (pilot — no funded winners) needs a Wayback CDX rescue and will be brittle.

---

## 2. Data Model

Three canonical entities, defined as JSON Schemas under `schemas/`. CSV exports flatten where reasonable.

### 2.1 `proposal`
```
proposal_id              # canonical key (we mint: f{fund}-{slug} or use Lidonation UUID)
fund                     # integer, 1–15
title
slug
proposer_ids             # list of proposer entity IDs
challenge / campaign     # category within the fund
amount_requested         # ADA
amount_received          # ADA (0 if not funded)
currency                 # usually ADA
yes_votes / no_votes / abstain_votes
ranking / scores         # alignment, feasibility, auditability (where available)
funding_status           # approved | not_approved | over_budget | leftover
project_status           # unfunded | funded | in_progress | complete | cancelled | unknown
funded_at
sources                  # array: [{source, url, fetched_at}]
confidence               # high | medium | low — per-field provenance bitmap also stored
links                    # ideascale_url, projectcatalyst_io_url, milestones_url, lidonation_url
ai_summary               # optional, attributed to Lidonation
```

### 2.2 `proposer`
```
proposer_id              # canonical key
display_name
team_members             # list
ideascale_profile_id     # if known
catalyst_profile_id      # if known
socials                  # twitter, github, discord, telegram, linkedin
proposal_ids             # back-reference
completed_count          # rolled up
outstanding_count
total_funded_amount
sources
```

### 2.3 `milestone` (F9 pilot + F10–F15)
```
proposal_id
milestone_number         # 1..N
title
budget
status                   # not_started | in_progress | submitted | accepted | rejected
delivered_at
poa_url                  # Proof of Achievement evidence
reviewer_signoffs        # list
closeout                 # boolean — is this the final closeout milestone (PCR/PCV)
sources
```

A `confidence` flag is **mandatory** on every row. F2–F5 completion fields default to `low`.

---

## 3. Per-Fund Source Map (decision table)

| Fund | Proposer + proposal | Win/Loss (authoritative) | Completion (authoritative) | Overall confidence |
|------|---------------------|--------------------------|----------------------------|---------------------|
| **F1** (pilot) | IdeaScale via Wayback CDX | N/A — no winners (pilot) | N/A | **Low / heroic** |
| **F2** | Lidonation API | `static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf` + IOG blog | IOG status flag only (10/11) | Medium |
| **F3** | Lidonation API | Google Drive PDF (linked from `/funds/3/voting-results`) | IOG status flag | Medium |
| **F4** | Lidonation API | Google Drive PDF | IOG status flag + scattered self-reports | Medium |
| **F5** | Lidonation API | Google Drive PDF | IOG status flag + Catalyst Swarm GitBook summaries | Medium |
| **F6** | Lidonation API | Google Drive PDF | IOG status flag + Lidonation `cx_monthly_reports` (sparse) | Medium |
| **F7** | Lidonation API | Drive PDF (`bit.ly/3HJNhuX`) | Lidonation monthly_reports | Medium-Good |
| **F8** | Lidonation API | Drive PDF | Monthly reports + proposer-hosted close-outs | Medium-Good |
| **F9** | Lidonation API | Drive PDF (`bit.ly/Fund9_Results`) | **Milestone Module (pilot, large projects)** + monthly reports | Good (large) / Medium (rest) |
| **F10** | Lidonation API + `projectcatalyst.io/funds/10` | `fund10-voting-results.pdf` + Lidonation | **Milestone Module (mandatory)** | **Excellent** |
| **F11** | Same | `/funds/11/voting-results` page | Milestone Module | **Excellent** |
| **F12** | Same | `/funds/12/voting-results` | Milestone Module | **Excellent** |
| **F13** | Same | `/funds/13/voting-results` | Milestone Module | **Excellent** |
| **F14** | Lidonation API (Catalyst Voices internal — no public API yet) | `/funds/14/voting-results` | Milestone Module (in-flight, 2 complete) | **Excellent** for delivered |
| **F15** | Same | TBD | Milestone Module (early) | Schema complete, no completions yet |

---

## 4. Repository Layout (GitHub-as-source-of-truth)

Proposed repo: **`mellod/catalyst-history-archive`** (open source).

```
catalyst-history-archive/
├── README.md
├── LICENSE-CODE                      # MIT
├── LICENSE-DATA                      # CC-BY-4.0  (attributes Lidonation, IOG, CF)
├── CITATION.cff
├── data/
│   ├── funds/
│   │   ├── fund-01/
│   │   │   ├── proposals.json
│   │   │   ├── proposals.csv
│   │   │   ├── proposers.csv
│   │   │   ├── _meta.json            # sources, fetched_at, coverage_notes, confidence
│   │   │   └── _provenance/
│   │   │       ├── lidonation/       # raw API page captures (gz)
│   │   │       ├── ideascale-wayback/
│   │   │       ├── iohk-pdfs/
│   │   │       └── milestones/
│   │   ├── fund-02/  ...  fund-15/
│   └── consolidated/
│       ├── all_proposals.csv         # unified schema across all funds
│       ├── all_proposers.csv         # deduped proposer entities
│       ├── all_milestones.csv        # F9+ where available
│       └── schema.md
├── schemas/
│   ├── proposal.schema.json
│   ├── proposer.schema.json
│   └── milestone.schema.json
├── etl/                              # Python, follows mellod-infra DEVELOPMENT_STANDARDS.md
│   ├── pyproject.toml                # ruff + pytest + type hints
│   ├── requirements.txt              # pinned
│   ├── .env.example
│   ├── README.md
│   ├── fetchers/
│   │   ├── lidonation_api.py
│   │   ├── projectcatalyst_funds.py
│   │   ├── milestones_scraper.py
│   │   ├── ideascale_wayback.py
│   │   └── on_chain_cip36.py         # optional sidecar
│   ├── normalizers/
│   │   ├── unify_proposals.py
│   │   └── reconcile_winners.py
│   └── validators/
│       └── validate_against_schema.py
├── docs/
│   ├── adr/
│   │   └── ADR-2026-05-13-source-strategy.md
│   ├── PER_FUND_SOURCES.md
│   ├── DATA_QUALITY.md
│   └── attributions.md
├── compose.yml                       # OPTIONAL Postgres + Jupyter for ad-hoc analysis
└── .github/
    └── workflows/
        ├── ci.yml                    # ruff + schema validate on PR
        ├── refresh-data.yml          # monthly cron → opens PR with diffs
        └── publish-snapshot.yml      # tag-based release
```

Design principles honored:
- **GitHub is the source of truth.** All datasets live in-repo as plain JSON/CSV. Diff-friendly.
- **Infrastructure as code.** ETL pipeline runs in GitHub Actions and (optionally) a Docker Compose service that mirrors mellod-infra conventions (Python N or N-1, ruff, type hints, `.env.example`, JSON-logs).
- **Never delete without approval.** Refresh job emits a PR; you merge.
- **Provenance preserved.** Raw captures live alongside normalized data; sources array on every row.

---

## 5. Phased Execution (6 weeks, plus ongoing)

**Phase 0 — Foundation (week 1)**
- Create GitHub repo, dual license, MIT (code) + CC-BY-4.0 (data).
- Write ADR-2026-05-13 documenting source strategy and confidence tiers.
- Define and lock JSON Schemas under `schemas/`.
- Scaffold `etl/` per `mellod-infra/docs/DEVELOPMENT_STANDARDS.md` (ruff, type hints, requirements pinned, `.env.example`).
- Wire CI (`ci.yml`).
- **Soft outreach:** email Lidonation introducing the project + proposing attribution + asking about rate limit guidance. (They explicitly call the API "free to the entire community" — but courtesy buys goodwill and possibly a higher rate-limit token.)

**Phase 1 — Lidonation ingestion (weeks 1–2)** — **biggest single ROI**
- Implement `fetchers/lidonation_api.py`.
- Polite client: 1–2 req/sec, exponential backoff on 429/5xx, identifiable `User-Agent: mellod-catalyst-archive/0.1 (lloydduhon@gmail.com)`.
- Endpoints: `/api/proposals` (475 pages × 24), `/api/fund-titles`, `/api/campaigns`, `/api/ideascale-profiles`, `/api/catalyst-profiles`, `/api/groups`, `/api/tags`, `/api/reviews`.
- Cache raw page JSON under `_provenance/lidonation/`.
- Normalize into per-fund `proposals.json` + `proposals.csv` + `proposers.csv`.
- **Result:** F2–F15 proposer/proposal data populated to ~95% completeness for the proposal entity.

**Phase 2 — Cross-verify winners with IOG voting-results (week 2)**
- Implement `fetchers/projectcatalyst_funds.py` — fetch each `/funds/N` HTML, parse Next.js JSON for `votingResultsUrl` + canonical counts.
- Download all linked PDFs (Drive links → curl with proper redirect handling).
- Parse with `pdfplumber` to extract proposal title + funded flag + ask.
- `normalizers/reconcile_winners.py` — produce `data/funds/fund-XX/_reconciliation.json` flagging any mismatch between Lidonation `funding_status` and IOG PDF. Manual triage of disputes.

**Phase 3 — Milestone capture for F10+ (week 3)**
- Implement `fetchers/milestones_scraper.py`.
- For each funded proposal in F9 (pilot)–F15, fetch `milestones.projectcatalyst.io/projects/{fundprefix}{proposal_id}` + sub-pages.
- Conservative concurrency (2 req/sec), gzip-cache HTML in `_provenance/milestones/`.
- Extract milestone count, statuses, evidence/PoA URLs, close-out report links.
- Output per-fund `milestones.csv`.

**Phase 4 — Fund 1 + low-confidence backfill (weeks 4–5, "heroic")**
- Wayback CDX query for `cardano.ideascale.com/*` snapshots in Sept–Dec 2020.
- Parse archived HTML with BeautifulSoup to recover Fund 1's ~56 proposals.
- Manual curation pass over Cardano Forum, IOG blog, and Catalyst Swarm GitBook for F1–F5 completion notes — captured as `_provenance/manual-notes/fund-XX.md`.
- Mark all F1–F5 completion fields as `confidence: low` with cited URLs.

**Phase 5 — On-chain registration sidecar (optional, week 5+)**
- Pull CIP-15/36 registrations via Koios `/tx_metalabels?_metalabels=eq.61284` for each fund's snapshot window.
- Reconstruct voting power per fund (or just store the raw registrations table).
- Lives under `data/registrations/fund-XX/cip36.csv` — **explicitly not** in the proposal/proposer/milestone schema. It's a sidecar, not a join key.

**Phase 6 — Consolidation, validation, release (week 6)**
- Generate `data/consolidated/all_proposals.csv` etc. via `normalizers/unify_proposals.py`.
- Run `validators/validate_against_schema.py` in CI on every PR.
- Write `docs/DATA_QUALITY.md` narrating per-fund confidence with concrete row counts.
- Cut a tagged GitHub Release: `snapshot-2026-MM-DD`.
- Announce on Cardano Forum + Lidonation, inviting community fixes via PR.

**Phase 7 — Ongoing (scheduled, indefinite)**
- `refresh-data.yml` runs monthly: re-pulls Lidonation API + Milestone Module deltas.
- Action opens an auto-PR with a diff summary ("3 new F15 proposals; 5 F14 milestones advanced; 1 F13 proposal flipped to complete").
- You review and merge — never auto-merge.
- Tag a fresh snapshot each quarter.

---

## 6. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| **Lidonation rate-limits / blocks us mid-crawl** | Polite client, identifiable UA, off-peak scheduling, contact them first, exponential backoff. Worst case: fall back to scraping the SPA HTML (Ziggy routes embedded). |
| **Catalyst Explorer breaks compatibly** (UUID migration like the legacy API) | Pin to JSON schema, snapshot raw responses in `_provenance/`, never delete old snapshots. We can replay from cache. |
| **Fund 1–5 completion data is fundamentally low quality** | Be explicit: `confidence: low`, cite every source, accept the limitation publicly in `DATA_QUALITY.md`. Don't fake precision. |
| **Catalyst Voices gateway becomes the new canonical source mid-build** | Monitor `api.projectcatalyst.io/api/v1/health/ready` weekly; when it returns 200, write `fetchers/catalyst_voices_gateway.py` as an additional fetcher and reconcile against Lidonation. |
| **PDF parsing of IOG voting-results misfires on weird PDF layouts** | Snapshot PDFs in `_provenance/iohk-pdfs/`. Spot-check parser output against known winner counts on the `/funds/N` page. Manual fixup CSVs allowed under `data/funds/fund-XX/_manual_corrections.csv`. |
| **License confusion** | MIT for our code, CC-BY-4.0 for the dataset, attribution table in `docs/attributions.md`, CITATION.cff at root. |
| **Scope creep ("let's also track DReps and governance actions")** | Out of scope for v1. Document in README as a possible future sidecar. |

---

## 7. Open Questions for Lloyd (before Phase 0)

These will shape Phase 0 directly. None block the research summary, but I want your call on each:

1. **Repo home.** Personal `lloydduhon/catalyst-history-archive`, the `mellod` org, or a new neutral org like `cardano-catalyst-archive`?
2. **License model.** MIT (code) + CC-BY-4.0 (data) is my recommendation. Alternative: CC0 (no attribution required) if you'd prefer the data be maximally reusable.
3. **Lidonation outreach.** Should I draft an email to Lidonation announcing the project and asking for rate-limit guidance before Phase 1?
4. **Catalyst Voices.** Should I email the Catalyst engineering team (`contact@projectcatalyst.io`) to ask for a working `cat-gateway` endpoint, or just wait for it to stabilize publicly?
5. **On-chain sidecar.** Include CIP-15/36 voter registration data in v1, or defer to a separate `catalyst-voting-power-archive` repo?
6. **F1–F5 completion data.** Accept "best-effort, low confidence" forever, or commit budget for manual reconstruction by a researcher?
7. **Compose service.** Ship a `compose.yml` with Postgres + Jupyter alongside the data (handy for analysis), or keep the repo pure data + ETL and let consumers BYO database?
8. **Naming.** "catalyst-history-archive" is descriptive but plain. Alternatives: "catalyst-corpus", "catalyst-record", "catalyst-historical-dataset"?

---

## 8. What gets done in Phase 0 (before any code)

1. You answer the 8 questions above.
2. I produce the ADR document and JSON Schemas as Markdown + JSON in this same `02-Projects/catalyst-history-archive/` folder for your review.
3. You approve the schemas.
4. I help you create the GitHub repo with `README`, `LICENSE-*`, schemas, and the `etl/` skeleton committed — but **no fetchers running yet**.
5. We pause for your sign-off before Phase 1.

Per your standing preference: **nothing gets deleted, nothing gets pushed to GitHub, no external service is hit until you approve each phase.**
