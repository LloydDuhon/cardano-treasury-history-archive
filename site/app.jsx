/* app.jsx — Treasury Fund 2 History Explorer */
const { useState, useMemo, useEffect, useRef, useCallback } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "tieThreshold": 3,
  "labelMode": "smart",
  "highlightHighTies": true,
  "showZeroHistory": false,
  "accent": "#0033AD"
}/*EDITMODE-END*/;

const VIEWS = [
  { id: "graph",  label: "Funding graph", hint: "Network" },
  { id: "ledger", label: "Proposal ledger",    hint: "Table"   },
  { id: "findings", label: "Similarity findings", hint: "Review" },
  { id: "flow",   label: "Funding flow",       hint: "Sankey"  }
];

/* ---------- KPI strip ---------- */
function KpiStrip({ stats }) {
  return (
    <div className="kpis">
      <div className="kpi">
        <div className="lbl">Current proposals</div>
        <div className="val">{stats.proposals}</div>
        <div className="sub">Treasury Fund 2 · live snapshot</div>
      </div>
      <div className="kpi">
        <div className="lbl">Display proposers</div>
        <div className="val">{stats.proposers}</div>
        <div className="sub">{stats.rawProposers} source names; MLabs alias merged</div>
      </div>
      <div className="kpi accent">
        <div className="lbl">Total ADA requested</div>
        <div className="val">₳ {fmtAda(stats.requestedAda, { short: true })}</div>
        <div className="sub">{fmtAda(stats.requestedAda)} ADA</div>
      </div>
      <div className="kpi">
        <div className="lbl">Prior funding matched</div>
        <div className="val">{stats.withHistory}<span style={{ color: "var(--ink-faint)", fontSize: 13, marginLeft: 6 }}>/{stats.proposers}</span></div>
        <div className="sub">{stats.rawWithHistory} source-name matches before alias merge</div>
      </div>
      <div className="kpi">
        <div className="lbl">Historical ADA matched</div>
        <div className="val">₳ {fmtAda(stats.priorAda, { short: true })}</div>
        <div className="sub">across {stats.priorProjects} prior projects</div>
      </div>
    </div>
  );
}

/* ---------- Sidebar (shared filters) ---------- */
function Sidebar({ filters, setFilters, view, threshold, setThreshold }) {
  const update = (k, v) => setFilters({ ...filters, [k]: v });
  return (
    <aside className="sidebar">
      <div className="group">
        <h3>Search</h3>
        <input
          type="search"
          placeholder="Proposer, proposal, project id…"
          value={filters.q}
          onChange={e => update("q", e.target.value)}
        />
      </div>

      <div className="group">
        <h3>Show proposals where proposer has…</h3>
        <label className="row">
          <input type="checkbox" checked={filters.priorCatalyst}
                 onChange={e => update("priorCatalyst", e.target.checked)} />
          <span className="swatch" style={{ background: "var(--src-catalyst)" }}></span>
          Project Catalyst funding history
        </label>
        <label className="row">
          <input type="checkbox" checked={filters.priorTf1}
                 onChange={e => update("priorTf1", e.target.checked)} />
          <span className="swatch" style={{ background: "var(--src-tf1)" }}></span>
          Treasury Fund 1 funding history
        </label>
        <label className="row">
          <input type="checkbox" checked={filters.has2025}
                 onChange={e => update("has2025", e.target.checked)} />
          <span className="swatch" style={{ background: "var(--src-2025)" }}></span>
          2025 Budget Process identity bridge
        </label>
        <label className="row">
          <input type="checkbox" checked={filters.multiProposal}
                 onChange={e => update("multiProposal", e.target.checked)} />
          <span className="swatch" style={{ background: "var(--tier-hi)" }}></span>
          Multiple Treasury Fund 2 proposals
        </label>
        <label className="row">
          <input type="checkbox" checked={filters.noHistory}
                 onChange={e => update("noHistory", e.target.checked)} />
          <span className="swatch" style={{ background: "var(--ink-faint)", borderRadius: 1 }}></span>
          No prior funding recorded
        </label>
      </div>

      <div className="group">
        <h3>History threshold</h3>
        <div className="range-wrap">
          <input
            type="range" min={0} max={10} step={1}
            value={threshold}
            onChange={e => setThreshold(parseInt(e.target.value))}
          />
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--ink-faint)" }}>
            <span>0</span>
            <span className="threshold-value">≥ {threshold} prior projects</span>
            <span>10</span>
          </div>
        </div>
        <div style={{ fontSize: 11, color: "var(--ink-mute)", lineHeight: 1.5, marginTop: 4 }}>
          Proposers at or above this count receive a subtle visual emphasis.
        </div>
      </div>

      <div className="group">
        <h3>Legend</h3>
        <div className="legend">
          <div className="item"><span className="marker" style={{ background: "var(--src-current)" }}></span> Current proposal</div>
          <div className="item"><span className="marker sq" style={{ background: "var(--src-catalyst)" }}></span> Project Catalyst record</div>
          <div className="item"><span className="marker sq" style={{ background: "var(--src-tf1)" }}></span> Treasury Fund 1 record</div>
        <div className="item"><span className="marker" style={{ background: "var(--paper)", border: "2px solid var(--tier-hi)" }}></span> At or above threshold</div>
        </div>
      </div>

      <div className="footnote">
        <strong>Note —</strong> Counts and amounts are taken from the open archive's matched records.
        Match confidence varies; see methodology. This view is descriptive and does not make
        recommendations.
      </div>
    </aside>
  );
}

