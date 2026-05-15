# IOG Voting Results Access Tracker

Last updated: 2026-05-15

This tracker records the authoritative Project Catalyst voting-results artifacts
needed for Phase 2 reconciliation. The archive can publish Lidonation v1
proposal data and Milestone Module data before this table is complete, but the
first "full snapshot" should wait until these artifacts are available and parsed.

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

If Catalyst provides CSV or XLSX files for F11-F13, add a parser path before
running reconciliation. The current parser only reads PDF artifacts.

## Artifact Status

| Fund | Source URL | Current status | Expected local file |
|---|---|---|---|
| F2 | `https://static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf` | Downloaded and parsed | `data/_raw/iohk-pdfs/fund-02.pdf` |
| F3 | `https://drive.google.com/file/d/1X6BnuFBvNO8yF2DeUgBqA3yyYSvqeKvg/view` | Drive permission blocked from CLI | `data/_raw/iohk-pdfs/fund-03.pdf` |
| F4 | `https://drive.google.com/file/d/19VMTYn_sv5Xsp2mC5VUN_-z_aXYHL_Dd/view` | Drive permission blocked from CLI | `data/_raw/iohk-pdfs/fund-04.pdf` |
| F5 | `https://drive.google.com/file/d/1HKmqyPebE87BUrPtE4AT5E2V4_yIZtT-/view` | Drive permission blocked from CLI | `data/_raw/iohk-pdfs/fund-05.pdf` |
| F6 | `https://drive.google.com/file/d/13h5JFtwqyylMUNMoRGXQZ-FJEM4bznOJ/view?usp=sharing` | Drive permission blocked from CLI | `data/_raw/iohk-pdfs/fund-06.pdf` |
| F7 | `https://bit.ly/3HJNhuX` | Redirected artifact blocked from CLI | `data/_raw/iohk-pdfs/fund-07.pdf` |
| F8 | `https://drive.google.com/file/d/1s3jCE7pmoUujy3ASMia-UhFl2KLi_hnf/view` | Drive permission blocked from CLI | `data/_raw/iohk-pdfs/fund-08.pdf` |
| F9 | `https://bit.ly/Fund9_Results` | Redirected artifact blocked from CLI | `data/_raw/iohk-pdfs/fund-09.pdf` |
| F10 | `https://projectcatalyst.io/fund10-voting-results.pdf` | Downloaded; parser returns 0 rows because layout differs from F2 | `data/_raw/iohk-pdfs/fund-10.pdf` |
| F11 | `https://docs.google.com/spreadsheets/d/18mDkdQn8fufBr7Ab9oSlV14UvBTMoUHeS43KAJiYPgQ/edit#gid=896673639` | Google Sheets CSV export returns 401 from CLI | `data/_raw/iohk-results/fund-11.csv` or `.xlsx` |
| F12 | `https://docs.google.com/spreadsheets/d/1Wq1XdPCJuiBDjDECSrpm7RvIfpNMEHitsbveqVaPWnk/edit?gid=837754658#gid=837754658` | Google Sheets CSV export returns 401 from CLI | `data/_raw/iohk-results/fund-12.csv` or `.xlsx` |
| F13 | `https://docs.google.com/spreadsheets/d/1Jesjo5hoLvBJfWF4E6_516urm_lfvtSW0fhkZhCMUmQ/edit?gid=1185817058#gid=1185817058` | Google Sheets CSV export returns 401 from CLI | `data/_raw/iohk-results/fund-13.csv` or `.xlsx` |

## Remaining Engineering Work

- Add a newer-layout PDF parser for F10 and any other matching PDF artifacts.
- Add CSV/XLSX parser support for F11-F13 if Catalyst provides sheet exports.
- Re-run `normalizers.reconcile_winners` after artifacts are available.
- Re-run `normalizers.apply_reconciliations`, `dedupe_proposers`, and
  `consolidate` after reconciliation changes.
- Update `docs/DATA_QUALITY.md` with final row counts and per-fund reconciliation
  coverage before tagging the first full snapshot.
