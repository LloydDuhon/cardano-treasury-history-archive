const COLORS = { P1: "var(--p1)", P2: "var(--p2)", P3: "var(--p3)", P4: "var(--p4)", P5: "var(--p5)", PX: "var(--px)" };
const state = { measure: "requested", unit: "count", dimension: "year", data: null };

function number(value) { return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value || 0); }
function amount(value, currency) {
  const prefix = currency === "ADA" ? "₳" : currency === "USD" ? "$" : currency === "USDM" ? "USDM " : "";
  return prefix + number(value);
}
function esc(value) {
  const node = document.createElement("span");
  node.textContent = String(value ?? "");
  return node.innerHTML;
}
function valueFor(row) {
  return state.unit === "count" ? row[`${state.measure}_proposals`] : row[`${state.measure}_amount`];
}
function periodLabel(value) { return state.dimension === "fund" ? `F${value}` : String(value); }

function renderLegend() {
  const el = document.getElementById("legend");
  el.innerHTML = Object.entries(state.data.pillars).map(([key, pillar]) =>
    `<span><i style="background:${COLORS[key]}"></i>${esc(key)} · ${esc(pillar.name)}</span>`
  ).join("");
}

function filteredRows() {
  const rows = state.data[state.dimension === "fund" ? "by_fund" : "by_year"];
  return state.unit === "count" ? rows : rows.filter(row => row.currency === state.unit);
}

function renderChart() {
  const rows = filteredRows();
  const dimension = state.dimension;
  const grouped = new Map();
  rows.forEach(row => {
    const key = row[dimension];
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(row);
  });
  const totals = [...grouped.entries()].map(([key, values]) => [key, values.reduce((sum, row) => sum + valueFor(row), 0)]);
  const max = Math.max(0, ...totals.map(([, total]) => total));
  const chart = document.getElementById("chart");
  const empty = document.getElementById("empty-chart");
  empty.hidden = max > 0;
  chart.hidden = max === 0;
  chart.innerHTML = totals.map(([period, total]) => {
    const segments = grouped.get(period).filter(row => valueFor(row) > 0).map(row => {
      const width = max ? (valueFor(row) / max) * 100 : 0;
      const label = `${row.pillar}: ${state.unit === "count" ? number(valueFor(row)) : amount(valueFor(row), state.unit)}`;
      return `<span class="segment" style="width:${width}%;background:${COLORS[row.pillar]}" title="${esc(label)}"></span>`;
    }).join("");
    const display = state.unit === "count" ? number(total) : amount(total, state.unit);
    return `<div class="bar-row"><span class="period">${periodLabel(period)}</span><span class="bar-track">${segments}</span><span class="bar-value">${display}</span></div>`;
  }).join("");
  const measure = state.measure[0].toUpperCase() + state.measure.slice(1);
  const unit = state.unit === "count" ? "proposals" : `${state.unit} amount`;
  document.getElementById("chart-title").textContent = `${measure} ${unit} by ${state.dimension}`;
}

function renderTable() {
  const rows = state.data[state.dimension === "fund" ? "by_fund" : "by_year"];
  document.getElementById("detail-rows").innerHTML = rows.map(row => `
    <tr>
      <td>${periodLabel(row[state.dimension])}</td>
      <td><span class="pillar-mark" style="background:${COLORS[row.pillar]}"></span>${esc(row.pillar)} · ${esc(row.pillar_name)}</td>
      <td>${esc(row.currency)}</td>
      <td>${number(row.requested_proposals)}</td><td>${amount(row.requested_amount, row.currency)}</td>
      <td>${number(row.funded_proposals)}</td><td>${amount(row.funded_amount, row.currency)}</td>
      <td>${number(row.delivered_proposals)}</td><td>${amount(row.delivered_amount, row.currency)}</td>
    </tr>`).join("");
}

function render() { renderChart(); renderTable(); }

document.querySelectorAll("[data-measure]").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll("[data-measure]").forEach(item => item.classList.remove("active"));
  button.classList.add("active");
  state.measure = button.dataset.measure;
  render();
}));
document.getElementById("unit-select").addEventListener("change", event => { state.unit = event.target.value; renderChart(); });
document.getElementById("dimension-select").addEventListener("change", event => { state.dimension = event.target.value; render(); });

fetch("funding-priorities-data.json")
  .then(response => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); })
  .then(data => {
    state.data = data;
    document.getElementById("asof").textContent = `Archive snapshot ${data.meta.source_snapshot.slice(0, 10)} · generated ${data.meta.generated_at.slice(0, 10)}`;
    document.getElementById("proposal-count").textContent = number(data.meta.proposal_count);
    const classified = data.meta.proposal_count - (data.meta.confidence_counts.low || 0);
    document.getElementById("coverage").textContent = `${((classified / data.meta.proposal_count) * 100).toFixed(1)}%`;
    renderLegend();
    render();
    document.getElementById("loading").hidden = true;
    document.getElementById("content").hidden = false;
  })
  .catch(() => {
    document.getElementById("loading").hidden = true;
    document.getElementById("error").hidden = false;
  });
