# On-chain Treasury Withdrawal Reconciliation

Generated: 2026-05-15T14:40:15Z
Koios TreasuryWithdrawals snapshot: 2026-05-15T13:36:32Z

Purpose: identify which Cardano on-chain TreasuryWithdrawals governance actions overlap with Treasury Fund 1 records, so viewers can use the on-chain source without double-counting TF1 contract amounts.

Counting policy: when an on-chain withdrawal overlaps TF1, count the on-chain row as the treasury action and use TF1 for contract and milestone details. Do not add the TF1 contract amount to the on-chain withdrawal amount. A negative amount delta usually means one TF1 contract is split across multiple on-chain withdrawal actions.

## Summary

- On-chain TreasuryWithdrawals analyzed: 72
- On-chain withdrawals with TF1 overlap: 35
- On-chain withdrawals without TF1 overlap: 37
- TF1 projects matched to on-chain withdrawals: 39
- High-confidence overlap rows: 34
- Medium-confidence overlap rows: 1

## Overlaps With Treasury Fund 1

### Withdraw ₳1,161,000 for zkFold ZK Rollup administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 1,161,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqwtnrdnx
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0009-25
- TF1 titles: zkFold ZK Rollup
- TF1 statuses: active
- TF1 contract total: 1,161,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0009-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigjofgwm4qtwn7r3e6nczaxo7jp4fmhzphozrpcuvnx5k2khlbtty

### Withdraw ₳1,300,000 for Blockfrost Platform community budget proposal

- On-chain status: enacted
- On-chain withdrawal amount: 1,300,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqyxzxz7k
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: UTXO-EC-0003-25
- TF1 titles: IOG - Blockfrost Platform Community Budget Proposal
- TF1 statuses: paused
- TF1 contract total: 1,300,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: UTXO-EC-0003-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreidgiirfod3axto3xf3nducsao5w4rp6vqrijeh5m6mqgdxotaafbq

### Withdraw ₳104,347 for MLabs Research towards Tooling for Elliptical Curves...

- On-chain status: enacted
- On-chain withdrawal amount: 104,347.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlzgf074ea
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0022-25,EC-0015-25,ER-0005-25
- TF1 titles: MLabs- Core Tool Maintenance: Cardano.nix & Plutarch, Research towards Tooling for Elliptical Curves
- TF1 statuses: paused
- TF1 contract total: 393,042.00 ADA
- Amount delta (on-chain minus TF1): -288,695.00 ADA
- Match: high (0.95)
- Basis: EC-0022-25,EC-0015-25,ER-0005-25: title=0.95; direct_title=0.95; amount=0.27
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreig4bosl5dfpmtqguybf4yaffkwo5hcaxxy2k7wlbwdl57twojfk2i

### Withdraw ₳12,000,000 for Cardano Builder DAO administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 12,000,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlp5u7pqqr
- Proposed/enacted epochs: 570 / 577
- TF1 project ids: EMI-0004-25
- TF1 titles: Rainfire DAO - Cardano Builder DAO 
- TF1 statuses: withdrawn
- TF1 contract total: 12,000,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EMI-0004-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreidlb2fusg7asmfcnugcrzmfkhk6sb32b4st5ieji2q3oxmbhm6sma

### Withdraw ₳130,903 for Lucid Evolution Maintenance administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 130,903.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqvckzwqt
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0008-25
- TF1 titles: Midgard Labs - Lucid Evolution Maintenance
- TF1 statuses: paused
- TF1 contract total: 130,903.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0008-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigfhg7nn4pshyogcokcuo7ohpjpw6gaatnm74hum5vungrqwvpxs4

### Withdraw ₳15,750,000 for a MBO for the Cardano ecosystem: Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 15,750,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlp2tyw3h6
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EG-0002-25
- TF1 titles: Intersect MBO - A member-based organization for the Cardano ecosystem
- TF1 statuses: paused
- TF1 contract total: 15,750,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EG-0002-25: title=1.00; direct_title=0.54; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreidy6xsjjpdccodhiurbdcvtcf5tqzkyfgx3ruuhso2ijjuovycuny

### Withdraw ₳199,911 for OpShin - Python Smart Contracts for Cardano

- On-chain status: enacted
- On-chain withdrawal amount: 199,911.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlzzy7m65d
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: ER-0002-25
- TF1 titles: OpShin - Python Smart Contracts for Cardano
- TF1 statuses: paused
- TF1 contract total: 199,911.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: ER-0002-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreialtiknfumaxc23xjqxs2r4g5qjca3tikopmottieu5iq2sr77b3i

### Withdraw ₳2,162,096 for Midgard - Optimistic Rollups administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 2,162,096.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqqfgyy3v
- Proposed/enacted epochs: 570 / 575
- TF1 project ids: EC-0001-25
- TF1 titles: Midgard - Optimistic Rollups
- TF1 statuses: paused
- TF1 contract total: 2,162,096.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0001-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreidjnukg5c7u5zlkxaciy4hkxfixvtquhx6uzlqpydvrxormfqpdm4

