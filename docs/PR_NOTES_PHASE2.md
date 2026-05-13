# Phase 2 PR Notes

Internal notes for the maintainer (Lloyd). Not part of the public docs.

## Branch and commit

Branch: `phase-2/iog-pdf-reconcile` (off `main` after Phase 1 merged).

Suggested commit message:

```
Phase 2: IOG voting-results PDF cross-check + diff-only reconciliation

- fetchers/projectcatalyst_funds.py: scrape /funds/N HTML for
  __NEXT_DATA__ JSON, download canonical PDF (handles
  static.iohk.io / Google Drive / inline patterns).
- parsers/iohk_pdf.py: pdfplumber-based row parser. Validated
  against F2: 78 rows / 11 funded, matches canonical counts.
- normalizers/reconcile_winners.py: passive sidecar that writes
  data/funds/fund-XX/_reconciliation.json. Does NOT modify
  proposals.json - per ADR-2026-05-13, corrections apply in Phase 6
  after maintainer review.
- schemas/reconciliation.schema.json: new schema, validated by
  validate_against_schema.py.
- 13 new tests; suite now 33 total.
- Fixtures: funds-2.html.gz (45 KB), iohk-pdfs/fund-02.pdf (1.8 MB).
- Pinned deps: pdfplumber 0.11.4, pypdf 5.0.1.

Refs: docs/CATALYST-HISTORY-CAPTURE-PLAN.md (Phase 2), 02-Projects/.../PHASE_2_NOTES.md
```

## Local PowerShell flow

```powershell
cd $HOME\Documents\claude-work\repos\catalyst-history-archive
git checkout main
git pull
git checkout -b phase-2/iog-pdf-reconcile

# Optional local preflight on Python 3.12
cd etl
.venv\Scripts\Activate.ps1   # or recreate the venv if Phase 1 venv is gone
pip install -r requirements-dev.txt
ruff check .; ruff format --check .
python -m pytest                # expect 33 passed
python -m mypy fetchers normalizers parsers validators
cd ..

# Phase 2 smoke (Fund 2 only)
cd etl
python -m fetchers.projectcatalyst_funds --fund 2
# The fetcher now also has cached F2 HTML + PDF on disk.
# Until we wire a parser CLI runner, parse + reconcile from a Python one-liner:
python -c "from pathlib import Path; from parsers.iohk_pdf import parse_voting_results_pdf, write_intermediate; from datetime import datetime, timezone; rows, s = parse_voting_results_pdf(Path('../data/_raw/iohk-pdfs/fund-02.pdf')); write_intermediate(rows, s, fund=2, data_root=Path('../data'), source_url='https://static.iohk.io/docs/catalyst/catalyst-voting-results-fund2.pdf', pdf_relpath='data/_raw/iohk-pdfs/fund-02.pdf', parsed_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"
python -m normalizers.reconcile_winners --fund 2
type ..\data\funds\fund-02\_reconciliation.json
cd ..

# Commit and PR
git add etl schemas docs CHANGELOG.md data\_raw\README.md
# Decide whether to commit smoke output too:
# git add data\funds\fund-02\_intermediate data\funds\fund-02\_reconciliation.json data\_raw\projectcatalyst_io data\_raw\iohk-pdfs
git status --short
git commit -F docs/PR_NOTES_PHASE2.md  # or use the message above
git push -u origin phase-2/iog-pdf-reconcile
gh pr create --base main --title "Phase 2: IOG voting-results cross-check + diff-only reconciliation" --body-file docs/PR_NOTES_PHASE2.md
```

## Test plan to run before merge

| Step | Command | Expected |
|------|---------|----------|
| Unit tests | `python -m pytest` (from etl/) | 33 passed |
| Type check | `python -m mypy fetchers normalizers parsers validators` | no issues |
| Schema validator | `python validators/validate_against_schema.py` | OK |
| Fetcher smoke | `python -m fetchers.projectcatalyst_funds --fund 2` | data/_raw/projectcatalyst_io/funds-02.html.gz + iohk-pdfs/fund-02.pdf created |
| Parser smoke | Python one-liner above | iohk_winners.json with 78 rows |
| Reconciler smoke | `python -m normalizers.reconcile_winners --fund 2` | _reconciliation.json written, agreement+disagreement counts printed |
| Validator on output | `python validators/validate_against_schema.py --fund 2 --strict` | _reconciliation.json passes its schema |

## Open follow-ups (deferred)

- **Parser CLI runner.** Phase 2b should add `python -m parsers.iohk_pdf <fund>` to remove the one-liner.
- **Per-fund parser variants.** F2 layout was the basis; F3-F9 may need small tweaks. Smoke-then-extend.
- **Google Drive 100MB confirm flow.** Implemented as a guarded RuntimeError; needs a real confirm-token follower if we hit it.
- **Apply reconciliation outcomes.** Phase 6 will read `_reconciliation.json` files and update `proposals.json` per the ADR-2026-05-13 rule (IOG wins).

## What I left out (deliberate)

- **No full F2-F13 sweep committed.** Phase 2 PR contains code + F2 smoke only.
- **No corrections to proposals.json.** Per the locked decision (diff-only sidecar).
- **No new CI workflow.** Existing `tests.yml` automatically picks up the new tests.

