## Summary

Describe what changed and why.

## Affected Data Or Code

- Records, reports, schemas, or workflows changed:
- Source URLs or primary evidence:

## Provenance Checklist

- [ ] Data changes update `sources[]`, source URLs, or report methodology notes as appropriate.
- [ ] Confidence labels are honest and conservative.
- [ ] Generated artifacts were regenerated from committed inputs where applicable.
- [ ] This PR does not introduce secrets or private credentials.

## Validation

List the commands run, for example:

- `ruff check .`
- `ruff format --check .`
- `python -m pytest`
- `python -m mypy fetchers normalizers validators`
- `python etl/validators/validate_against_schema.py`
- `python etl/scripts/generate_treasury_dashboard_data.py --repo-root . --out site`