### Withdraw ₳212,000 for AdaStat.net Cardano blockchain explorer

- On-chain status: enacted
- On-chain withdrawal amount: 212,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpgcp0jyh
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EG-0001-25-02; EG-0001-25
- TF1 titles: AdaStat.net Cardano blockchain explorer (2 of 2); AdaStat.net Cardano blockchain explorer (1 of 2)
- TF1 statuses: active; active
- TF1 contract total: 212,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EG-0001-25-02: title=1.00; direct_title=1.00; amount=0.28; EG-0001-25: title=1.00; direct_title=1.00; amount=0.72
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigivcba5jtrmzvr4ilvokyyzbryry63cz6ctow7tjmmkjxpvgfbsq

### Withdraw ₳220,914 for Dolos: Sustaining a Lightweight Cardano Data Node

- On-chain status: enacted
- On-chain withdrawal amount: 220,914.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqsufvuyl
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0006-25,EC-0007-25,EC-0010-25
- TF1 titles: TxPipe - Pallas, UTxO RPC, Dolos
- TF1 statuses: paused
- TF1 contract total: 662,742.00 ADA
- Amount delta (on-chain minus TF1): -441,828.00 ADA
- Match: high (0.95)
- Basis: EC-0006-25,EC-0007-25,EC-0010-25: title=0.95; direct_title=0.95; amount=0.33
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreihqhuiuwdjyukw4ul5obxz656ndyz5najokjhdw7mbdscskyaalfu

### Withdraw ₳220,914 for Pallas: Sustaining Critical Rust Tooling for Cardano

- On-chain status: enacted
- On-chain withdrawal amount: 220,914.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqghuqg03
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0006-25,EC-0007-25,EC-0010-25
- TF1 titles: TxPipe - Pallas, UTxO RPC, Dolos
- TF1 statuses: paused
- TF1 contract total: 662,742.00 ADA
- Amount delta (on-chain minus TF1): -441,828.00 ADA
- Match: high (0.95)
- Basis: EC-0006-25,EC-0007-25,EC-0010-25: title=0.95; direct_title=0.95; amount=0.33
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigm5xreg7ezyedhowwecyy2qnue3bfhbw5dex5odmvunddeg5jsem

### Withdraw ₳220,914 for UTxO RPC: Sustaining Cardano Blockchain Integration

- On-chain status: enacted
- On-chain withdrawal amount: 220,914.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlq2yeptuu
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0006-25,EC-0007-25,EC-0010-25
- TF1 titles: TxPipe - Pallas, UTxO RPC, Dolos
- TF1 statuses: paused
- TF1 contract total: 662,742.00 ADA
- Amount delta (on-chain minus TF1): -441,828.00 ADA
- Match: high (0.95)
- Basis: EC-0006-25,EC-0007-25,EC-0010-25: title=0.95; direct_title=0.95; amount=0.33
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreibcranrq3y5eh7pcjuvq2tcmlapfw2pc7x3nazwp5lonx6docoayu

### Withdraw ₳26,840,000 for Input Output Research (IOR): Cardano Vision - Wor...

- On-chain status: enacted
- On-chain withdrawal amount: 26,840,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlzqhm6e8q
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: UTXO-ER-0001-25
- TF1 titles: IOR - Cardano Vision Work Program 2025
- TF1 statuses: withdrawn
- TF1 contract total: 26,840,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.96)
- Basis: UTXO-ER-0001-25: title=0.95; direct_title=0.47; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigq3zbxymon7of3x4jtn7zrzjk2merntcd54yhvmgsjsduq6h3zwa

### Withdraw ₳266,667 for Cexplorer.io -- Developer-Focused Blockchain Explorer...

- On-chain status: enacted
- On-chain withdrawal amount: 266,667.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpyflfc4s
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0021-25
- TF1 titles: Vellum Labs: Developer-Focused Blockchain Explorer for Cardano
- TF1 statuses: withdrawn
- TF1 contract total: 266,667.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: medium (0.86)
- Basis: EC-0021-25: title=0.83; direct_title=0.83; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreicrrim5wicmsnrjpw7gp52jmebn7a2ly6j4eopjkvdsol6adyboqu

### Withdraw ₳3,126,000 for Ecosystem Exchange Listing and Market Making service...

- On-chain status: enacted
- On-chain withdrawal amount: 3,126,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpcdq823y
- Proposed/enacted epochs: 570 / 578
- TF1 project ids: EMI-0006a-25&EMI-0006b-25
- TF1 titles: Flowdesk - Market Making as a service & Ecosystem Exchange Listing
- TF1 statuses: paused
- TF1 contract total: 3,126,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EMI-0006a-25&EMI-0006b-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreidb56gwlzeuzav2xfubcbqa7txllbl2byiadnlxjdr2dgaqgb7z4m

