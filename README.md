# cardano-treasury-history-archive

An open archive of Cardano funding history across Project Catalyst, Treasury Fund 1, and current Treasury Fund 2 budget-process data. The archive preserves raw source snapshots, normalized datasets, provenance notes, and generated reports for comparing proposer funding history and proposal-scope overlap.

## What Is Here

- **Project Catalyst history:** normalized proposal, proposer, milestone, and funding-status data for Catalyst funds captured under `data/funds/` and `data/consolidated/`.
- **Treasury Fund 1 history:** Sundae Treasury contract, vendor, and milestone data under `data/historical/treasury-fund-01/`.
- **2025 Budget Reconciliation / Ekklesia data:** raw owner and proposal metadata from `2025budget.intersectmbo.org` under `data/_raw/intersect_budget_2025/`.
- **Cardano on-chain treasury withdrawals:** Koios governance-action data for `TreasuryWithdrawals` under `data/historical/cardano-treasury-withdrawals/`.
- **Treasury Fund 2 current snapshot:** raw 2026 Cardano Budget Process data from Hydra Voting under `data/_raw/hydra_voting/`.
- **Generated reports:** Treasury Fund 2 proposer-history, proposal-similarity, 2025 identity bridge, and TF1-to-2025 reconciliation outputs under `reports/treasury-fund-2/`.
- **Static explorer:** a browser-based Treasury Fund 2 history viewer under `site/`.
- **ETL and validation:** Python fetchers, normalizers, report generation, and schemas under `etl/` and `schemas/`.

## Current Reports

The primary working reports are in `reports/treasury-fund-2/`:

- `proposer-history.md` / `.csv` answers: for each Treasury Fund 2 proposer, where have they previously received funds in Project Catalyst and/or Treasury Fund 1, how much ADA did they receive, what outputs are documented, and are there delivery-risk signals?
- `scope-similarity.md` / `.csv` answers: for each Treasury Fund 2 proposal, what funded and completed Catalyst or Treasury Fund 1 projects appear similar in scope, with similarity score and confidence.
- `identity-bridge-2025.md` / `.csv` links current Treasury Fund 2 proposer names to 2025 Budget Process proposer/owner metadata.
- `tf1-ekklesia-reconciliation.md` / `.csv` reconciles Treasury Fund 1 contract records from the Sundae Treasury site against the original 2025 Ekklesia budget-process proposal records.
- `onchain-treasury-reconciliation.md` / `.csv` reconciles on-chain Cardano `TreasuryWithdrawals` actions against Treasury Fund 1 so overlapping amounts are visible and not double-counted.
- `_summary.json` records the current snapshot timestamps and generated row counts.

The static viewer in `site/` gives a browser interface over the same current
Treasury Fund 2 data and matched historical records. It can be served locally
with `python3 -m http.server` from the `site/` directory or published with the
included GitHub Pages workflow.

## Confidence

This is a provenance-first research dataset, not a final audit opinion. Each report includes confidence labels and source URLs where available.

Project Catalyst history is useful now for experimentation and broad proposer-history analysis. Completion and closeout evidence is strongest where milestone data exists and weaker for early Catalyst funds that depend on reconstructed or partial sources.

Treasury Fund 1 contract and milestone status comes from the Sundae Treasury data. The TF1-to-2025 reconciliation adds human-readable owner metadata from the Ekklesia process; high and medium matches are used conservatively in reports, while low-confidence candidates are retained for manual review.

On-chain Cardano treasury withdrawal actions come from Koios `proposal_list` governance data. This source is authoritative for the governance action and requested withdrawal amount, but it is not the same thing as downstream vendor disbursement or project delivery. Some rows overlap with Treasury Fund 1 and should not be double-counted without reconciliation.

Treasury Fund 2 data is a point-in-time snapshot of the current budget process and should be refreshed before publication or any final decision support.

## Using The Data

You do not need to run the ETL to inspect the archive:

```bash
git clone https://github.com/lloydduhon/cardano-treasury-history-archive
cd cardano-treasury-history-archive
ls data/consolidated/
ls reports/treasury-fund-2/
```

JSON Schemas under `schemas/` define the normalized Catalyst data model. Report CSVs are designed for spreadsheet review; Markdown versions are designed for human reading.

## Refreshing Reports

See `etl/README.md` for environment setup. The Treasury Fund 2 reports are generated from the ETL package:

```bash
cd etl
python -m scripts.generate_treasury_fund_reports
python scripts/generate_treasury_dashboard_data.py --repo-root .. --out ../site
```

Refresh raw snapshots before relying on the reports for publication, because the Hydra Voting and budget-process sites can change.

## Licensing

- **Code** under `etl/`, schemas, and workflows: MIT, see `LICENSE-CODE`.
- **Data** under `data/` and generated report artifacts: CC-BY-4.0, see `LICENSE-DATA`.

Attribution to upstream sources is required and documented in `docs/attributions.md`.

## Contributing

Corrections and additions are welcome by PR. The most valuable contributions are:

- Primary-source PDF or raw-data validation for Catalyst and budget-process records.
- Manual review of low-confidence TF1-to-2025 reconciliation candidates.
- Additional completion, closeout, or delivery-status evidence for historical funded projects.
- Entity-resolution corrections for proposers operating under multiple names.

## Acknowledgements

This archive builds on public data and tooling from Lidonation Catalyst Explorer, Project Catalyst, IOG / Input Output, Cardano Foundation, Intersect, Sundae Labs, and the Cardano community.
