"""Generate Treasury Fund 2 proposer-history visualizations.

Inputs:
    reports/treasury-fund-2/proposer-history.csv
    reports/treasury-fund-2/onchain-treasury-reconciliation.csv
    reports/treasury-fund-2/_summary.json
    data/_raw/hydra_voting/cardano-budget-2026.json

Outputs:
    reports/treasury-fund-2/figures/01-prior-ada-by-proposer.png
    reports/treasury-fund-2/figures/02-prior-proposal-count-by-proposer.png
    reports/treasury-fund-2/figures/03-status-mix-overall.png
    reports/treasury-fund-2/figures/04-first-time-tf2-proposers.png
    reports/treasury-fund-2/figures/tf2-proposer-history-dashboard.html
    reports/treasury-fund-2/figures/figures-data.csv
    reports/treasury-fund-2/figures/first-time-proposers.csv
    reports/treasury-fund-2/figures/_figures-summary.json

The figures answer two questions for the Cardano Budget Committee and the
broader Cardano audience:
  1. For the 17 TF2 proposers who have previously received treasury funds
     (Project Catalyst and/or Treasury Fund 1 according to the archive),
     what have they delivered with that funding so far?
  2. Which TF2 proposers have not received any treasury funds from any
     source represented in the archive (Catalyst + TF1 + on-chain
     TreasuryWithdrawals governance actions)?

Caveats surfaced in the dashboard:
  * 20% of historical rows are USD-denominated (early Catalyst funds);
    ADA totals exclude those rows and therefore under-state activity.
  * The proposer-history join uses medium-confidence "proposer mentioned in
    proposal text" matching for Catalyst rows, and high-confidence
    contract-level matching for TF1 rows. This is a research dataset, not
    an audit opinion.
  * "MLabs LTD" and "MLabsLTD" appear separately in the source CSV; we
    treat them as one entity for the figures and note the entity-resolution
    issue for upstream cleanup.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------
# Palette: Cardano-neutral blues with semantic accents. Colourblind-safe.
# ---------------------------------------------------------------------------
STATUS_COLORS: dict[str, str] = {
    "complete": "#1F4F8F",  # deep blue -- delivered
    "in_progress": "#5C8FCF",  # mid blue -- in flight
    "active": "#9CC4E4",  # light blue -- active contract
    "paused": "#E8A23E",  # amber -- needs attention
    "withdrawn": "#B23A48",  # muted red -- non-delivery
}
STATUS_ORDER: list[str] = ["complete", "in_progress", "active", "paused", "withdrawn"]
STATUS_LABELS: dict[str, str] = {
    "complete": "Complete",
    "in_progress": "In progress",
    "active": "Active",
    "paused": "Paused",
    "withdrawn": "Withdrawn",
}

# Entity-resolution merges. Keep upstream source data untouched; merge
# only at the display layer. Document each merge in the README.
NAME_ALIASES: dict[str, str] = {
    "MLabsLTD": "MLabs LTD",
}


@dataclass(frozen=True)
class Paths:
    repo: Path

    @property
    def proposer_history_csv(self) -> Path:
        return self.repo / "reports/treasury-fund-2/proposer-history.csv"

    @property
    def onchain_csv(self) -> Path:
        return self.repo / "reports/treasury-fund-2/onchain-treasury-reconciliation.csv"

    @property
    def summary_json(self) -> Path:
        return self.repo / "reports/treasury-fund-2/_summary.json"

    @property
    def hydra_json(self) -> Path:
        return self.repo / "data/_raw/hydra_voting/cardano-budget-2026.json"

    @property
    def out_dir(self) -> Path:
        return self.repo / "reports/treasury-fund-2/figures"


def _canonicalize_name(name: object) -> str:
    """Apply known display-time merges. Trim whitespace."""
    if pd.isna(name):
        return ""
    trimmed = str(name).strip()
    return NAME_ALIASES.get(trimmed, trimmed)


def load_tf2_proposals(hydra_path: Path) -> pd.DataFrame:
    payload: dict[str, Any] = json.loads(hydra_path.read_text())
    rows: list[dict[str, Any]] = []
    for p in payload["proposals_response"]["data"]:
        md = p.get("metaData", {})
        rows.append(
            {
                "proposal_id": p.get("_id"),
                "proposer": md.get("proposerDetails", {}).get("name"),
                "total_budget_ada": md.get("totalBudget"),
                "title": p.get("title"),
            }
        )
    df = pd.DataFrame(rows)
    df["proposer_canonical"] = df["proposer"].apply(_canonicalize_name)
    return df


def load_history(history_path: Path) -> pd.DataFrame:
    df = pd.read_csv(history_path)
    df["proposer_canonical"] = df["current_proposer_name"].apply(_canonicalize_name)
    df["amount_ada"] = pd.to_numeric(df["amount_ada"], errors="coerce")
    df["amount_ada_filled"] = df["amount_ada"].fillna(0.0)
    return df


def build_proposer_summary(history: pd.DataFrame) -> pd.DataFrame:
    """One row per canonical proposer with totals and status counts."""
    rows: list[dict[str, Any]] = []
    for name, grp in history.groupby("proposer_canonical"):
        status_counts = Counter(grp["historical_status"].dropna())
        risk_flag_rows = (
            grp["delivery_flags"]
            .astype(str)
            .str.contains(
                "treasury_project_status",
                na=False,
            )
            .sum()
        )
        usd_only_rows = grp["amount_ada"].isna().sum()
        rows.append(
            {
                "proposer": name,
                "total_ada": float(grp["amount_ada_filled"].sum()),
                "n_records": int(len(grp)),
                "n_complete": int(status_counts.get("complete", 0)),
                "n_in_progress": int(status_counts.get("in_progress", 0)),
                "n_active": int(status_counts.get("active", 0)),
                "n_paused": int(status_counts.get("paused", 0)),
                "n_withdrawn": int(status_counts.get("withdrawn", 0)),
                "n_risk_flagged": int(risk_flag_rows),
                "n_usd_only": int(usd_only_rows),
                "ada_complete": float(
                    grp.loc[grp["historical_status"] == "complete", "amount_ada_filled"].sum()
                ),
                "ada_in_progress": float(
                    grp.loc[grp["historical_status"] == "in_progress", "amount_ada_filled"].sum()
                ),
                "ada_active": float(
                    grp.loc[grp["historical_status"] == "active", "amount_ada_filled"].sum()
                ),
                "ada_paused": float(
                    grp.loc[grp["historical_status"] == "paused", "amount_ada_filled"].sum()
                ),
                "ada_withdrawn": float(
                    grp.loc[grp["historical_status"] == "withdrawn", "amount_ada_filled"].sum()
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("total_ada", ascending=False).reset_index(drop=True)


def find_onchain_only_proposers(
    tf2: pd.DataFrame, history: pd.DataFrame, onchain_path: Path
) -> set[str]:
    """Return TF2 proposers whose names appear in on-chain withdrawal titles
    but are NOT already present in proposer-history.csv. Used to refine the
    'first-time' list under the strictest 'all sources' definition.
    """
    onchain = pd.read_csv(onchain_path)
    history_proposers: set[str] = set(history["proposer_canonical"].dropna().unique())
    titles: list[str] = [str(t) for t in onchain["onchain_title"].dropna().tolist()]
    found: set[str] = set()
    for name in set(tf2["proposer_canonical"].dropna()):
        if name in history_proposers:
            continue
        needle = str(name).strip().lower()
        if len(needle) < 3:
            continue
        if any(needle in t.lower() for t in titles):
            found.add(name)
    return found


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------


def _format_ada(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M ADA"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K ADA"
    return f"{value:.0f} ADA"


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#444",
            "axes.labelcolor": "#222",
            "xtick.color": "#444",
            "ytick.color": "#222",
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.titlecolor": "#111",
            "axes.grid": True,
            "grid.color": "#E5E5E5",
            "grid.linestyle": "-",
            "grid.linewidth": 0.7,
            "axes.axisbelow": True,
        }
    )


def plot_ada_by_proposer(summary: pd.DataFrame, out_path: Path) -> None:
    df = summary.sort_values("total_ada", ascending=True)
    fig, ax = plt.subplots(figsize=(12, 7))
    left = pd.Series([0.0] * len(df), index=df.index)
    for status in STATUS_ORDER:
        col = f"ada_{status}"
        values = df[col]
        ax.barh(
            df["proposer"],
            values,
            left=left,
            color=STATUS_COLORS[status],
            edgecolor="white",
            linewidth=0.6,
            label=STATUS_LABELS[status],
        )
        left = left + values

    for idx, total in enumerate(df["total_ada"]):
        ax.text(total * 1.01, idx, _format_ada(total), va="center", fontsize=9, color="#222")

    ax.set_xlabel("Prior treasury ADA received (Catalyst + TF1)")
    ax.set_title(
        "Returning TF2 proposers: prior treasury ADA, by historical project status",
        loc="left",
    )
    ax.set_xlim(0, df["total_ada"].max() * 1.18)

    def _xfmt(x: float, _pos: int) -> str:
        if x == 0:
            return "0"
        if x >= 1_000_000:
            return f"{x / 1_000_000:.0f}M"
        if x >= 1_000:
            return f"{x / 1_000:.0f}K"
        return f"{x:.0f}"

    ax.xaxis.set_major_formatter(plt.FuncFormatter(_xfmt))
    ax.legend(loc="lower right", frameon=False, fontsize=9, ncol=5)
    ax.text(
        0.0,
        -0.10,
        "Source: cardano-treasury-history-archive / proposer-history.csv. "
        "ADA totals exclude USD-denominated rows (122 of 607 historical records). "
        "MLabs LTD and MLabsLTD merged for display.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#666",
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_count_by_proposer(summary: pd.DataFrame, out_path: Path) -> None:
    df = summary.copy()
    df = df.assign(
        total_count=df[["n_complete", "n_in_progress", "n_active", "n_paused", "n_withdrawn"]].sum(
            axis=1
        )
    ).sort_values("total_count", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    left = pd.Series([0.0] * len(df), index=df.index)
    for status in STATUS_ORDER:
        values = df[f"n_{status}"]
        ax.barh(
            df["proposer"],
            values,
            left=left,
            color=STATUS_COLORS[status],
            edgecolor="white",
            linewidth=0.6,
            label=STATUS_LABELS[status],
        )
        left = left + values

    for idx, total in enumerate(df["total_count"]):
        ax.text(total + 2, idx, f"{int(total)}", va="center", fontsize=9, color="#222")

    ax.set_xlabel("Count of prior funded proposals")
    ax.set_title(
        "Returning TF2 proposers: count of prior funded proposals, by status",
        loc="left",
    )
    ax.set_xlim(0, df["total_count"].max() * 1.10)
    ax.legend(loc="lower right", frameon=False, fontsize=9, ncol=5)
    ax.text(
        0.0,
        -0.10,
        "Source: cardano-treasury-history-archive / proposer-history.csv. "
        "Counts include records denominated in USD (excluded from ADA totals).",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#666",
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_status_mix_overall(summary: pd.DataFrame, out_path: Path) -> None:
    totals = {s: int(summary[f"n_{s}"].sum()) for s in STATUS_ORDER}
    total_n = sum(totals.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), gridspec_kw={"width_ratios": [1, 1]})

    sizes = [totals[s] for s in STATUS_ORDER]
    colors = [STATUS_COLORS[s] for s in STATUS_ORDER]
    labels = [
        f"{STATUS_LABELS[s]}  ({totals[s]}  /  {totals[s] / total_n:.0%})" for s in STATUS_ORDER
    ]
    ax1.pie(
        sizes,
        colors=colors,
        startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
    )
    ax1.set_title(
        f"Historical project status across all {total_n} records",
        loc="center",
        fontsize=12,
    )
    ax1.legend(labels, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)

    ada_totals = {s: float(summary[f"ada_{s}"].sum()) for s in STATUS_ORDER}
    ada_total = sum(ada_totals.values())
    sizes_a = [ada_totals[s] for s in STATUS_ORDER]
    labels_a = [
        f"{STATUS_LABELS[s]}  ({_format_ada(ada_totals[s])}  /  {ada_totals[s] / ada_total:.0%})"
        for s in STATUS_ORDER
    ]
    ax2.pie(
        sizes_a,
        colors=colors,
        startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
    )
    ax2.set_title(
        f"ADA-weighted status (excludes USD-only rows / total {_format_ada(ada_total)})",
        loc="center",
        fontsize=12,
    )
    ax2.legend(labels_a, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)

    fig.suptitle(
        "Delivery status of past treasury-funded work for the 17 returning TF2 proposers",
        fontsize=14,
        fontweight="bold",
        y=1.02,
        x=0.05,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_first_time_proposers(first_timers: pd.DataFrame, out_path: Path) -> None:
    df = first_timers.sort_values("total_budget_ada", ascending=True)
    fig, ax = plt.subplots(figsize=(12, max(7, len(df) * 0.32)))
    bars = ax.barh(
        df["proposer_canonical"],
        df["total_budget_ada"],
        color="#5C8FCF",
        edgecolor="white",
        linewidth=0.6,
    )
    for bar, value in zip(bars, df["total_budget_ada"], strict=False):
        if pd.isna(value):
            continue
        ax.text(
            value * 1.01,
            bar.get_y() + bar.get_height() / 2,
            _format_ada(value),
            va="center",
            fontsize=9,
            color="#222",
        )

    max_v = float(df["total_budget_ada"].max())
    ax.set_xlim(0, max_v * 1.20)

    def _xfmt(x: float, _pos: int) -> str:
        if x == 0:
            return "0"
        if x >= 1_000_000:
            return f"{x / 1_000_000:.0f}M"
        if x >= 1_000:
            return f"{x / 1_000:.0f}K"
        return f"{x:.0f}"

    ax.xaxis.set_major_formatter(plt.FuncFormatter(_xfmt))
    ax.set_xlabel("TF2 proposal ask amount (ADA)")
    ax.set_title(
        f"First-time TF2 proposers: {len(df)} proposers with no prior treasury funding "
        "(Catalyst + TF1 + on-chain)",
        loc="left",
    )
    ax.text(
        0.0,
        -0.04,
        "Source: cardano-treasury-history-archive / hydra_voting + proposer-history + "
        "onchain-treasury-reconciliation. Where one proposer has multiple TF2 proposals, "
        "the ask shown is the sum of their proposals' total budgets.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#666",
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# HTML dashboard
# ---------------------------------------------------------------------------

DASHBOARD_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TF2 proposer history -- visualization dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --ink: #111;
    --muted: #555;
    --bg: #fff;
    --line: #e5e5e5;
    --accent: #1F4F8F;
    --warn: #E8A23E;
    --danger: #B23A48;
  }}
  body {{
    margin: 0;
    font-family:
      -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
      Arial, sans-serif;
    color: var(--ink);
    background: var(--bg);
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px 64px; }}
  header {{ border-bottom: 1px solid var(--line); padding-bottom: 16px; margin-bottom: 32px; }}
  h1 {{ font-size: 22px; margin: 0 0 6px; font-weight: 600; }}
  .sub {{ color: var(--muted); font-size: 14px; }}
  .meta {{ font-size: 12px; color: var(--muted); margin-top: 8px; }}
  h2 {{ font-size: 16px; margin: 40px 0 8px; font-weight: 600; }}
  h2 .count {{ color: var(--muted); font-weight: 400; }}
  p {{ line-height: 1.55; font-size: 14px; color: #222; }}
  .grid-kpi {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0 24px;
  }}
  .kpi {{
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 16px;
    background: #fafafa;
  }}
  .kpi .label {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
  }}
  .kpi .value {{ font-size: 22px; font-weight: 600; margin-top: 4px; color: var(--ink); }}
  figure {{ margin: 0 0 24px; }}
  figure img {{
    width: 100%;
    height: auto;
    display: block;
    border: 1px solid var(--line);
    border-radius: 6px;
    background: white;
  }}
  figcaption {{ font-size: 12px; color: var(--muted); margin-top: 6px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
  th {{ background: #fafafa; font-weight: 600; color: #333; cursor: pointer; user-select: none; }}
  th .arrow {{ color: #bbb; font-size: 10px; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .controls {{ display: flex; gap: 12px; align-items: center; margin: 12px 0; }}
  .controls input[type=search] {{
    flex: 1;
    padding: 8px 10px;
    border: 1px solid var(--line);
    border-radius: 6px;
    font-size: 13px;
  }}
  .note {{
    background: #fff8e6;
    border-left: 3px solid var(--warn);
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 13px;
    color: #6a4a10;
    margin: 18px 0;
  }}
  footer {{
    margin-top: 48px;
    font-size: 12px;
    color: var(--muted);
    border-top: 1px solid var(--line);
    padding-top: 16px;
  }}
  a {{ color: var(--accent); }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    background: #f4f4f4;
    padding: 1px 5px;
    border-radius: 4px;
  }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Treasury Fund 2 proposer history</h1>
  <div class="sub">
    What returning TF2 proposers have delivered with prior treasury funds
    &mdash; and which TF2 proposers have never previously taken treasury funds.
  </div>
  <div class="meta">
    Snapshot generated {generated_at} &middot;
    Hydra Voting snapshot {hydra_fetched_at} &middot;
    Archive:
    <a
      href="https://github.com/LloydDuhon/cardano-treasury-history-archive"
      target="_blank"
      rel="noopener"
    >cardano-treasury-history-archive</a>
  </div>
</header>

<section>
  <div class="grid-kpi">
    <div class="kpi">
      <div class="label">TF2 proposals</div>
      <div class="value">{tf2_proposals}</div>
    </div>
    <div class="kpi">
      <div class="label">Unique TF2 proposers</div>
      <div class="value">{tf2_proposers}</div>
    </div>
    <div class="kpi">
      <div class="label">Returning (with prior funding)</div>
      <div class="value">{returning}</div>
    </div>
    <div class="kpi">
      <div class="label">First-time proposers</div>
      <div class="value">{first_timers}</div>
    </div>
  </div>
  <p>
    The Cardano treasury history archive joins each of the 69 current TF2 proposals to historical
    records from Project Catalyst (funds 1&ndash;15) and Treasury Fund 1, then cross-checks against
    on-chain <code>TreasuryWithdrawals</code> governance actions. {returning} of the {tf2_proposers}
    unique TF2 proposers appear in that historical dataset; the remaining {first_timers} have no
    prior treasury record under any of the three sources. None of the {first_timers} first-time
    proposers were reclassified after the on-chain cross-check.
  </p>
  <div class="note">
    <strong>Methodology and confidence.</strong> Catalyst rows are matched at "proposer mentioned
    in proposal text" (medium confidence); TF1 rows are matched at the contract level (high
    confidence). 122 of 607 historical rows are USD-denominated (early Catalyst funds) and have no
    ADA value, so ADA totals understate activity. "MLabs LTD" and "MLabsLTD" are merged for
    display. This is a provenance-first research view, not a final audit opinion.
  </div>
</section>

<section>
  <h2>
    1. Prior treasury ADA by returning proposer
    <span class="count">&mdash; stacked by historical project status</span>
  </h2>
  <figure>
    <img
      src="01-prior-ada-by-proposer.png"
      alt="Prior treasury ADA per returning TF2 proposer by completion status"
    >
    <figcaption>
      Bars are total ADA across all prior Catalyst and TF1 records. Stack
      segments show how that ADA splits across completion status.
    </figcaption>
  </figure>
</section>

<section>
  <h2>2. Count of prior funded proposals <span class="count">&mdash; stacked by status</span></h2>
  <figure>
    <img
      src="02-prior-proposal-count-by-proposer.png"
      alt="Prior proposal counts per returning TF2 proposer by status"
    >
    <figcaption>
      Count view balances the ADA view. Proposers with many small-grant Catalyst
      records appear here even where their ADA totals are modest.
    </figcaption>
  </figure>
</section>

<section>
  <h2>
    3. Overall delivery status mix
    <span class="count">&mdash; across all prior work of the 17 returners</span>
  </h2>
  <figure>
    <img
      src="03-status-mix-overall.png"
      alt="Project-count mix and ADA-weighted mix of historical status"
    >
    <figcaption>
      Left: project count. Right: ADA weight. Status comes from the upstream
      source data (Catalyst and TF1 milestone module / contract status).
    </figcaption>
  </figure>
</section>

<section>
  <h2>
    4. First-time TF2 proposers
    <span class="count">&mdash; {first_timers} proposers with no prior treasury funding</span>
  </h2>
  <figure>
    <img
      src="04-first-time-tf2-proposers.png"
      alt="TF2 ask amounts for first-time proposers"
    >
    <figcaption>
      Each bar is the proposer's total TF2 ask (sum of their proposals'
      <code>totalBudget</code> from the Hydra Voting snapshot).
    </figcaption>
  </figure>
</section>

<section>
  <h2>5. Per-proposer detail table</h2>
  <div class="controls">
    <input type="search" id="q" placeholder="Filter by proposer name...">
  </div>
  <table id="t">
    <thead>
      <tr>
        <th data-key="proposer">Proposer</th>
        <th data-key="total_ada" class="num">Total prior ADA</th>
        <th data-key="n_records" class="num">Records</th>
        <th data-key="n_complete" class="num">Complete</th>
        <th data-key="n_in_progress" class="num">In progress</th>
        <th data-key="n_paused" class="num">Paused</th>
        <th data-key="n_withdrawn" class="num">Withdrawn</th>
        <th data-key="n_risk_flagged" class="num">Flagged</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</section>

<section>
  <h2>6. First-time proposer detail</h2>
  <table>
    <thead>
      <tr>
        <th>Proposer</th>
        <th class="num">TF2 ask (ADA)</th>
        <th class="num">TF2 proposals</th>
      </tr>
    </thead>
    <tbody>{first_rows_html}</tbody>
  </table>
</section>

<footer>
  Generated by <code>etl/scripts/generate_treasury_fund_figures.py</code> &middot;
  Data CC-BY-4.0, code MIT (see archive licenses) &middot;
  Refresh by re-running the upstream report generator, then this script.
</footer>

</div>

<script>
(function() {{
  var q = document.getElementById('q');
  var rows = Array.prototype.slice.call(document.querySelectorAll('#t tbody tr'));
  q.addEventListener('input', function() {{
    var v = q.value.trim().toLowerCase();
    rows.forEach(function(r) {{
      r.style.display = r.dataset.name.toLowerCase().indexOf(v) === -1 ? 'none' : '';
    }});
  }});
  var headers = document.querySelectorAll('#t thead th');
  var lastKey = null; var asc = false;
  headers.forEach(function(h) {{
    h.addEventListener('click', function() {{
      var key = h.dataset.key;
      asc = (key === lastKey) ? !asc : false;
      lastKey = key;
      var sorted = rows.slice().sort(function(a, b) {{
        var av = a.dataset[key], bv = b.dataset[key];
        var an = parseFloat(av), bn = parseFloat(bv);
        if (!isNaN(an) && !isNaN(bn)) {{ return asc ? an - bn : bn - an; }}
        return asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
      }});
      var tbody = document.querySelector('#t tbody');
      sorted.forEach(function(r) {{ tbody.appendChild(r); }});
    }});
  }});
}})();
</script>
</body>
</html>
"""