### Withdraw ₳300,000 for Ledger App Rewrite administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 300,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqj0vdlhj
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0011-25 EC-0005-25
- TF1 titles: VacuumLabs - Hardware Wallets Maintenance & Ledger App Rewrite
- TF1 statuses: paused
- TF1 contract total: 724,800.00 ADA
- Amount delta (on-chain minus TF1): -424,800.00 ADA
- Match: high (0.95)
- Basis: EC-0011-25 EC-0005-25: title=0.95; direct_title=0.95; amount=0.41
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreibwg74hpx5vyyixzggxdkunrqy6kdkx2mpp57r6fknkqe7z263omm

### Withdraw ₳314,800 for PyCardano administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 314,800.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlzyc3clg6
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: ER-0003-25
- TF1 titles: PyCardano - FAIR IO, LLC
- TF1 statuses: active
- TF1 contract total: 314,800.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.96)
- Basis: ER-0003-25: title=0.95; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigrw7v6q2wcnbgjd22ev6eepitgaegtkkmhzwmsccfxmejkc3okbm

### Withdraw ₳4,000,000 for Expanding Stablecoin / Cardano Native Asset Support...

- On-chain status: enacted
- On-chain withdrawal amount: 4,000,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlp730y0dn
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EMI-0009-25
- TF1 titles: Anzens - Expanding Stablecoin / Cardano Native Asset Support / Fiat Ramps
- TF1 statuses: paused
- TF1 contract total: 4,000,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EMI-0009-25: title=1.00; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreihki45xehzrcyk6e7onyjc3u4mjg3vbd72oi5wfg2h6blemtr65yq

### Withdraw ₳424,800 for Hardware Wallets Maintenance administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 424,800.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqx488pdm
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0011-25 EC-0005-25
- TF1 titles: VacuumLabs - Hardware Wallets Maintenance & Ledger App Rewrite
- TF1 statuses: paused
- TF1 contract total: 724,800.00 ADA
- Amount delta (on-chain minus TF1): -300,000.00 ADA
- Match: high (0.95)
- Basis: EC-0011-25 EC-0005-25: title=0.95; direct_title=0.95; amount=0.59
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreicmz5a6ylplflowjdj7vjzp6glt45k2r6mnhwlmzq7kjkl3fvuzeu

### Withdraw ₳5,885,000 for OSC Budget Proposal - Paid Open Source Model...

- On-chain status: enacted
- On-chain withdrawal amount: 5,885,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqkqx0ecg
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0013(1,2,7)-25
- TF1 titles: OSC - Maintainer Retainer, Tooling Sustainability, Security Incident Management Programs
- TF1 statuses: paused
- TF1 contract total: 3,975,000.00 ADA
- Amount delta (on-chain minus TF1): 1,910,000.00 ADA
- Match: high (0.95)
- Basis: EC-0013(1,2,7)-25: title=0.95; direct_title=0.41; amount=0.68
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreiedjhlwerulq5qg5tku2qqremf2cf2dguxvktttnjddei3fxct37a

### Withdraw ₳578,571 for Gerolamo - Cardano node in typescript

- On-chain status: enacted
- On-chain withdrawal amount: 578,571.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqczags6z
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0014-25
- TF1 titles: Harmonic Laboratories: Gerolamo - Cardano Node in typescript
- TF1 statuses: paused
- TF1 contract total: 578,571.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.96)
- Basis: EC-0014-25: title=0.95; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreig7hi75t33nvu5t6y4hqf26thdpwvwvqcuzo3o3ehccslrwtf6bwe

### Withdraw ₳583,000 for Eternl Maintenance administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 583,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpqx4t762
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0018-25
- TF1 titles: Tastenkunst GmbH - Eternl Maintenance
- TF1 statuses: paused
- TF1 contract total: 583,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0018-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreiechnwimuhwdwovwscljcsypzjlidrmktcbcssoovbgwgxkm4g4d4

### Withdraw ₳592,780 for Beyond Minimum Viable Governance: Iteratively Improvin....

- On-chain status: enacted
- On-chain withdrawal amount: 592,780.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpvhtd5td
- Proposed/enacted epochs: 570 / 578
- TF1 project ids: UTXO-EG-0003-25
- TF1 titles: IOG - Beyond Minimum Viable Governance
- TF1 statuses: active
- TF1 contract total: 592,780.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.96)
- Basis: UTXO-EG-0003-25: title=0.95; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigltrp3abb6s667vrtnyspriii2j4wg25cieulbn26s3v36d4qsay

### Withdraw ₳6,000,000 for Cardano Summit 2025 and regional tech events

- On-chain status: enacted
- On-chain withdrawal amount: 6,000,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpsn5rx0e
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EMI-0002-25
- TF1 titles: Cardano Foundation - Cardano Summit 2025 and regional tech events
- TF1 statuses: withdrawn
- TF1 contract total: 6,000,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EMI-0002-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreidcvqu57gic4bigicuk6ssiykrkrfzi7c3jlwgiyxuskggqnyvcim

