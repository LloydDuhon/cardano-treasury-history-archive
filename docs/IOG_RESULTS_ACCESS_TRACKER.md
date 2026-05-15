# IOG Voting Results Access Tracker

Last updated: 2026-05-15

This tracker records the authoritative Project Catalyst voting-results artifacts
needed for Phase 2 reconciliation. Project Catalyst staff recommended using the
CSV files linked from `https://projectcatalyst.io/funds`; those links now serve
as the preferred voting-results source for F2-F14.

## Local Import Contract

Place manually acquired artifacts under these paths:

| Artifact type | Local path pattern |
|---|---|
| PDF voting results | `data/_raw/iohk-pdfs/fund-NN.pdf` |
| CSV voting results | `data/_raw/iohk-results/fund-NN.csv` |
| XLSX voting results | `data/_raw/iohk-results/fund-NN.xlsx` |

After adding files, rerun the Phase 2 parser/reconciler:

```bash
cd etl
python -m scripts.parse_iohk_pdfs
python -m normalizers.reconcile_winners
```

The current parser only reads PDF artifacts. The CSVs below are cached raw
source files and still need a parser path before running reconciliation.

## Artifact Status

| Fund | Source URL | Current status | Expected local file |
|---|---|---|---|
| F1 | Local staff-provided PDF `Fund1_voting_results.pdf` | PDF cached and parsed; 45 result rows / 8 funded; drives `data/funds/fund-01/proposals.json`. | `data/_raw/iohk-pdfs/fund-01.pdf` |
| F2 | `https://projectcatalyst.io/funds/2/voting-results` -> Google Sheet `1beHJPUoLvOoSmqN69NIxGmZSWEUJOeI4Lf2TwTfRRVs`, gid `1751929066` | CSV cached and parsed; 78 rows / 11 funded; one status correction applied. | `data/_raw/iohk-results/fund-02.csv` |
| F3 | `https://projectcatalyst.io/funds/3/voting-results` -> Google Sheet `1ibl-9qpLRQiFhJQfcvIeSdfJr9LjGpU6WqHce6VIUnE`, gid `1538672709` | CSV cached and parsed; 76 rows / 8 funded; no status disagreements. | `data/_raw/iohk-results/fund-03.csv` |
| F4 | `https://projectcatalyst.io/funds/4/voting-results` -> Google Sheet `13NC6SZ5MzQsYb-ufbuQHakxvLvPtZWv_02Aq17PFErI`, gid `1538672709` | CSV cached and parsed; 104 rows / 7 funded; one status correction applied. | `data/_raw/iohk-results/fund-04.csv` |
| F5 | `https://projectcatalyst.io/funds/5/voting-results` -> Google Sheet `156SdqPYOBkC5iQQeOOZc9yXSYoNHb-J-wJrem-xax78`, gid `1848314097` | CSV cached and parsed; 43 rows / 24 funded; no status disagreements. | `data/_raw/iohk-results/fund-05.csv` |
| F6 | `https://projectcatalyst.io/funds/6/voting-results` -> Google Sheet `1y-7U88FRvsEEzm98KbEswUGuy4q-eTeoFTV3EFrc6b4`, gid `1183771745` | CSV cached and parsed; 102 rows / 20 funded; no status disagreements. | `data/_raw/iohk-results/fund-06.csv` |
| F7 | `https://projectcatalyst.io/funds/7/voting-results` -> Google Sheet `19_TEovS_Gemwvz2qlc6jGPizqAY8ZeDrzbH3DSeXyto`, gid `309291557` | CSV cached and parsed; 38 rows / 9 funded; no status disagreements. Verify whether additional workbook tabs are needed. | `data/_raw/iohk-results/fund-07.csv` |
| F8 | `https://projectcatalyst.io/funds/8/voting-results` -> Google Sheet `15ELXp81NfvXHgrerTbuIofZOXBsdjocN1YgBK0gPP3E`, gid `2111315347` | CSV cached and parsed; 38 rows / 12 funded; one status correction applied. Verify whether additional workbook tabs are needed. | `data/_raw/iohk-results/fund-08.csv` |
| F9 | `https://projectcatalyst.io/funds/9/voting-results` -> Google Sheet `1MycQL-dkqf1xEW8xcr7vqcfHY6D7MHnG9ylDKNLSnAA`, default gid `0` | CSV cached and parsed; 9 rows / 1 funded; no status disagreements. This workbook appears multi-tab; extract relevant gids before treating coverage as complete. | `data/_raw/iohk-results/fund-09.csv` |
| F10 | `https://projectcatalyst.io/funds/10/voting-results` -> Google Sheet `1NxtUdvC-BRSh2kIczpV1rLuxJKkJfbxnRwxUsYJ9O8Y`, gid `885359704` | CSV cached and parsed; 187 rows / 28 funded; no status disagreements. | `data/_raw/iohk-results/fund-10.csv` |
| F11 | `https://projectcatalyst.io/funds/11/voting-results` -> Google Sheet `18mDkdQn8fufBr7Ab9oSlV14UvBTMoUHeS43KAJiYPgQ`, gid `896673639` | CSV cached and parsed; 312 rows / 78 funded; no status disagreements. | `data/_raw/iohk-results/fund-11.csv` |
| F12 | `https://projectcatalyst.io/funds/12/voting-results` -> Google Sheet `1Wq1XdPCJuiBDjDECSrpm7RvIfpNMEHitsbveqVaPWnk`, gid `837754658` | CSV cached and parsed; 189 rows / 63 funded; no status disagreements. | `data/_raw/iohk-results/fund-12.csv` |
| F13 | `https://projectcatalyst.io/funds/13/voting-results` -> Google Sheet `1Jesjo5hoLvBJfWF4E6_516urm_lfvtSW0fhkZhCMUmQ`, gid `1185817058` | CSV cached and parsed; 357 rows / 53 funded; no status disagreements. | `data/_raw/iohk-results/fund-13.csv` |
| F14 | `https://projectcatalyst.io/funds/14/voting-results` -> Google Sheet `1C_zftHxwGN__vxFscZosv_qynnhOd-zJl_bMezs7joo`; result tabs `161104218`, `689513427`, `1185817058`, `362975940`, `961791716`, `791046878` | Multi-tab CSVs cached and parsed; 1,283 unique rows / 131 funded-or-leftover outcomes; reconciles with 0 disagreements. Default gid `0` is retained only as the broken template export. | `data/_raw/iohk-results/fund-14-*.csv` |

## Remaining Engineering Work

- For F7-F9, inspect the linked workbooks for additional tabs/gids before
  treating the cached parsed rows as complete.
- Add a newer-layout PDF parser for F10 only if we still need PDF parity after
  CSV reconciliation.
- Re-run `normalizers.apply_reconciliations`, `dedupe_proposers`, and
  `consolidate` after reconciliation changes.
- Update `docs/DATA_QUALITY.md` with final row counts and per-fund reconciliation
  coverage before tagging the first full snapshot.
