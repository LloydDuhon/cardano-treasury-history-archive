# Methodology: Vision 2030 funding-priority history

## Research question

How did Project Catalyst proposal demand, voter-selected funding, and documented
delivery vary over time when earlier proposals are retrospectively grouped under
the five pillars of the draft Cardano 2030 Strategic Framework?

The framework is a present-day analytical lens. It did not govern the older
funds and this report does not imply that historical proposers claimed alignment.

## Measures

- **Requested** includes every archived proposal. Amount is `amount_requested`.
- **Funded** includes `funding_status` values `approved` and `leftover`. Amount is
  `amount_received`; missing values remain missing rather than being imputed.
- **Delivered** requires both a funded outcome and `project_status: complete`.
  This guard prevents reused or inconsistent source status values on officially
  unfunded proposals from entering delivery totals.
- **Delivered amount** is the recorded award value attached to completed
  proposals, not a claim about project expenditure or tranche disbursement.
- Counts and amounts are reported. ADA, USD, and USDM remain separate; there is
  no retrospective conversion or cross-currency total.

The year is the year in which the fund's voting result was determined: F1 2020;
F2–F6 2021; F7–F9 2022; F10 2023; F11–F13 2024; F14 2025; F15 2026.

## Taxonomy

1. **Infrastructure & Research Excellence** — protocol and scaling;
   interoperability; security and resilience; core research.
2. **Adoption & Utility** — products and applications; DeFi and payments;
   identity; enterprise and real-world use; developer experience.
3. **Governance** — governance participation and tooling; Catalyst and funding
   systems; DAOs and collective decisions; auditability and policy.
4. **Community & Ecosystem Growth** — education and talent; regional growth;
   hubs and events; onboarding, communications, and outreach.
5. **Ecosystem Sustainability & Resilience** — treasury and tokenomics; SPO
   incentives; decentralization and long-term network economics.

`PX — Ambiguous / cross-pillar` is retained as a first-class review queue.
Environmental-use-case proposals are normally Adoption & Utility, not Pillar 5;
Pillar 5 follows the framework's network-economic meaning of sustainability.

## Classification

One primary pillar is assigned to each proposal so rollups do not double count.

1. A specific historical challenge name produces a high-confidence assignment.
2. Broad, open, miscellaneous, or missing challenges use deterministic phrase
   scoring across title, summary, problem, solution, and success definition.
3. A text assignment requires at least two phrase matches and a lead of at least
   two points over the second-place pillar. Otherwise the row remains `PX`.

The complete decision trail is in `classification-audit.csv`. Subcategory
rollups are published in `by-fund-subcategory.csv` and
`by-year-subcategory.csv`. The rules are version-controlled in
`etl/scripts/generate_funding_priorities_report.py`.

## Limits

- Delivery is documented completion, not an independent impact assessment.
- Funds 2–5 have weak per-project closeout evidence; Funds 6–9 are partial;
  Fund 10 onward is milestone-based. Recent funds are still accruing delivery.
- Fund 15 has no final funding outcomes in this archive snapshot.
- Requested and received amounts reflect source denominations and may not equal
  contemporary USD value or cash actually disbursed on a specific date.
- A primary-pillar classification simplifies genuinely cross-pillar work.

## Sources

- Cardano 2030 Strategic Framework (draft):
  <https://product.cardano.intersectmbo.org/vision/strategy-2030/>
- Archive source and confidence notes: `docs/PER_FUND_SOURCES.md` and
  `docs/DATA_QUALITY.md`.