### Withdraw ₳6,000,000 for Unveiling the First Unified Global Events Marketing S...

- On-chain status: enacted
- On-chain withdrawal amount: 6,000,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpjq3z9u5
- Proposed/enacted epochs: 570 / 577
- TF1 project ids: EMI-0003-25
- TF1 titles: Cardano Foundation - Unveiling the First Unified Global Events Marketing Strategy for Cardano
- TF1 statuses: withdrawn
- TF1 contract total: 6,000,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EMI-0003-25: title=1.00; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreihhdmx6eumwipv4zlhlrbbkz6uj52y6xpzpjgwfnkzzzamtqgmq4u

### Withdraw ₳600,000 for Complete Web3 developer stack to make Cardano the smart...

- On-chain status: enacted
- On-chain withdrawal amount: 600,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlq5nrw6t9
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0012-25
- TF1 titles: GO MAESTRO INC - Complete Web3 developer stack
- TF1 statuses: withdrawn
- TF1 contract total: 600,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.96)
- Basis: EC-0012-25: title=0.95; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreicc2dbqlrkqhahasq2qqho3lry2axt4adrfnamro43m56v5sib7hi

### Withdraw ₳605,000 for A free Native Asset CDN for Cardano Developers

- On-chain status: enacted
- On-chain withdrawal amount: 605,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpx66gmxa
- Proposed/enacted epochs: 570 / 578
- TF1 project ids: EC-0023-25
- TF1 titles: NFTCDN - A free Native Asset CDN for Cardano Developers
- TF1 statuses: active
- TF1 contract total: 605,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0023-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreihd2hqcfvssop4aqxxqoch63ds6mkpapsfm7j7onyvemzayiby4ua

### Withdraw ₳657,692 for Scalus - DApps Development Platform

- On-chain status: enacted
- On-chain withdrawal amount: 657,692.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpz4s2af8
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0020-25
- TF1 titles: Lantr - Scalus: DApps Development Platform
- TF1 statuses: active
- TF1 contract total: 657,692.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0020-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreiceukwtpmes66twb3axkdmftpg3p5vyfolgcyhkentlbuilc274fq

### Withdraw ₳69,459,000 for Catalyst 2025 Proposal by Input Output: Advancing De...

- On-chain status: enacted
- On-chain withdrawal amount: 69,459,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpwywvhcq
- Proposed/enacted epochs: 570 / 575
- TF1 project ids: UTXO-EMI-0001-25; EMI-0001a-25
- TF1 titles: IOG - Advancing Decentralised Community Innovation Funding & Infrastructure; Catalyst FC - Catalyst 2025 Proposal
- TF1 statuses: paused; paused
- TF1 contract total: 69,459,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.95)
- Basis: UTXO-EMI-0001-25: title=0.95; direct_title=0.24; amount=0.07; EMI-0001a-25: title=0.95; direct_title=0.95; amount=0.92
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreid2pq5icpp77nfvdvnb5ipy3fqs77tpnls4ngxy6semzkdq7d2z7y

### Withdraw ₳700,000 for ZK Bridge administered by Intersect

- On-chain status: enacted
- On-chain withdrawal amount: 700,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlq77jt4x4
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0017-25
- TF1 titles: Cooperativa de Trabajo Eryx - ZK Bridge
- TF1 statuses: active
- TF1 contract total: 700,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0017-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreians5wdbxjgttbajinzfrhdxd7q7mzpfahsyyjntcq4xekts4qasu

### Withdraw ₳750,000 for Cardano Product Committee: Community-driven 2030 Carda...

- On-chain status: enacted
- On-chain withdrawal amount: 750,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlzxt5eumh
- Proposed/enacted epochs: 570 / 578
- TF1 project ids: ER-0004b-25
- TF1 titles: Product Research (1of2)
- TF1 statuses: withdrawn
- TF1 contract total: 80,000.00 ADA
- Amount delta (on-chain minus TF1): 670,000.00 ADA
- Match: high (0.95)
- Basis: ER-0004b-25: title=0.95; direct_title=0.52; amount=0.11
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreicjt5d4y7phbqwyhfkmtz75u2nck3is5cuywkcisnmtsuibdrm3li

### Withdraw ₳889,500 for Cardano Ecosystem Pavilions at Exhibitions

- On-chain status: enacted
- On-chain withdrawal amount: 889,500.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlp679xfzf
- Proposed/enacted epochs: 570 / 578
- TF1 project ids: EMI-0007-25
- TF1 titles: Supplyoneers FZ-LLC - Cardano Ecosystem Pavilions at Exhibitions
- TF1 statuses: mixed
- TF1 contract total: 889,500.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EMI-0007-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreicewinu7ogkkxho7ubwpi6q4iy2xqs2pv4lhvueyz6qe3rkc2icru

