# data/

This directory holds the captured dataset. Currently empty — Phase 0 of the project has only set up the scaffolding.

## Layout

```
data/
├── _raw/                                # centralized raw captures (see _raw/README.md)
│   └── lidonation/
│       ├── fund-titles.json             # fund UUID -> title map
│       └── page-NNNN.json.gz            # one Laravel paginator response per page
├── funds/
│   ├── fund-01/
│   │   ├── proposals.json          # normalized array of proposal records
│   │   ├── proposals.csv           # flattened tabular view
│   │   ├── proposers.csv           # proposers referenced by this fund
│   │   ├── milestones.csv          # empty for F1–F8
│   │   ├── _meta.json              # sources used, fetched_at, coverage notes
│   │   ├── _reconciliation.json    # cross-source disagreements (when present)
│   │   └── _provenance/
│   │       ├── lidonation/         # raw API page captures (gz)
│   │       ├── ideascale-wayback/  # archived HTML snapshots
│   │       ├── iohk-pdfs/          # canonical voting-results PDFs
│   │       └── milestones/         # raw Milestone Module HTML
│   └── fund-02/ ... fund-15/
├── consolidated/
│   ├── all_proposals.csv           # all funds, unified schema
│   ├── all_proposers.csv           # deduped proposer entities
│   ├── all_milestones.csv          # F9+ where available
│   └── schema.md                   # tabular schema explanation
└── registrations/                  # deferred — on-chain CIP-15/36, future
```

## How records are written

Every file in `data/` is the output of an ETL run under `etl/`. Hand-edits are allowed for corrections but must update `sources[]` and `field_confidence` on affected records, and should ideally be re-runnable.

## How to consume

If you just want the data:

```bash
# Per-fund
cat data/funds/fund-10/proposals.csv

# Everything
cat data/consolidated/all_proposals.csv
```

If you want JSON Schema-validated structured data:

```bash
cat data/funds/fund-10/proposals.json | jq '.[] | select(.funding_status == "approved")'
```

See `schemas/` for the canonical data model.