def _fmt_ada_int(value: float) -> str:
    return f"{int(round(value)):,}"


def build_dashboard_rows_html(summary: pd.DataFrame) -> str:
    out: list[str] = []
    for _, row in summary.iterrows():
        out.append(
            '<tr data-name="{name}" data-proposer="{name}" data-total_ada="{ada}" '
            'data-n_records="{nr}" data-n_complete="{nc}" data-n_in_progress="{nip}" '
            'data-n_paused="{np}" data-n_withdrawn="{nw}" data-n_risk_flagged="{nrf}">'
            "<td>{name}</td>"
            '<td class="num">{ada_fmt}</td>'
            '<td class="num">{nr}</td>'
            '<td class="num">{nc}</td>'
            '<td class="num">{nip}</td>'
            '<td class="num">{np}</td>'
            '<td class="num">{nw}</td>'
            '<td class="num">{nrf}</td>'
            "</tr>".format(
                name=row["proposer"],
                ada=row["total_ada"],
                ada_fmt=_fmt_ada_int(row["total_ada"]),
                nr=row["n_records"],
                nc=row["n_complete"],
                nip=row["n_in_progress"],
                np=row["n_paused"],
                nw=row["n_withdrawn"],
                nrf=row["n_risk_flagged"],
            )
        )
    return "\n".join(out)