### Withdraw ₳96,817,080 for 2025 Input Output Engineering Core Development Proposal

- On-chain status: enacted
- On-chain withdrawal amount: 96,817,080.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqz6d98zp
- Proposed/enacted epochs: 570 / 575
- TF1 project ids: UTXO-EC-0002-25-06; UTXO-EC-0002-25-05; UTXO-EC-0002-25-04; UTXO-EC-0002-25-03; UTXO-EC-0002-25-02; UTXO-EC-0002-25-01
- TF1 titles: Input Output Engineering Core Development Proposal (6of6); Input Output Engineering Core Development Proposal (5of6); Input Output Engineering Core Development Proposal (4of6); Input Output Engineering Core Development Proposal (3of6); Input Output Engineering Core Development Proposal (2of6); Input Output Engineering Core Development Proposal (1of6)
- TF1 statuses: paused; paused; paused; paused; paused; paused
- TF1 contract total: 84,585,391.00 ADA
- Amount delta (on-chain minus TF1): 12,231,689.00 ADA
- Match: high (1.00)
- Basis: UTXO-EC-0002-25-06: title=1.00; direct_title=1.00; amount=0.35; UTXO-EC-0002-25-05: title=1.00; direct_title=1.00; amount=0.12; UTXO-EC-0002-25-04: title=1.00; direct_title=1.00; amount=0.05; UTXO-EC-0002-25-03: title=1.00; direct_title=1.00; amount=0.04; UTXO-EC-0002-25-02: title=1.00; direct_title=1.00; amount=0.07; UTXO-EC-0002-25-01: title=1.00; direct_title=1.00; amount=0.25
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreigt5xy56qjxd7dl2s7u6jxec2cfxevynppvgnnjifc2wawr7md5ha

### Withdraw ₳99,600 for BloxBean Java Tools Maintenance and Enhancement

- On-chain status: enacted
- On-chain withdrawal amount: 99,600.00 ADA
- On-chain proposal id: gov_action193leqzml768nz7nmpepzx822a5mzyanqhtewaxjtul5gp6uhwvfsqgl2qg0
- Proposed/enacted epochs: 570 / 576
- TF1 project ids: EC-0019-25
- TF1 titles: BloxBean Java Tools Maintenance and Enhancement
- TF1 statuses: active
- TF1 contract total: 99,600.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (1.00)
- Basis: EC-0019-25: title=1.00; direct_title=1.00; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: ipfs://bafkreibelpp2qzjcpeizeobf57tmhl4q6kauutytdve3mqzzjxzp2jqjxm

### Withdraw ₳5M for Cardano's Global Listing Expansion - Powered by Snek

- On-chain status: expired
- On-chain withdrawal amount: 5,000,000.00 ADA
- On-chain proposal id: gov_action1r44w54hx553mz0sr4cc07f8tlxzj2sa57l2pt3l9pa2ldw42fc7sq5q3rtn
- Proposed/enacted epochs: 573 / not enacted
- TF1 project ids: EMI-0010-25
- TF1 titles: Snek Foundation - ₳5M Loan for Cardano's Global Listing Expansion 
- TF1 statuses: withdrawn
- TF1 contract total: 5,000,000.00 ADA
- Amount delta (on-chain minus TF1): 0.00 ADA
- Match: high (0.96)
- Basis: EMI-0010-25: title=0.95; direct_title=0.95; amount=1.00
- Counting guidance: TF1 overlap: use the on-chain row as the treasury action and TF1 rows for contract/milestone detail; do not add these amounts together.
- Metadata: https://raw.githubusercontent.com/snekadmin/Public/refs/heads/main/data_final.jsonld

## No TF1 Overlap Found

### [OriLife × TonFarm] Identifying 180 Million Durians Without Physical Labels

- On-chain status: active
- On-chain withdrawal amount: 2,400,000.00 ADA
- On-chain proposal id: gov_action19avrmrhm0gqa4qwlgvh4vxj6nwe02ay42h828cva2zt6n0asddfqqtgph5d
- Proposed/enacted epochs: 628 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: https://most-brass-sun.quicknode-ipfs.com/ipfs/QmSNGYbjMQfb8tMvPtqi5bdMeXsV5M27iFecFvddWmC8xL

### Blockfrost: Maintenance and Next Generation Indexing

- On-chain status: active
- On-chain withdrawal amount: 7,920,000.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qwt8k9fx
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmSaGx6WutdwLgfsw34JyawNf1a7XuK1YchEerdKSp8EkT

### Cardano at TOKEN2049 Singapore 2026: Baseline ‘Platinum' Sponsorship Proposal

- On-chain status: active
- On-chain withdrawal amount: 3,303,750.00 ADA
- On-chain proposal id: gov_action18u8lpkzge2csxe3plynn9lh4agwtv3nrqkyfwalwj4ykjv7l68jqqzmul9z
- Proposed/enacted epochs: 628 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreibmdzs4o5samwbjct7j6ufjbvqfyqj7yudgrklnb2yi3yznle3yae

