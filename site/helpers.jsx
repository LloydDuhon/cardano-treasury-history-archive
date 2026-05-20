/* helpers.jsx — shared utilities for the explorer */

const DATA = window.__TREASURY_DATA;

/* ---------- External links ---------- */
function safeHref(value) {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  try {
    const url = new URL(trimmed, window.location.href);
    return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
  } catch {
    return null;
  }
}

function urlLabel(value) {
  if (typeof value !== "string") return "";
  return value.replace(/^https?:\/\//, "").replace(/\/$/, "");
}

function ExternalLink({ href, children, className, style }) {
  const safe = safeHref(href);
  if (!safe) return null;
  return (
    <a href={safe} target="_blank" rel="noopener noreferrer" className={className} style={style}>
      {children}
    </a>
  );
}

/* ---------- Number formatting ---------- */
function fmtAda(n, opts = {}) {
  if (n == null || isNaN(n)) return "—";
  const abs = Math.abs(n);
  if (opts.short && abs >= 1_000_000) return (n / 1_000_000).toFixed(abs >= 10_000_000 ? 1 : 2).replace(/\.?0+$/, "") + "M";
  if (opts.short && abs >= 1_000) return (n / 1_000).toFixed(abs >= 10_000 ? 0 : 1).replace(/\.?0+$/, "") + "k";
  return Math.round(n).toLocaleString("en-US");
}
function fmtCount(n) { return n.toLocaleString("en-US"); }

/* ---------- Proposer normalization (handles "MLabs LTD" / "MLabsLTD") ---------- */
function normName(s) {
  return (s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
}

/* Canonicalize proposer names: pick the most-common spelling per normalized key.
   This is applied IN-PLACE to DATA.proposals so every downstream view agrees. */
(function canonicalizeProposers() {
  const tally = new Map(); // normKey -> Map(rawName -> count)
  for (const p of DATA.proposals) {
    const k = normName(p.proposer);
    if (!tally.has(k)) tally.set(k, new Map());
    const m = tally.get(k);
    m.set(p.proposer, (m.get(p.proposer) || 0) + 1);
  }
  const canon = new Map(); // normKey -> canonical name
  for (const [k, m] of tally) {
    let best, bestN = -1;
    for (const [name, c] of m) {
      if (c > bestN) { bestN = c; best = name; }
    }
    canon.set(k, best);
  }
  /* Rewrite proposals + proposerProposals map */
  for (const p of DATA.proposals) p.proposer = canon.get(normName(p.proposer)) || p.proposer;
  const newPP = {};
  for (const p of DATA.proposals) {
    if (!newPP[p.proposer]) newPP[p.proposer] = { name: p.proposer, proposalIds: [], requestedAda: 0 };
    newPP[p.proposer].proposalIds.push(p.id);
    newPP[p.proposer].requestedAda += p.requested_ada || 0;
  }
  DATA.proposerProposals = newPP;
})();

/* Build a normalized lookup from the proposer-history aggregations so we can
   find history records even when the names disagree slightly. Pick the entry
   with the most projects as the authoritative one. */
const __histByNorm = (() => {
  const m = new Map();
  for (const [name, agg] of Object.entries(DATA.proposerHistory)) {
    const k = normName(name);
    const prior = m.get(k);
    if (!prior || agg.totalProjects > prior.agg.totalProjects) m.set(k, { name, agg });
  }
  return m;
})();
function historyFor(proposerName) {
  const k = normName(proposerName);
  return __histByNorm.get(k)?.agg || null;
}

/* ---------- Identity bridge / TF1 lookups ---------- */
function bridgeFor(proposalId) { return DATA.identityBridge[proposalId] || []; }
function similarityFor(proposalId) { return DATA.similarity[proposalId] || []; }
function workOverlapFor(proposalId) { return DATA.workOverlap?.[proposalId] || []; }

/* ---------- Matched-history metrics ---------- */
function tieMetrics(proposal) {
  const proposer = proposal.proposer;
  const peerProposalIds = DATA.proposerProposals[proposer]?.proposalIds || [proposal.id];
  const h = historyFor(proposer);
  const bridge = bridgeFor(proposal.id);
  const sim = similarityFor(proposal.id);
  const overlap = workOverlapFor(proposal.id);
  return {
    peerProposals: peerProposalIds.length,                /* count of OTHER current proposals from same proposer */
    priorProjects: h?.totalProjects || 0,
    priorAda: h?.totalAda || 0,
    catalystProjects: h?.catalystProjects || 0,
    tf1Projects: h?.tf1Projects || 0,
    has2025: bridge.length > 0,
    similarProjects: sim.length,
    workOverlapMatches: overlap.length,
    withdrawnAda: h?.withdrawnAda || 0,
    pausedAda: h?.pausedAda || 0,
    ongoing: h?.ongoing || 0,
    /* Composite weight used to size graph nodes and rank rows. Heuristic only. */
    weight: (peerProposalIds.length - 1) * 2 + (h?.totalProjects || 0) * 0.6 + (bridge.length > 0 ? 2 : 0)
  };
}

/* ---------- Markdown-lite renderer for proposal summaries ---------- */
/* The proposal summaries use simple **bold** markup. Render with minimal tags. */
function renderMd(text) {
  if (!text) return null;
  const paras = text.split(/\n{2,}/).filter(p => p.trim());
  return paras.map((para, i) => {
    const parts = [];
    let buf = "";
    let inB = false, j = 0;
    while (j < para.length) {
      if (para[j] === "*" && para[j+1] === "*") {
        if (buf) parts.push(inB ? <strong key={`${i}-${parts.length}`}>{buf}</strong> : buf);
        buf = "";
        inB = !inB;
        j += 2;
      } else { buf += para[j]; j++; }
    }
    if (buf) parts.push(inB ? <strong key={`${i}-end`}>{buf}</strong> : buf);
    return <p key={i}>{parts}</p>;
  });
}

/* ---------- Source palette (matches styles.css tokens) ---------- */
const SOURCE = {
  current:    { stroke: "var(--src-current)",  fill: "var(--src-current)",  label: "Treasury Fund 2 (current)" },
  catalyst:   { stroke: "var(--src-catalyst)", fill: "var(--src-catalyst)", label: "Project Catalyst (historical)" },
  tf1:        { stroke: "var(--src-tf1)",      fill: "var(--src-tf1)",      label: "Treasury Fund 1 (historical)" },
  onchain:    { stroke: "var(--src-2025)",     fill: "var(--src-2025)",     label: "On-chain treasury withdrawal" },
  builderdao: { stroke: "var(--src-current)",  fill: "var(--src-current)",  label: "BuilderDAO downstream disbursement" },
  b2025:      { stroke: "var(--src-2025)",     fill: "var(--src-2025)",     label: "2025 Budget Process (identity)" }
};
function sourceKey(src) {
  if (src === "Project Catalyst") return "catalyst";
  if (src === "Treasury Fund 1") return "tf1";
  if (src === "On-chain TreasuryWithdrawals") return "onchain";
  if (src === "BuilderDAO downstream disbursement") return "builderdao";
  return "current";
}
function statusClass(s) {
  if (!s) return "";
  if (s === "in_progress") return "in_progress";
  return s.replace(/[^a-z]/g, "");
}

/* ---------- Status label ---------- */
function statusLabel(s) {
  return ({
    complete: "Complete",
    in_progress: "In progress",
    active: "Active",
    withdrawn: "Withdrawn",
    paused: "Paused",
    not_started: "Not started",
    contracted: "Contracted",
    approved: "Approved",
    live: "Live"
  })[s] || s || "—";
}

/* Catalyst fund number from project id like "f10-..." */
function fundNumber(pid) {
  const m = /^f(\d{1,2})/.exec(pid || "");
  return m ? `Fund ${parseInt(m[1], 10)}` : null;
}

Object.assign(window, {
  DATA, fmtAda, fmtCount, normName, historyFor, bridgeFor, similarityFor, workOverlapFor,
  tieMetrics, renderMd, SOURCE, sourceKey, statusClass, statusLabel, fundNumber,
  safeHref, urlLabel, ExternalLink
});