/* ---------- Tab bar ---------- */
function TabBar({ view, setView, onOpenMethodology }) {
  return (
    <div className="tabbar">
      <div className="tabs">
        {VIEWS.map(v => (
          <button
            key={v.id}
            className={"tab " + (view === v.id ? "active" : "")}
            onClick={() => setView(v.id)}
          >
            <ViewIcon view={v.id} />
            {v.label}
            <span className="tabhint">{v.hint}</span>
          </button>
        ))}
      </div>
      <button className="method-pill" onClick={onOpenMethodology}>
        <span className="d"></span>Methodology & sources
      </button>
    </div>
  );
}
function ViewIcon({ view }) {
  if (view === "graph") return <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <circle cx="3" cy="3" r="2" stroke="currentColor" /><circle cx="11" cy="3" r="2" stroke="currentColor" />
    <circle cx="7" cy="11" r="2" stroke="currentColor" /><path d="M3 3 L7 11 M11 3 L7 11 M3 3 L11 3" stroke="currentColor" />
  </svg>;
  if (view === "ledger") return <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M2 3h10M2 7h10M2 11h10" stroke="currentColor" /><path d="M5 3v8" stroke="currentColor" />
  </svg>;
  if (view === "findings") return <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M2 2.5h6M2 6.5h10M2 10.5h7" stroke="currentColor" />
    <circle cx="10.5" cy="2.5" r="1.5" stroke="currentColor" />
    <path d="M11.6 3.6L13 5" stroke="currentColor" />
  </svg>;
  return <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M2 4c4 0 4 6 8 6h2" stroke="currentColor" strokeWidth="2" />
    <path d="M2 8c3 0 3 -4 7 -4h3" stroke="currentColor" strokeWidth="1" />
  </svg>;
}