### Cardano at TOKEN2049 Singapore 2026: Top-Up ‘Title’ Sponsorship Upgrade

- On-chain status: active
- On-chain withdrawal amount: 1,768,167.00 ADA
- On-chain proposal id: gov_action1kj6ghzuz9wcq88f3y72cyyeekdcemlq0dqk4zpjd4eck5assuypqq0pckkw
- Proposed/enacted epochs: 628 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreifl24qjwnj4qa2vqaun3wfwg7z4lzcgg3okdpdbqoa4oiouwfwdsi

### Cardano dOSPO and OMF Program

- On-chain status: active
- On-chain withdrawal amount: 12,000,000.00 ADA
- On-chain proposal id: gov_action1pv7g8d0x9f3kqw2gcfrmgl8aqy38jat05wx0wwcvdsvuuclss6xqqhpzemv
- Proposed/enacted epochs: 630 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmP76MXJwp19ZAcX8soUPyh5jcvMoK1DoLbxAJT9LLRhDK

### Cardano Vision 2026: Human Centred, Scalable, Post Quantum Secure - IO Research

- On-chain status: active
- On-chain withdrawal amount: 32,916,000.00 ADA
- On-chain proposal id: gov_action1ttgs45ulfxs0jwkfrecystc3flduhszmyzk8wnd7yw5za77tsg9qq4afmus
- Proposed/enacted epochs: 629 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://Qmd1pXncVGaAwaZEBcDQqyj9jLjixk2mRpBwpuf24occP9

### Eternl: Path to Sustainability (2026-2027)

- On-chain status: active
- On-chain withdrawal amount: 1,680,000.00 ADA
- On-chain proposal id: gov_action1ngpqafax5rvp8lcgey4asvqtycrh4e56fwp8cn2r9trx2ysryhtsqdm3w3z
- Proposed/enacted epochs: 631 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmWmEKFTae7Q12HUeVyMui6ReCuTXRx55W6eahBGn9ECgn

### IO & Ensurable Systems: Cardano Maintenance Initiative

- On-chain status: active
- On-chain withdrawal amount: 62,134,630.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qx4njfhm
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmZMFAZvCxW6HpRC1EKzNcensJv9N89yzKPn7uRTTJdTpx

### IO & Midgard Labs: L2 Scalability Initiative

- On-chain status: active
- On-chain withdrawal amount: 10,425,871.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qghg4q43
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://Qmf3GSWna8PQFF2Vi5Css4R5pvGfaVUZ1zhCfHw9LqGKNV

### IO & VacuumLabs: Enhancing Plutus - Performance, Correctness, and Usability

- On-chain status: active
- On-chain withdrawal amount: 11,877,575.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qvczhx6t
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmPkZ6Azo1tJfWVRjwn8G1Qk7k1SC3Vk3L21WFPSracCzg

### IO: Cardano High Assurance Technical Collaboration

- On-chain status: active
- On-chain withdrawal amount: 13,078,578.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3q2yd5rxu
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmfM3VRtGvpmxTDYrgGJoPSLW41SiNyeazfjusg98jrATS

### IO: Cardano Upgrades

- On-chain status: active
- On-chain withdrawal amount: 13,103,039.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qz6es0cp
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmeNzwKE9bMyr65E4Dxtvoji7WBbazXUVykqQWq1pHXZvQ

### IO: Consensus Initiative

- On-chain status: active
- On-chain withdrawal amount: 27,714,342.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qyxkn2yk
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmNqVt8X1EX9iJJXGaEeiZ5nbePL91NkZcoVedpn6gfKWA

### IO: Developer Experience Initiative

- On-chain status: active
- On-chain withdrawal amount: 3,601,926.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qqfu3vtv
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmUnSimkwuaXX357ugYxDkiUMzsKTYgcWvV74xWbiXUt3Y

### Pebble & Ecosystem maintenance: TypeScript core of Cardano

- On-chain status: active
- On-chain withdrawal amount: 4,600,000.00 ADA
- On-chain proposal id: gov_action1ggr2uz7prwn5l84cdn2krwngfez0p7wluy4u3u3ez9pz5ls2whesqnsjly8
- Proposed/enacted epochs: 629 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmYJynuvpv1mY7yWDL763LcscHrFSCAW9d8SvCDf4BRdHK

### Pogun: Capital Without Compromise

- On-chain status: active
- On-chain withdrawal amount: 12,290,000.00 ADA
- On-chain proposal id: gov_action1w0shrfxqwv95kk0v4cn34wylz25a2cmqkq5jpc0e2yrahhqava3qsuae57l
- Proposed/enacted epochs: 626 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmVdGh1cXgsMXGRS7mzxurxtkaqhU7VJMjx4piNSSHrBs2

### Revised Cardano Summit 2026 Singapore

