# Treasury Fund 2 History Explorer

Static frontend for reviewing current Treasury Fund 2 proposals alongside prior
Cardano funding records matched by the archive.

The viewer includes graph, ledger, funding-flow, and similarity-findings tabs.
The similarity-findings tab presents prior-work overlap triage rows with
explicit `AI Matched` or `Human Reviewed` provenance.

## Local Preview

```bash
cd site
npm ci
npm run build
python3 -m http.server 8000
```

Open `http://localhost:8000`. The page must be served over HTTP because the
browser fetches `data.json` before loading the compiled application bundle.

## Refresh Data

From the repository root:

```bash
python3 etl/scripts/generate_treasury_dashboard_data.py --repo-root . --out site
```

The generated payloads are:

- `site/data.json` for the browser and downstream reuse

## Deployment

`.github/workflows/pages.yml` builds `site/bundle.js` with esbuild and publishes
the `site/` directory to GitHub Pages on pushes to `main` that touch the viewer.