/* ---------- Methodology modal ---------- */
function Methodology({ onClose, meta }) {
  return (
    <div className="modal-back" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="h">
          <h2>Methodology & sources</h2>
          <button onClick={onClose}>×</button>
        </div>
        <div className="c">
          <p>This explorer is a presentation layer over the <code>cardano-treasury-history-archive</code> open dataset.
             It shows current proposals alongside historical funding records matched by the archive.</p>

          <h3>What is shown</h3>
          <ul>
            <li><strong>69 current proposals</strong> from the Cardano Budget 2026 (Treasury Fund 2) snapshot.</li>
            <li><strong>Prior Project Catalyst funding</strong> matched by proposer name / proposal-text mention.</li>
            <li><strong>Treasury Fund 1 contracts</strong> reconciled against the 2025 Budget Process ekklesia metadata.</li>
            <li><strong>2025 Budget Process identity bridges</strong> — company name, domain, social handles, vote summary.</li>
            <li><strong>Similarity findings</strong> from the prior-work overlap review. AI Matched rows are screening results and require human review before final use.</li>
          </ul>

          <h3>History threshold</h3>
          <p>The threshold is a count: <em>k or more matched prior projects</em> for the same proposer.
             Rows at or above the threshold receive a subtle visual emphasis.</p>

          <h3>Match confidence</h3>
          <p>Most proposer↔history joins are at <code>medium</code> confidence (0.82 mention-based) or <code>high</code> (0.92+ identity-bridge / TF1).
             Confidence is shown on each history row in the detail drawer.</p>

          <h3>Limits</h3>
          <ul>
            <li>Not a vendor disbursement record — Catalyst "approved" ≠ paid out, and TF1 contract amounts can include withdrawn / paused tranches.</li>
            <li>Not a closeout audit — milestone completion evidence is partial.</li>
            <li>Not exhaustive — proposers with no prior match still appear; absence is not evidence of absence.</li>
          </ul>

          <h3>Snapshot</h3>
          <p style={{ fontFamily: "var(--mono)", fontSize: 12 }}>
            Generated: {meta.generated_at}<br />
            Source: <ExternalLink href={meta.snapshot_source}>{meta.snapshot_source}</ExternalLink><br />
            Archive: <ExternalLink href="https://github.com/LloydDuhon/cardano-treasury-history-archive">github.com/LloydDuhon/cardano-treasury-history-archive</ExternalLink>
          </p>
        </div>
      </div>
    </div>
  );
}

/* ---------- Filter logic ---------- */
function applyFilters(proposals, filters) {
  return proposals.filter(p => {
    if (filters.q) {
      const q = filters.q.toLowerCase();
      const t = (p.title + " " + p.proposer + " " + p.id).toLowerCase();
      if (!t.includes(q)) return false;
    }
    const m = tieMetrics(p);
    if (!filters.priorCatalyst && !filters.priorTf1 && !filters.has2025 && !filters.multiProposal && !filters.noHistory) {
      return true; // nothing selected = show all
    }
    if (filters.priorCatalyst && m.catalystProjects > 0) return true;
    if (filters.priorTf1 && m.tf1Projects > 0) return true;
    if (filters.has2025 && m.has2025) return true;
    if (filters.multiProposal && m.peerProposals > 1) return true;
    if (filters.noHistory && m.priorProjects === 0 && !m.has2025) return true;
    return false;
  });
}

