# data/_raw/

Centrally-cached raw responses from upstream sources. Each subdirectory holds
the unmodified-as-fetched data for one source.

## Why centralized rather than per-fund?

The Lidonation API serves pages of 24 proposals that mix funds together
(every page contains records from many different funds), and the server-side
fund filter is currently broken. So we cannot fetch fund-scoped slices from
the upstream - we walk the entire flat /api/proposals stream once and split
by fund in the normalizer.

For sources that DO support fund-scoped fetches (e.g., the
`milestones.projectcatalyst.io` per-project pages), their raw captures live
under `data/funds/fund-XX/_provenance/<source>/` instead.

See [ADR-2026-05-13 Implementation Notes](../../docs/adr/ADR-2026-05-13-source-strategy.md#implementation-notes-phase-1).

## Current contents

- `lidonation/fund-titles.json` - canonical fund UUID -> title map.
- `lidonation/page-NNNN.json.gz` - one gzipped Laravel-paginator response per
  page of `/api/proposals?p=N`. NNNN is the page number, zero-padded to 4.
- `projectcatalyst_io/funds-NN.html.gz` - raw HTML capture of
  `https://projectcatalyst.io/funds/N`. NN is the fund number, zero-padded.
- `projectcatalyst_io/funds-NN.summary.json` - distilled summary extracted
  from the `__NEXT_DATA__` blob (fund name, counts, votingResultsUrl).
- `iohk-pdfs/fund-NN.pdf` - the canonical IOG voting-results PDF for each
  fund where one exists (F2-F13). Downloaded from static.iohk.io,
  Google Drive, or projectcatalyst.io inline depending on the fund.

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
