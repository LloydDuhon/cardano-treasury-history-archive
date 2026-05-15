# ADR: Project Catalyst Historical Data — Source Strategy and Confidence Tiers

**Date:** 2026-05-13
**Status:** Proposed
**Author:** Lloyd Duhon
**Applies To:** `catalyst-history-archive` repository (personal, `lloydduhon/cardano-treasury-history-archive`)

---

## Context

Project Catalyst, Cardano's community treasury program, has run from 2020 (Fund 1, pilot) through Fund 15 (active in 2026), funding thousands of community proposals across four distinct technology eras:

| Era | Funds | Voting tech | Proposal tech |
|---|---|---|---|
| Pilot | F1 | manual / forum | IdeaScale |
| IdeaScale + Jörmungandr | F2 – ~F11 | Jörmungandr sidechain | IdeaScale |
| Catalyst Core | ~F8 – F13 | catalyst-core + Jörmungandr | IdeaScale (deprecating) |
| Catalyst Voices | F14 + | Hydra / on-Cardano (in progress) | Catalyst Voices Flutter app |

There is **no single canonical source** for the full historical record. Available sources are heterogeneous in coverage, freshness, and authoritativeness. This ADR records the source-selection strategy for capturing proposer / proposal / win-loss / completion data for every fund, with explicit confidence tiers.

Research evidence supporting this decision is summarized in `../CATALYST-HISTORY-CAPTURE-PLAN.md` and was gathered on 2026-05-13.

---

## Decision

Adopt a **multi-source, provenance-preserved, confidence-tiered** capture strategy with the following layers:

### Layer 1 — Primary structured source (F2–F15)

**`https://www.catalystexplorer.com/api/*`** (Lidonation Catalyst Explorer).

