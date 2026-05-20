# Attributions

This dataset is derived from multiple upstream sources. Per the CC-BY-4.0 license on the data, downstream users must preserve these attributions when redistributing.

## Primary structured source — Funds 2–15

**Lidonation Catalyst Explorer** — https://catalystexplorer.com

- Operator: **Lidonation Foundation Inc.**
- Code: https://github.com/lidonation/catalystexplorer (Apache-2.0)
- API: `https://www.catalystexplorer.com/api/v1/*` — no auth required for read endpoints
- Coverage: Funds 2 through 15, 11,528 proposals in the 2026-05-14 interim sweep
- License posture: Lidonation has consistently described the Catalyst Explorer API as "free to the entire community."

Lidonation's work is the single largest enabler of this archive. The Catalyst Explorer project was itself funded through Project Catalyst (Fund 9 onward), so attribution flows in both directions — much of the underlying labor was already paid for by the community via the same program this archive documents.

## Authoritative win/loss artifacts — Funds 2–13

**IOG / Input Output** — voting-results publications

- Per-fund landing pages: `https://projectcatalyst.io/funds/{N}/voting-results`
- Fund 2 PDF (canonical example): https://static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf
- Funds 3–9 voting-results PDFs are linked via Google Drive from the per-fund landing pages.

These artifacts are the canonical post-vote record for each fund. They are referenced in this archive via the `iohk_voting_results_pdf` source enum and snapshotted under `data/funds/fund-XX/_provenance/iohk-pdfs/`.

## Completion data — Funds 9 (pilot) through 15

**Catalyst Milestone Module** — https://milestones.projectcatalyst.io

- Operator: Project Catalyst team
- Pilot: Fund 9 (large projects only)
- Mandatory: Fund 10 onward
- Open-source companion repo: https://github.com/input-output-hk/catalyst-som

Milestone-level data, evidence URLs, reviewer signoffs, and close-out reports/videos all come from this system for F10+ records.

## Future system of record — Fund 14+

**Cardano Foundation Catalyst Voices** — https://github.com/cardano-foundation/catalyst-voices

- Operators: Cardano Foundation, formerly Input Output
- Rust gateway: `catalyst-gateway` (poem-openapi)
- Flutter app: https://app.projectcatalyst.io
- Standards: CIP-15, CIP-36 (defined at https://github.com/cardano-foundation/CIPs)

As of 2026-05-13 the public deployed gateway returns HTTP 500 and is not yet usable as a data source. This archive will integrate it when stable.

## Fund 1 — Internet Archive

The Fund 1 pilot proposals were never re-archived in any structured form. Recovery relies on:

- **Internet Archive Wayback Machine** — https://web.archive.org
- CDX endpoint used: `web.archive.org/cdx/search/cdx?url=cardano.ideascale.com/*`
- The Internet Archive is a 501(c)(3) nonprofit; please consider donating: https://archive.org/donate

## Standards and protocols

- **CIP-15** (Catalyst voting registration v1) — https://cips.cardano.org/cip/CIP-15
- **CIP-36** (Catalyst voting registration v2) — https://cips.cardano.org/cip/CIP-36

## Tooling referenced (not directly ingested in v1)

- `input-output-hk/voting-tools` — CIP-15/36 snapshot generator
- `input-output-hk/catalyst-core` — legacy Jörmungandr-era governance engine
- `input-output-hk/catalyst-toolbox` — tally and rewards calculator
- `input-output-hk/catalyst-fund-archive-tool` — Jörmungandr DB → CSV
- `cardano-foundation/hydra-voting-poc` — Hydra-based decentralized tally PoC

## Community sources

For best-effort backfill of low-confidence fields, the following community sources are cited inline where used:

- **Cardano Forum** — https://forum.cardano.org
- **IOG blog** — https://iog.io/news
- **Catalyst Swarm GitBook** — https://catalyst-swarm.gitbook.io
- Various proposer-hosted close-out pages (cited per record)

## AI-assisted review tooling

The Treasury Fund 2 prior-work overlap report uses a staged review process:

- Deterministic Python retrieval ranks historical Catalyst, Treasury Fund 1, on-chain treasury, and BuilderDAO records against each current Treasury Fund 2 proposal.
- Manual console adjudication rows are human analyst judgments recorded in the review JSONL.
- Local first-round AI screening rows are draft triage judgments generated on a workstation running Ollama with Qwen 3.5 4B.
- OpenAI Responses API adjudication, when used, is a separate review stage and should be attributed by model in the generated report metadata.

AI-assisted rows are not final audit findings. They are screening aids for prioritizing human review of candidate overlaps. The generated report records the adjudication source/model counts so downstream readers can separate deterministic retrieval, local model screening, OpenAI adjudication, and manual review.

## Maintainer

This archive is maintained by **Lloyd Duhon** (lloydduhon@gmail.com). It is a personal open-source project and is not affiliated with Lidonation, IOG, Cardano Foundation, or the Project Catalyst team. Errors are the maintainer's responsibility — corrections welcome via pull request.
