# catalyst-history-archive

An open historical record of [Project Catalyst](https://projectcatalyst.io/) on Cardano — proposers, proposals, win/loss, and completion status — captured from Fund 1 (2020) onward.

This repository is the source of truth for the dataset. It contains:

- **`data/funds/fund-XX/`** — per-fund normalized JSON + CSV, plus raw provenance captures
- **`data/consolidated/`** — unified CSV/JSON across all funds
- **`schemas/`** — JSON Schemas defining the canonical data model
- **`etl/`** — Python pipeline that fetches, normalizes, and validates the data
- **`docs/`** — ADRs, per-fund source map, data-quality narrative, attributions

## Status

- **Current phase:** Phase 0 (scaffolding). No data has been captured yet.
- **Next:** Phase 1 — Lidonation Catalyst Explorer API ingestion for Funds 2–15.
- See [`docs/CATALYST-HISTORY-CAPTURE-PLAN.md`](docs/CATALYST-HISTORY-CAPTURE-PLAN.md) for the full plan.

## Why this exists

Catalyst data is fragmented across four technology eras (IdeaScale, Jörmungandr, Catalyst Core, Catalyst Voices) and at least eight sources of varying authoritativeness. No single upstream offers a complete historical record. This repository consolidates what is available, preserves provenance, and labels confidence honestly so researchers can build on it.

## Data sources and confidence

Every record in this dataset carries a `sources[]` array (with raw artifact paths under `_provenance/`) and a `confidence` rating. Funds 10–15 are high-confidence end-to-end; Funds 2–9 are reliable for proposal core and win/loss but partial for completion; Fund 1 is fragile (recovered from Internet Archive snapshots) and Funds 1–5 completion data is explicitly best-effort.

Full attribution and source detail in [`docs/attributions.md`](docs/attributions.md) and the [source-strategy ADR](docs/adr/ADR-2026-05-13-source-strategy.md).

## Licensing

- **Code** (under `etl/`, workflows, schemas): MIT — see [`LICENSE-CODE`](LICENSE-CODE).
- **Data** (under `data/`): Creative Commons Attribution 4.0 International (CC-BY-4.0) — see [`LICENSE-DATA`](LICENSE-DATA). Attribution to upstream sources (Lidonation, IOG, Cardano Foundation, IdeaScale, community contributors) is required and documented in `docs/attributions.md`.

If you use this dataset in research or tooling, please cite per [`CITATION.cff`](CITATION.cff).

## Using the data

You don't need to run anything. Just clone and read the CSV/JSON files:

```bash
git clone https://github.com/lloydduhon/catalyst-history-archive
cd catalyst-history-archive
ls data/funds/
# Or pull just the consolidated dataset:
cat data/consolidated/all_proposals.csv | head
```

JSON Schemas under `schemas/` formally define every field.

## Running the ETL pipeline

See [`etl/README.md`](etl/README.md). Not required to use the data — only to refresh it.

## Contributing

Corrections and additions are welcome via PR. See [`CONTRIBUTING.md`](CONTRIBUTING.md). The most valuable contributions right now are:

- Filling in F1–F5 completion data from primary sources
- Identifying proposer-entity duplicates in `duplicate_candidates`
- Flagging incorrect win/loss or completion records

## Acknowledgements

This archive would not exist without prior work by:

- **[Lidonation](https://lidonation.com/)** and Darlington Wleh — the Catalyst Explorer team — for the open API and dataset that powers most of Funds 2–15. Code is Apache-2.0 at [`lidonation/catalystexplorer`](https://github.com/lidonation/catalystexplorer).
- **IOG / Input Output** for publishing per-fund voting-results PDFs and operating the Milestone Module.
- **Cardano Foundation** for the [`catalyst-voices`](https://github.com/cardano-foundation/catalyst-voices) program and CIP-15 / CIP-36 standards.
- **The Cardano community** for the proposals themselves.