- No auth, JSON, paginated (~475 pages of 24 proposals = 11,385 total at time of survey).
- Apache-2.0 codebase at `github.com/lidonation/catalystexplorer`.
- Covers Funds 2–15. Rich fields including proposer team, vote tallies, funding/project status, scores, AI summary.
- Data licensed for free community use (Lidonation's stated position).

**Decision:** Use as primary structured source for F2–F15 proposer/proposal data. Snapshot raw paginated responses under `_provenance/lidonation/` for replay.

### Layer 2 — Authoritative winner truth (F2–F13)

**`https://projectcatalyst.io/funds/{N}/voting-results`** with the embedded `votingResultsUrl` (typically PDFs on `static.iohk.io` for F2, Google Drive for F3–F9, inline PDFs from F10 onward).

**Decision:** Treat the IOG-published voting-results artifact as ground truth for win/loss. Cross-reconcile against Lidonation `funding_status`; flag and triage discrepancies. Snapshot PDFs under `_provenance/iohk-pdfs/`.

### Layer 3 — Authoritative completion truth (F10–F15)

**`https://milestones.projectcatalyst.io/projects/{id}`** + `/milestones/{n}`.

- No public API; HTML scrape. Conservative concurrency.
- Mandatory for all funded projects from Fund 10 forward.
- Snapshot HTML under `_provenance/milestones/`.

**Decision:** Use the Milestone Module as authoritative for F10–F15 completion data. Fund 9 partial coverage (pilot, large projects only) is also captured here when present.

### Layer 4 — Fallback for Fund 1 only

**Internet Archive Wayback CDX** (`web.archive.org/cdx/search/cdx?url=cardano.ideascale.com/*`) snapshots of `cardano.ideascale.com` proposal pages from September–December 2020.

**Decision:** Wayback CDX scrape is the only practical path for F1 (~56 pilot proposals, no funded winners). Accept fragility.

### Layer 5 — Confidence-tagged best-effort (F1–F5 completion)

Manual curation pass against Cardano Forum, IOG blog (`iog.io/news`), Catalyst Swarm GitBook, and the now-frozen "Catalyst Funded Reporting" Google Sheet.

**Decision:** F1–F5 completion fields are stored with `confidence: low` and citation URLs. We do **not** invent precision. `DATA_QUALITY.md` declares this publicly.

### Explicitly deferred — Catalyst Voices Gateway

`https://api.projectcatalyst.io` and the `cat-gateway` Rust service in `cardano-foundation/catalyst-voices` are the future canonical source. As of 2026-05-13 the public endpoint returns HTTP 500 and the seed data covers only F14–F15.

**Decision:** Monitor `/api/v1/health/ready` periodically. When the endpoint stabilizes, add a separate `fetchers/catalyst_voices_gateway.py` and reconcile against Lidonation. Not blocking for v1.

### Explicitly deferred — On-chain CIP-15/CIP-36 voter registrations

On-chain metadata label 61284 records voter eligibility and stake-weighted voting power, but **not** proposal outcomes (votes were cast off-chain on Jörmungandr / Hydra).

**Decision:** Defer to a separate future repository (`catalyst-voting-power-archive` or similar). Not part of v1 schema. Not a join key on `proposal`.

---

## Confidence Tiers

Every row in every fund's dataset carries a `confidence` field with one of:

- **`high`** — Authoritative source for that field is fully captured and machine-verified.
- **`medium`** — Authoritative source captured, but one or more secondary fields are inferred or cross-source reconciled.
- **`low`** — Best-effort reconstruction from secondary sources; expect inaccuracy.

Default confidence by fund and field family:

| Fund range | Proposal core | Win/loss | Completion |
|---|---|---|---|
| F1 | low | n/a (pilot) | n/a |
| F2–F5 | high | high | **low** |
| F6–F8 | high | high | medium |
| F9 | high | high | medium (high for pilot / large projects) |
| F10–F15 | high | high | high |

---

## Repository Structure (relevant decisions)

- **GitHub is the source of truth.** All data lives in-repo as plain JSON + CSV.
- **Personal repo:** `lloydduhon/cardano-treasury-history-archive`.
- **Licensing:** MIT for code (`LICENSE-CODE`), CC-BY-4.0 for data (`LICENSE-DATA`). `CITATION.cff` at root.
- **Provenance is mandatory.** Raw API/HTML/PDF captures preserved alongside normalized data under `_provenance/` per fund.
- **No deletion without approval.** Refresh runs open PRs; no auto-merge.
- **Compose service deferred.** Repo is pure data + ETL; consumers BYO database.

---

## Consequences

**Positive:**
- One repo, browsable on GitHub, with diff-friendly JSON/CSV. No infrastructure required to consume.
- Provenance preserved means we can replay normalization without re-hitting third-party services.
- Confidence tiers are honest about gaps rather than faking precision.
- Multi-source reconciliation produces a built-in audit trail.

**Negative / accepted limitations:**
- Fund 1 capture is fragile (Wayback dependency).
- F1–F5 completion data will never be machine-quality. This is documented publicly.
- Lidonation API is single-vendor for the bulk of the data. If it becomes unavailable, we have raw snapshots but new data flow stops until a fallback is built.
- Catalyst Voices integration is deferred; coverage of F14+ will lag the upstream system of record once it goes live.

**Mitigations:**
- Raw provenance allows full replay.
- Monthly refresh PRs surface upstream drift early.
- All sources documented in `docs/attributions.md` so a future maintainer can re-evaluate.

---

## Review

- Initial author review: Lloyd, 2026-05-13.
- Next review: at the close of Phase 6 (initial release) or when Catalyst Voices Gateway becomes publicly stable, whichever is first.

---

## Implementation Notes (Phase 1)

Added 2026-05-13 after probing the live Lidonation API. These are operational
specifics that do not change the source-strategy decision above but affect how
Layer 1 is implemented.

**Server-side fund filter is unavailable.** Live probes showed that
`?f[]={fund_uuid}` returns HTTP 500. Other variants (`fund=`, `fund_id=`,
`funds[]=`, `fund[]=`) return 200 but silently ignore the parameter (verified
by `total` remaining 11,385). `?per_page=` is rejected (HTML 500); page size is
locked at 24. The `?sort=` parameter is silently ignored. Pages are
mixed-fund - every page sampled contained proposals from ~8 different funds.

**Consequence: we do a flat sweep.** The Phase 1 fetcher walks
`/api/proposals?p=1..last_page` linearly without filter and caches each page to
a CENTRAL location:

    data/_raw/lidonation/fund-titles.json
    data/_raw/lidonation/page-NNNN.json.gz

The per-fund split happens in the normalizer
(`etl/normalizers/unify_proposals.py`), keyed off each record's
`record.fund.title` ("Fund 10" -> fund_number=10).

**Authoritative fund linkage is `record.fund.id` (UUID) and
`record.fund.title`** ("Fund 10"). The originally documented
`record.campaign.fund_id` is null in current responses; do not rely on it.

**Schema-vs-API surface notes:**
- `record.id` is a UUID (stored as `external_ids.lidonation_uuid`).
- `record.funding_status` matches our enum directly (`approved` /
  `not_approved`); we also map legacy `funded` / `unfunded`.
- `record.status` is the project status; we map `in-progress` -> `in_progress`
  and `completed` -> `complete` to match the schema enum.
- `record.currency` may be `USD`, `ADA`, or other; we normalize unknown values
  to `UNKNOWN` rather than silently dropping.
- `yes_votes_count` is raw lovelace for older funds; units vary by fund. We
  preserve the raw value and document the units caveat in `DATA_QUALITY.md`
  rather than convert.

**Politeness defaults baked into the fetcher:** 1.5 rps, identifiable
User-Agent with repo URL, exponential backoff (base 1.5, max 30s, 5 attempts),
atomic-write with fsync, idempotent re-runs (cached pages skipped unless
`--force`). All settings tunable via `.env`.

**Performance:** Full sweep at 1.5 rps is ~6 minutes wall, ~7 MB gzipped on
disk for 475 pages.

If the Lidonation API ever fixes the fund filter, this implementation note
should be revisited - per-fund snapshots would be cleaner.

## Implementation Notes (Phase 3)

Added 2026-05-13 after probing the Milestone Module.

**Layer 3 source is Supabase, not HTML.** The `milestones.projectcatalyst.io`
site is a Vite-built SPA (the served HTML is a 546-byte shell containing
only `<div id="app"></div>` plus script tags). All data is fetched from
a public Supabase project: `https://hutbpqoulajxnzwykvrf.supabase.co`.
The anon key is exposed in `/env.js` and is intended for client-side use.
We respect the same key from server-side (read-only) and identify our
client via a polite User-Agent.

**Tables we read (read-only via PostgREST):**
- `funds` (id 1..6 -> Fund 9..14)
- `challenges` (id, title, fund_id)
- `proposals` (one row per funded project)
- `soms` Statement of Milestones; **`current=true` filter required** to
  drop revision history from the normalized output
- `poas` Proof of Achievement (markdown content + active_reviews counter)
- `signoffs` (linking som_id <-> poa_id with reviewer user_id)

**Derived per-milestone status mapping:**
- `accepted` <- at least one row in `signoffs` for this som_id
- `under_review` <- a current PoA exists with `active_reviews > 0`
- `submitted` <- a current PoA exists with `active_reviews == 0`
- `not_started` <- no current PoA

`rejected`/`stalled`/`withdrawn` cannot be derived from the visible tables;
records in those states are left as the closest enum value or `unknown`,
to be corrected by hand if/when needed.

**Performance:** Full sweep is ~36 endpoint calls (6 tables x 6 funds),
under one minute at 1.0 rps. Versus the originally planned per-proposal
HTML scrape (would have been ~1,146 page fetches), this is a ~30x
reduction in upstream load.

If the Milestone Module ever migrates off Supabase, we revisit this
section. Provenance is preserved via gzipped JSON of every table response.
