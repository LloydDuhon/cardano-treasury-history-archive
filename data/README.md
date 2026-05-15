# data/

This directory holds the captured dataset. The current checked-in data is an
interim snapshot: Lidonation v1 proposal coverage for F2-F15, Milestone Module
data for F9-F14, and partial IOG/CF voting-results artifacts. It is not yet the
first full snapshot because Phase 2 reconciliation is blocked on missing
voting-results files.

## Layout

```
data/
├── _raw/                                # centralized raw captures (see _raw/README.md)
│   └── lidonation/
│       ├── fund-titles.json             # fund UUID -> title map
│       └── page-NNNN.json.gz            # one v1 paginator response per page
│   ├── koios_governance/
│   │   └── treasury-withdrawal-proposals.json # raw Koios governance actions
│   └── sundae_treasury/
│       └── treasury-fund-01-projects.json # raw Sundae GraphQL capture
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
│   ├── all_milestones.csv          # F9-F14 where available in interim data
│   └── schema.md                   # tabular schema explanation
├── historical/
│   ├── cardano-treasury-withdrawals/
│   │   ├── withdrawals.json         # on-chain TreasuryWithdrawals governance actions
│   │   └── _meta.json              # source and normalization metadata
│   └── treasury-fund-01/
│       ├── projects.json           # Sundae Treasury projects/contracts
│       ├── vendors.json            # report-ready vendor rollups
│       ├── milestones.json         # milestone payment states
│       └── _meta.json              # source and normalization metadata
└── registrations/                  # deferred — on-chain CIP-15/36, future
```

## Historical non-Catalyst sources

`data/historical/treasury-fund-01/` is a separate historical funding dataset
captured from the public Sundae Treasury GraphQL API behind
`https://treasury.sundae.fi`. It represents the `Intersect Treasury Contracts 1`
instance, not a Project Catalyst vote. Use it alongside `consolidated/` when
asking whether a current proposer has prior funding history in either Catalyst
or Treasury Fund 1.

For reports, join `treasury-fund-01/vendors.json` to current proposers by
normalized vendor/proposer name and, where present, by stake-address-like vendor
labels. Treat `total_contract_ada` as contracted/allocated value; milestone
status fields distinguish `Matured`, `Active`, `Paused`, and `Withdrawn` amounts.

`data/historical/cardano-treasury-withdrawals/` is a separate on-chain dataset
captured from Koios governance proposal data. It contains Conway-era
`TreasuryWithdrawals` governance actions, including withdrawal stake addresses,
requested lovelace/ADA amounts, proposal metadata, and ratification/enactment
status epochs. Treat this as authoritative for the on-chain governance action
and requested treasury withdrawal amount, not as evidence of downstream vendor
payment or project delivery.

Some on-chain withdrawals overlap with Treasury Fund 1. Join by proposal title,
amount, receiving stake address, and governance metadata before adding totals,
otherwise TF1 can be double-counted.

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

See `schemas/` for the canonical data model. See
`docs/IOG_RESULTS_ACCESS_TRACKER.md` for the remaining source artifacts needed
before a final full snapshot release.
