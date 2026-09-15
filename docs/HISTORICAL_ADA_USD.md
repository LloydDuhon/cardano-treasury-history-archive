# Historical ADA/USD Daily Price Data

This archive includes a reusable daily ADA/USD market-price dataset for
estimating ADA equivalents of USD-denominated Catalyst funding records.

## Location

- Raw API capture: `data/_raw/ccdata/ada-usd-histoday-all.json`
- Normalized JSON: `data/historical/ada-usd-daily/prices.json`
- Normalized CSV: `data/historical/ada-usd-daily/prices.csv`
- Metadata: `data/historical/ada-usd-daily/_meta.json`

## Source

The dataset is fetched from CCData/CryptoCompare's public historical daily
endpoint:

`https://min-api.cryptocompare.com/data/v2/histoday?fsym=ADA&tsym=USD&allData=true`

The raw response is stored unchanged under `data/_raw/ccdata/` before
normalization. Normalized rows exclude zero-price rows that appear before ADA
had a live market price in the provider's `allData` response.

CoinGecko was evaluated first because its market chart endpoint is widely used,
but its public API rejected full-range Cardano history during implementation
with a 365-day public-plan limit. CCData currently provides the full daily
history needed for early Catalyst funds without an API key.

## Columns

The normalized JSON and CSV expose:

| Field | Meaning |
|---|---|
| `date` | UTC calendar date (`YYYY-MM-DD`) |
| `timestamp` | UTC daily bucket timestamp from the source |
| `open_usd` | ADA opening price in USD |
| `high_usd` | ADA high price in USD |
| `low_usd` | ADA low price in USD |
| `close_usd` | ADA closing price in USD |
| `volume_ada` | Daily ADA volume from the source |
| `volume_usd` | Daily USD volume from the source |
| `conversion_type` | Source conversion method |
| `conversion_symbol` | Source conversion symbol, when any |

## Intended Use

For USD-denominated Catalyst records, use `close_usd` on a documented policy
date to estimate ADA:

`estimated_ada = usd_amount / close_usd`

The policy date must be explicit. Reasonable choices include:

- `funded_at` when a proposal has a known funding timestamp
- voting result publication date when `funded_at` is missing
- a manually curated first-payment date when transaction evidence exists

These estimates should be stored separately from verified ADA amounts. Market
price conversion can answer "what was this USD amount worth in ADA on this
date"; it does not prove the actual ADA disbursed.

## Refresh

From `etl/`:

```bash
python -m fetchers.ada_usd_daily --force
python -m normalizers.ada_usd_daily
```

The fetcher is idempotent without `--force`; it reuses the existing raw capture.
