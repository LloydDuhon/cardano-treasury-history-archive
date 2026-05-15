# data/_raw/

Centrally-cached raw responses from upstream sources. Each subdirectory holds
the unmodified-as-fetched data for one source.

## Why centralized rather than per-fund?

The Lidonation v1 API serves paginated proposal pages that may mix funds
together. We walk the entire flat `/api/v1/proposals` stream once with
`include=campaign,fund,team` and split by fund in the normalizer.

For sources that DO support fund-scoped fetches (e.g., the
`milestones.projectcatalyst.io` per-project pages), their raw captures live
under `data/funds/fund-XX/_provenance/<source>/` instead.

See [ADR-2026-05-13 Implementation Notes](../../docs/adr/ADR-2026-05-13-source-strategy.md#implementation-notes-phase-1).

## Current contents

- `lidonation/fund-titles.json` - raw `/api/v1/funds` response.
- `lidonation/page-NNNN.json.gz` - one gzipped Laravel-paginator response per
  page of `/api/v1/proposals?page=N&per_page=60&include=campaign,fund,team`.
  NNNN is the page number, zero-padded to 4. The normalizer honors the v1
  `meta.last_page` value, so stale legacy pages beyond the current v1 page
  count are ignored on replay.
- `projectcatalyst_io/funds-NN.html.gz` - raw HTML capture of
  `https://projectcatalyst.io/funds/N`. NN is the fund number, zero-padded.
- `projectcatalyst_io/funds-NN.summary.json` - distilled summary extracted
  from the `__NEXT_DATA__` blob (fund name, counts, votingResultsUrl).
- `iohk-pdfs/fund-NN.pdf` - canonical IOG/CF voting-results PDF artifacts that
  are currently accessible. The interim snapshot has F2 and F10 only; missing
  artifacts are tracked in `docs/IOG_RESULTS_ACCESS_TRACKER.md`.

The Milestone Module's raw captures live PER-FUND (not in this central
`_raw/`) because the Supabase queries naturally scope by fund_id:
`data/funds/fund-XX/_provenance/milestones_supabase/`.

## Replay

These captures can be replayed through the normalizer without re-hitting any
upstream:

```bash
cd etl
python -m normalizers.unify_proposals          # all funds
python -m normalizers.unify_proposals --fund 10 # only F10
```

## Provenance integrity

- Never edit a file under `_raw/` by hand. If you find a record needs fixing,
  fix it in the normalized output and explain why in `notes`.
- Never delete a file under `_raw/`. Old captures are evidence; replacing a
  capture should happen via `--force` re-fetch which preserves the prior file
  via git history.