- On-chain status: active
- On-chain withdrawal amount: 7,800,000.00 ADA
- On-chain proposal id: gov_action10dp9wzmgt2nqshyrghufff4sfhcxedhmzluly5k0azguatnsthwqqs84cjf
- Proposed/enacted epochs: 627 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmQeNSMNUDWy75tgjPLqqUXDN7YvkVH6GS8iHx6P8adCAy

### Scalus: Cardano’s Application Platform for Building, Launching, and Scaling

- On-chain status: active
- On-chain withdrawal amount: 8,503,000.00 ADA
- On-chain proposal id: gov_action1uzgqlh049u0j7epel29r425vyf9ttxmqwngw9kemyly0q6cwt5esqpwp09a
- Proposed/enacted epochs: 630 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmPuukXDGrY4VjeprLZhovQfWCY5RDyXjQAPUKhRFNPiDT

### The first node in the browser; a Cardano USP

- On-chain status: active
- On-chain withdrawal amount: 4,600,000.00 ADA
- On-chain proposal id: gov_action1guz68e8zkwphcdc8wnp40cclkv92qgnel7xnffmsmp2ljp09qtwqq596k4c
- Proposed/enacted epochs: 629 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmbQPrRhUUtvqNitu9mgC8esM3kXmR5iHGhEkLX1UZaLDy

### Tweag Core Cardano Infrastructure: Treasury Withdrawal 2026–2028

- On-chain status: active
- On-chain withdrawal amount: 39,787,316.00 ADA
- On-chain proposal id: gov_action14u26vcn3wmcnhc5pqrt6494ypugr7c7f3e2ns60r32cntl6zjtxsqqgeu8p
- Proposed/enacted epochs: 628 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreifdoitcxw4anxadosoqi5y5ny647hym4u62gpyvkkuyg7wpnq6gbi

### Amaru Treasury Withdrawal 2025

- On-chain status: enacted
- On-chain withdrawal amount: 1,500,000.00 ADA
- On-chain proposal id: gov_action1vrkk4dpuss8l3z9g4uc2rmf8ks0f7j534zvz9v4k85dlc54wa3zsqq68rx0
- Proposed/enacted epochs: 566 / 571
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreifw3qs7brjn4tdvyprnh2r343oerbdghasp5ws6ro55frbpll3dta

### Amaru Treasury Withdrawal 2026

- On-chain status: enacted
- On-chain withdrawal amount: 10,142,000.00 ADA
- On-chain proposal id: gov_action19uhuy5uame2s60yrh6n8cyds8ps5q7tkh05dqlzmpcfy429p9w4qq5ll3g0
- Proposed/enacted epochs: 614 / 621
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreicshobgfe6o6siinj6ym4yxpz4dyyf3dqfex3w42htfvhpdn6msfu

### Cardano Defi Liquidity Budget - Withdrawal 1

- On-chain status: enacted
- On-chain withdrawal amount: 800,000.00 ADA
- On-chain proposal id: gov_action1uhzd06a26qavzflvrx3gvcz6rzxkl6su2ns8t3seef5e8dl6nlgsqcgtufg
- Proposed/enacted epochs: 617 / 625
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: https://raw.githubusercontent.com/theeldermillenial/2025-liquidity-budget/f824da7f0c2dbab15e324d1736a967de87d34f7d/w1.jsonld

### Cardano x Draper Dragon: Orion Fund

- On-chain status: enacted
- On-chain withdrawal amount: 50,000,000.00 ADA
- On-chain proposal id: gov_action13qr78nhrhetywapvx2wpm63y9uxpc2dc45zsu9gkncasxqhuhltqqqfu32x
- Proposed/enacted epochs: 618 / 624
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmPXYnQ65EuKCVPrWfDqFZmiF8Y4PzxZ87XrGs6UaMkNru

### Dingo: a Production-Grade Block Producer in Go by Blink Labs

- On-chain status: enacted
- On-chain withdrawal amount: 6,900,000.00 ADA
- On-chain proposal id: gov_action17dfgtkeufcy945e3ssanqpmn09ft3gezhvepvvg7msmlmaz260dqqjtsmpe
- Proposed/enacted epochs: 617 / 625
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreibeffgc4ow5rxbttesgqqe36copa5rejtsw6b4jruwow2p3wahxtq

### Loan ₳5,000,000 to Expand Cardano's Global Listings

- On-chain status: enacted
- On-chain withdrawal amount: 5,000,000.00 ADA
- On-chain proposal id: gov_action1q0m8z7glm9cprucwf44hdjdfra8khnakpm3hu5ueh929hvljw4aqqzuxfxz
- Proposed/enacted epochs: 590 / 598
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreidl43ghacdpczaims63glq5kepaa63d63cr5mrpznv56jdm7e2eny

### Withdraw ₳11,070,323 for TWEAG's Proposals for multiple core budget project...

- On-chain status: enacted
- On-chain withdrawal amount: 11,070,323.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlqudh2k4c
- Proposed/enacted epochs: 570 / 576
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreidlgy2mljdxjknsxzpy6im5xkgsw4ticvwqmgedecs53dzdqhgdlu