/* ---------- App root ---------- */
function App() {
  const [t, setT] = useState(TWEAK_DEFAULTS);
  const setTweak = useCallback((key, value) => {
    setT(current => ({ ...current, [key]: value }));
  }, []);
  const [view, setView] = useState("graph");
  const [filters, setFilters] = useState({
    q: "",
    priorCatalyst: false,
    priorTf1: false,
    has2025: false,
    multiProposal: false,
    noHistory: false
  });
  const [selected, setSelected] = useState(null); // { kind:'proposal'|'proposer', id }
  const [methodOpen, setMethodOpen] = useState(false);

  /* Apply accent live */
  useEffect(() => {
    document.documentElement.style.setProperty("--cardano", t.accent);
  }, [t.accent]);

  const filteredProposals = useMemo(
    () => applyFilters(DATA.proposals, filters),
    [filters]
  );

  const stats = useMemo(() => ({
    proposals: DATA.proposals.length,
    proposers: DATA.meta.unique_proposers,
    rawProposers: DATA.meta.raw_unique_proposers || DATA.meta.unique_proposers,
    requestedAda: DATA.meta.total_requested_ada,
    withHistory: DATA.meta.proposers_with_history,
    rawWithHistory: DATA.meta.raw_proposers_with_history || DATA.meta.proposers_with_history,
    priorAda: DATA.meta.total_historical_ada,
    priorProjects: Object.values(DATA.proposerHistory).reduce((s, a) => s + a.totalProjects, 0),
    multiProposers: DATA.meta.multi_proposal_proposers
  }), []);

  const openProposal = useCallback((id) => setSelected({ kind: "proposal", id }), []);
  const openProposer = useCallback((name) => setSelected({ kind: "proposer", id: name }), []);
  const closeDrawer = useCallback(() => setSelected(null), []);

  return (
    <div className={"app " + (view === "findings" ? "findings-active" : "")}>
      <header className="topbar">
        <div className="brand">
          <div className="eyebrow"><span className="dot"></span> Cardano · Budget Committee briefing</div>
          <h1>Treasury Fund 2 — History Explorer</h1>
          <div className="sub">Explore the 69 current proposals, 51 proposers, and prior Cardano funding records matched by the open archive.</div>
        </div>
        <div className="meta">
          <span><a href="funding-priorities.html">funding priorities</a></span>
          <span><span className="meta-k">snapshot </span><span className="meta-v">{(DATA.meta.generated_at || "").slice(0,10)}</span></span>
          <span><span className="meta-k">source </span><ExternalLink href={DATA.meta.snapshot_source}>hydra-voting</ExternalLink></span>
        </div>
      </header>

      <KpiStrip stats={stats} />

      <div className={"body " + (view === "findings" ? "findings-mode" : "")}>
        <Sidebar filters={filters} setFilters={setFilters} view={view}
                 threshold={t.tieThreshold} setThreshold={v => setTweak("tieThreshold", v)} />
        <div className="main">
          <TabBar view={view} setView={setView} onOpenMethodology={() => setMethodOpen(true)} />
          <div className="viewport">
            {view === "graph" && (
              <GraphView
                proposals={filteredProposals}
                threshold={t.tieThreshold}
                labelMode={t.labelMode}
                highlightHighTies={t.highlightHighTies}
                showZeroHistory={t.showZeroHistory}
                selected={selected}
                onOpenProposal={openProposal}
                onOpenProposer={openProposer}
              />
            )}
            {view === "ledger" && (
              <LedgerView
                proposals={filteredProposals}
                threshold={t.tieThreshold}
                selected={selected}
                onOpenProposal={openProposal}
              />
            )}
            {view === "findings" && (
              <FindingsView
                proposals={filteredProposals}
                onOpenProposal={openProposal}
              />
            )}
            {view === "flow" && (
              <FlowView
                proposals={filteredProposals}
                threshold={t.tieThreshold}
                onOpenProposer={openProposer}
              />
            )}
          </div>
        </div>
      </div>

      {selected && <Drawer selected={selected} onClose={closeDrawer} onJump={(s) => setSelected(s)} threshold={t.tieThreshold} />}
      {methodOpen && <Methodology onClose={() => setMethodOpen(false)} meta={DATA.meta} />}

    </div>
  );
}

/* ---------- Drawer ---------- */
function Drawer({ selected, onClose, onJump, threshold }) {
  if (selected.kind === "proposal") return <ProposalDrawer id={selected.id} onClose={onClose} onJump={onJump} threshold={threshold} />;
  return <ProposerDrawer name={selected.id} onClose={onClose} onJump={onJump} threshold={threshold} />;
}

