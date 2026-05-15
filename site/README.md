# Treasury Fund 2 History Explorer

Static frontend for reviewing current Treasury Fund 2 proposals alongside prior
Cardano funding records matched by the archive.

## Local Preview

```bash
cd site
python3 -m http.server 8000
```

Open `http://localhost:8000`. The page must be served over HTTP because the
browser loads the JSX files and `data.js` as separate resources.

## Refresh Data

From the repository root:

```bash
python3 etl/scripts/generate_treasury_dashboard_data.py --repo-root . --out site
```

The generated payloads are:

- `site/data.js` for the browser
- `site/data.json` for inspection and downstream reuse

## Deployment

`.github/workflows/pages.yml` publishes the `site/` directory to GitHub Pages
on pushes to `main` that touch the viewer.