### Withdraw ₳243,478 for MLabs Core Tool Maintenance & Enhancement: Plutarch

- On-chain status: enacted
- On-chain withdrawal amount: 243,478.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlq63cfnf0
- Proposed/enacted epochs: 570 / 576
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreienjc55atyjxfy7ij2mthoud6m2um5snifhjvurflfujf4s2sa3le

### Withdraw ₳45,217 for MLabs Core Tool Maintenance & Enhancement: Cardano.nix

- On-chain status: enacted
- On-chain withdrawal amount: 45,217.00 ADA
- On-chain proposal id: gov_action18nefry4qacd80xzs2srjahxm2e4vz3c8wvrr03rrtk8mdqfuknysq66459t
- Proposed/enacted epochs: 570 / 576
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreihj3ddbz7c52l2s3klalsf4ux5xqkawktom5v5apfral37hs6kpki

### Withdraw ₳70,000,000 for Cardano Critical Integrations Budget

- On-chain status: enacted
- On-chain withdrawal amount: 70,000,000.00 ADA
- On-chain proposal id: gov_action1lqun78lcznfa2gek49m3ydslakfnm8heargfp8sax9fk54yl6ghsqp042zv
- Proposed/enacted epochs: 599 / 606
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreiecqskxkmakkrzrs2xs2olh5jcwbuz5qr5gesp6merwcaydcaojiq

### Cardano DeFi Liquidity Budget - Withdrawal 1

- On-chain status: expired
- On-chain withdrawal amount: 500,000.00 ADA
- On-chain proposal id: gov_action1fvgw27fjpr9c7g582mszzyez0jgkqgjgatzdnyngrg8wwc9kcn3qqxtz8r7
- Proposed/enacted epochs: 607 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: https://raw.githubusercontent.com/theeldermillenial/2025-liquidity-budget/refs/heads/master/withdrawal-1/data.jsonld

### Cardano Global Listing Expansion - Powered by Snek

- On-chain status: expired
- On-chain withdrawal amount: 5.00 ADA
- On-chain proposal id: gov_action1fl6r784t2ffw7q96du2znhprw90r3xvrfugvqelgqewgxex42kdqq9tgrd5
- Proposed/enacted epochs: 573 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: https://raw.githubusercontent.com/snekadmin/Public/refs/heads/main/data.jsonld

### Cardano Summit 2026 and TOKEN2049 Singapore

- On-chain status: expired
- On-chain withdrawal amount: 14,076,539.00 ADA
- On-chain proposal id: gov_action1hkgl5l4fknsf7aktmcatkz6kfl7xpvn7rzh5vnxwexl0n3cc6zrsqt5459v
- Proposed/enacted epochs: 623 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmPZ6yDL62ms5ZGQfrPUXEDANrY9e2qrrzWVXRzbhJennk

### Pebble + Gerolamo - HLabs 2026 Budget

- On-chain status: expired
- On-chain withdrawal amount: 8,035,714.00 ADA
- On-chain proposal id: gov_action1ky2j077de82par6f0hny5q56rpnn5hh0csfhrpzeq3hsk7s6vetqquz3scv
- Proposed/enacted epochs: 621 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://QmNuDfoojLyBNqk7qEXjd4UvZUKRX5aALjRUydrrr1pxWb

### Withdraw ₳1,150,000 for GovTool 12 months active maintenance and development

- On-chain status: expired
- On-chain withdrawal amount: 1,150,000.00 ADA
- On-chain proposal id: gov_action16tdkp3fs0j6303e4utgp8rftdug0ckezr4sslgv8wxdaeq40ngpsq5sr06h
- Proposed/enacted epochs: 584 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreihju7a6zywpv3adaeeg4nnyrkewurng5csavsspmqsgikzg2suhry

### Withdraw ₳1,500,000 for Complement Catalyst: Extended Quadratic Funding---Zer...

- On-chain status: expired
- On-chain withdrawal amount: 1,500,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpk0mqrnw
- Proposed/enacted epochs: 570 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreicek47fmmvljbc2bjosg23x7hj5h7ijg7on447oy5gfuii7opgm6y

### Withdraw ₳3,000,000 for High-yield RWA Asset for Cardano: Tokenized Real Estate

- On-chain status: expired
- On-chain withdrawal amount: 3,000,000.00 ADA
- On-chain proposal id: gov_action13tfag48nf94rtjcdq7c06vhkslmxxw9h6c88sl7q5g5nnewcsvlpuz29v77
- Proposed/enacted epochs: 570 / not enacted
- Counting guidance: No TF1 overlap found in this archive; treat as an independent on-chain treasury withdrawal candidate unless another source reconciles it.
- Metadata: ipfs://bafkreidccjzvdy7np2uybq22w4n52cqu2qguoaws4o3j3wvu2rk4n27npq