def build_first_timer_rows_html(first_timers: pd.DataFrame) -> str:
    out: list[str] = []
    for _, row in first_timers.sort_values("total_budget_ada", ascending=False).iterrows():
        out.append(
            '<tr><td>{name}</td><td class="num">{ada}</td><td class="num">{n}</td></tr>'.format(
                name=row["proposer_canonical"],
                ada=_fmt_ada_int(row["total_budget_ada"]),
                n=int(row["n_tf2_proposals"]),
            )
        )
    return "\n".join(out)


def render_dashboard(
    summary: pd.DataFrame,
    first_timers: pd.DataFrame,
    summary_json: dict[str, Any],
    hydra_fetched_at: str,
    out_path: Path,
) -> None:
    html = DASHBOARD_TEMPLATE.format(
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        hydra_fetched_at=hydra_fetched_at,
        tf2_proposals=summary_json["current_proposals"],
        tf2_proposers=summary_json["current_unique_proposers"],
        returning=summary_json["proposers_with_prior_history"],
        first_timers=len(first_timers),
        rows_html=build_dashboard_rows_html(summary),
        first_rows_html=build_first_timer_rows_html(first_timers),
    )
    out_path.write_text(html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(repo_root: Path) -> None:
    paths = Paths(repo_root)
    paths.out_dir.mkdir(parents=True, exist_ok=True)

    summary_json: dict[str, Any] = json.loads(paths.summary_json.read_text())
    history = load_history(paths.proposer_history_csv)
    tf2 = load_tf2_proposals(paths.hydra_json)

    history_proposers = set(history["proposer_canonical"].dropna().unique())
    onchain_only = find_onchain_only_proposers(tf2, history, paths.onchain_csv)
    all_known = history_proposers | onchain_only

    first_timer_names = sorted(set(tf2["proposer_canonical"]) - all_known)
    first_timers = (
        tf2[tf2["proposer_canonical"].isin(first_timer_names)]
        .groupby("proposer_canonical", as_index=False)
        .agg(total_budget_ada=("total_budget_ada", "sum"), n_tf2_proposals=("proposal_id", "count"))
    )

    summary = build_proposer_summary(history)

    _setup_style()
    plot_ada_by_proposer(summary, paths.out_dir / "01-prior-ada-by-proposer.png")
    plot_count_by_proposer(summary, paths.out_dir / "02-prior-proposal-count-by-proposer.png")
    plot_status_mix_overall(summary, paths.out_dir / "03-status-mix-overall.png")
    plot_first_time_proposers(first_timers, paths.out_dir / "04-first-time-tf2-proposers.png")

    summary.to_csv(paths.out_dir / "figures-data.csv", index=False)
    first_timers.sort_values("total_budget_ada", ascending=False).to_csv(
        paths.out_dir / "first-time-proposers.csv", index=False
    )

    render_dashboard(
        summary=summary,
        first_timers=first_timers,
        summary_json=summary_json,
        hydra_fetched_at=json.loads(paths.hydra_json.read_text())["fetched_at"],
        out_path=paths.out_dir / "tf2-proposer-history-dashboard.html",
    )

    figures_summary: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_summary": str(paths.summary_json.relative_to(repo_root)),
        "tf2_proposals": int(summary_json["current_proposals"]),
        "tf2_unique_proposers": int(summary_json["current_unique_proposers"]),
        "proposers_with_prior_history_per_archive": int(
            summary_json["proposers_with_prior_history"]
        ),
        "returning_proposers_after_alias_merge": int(len(summary)),
        "first_time_proposers_all_sources": int(len(first_timers)),
        "first_time_proposers_catalyst_tf1_only": int(
            len({p for p in tf2["proposer_canonical"].dropna()} - history_proposers)
        ),
        "onchain_only_matches": sorted(onchain_only),
        "entity_resolution_merges": NAME_ALIASES,
        "caveats": [
            "20% of historical rows (122 / 607) are USD-denominated; ADA totals exclude these.",
            "Catalyst rows use medium-confidence proposer-text matching.",
            "On-chain rows overlapping TF1 are not double-counted per archive guidance.",
        ],
    }
    (paths.out_dir / "_figures-summary.json").write_text(
        json.dumps(figures_summary, indent=2) + "\n"
    )

    print(json.dumps(figures_summary, indent=2))


def _argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Path to repository root (defaults to two levels up from this script).",
    )
    return p


if __name__ == "__main__":
    args = _argparser().parse_args()
    main(Path(args.repo_root))
