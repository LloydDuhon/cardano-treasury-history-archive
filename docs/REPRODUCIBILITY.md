# Reproducibility

This repository is intended to make the path from source snapshots to reports
and the static site inspectable.

## Environment

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r etl/requirements-dev.txt
cd site
npm ci
```

## Validate The Committed Dataset

```bash
cd etl
ruff check .
ruff format --check .
python -m pytest
python -m mypy fetchers normalizers validators
cd ..
python etl/validators/validate_against_schema.py
```

## Regenerate Treasury Fund 2 Reports

```bash
cd etl
python -m scripts.generate_treasury_fund_reports
cd ..
python etl/scripts/generate_treasury_dashboard_data.py --repo-root . --out site
```

The committed `site/data.json` should be reproducible from committed raw inputs
and report CSVs:

```bash
python etl/scripts/generate_treasury_dashboard_data.py --repo-root . --out /tmp/treasury-dashboard-data
diff -u site/data.json /tmp/treasury-dashboard-data/data.json
```

## Build The Static Site

```bash
cd site
npm run build
python3 -m http.server 8000
```

Open `http://localhost:8000`.

The GitHub Pages workflow regenerates `site/data.json`, builds `site/bundle.js`,
and deploys the static directory.

## Expected Drift

Raw upstream sources can change. Before relying on reports for publication,
refresh raw snapshots using the documented ETL fetchers and review the resulting
diffs. Do not silently overwrite source snapshots or generated reports without
reviewing provenance, timestamps, and row counts.

AI-assisted overlap review is a triage mechanism unless a row is marked as
human-reviewed. Regenerating AI-assisted files can change wording or rankings;
preserve model attribution and review notes.