function ProposalDrawer({ id, onClose, onJump, threshold }) {
  const p = DATA.proposals.find(x => x.id === id);
  const [expanded, setExpanded] = useState(false);
  if (!p) return null;
  const m = tieMetrics(p);
  const bridge = bridgeFor(id);
  const sim = similarityFor(id);
  const overlap = workOverlapFor(id);
  const peers = DATA.proposerProposals[p.proposer]?.proposalIds || [];
  const hi = m.priorProjects >= threshold || m.peerProposals > 1;

  return (
    <aside className="drawer">
      <div className="x">
        <span>Proposal · TF2</span>
        <button onClick={onClose} aria-label="Close">×</button>
      </div>
      <div className="head">
        <div className="kind">{p.entityType ? p.entityType : "—"} · submitted {p.submittedAt?.slice(0,10)}</div>
        <h2>{p.title}</h2>
        <div className="id">{p.id}</div>
        <div className="ada">
          <div>
            <div className="l">Requested</div>
            <div className="v">₳ {fmtAda(p.requested_ada)}</div>
          </div>
          <div>
            <div className="l">Proposer</div>
            <div className="v" style={{ cursor: "pointer", textDecoration: "underline", textDecorationColor: "var(--cardano-soft)" }}
                 onClick={() => onJump({ kind: "proposer", id: p.proposer })}>
              {p.proposer}
            </div>
          </div>
          <div style={{ marginLeft: "auto" }}>
            <div className="l">Matched history</div>
            <div className="v">
              <span className={"tier " + (hi ? "hi" : "")}>
                <span className="b"></span>
                {m.priorProjects} prior · {m.peerProposals} current
              </span>
            </div>
          </div>
        </div>
      </div>

      {p.summary && (
        <div className="section">
          <h3>Summary <span className="count">from proposer</span></h3>
          <div className={"summary " + (expanded ? "expanded" : "")}>{renderMd(p.summary)}</div>
          <button className="expand-btn" onClick={() => setExpanded(!expanded)}>
            {expanded ? "↑ collapse" : "↓ read more"}
          </button>
        </div>
      )}

      {peers.length > 1 && (
        <div className="section">
          <h3>Other current proposals from {p.proposer} <span className="count">{peers.length - 1}</span></h3>
          <div className="history-list">
            {peers.filter(pid => pid !== id).map(pid => {
              const peer = DATA.proposals.find(x => x.id === pid);
              if (!peer) return null;
              return (
                <div key={pid} className="history-row" style={{ cursor: "pointer" }} onClick={() => onJump({ kind: "proposal", id: pid })}>
                  <div>
                    <div className="ht">{peer.title}</div>
                    <div className="hm"><span className="src" style={{ color: "var(--src-current)", background: "oklch(0.30 0.06 264 / 0.08)" }}>TF2 · current</span></div>
                  </div>
                  <div className="ada">{fmtAda(peer.requested_ada, { short: true })}<span className="unit"> ADA</span></div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <ProposerHistorySection name={p.proposer} />

      {bridge.length > 0 && (
        <div className="section">
          <h3>2025 Budget Process identity bridge <span className="count">{bridge.length}</span></h3>
          {bridge.slice(0, 3).map((b, i) => (
            <div key={i} className="identity-block" style={{ marginBottom: 12 }}>
              <div className="identity-row"><span className="l">Company</span><span className="v">{b.company_name || "—"}</span></div>
              {b.group_name && <div className="identity-row"><span className="l">Group</span><span className="v">{b.group_name}</span></div>}
              {safeHref(b.domain) && <div className="identity-row"><span className="l">Domain</span><span className="v"><ExternalLink href={b.domain}>{urlLabel(b.domain)}</ExternalLink></span></div>}
              {b.social_handles && <div className="identity-row"><span className="l">Socials</span><span className="v mono">{b.social_handles}</span></div>}
              {b.public_champion && <div className="identity-row"><span className="l">Champion</span><span className="v">{b.public_champion}</span></div>}
              <div className="identity-row"><span className="l">2025 ask</span><span className="v">₳ {fmtAda(b.budget_2025_cost_ada)} · threshold {b.threshold_reached ? "reached" : "not reached"}</span></div>
              <div className="identity-row"><span className="l">2025 title</span><span className="v">{b.budget_2025_title}</span></div>
              <div className="identity-row"><span className="l">Match</span><span className="v mono">{b.match_confidence} · {b.match_score?.toFixed(2)}</span></div>
            </div>
          ))}
        </div>
      )}

      {overlap.length > 0 && (
        <div className="section">
          <h3>Prior work overlap review <span className="count">{overlap.length}</span></h3>
          <div className="method-note">
            Candidate matches are screening results. Rows marked AI Matched require human review before final use.
          </div>
          <div className="history-list">
            {overlap.map((o, i) => (
              <div key={i} className="history-row overlap-row">
                <div>
                  <div className="ht">{o.historical_title}</div>
                  <div className="hm">
                    <span className={"src " + sourceKey(o.historical_source)}>{o.historical_source}</span>
                    {fundNumber(o.historical_project_id) && <span>· {fundNumber(o.historical_project_id)}</span>}
                    <span className={"status " + statusClass(o.historical_status)}>{statusLabel(o.historical_status)}</span>
                    <span className={"review-chip " + (o.adjudication_source === "Human Reviewed" ? "human" : "ai")}>{o.adjudication_source}</span>
                  </div>
                  <div className="overlap-metrics">
                    <span className={"confidence " + o.match_confidence}>{o.match_confidence}</span>
                    <span>{o.work_overlap_percent}% overlap</span>
                    <span>{o.overlap_type}</span>
                    <span>funding: {o.previously_funded_relevance}</span>
                    <span>proposer: {o.same_or_related_proposer}</span>
                  </div>
                  {o.overlap_evidence && <div className="evidence">{o.overlap_evidence}</div>}
                  {o.funding_evidence && <div className="evidence muted">{o.funding_evidence}</div>}
                </div>
                <ExternalLink href={o.source_url} style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--cardano)" }}>open ↗</ExternalLink>
              </div>
            ))}
          </div>
        </div>
      )}

      {sim.length > 0 && (
        <div className="section">
          <h3>Scope-similar past projects <span className="count">{sim.length}</span></h3>
          <div className="history-list">
            {sim.map((s, i) => (
              <div key={i} className="history-row">
                <div>
                  <div className="ht">{s.historical_title}</div>
                  <div className="hm">
                    <span className={"src " + sourceKey(s.source)}>{s.source}</span>
                    {fundNumber(s.historical_project_id) && <span>· {fundNumber(s.historical_project_id)}</span>}
                    <span className={"status " + statusClass(s.historical_status)}>{statusLabel(s.historical_status)}</span>
                    <span>· similarity {s.similarity.toFixed(2)} ({s.confidence})</span>
                  </div>
                  <div style={{ fontSize: 11, color: "var(--ink-faint)", marginTop: 3, fontStyle: "italic" }}>{s.rationale}</div>
                </div>
                <ExternalLink href={s.source_url} style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--cardano)" }}>open ↗</ExternalLink>
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}

function ProposerDrawer({ name, onClose, onJump, threshold }) {
  const proposerInfo = DATA.proposerProposals[name];
  const h = historyFor(name);
  const totalRequested = proposerInfo?.requestedAda || 0;
  const hi = (h?.totalProjects || 0) >= threshold;
  return (
    <aside className="drawer">
      <div className="x">
        <span>Proposer</span>
        <button onClick={onClose} aria-label="Close">×</button>
      </div>
      <div className="head">
        <div className="kind">Aggregated profile across TF2 + history</div>
        <h2>{name}</h2>
        <div className="ada">
          <div>
            <div className="l">Current proposals</div>
            <div className="v">{proposerInfo?.proposalIds.length || 0}</div>
          </div>
          <div>
            <div className="l">Requested TF2</div>
            <div className="v">₳ {fmtAda(totalRequested, { short: true })}</div>
          </div>
          <div>
            <div className="l">Prior matched ADA</div>
            <div className="v">₳ {fmtAda(h?.totalAda || 0, { short: true })}</div>
          </div>
          <div style={{ marginLeft: "auto" }}>
            <div className="l">Matched history</div>
            <div className="v">
              <span className={"tier " + (hi ? "hi" : "")}>
                <span className="b"></span>
                {h?.totalProjects || 0} prior
              </span>
            </div>
          </div>
        </div>
      </div>

      {proposerInfo?.proposalIds && (
        <div className="section">
          <h3>Current Treasury Fund 2 proposals <span className="count">{proposerInfo.proposalIds.length}</span></h3>
          <div className="history-list">
            {proposerInfo.proposalIds.map(pid => {
              const p = DATA.proposals.find(x => x.id === pid);
              if (!p) return null;
              return (
                <div key={pid} className="history-row" style={{ cursor: "pointer" }} onClick={() => onJump({ kind: "proposal", id: pid })}>
                  <div>
                    <div className="ht">{p.title}</div>
                    <div className="hm"><span style={{ fontFamily: "var(--mono)" }}>{p.id}</span></div>
                  </div>
                  <div className="ada">{fmtAda(p.requested_ada)}<span className="unit"> ADA</span></div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <ProposerHistorySection name={name} compact />
    </aside>
  );
}

/* Reusable section listing prior funding history */
function ProposerHistorySection({ name, compact }) {
  const h = historyFor(name);
  if (!h || h.totalProjects === 0) {
    return (
      <div className="section">
        <h3>Prior Cardano funding history</h3>
        <div className="empty">No matched prior Catalyst or Treasury Fund 1 record for this proposer in the archive snapshot.</div>
      </div>
    );
  }
  const projects = [...h.projects].sort((a, b) => (b.amount_ada || 0) - (a.amount_ada || 0));
  return (
    <div className="section">
      <h3>Prior Cardano funding history <span className="count">{h.totalProjects} projects · ₳ {fmtAda(h.totalAda, { short: true })}</span></h3>
      <div style={{ display: "flex", gap: 16, marginBottom: 12, fontFamily: "var(--mono)", fontSize: 11, color: "var(--ink-mute)" }}>
        <span><span style={{ color: "var(--src-catalyst)" }}>● </span>Catalyst: {h.catalystProjects}</span>
        <span><span style={{ color: "var(--src-tf1)" }}>● </span>TF1: {h.tf1Projects}</span>
        {h.ongoing > 0 && <span><span className="status in_progress" style={{ color: "var(--st-progress)" }}>● </span>{h.ongoing} ongoing</span>}
        {h.withdrawnAda > 0 && <span><span className="status" style={{ color: "var(--st-withdrawn)" }}>● </span>{fmtAda(h.withdrawnAda, { short: true })} withdrawn</span>}
        {h.pausedAda > 0 && <span><span className="status" style={{ color: "var(--st-paused)" }}>● </span>{fmtAda(h.pausedAda, { short: true })} paused</span>}
      </div>
      <div className="history-list">
        {projects.slice(0, compact ? 12 : 30).map((p, i) => (
          <div key={i} className="history-row">
            <div>
              <div className="ht">{p.title}</div>
              <div className="hm">
                <span className={"src " + sourceKey(p.source)}>{p.source}</span>
                {fundNumber(p.project_id) && <span>· {fundNumber(p.project_id)}</span>}
                <span className={"status " + statusClass(p.status)}>{statusLabel(p.status)}</span>
                <span style={{ color: "var(--ink-faint)" }}>· {p.match_confidence} match</span>
                <ExternalLink href={p.source_url} style={{ marginLeft: 4, color: "var(--cardano)" }}>↗</ExternalLink>
              </div>
            </div>
            <div className="ada">
              {p.amount_ada ? fmtAda(p.amount_ada) : (p.amount_original || "—")}
              {p.amount_ada ? <span className="unit"> ADA</span> : null}
            </div>
          </div>
        ))}
        {projects.length > (compact ? 12 : 30) && (
          <div style={{ padding: "8px 0", color: "var(--ink-faint)", fontSize: 11, fontFamily: "var(--mono)" }}>
            …and {projects.length - (compact ? 12 : 30)} more
          </div>
        )}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
