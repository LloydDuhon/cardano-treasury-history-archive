/* flow-view.jsx — Sankey flow from prior funding → proposer → current asks */
const { useRef: useRefFV, useEffect: useEffectFV, useMemo: useMemoFV, useState: useStateFV } = React;

function FlowView({ proposals, threshold, onOpenProposer }) {
  const wrapRef = useRefFV(null);
  const svgRef  = useRefFV(null);
  const [hover, setHover] = useStateFV(null);

  /* Build sankey input: 3-column layout:
       (0) prior source (Catalyst, TF1, 2025 BP-flag)
       (1) proposer
       (2) current proposal
     Only include proposers that have a recorded prior history or 2025 bridge or multi-proposal.
  */
  const graph = useMemoFV(() => {
    const proposerSet = new Map();
    for (const p of proposals) {
      if (!proposerSet.has(p.proposer)) proposerSet.set(p.proposer, []);
      proposerSet.get(p.proposer).push(p);
    }

    const eligible = [...proposerSet.entries()].filter(([name, ps]) => {
      const h = historyFor(name);
      return (h && h.totalProjects > 0) || ps.length > 1;
    });

    const nodes = [];
    const idx = new Map();
    function add(id, label, kind, meta = {}) {
      if (!idx.has(id)) { idx.set(id, nodes.length); nodes.push({ id, label, kind, ...meta }); }
      return idx.get(id);
    }
    const links = [];

    /* Source columns */
    add("src:catalyst", "Project Catalyst (prior)", "source", { color: "var(--src-catalyst)" });
    add("src:tf1",      "Treasury Fund 1 (prior)",   "source", { color: "var(--src-tf1)" });

    /* Aggregate per proposer */
    const includedProposers = [];
    for (const [name, currentList] of eligible) {
      const h = historyFor(name);
      const reqSum = currentList.reduce((s,p) => s + (p.requested_ada || 0), 0);
      add("prop:" + name, name, "proposer", { ada: reqSum, priorProjects: h?.totalProjects || 0, priorAda: h?.totalAda || 0 });
      includedProposers.push(name);

      /* Flow from sources */
      if (h && h.catalystAda > 0) links.push({ source: "src:catalyst", target: "prop:" + name, value: h.catalystAda, kind: "prior" });
      if (h && h.tf1Ada > 0)      links.push({ source: "src:tf1",      target: "prop:" + name, value: h.tf1Ada,      kind: "prior" });
    }

    /* Current TF2 proposals as targets */
    for (const name of includedProposers) {
      const currentList = proposerSet.get(name);
      for (const p of currentList) {
        add("p:" + p.id, p.title, "proposal", { ada: p.requested_ada, proposalId: p.id, proposer: name });
        if (p.requested_ada > 0) links.push({ source: "prop:" + name, target: "p:" + p.id, value: p.requested_ada, kind: "current" });
      }
    }

    /* Resolve string refs to numeric */
    const resolvedLinks = links.map(l => ({ source: l.source, target: l.target, value: l.value, kind: l.kind }));
    return { nodes, links: resolvedLinks, includedCount: includedProposers.length };
  }, [proposals]);

  /* Sankey layout & render */
  useEffectFV(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const wrap = wrapRef.current;
    const W = wrap.clientWidth;
    const proposerCount = graph.nodes.filter(n => n.kind === "proposer").length;
    const proposalCount = graph.nodes.filter(n => n.kind === "proposal").length;
    /* Dynamic height: enough for each proposal target on the right */
    const H = Math.max(720, proposalCount * 42 + 80);
    svg.attr("viewBox", `0 0 ${W} ${H}`).attr("width", W).attr("height", H);

    if (graph.nodes.length === 0 || graph.links.length === 0) {
      svg.append("text")
        .attr("x", W / 2).attr("y", H / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "var(--ink-faint)")
        .attr("font-family", "var(--mono)").attr("font-size", 12)
        .text("No records in current filter — broaden filters or include zero-history.");
      return;
    }

    const sankeyLayout = d3.sankey()
      .nodeId(d => d.id)
      .nodeWidth(14)
      .nodePadding(20)
      .extent([[180, 30], [W - 280, H - 20]]);

    /* Deep clone so d3-sankey can mutate */
    const sankeyData = sankeyLayout({
      nodes: graph.nodes.map(n => ({ ...n })),
      links: graph.links.map(l => ({ ...l }))
    });

    /* Links */
    svg.append("g").selectAll("path")
      .data(sankeyData.links).enter().append("path")
      .attr("class", "sankey-link")
      .attr("d", d3.sankeyLinkHorizontal())
      .attr("fill", "none")
      .attr("stroke", d => d.kind === "prior" ? (d.source.color || "var(--ink-faint)") : "var(--src-current)")
      .attr("stroke-opacity", 0.18)
      .attr("stroke-width", d => Math.max(1.2, d.width))
      .on("mouseenter", function (e, d) {
        d3.select(this).attr("stroke-opacity", 0.45);
        setHover({ kind: "link", source: d.source.label, target: d.target.label, value: d.value });
      })
      .on("mouseleave", function () { d3.select(this).attr("stroke-opacity", 0.18); setHover(null); });

    /* Nodes */
    const nodeG = svg.append("g").selectAll("g")
      .data(sankeyData.nodes).enter().append("g")
      .attr("class", "sankey-node")
      .style("cursor", d => d.kind === "proposer" ? "pointer" : "default")
      .on("click", (e, d) => { if (d.kind === "proposer") onOpenProposer(d.label); });

    nodeG.append("rect")
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("height", d => Math.max(2, d.y1 - d.y0))
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => {
        if (d.kind === "source") return d.color;
        if (d.kind === "proposer") return "var(--ink)";
        return "var(--src-current)";
      })
      .attr("stroke", "none");

    /* Threshold emphasis: amber rule on proposers at or above the selected count. */
    nodeG.filter(d => d.kind === "proposer" && d.priorProjects >= threshold)
      .append("rect")
      .attr("x", d => d.x0 - 4)
      .attr("y", d => d.y0)
      .attr("height", d => Math.max(2, d.y1 - d.y0))
      .attr("width", 2)
      .attr("fill", "var(--tier-hi)");

    /* Labels — paper-colored stroke for readability over ribbons */
    nodeG.append("text")
      .attr("x", d => d.kind === "source" ? d.x0 - 8 : d.x1 + 8)
      .attr("y", d => (d.y0 + d.y1) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.kind === "source" ? "end" : "start")
      .attr("paint-order", "stroke")
      .attr("stroke", "var(--paper-soft)")
      .attr("stroke-width", 3)
      .attr("stroke-linejoin", "round")
      .text(d => {
        if (d.kind === "source") return d.label;
        if (d.kind === "proposer") return d.label;
        return d.label.length > 56 ? d.label.slice(0, 55) + "…" : d.label;
      });

    /* Secondary line under proposer with ADA totals */
    nodeG.filter(d => d.kind === "proposer")
      .append("text")
      .attr("x", d => d.x1 + 8)
      .attr("y", d => (d.y0 + d.y1) / 2 + 14)
      .attr("class", "amount")
      .attr("paint-order", "stroke")
      .attr("stroke", "var(--paper-soft)")
      .attr("stroke-width", 3)
      .attr("stroke-linejoin", "round")
      .text(d => `↳ ₳${fmtAda(d.priorAda, { short: true })} prior · ${d.priorProjects} projects`);

    /* Proposal ADA on the right */
    nodeG.filter(d => d.kind === "proposal")
      .append("text")
      .attr("x", d => d.x1 + 8)
      .attr("y", d => (d.y0 + d.y1) / 2 + 14)
      .attr("class", "amount")
      .text(d => `₳ ${fmtAda(d.ada, { short: true })} requested`);
  }, [graph, threshold]);

  return (
    <div className="flow-stage" ref={wrapRef}>
      <div className="flow-head">
        <div>Prior funding source →</div>
        <div>Proposer</div>
        <div>← Current TF2 proposal</div>
      </div>
      <div style={{ fontSize: 12, color: "var(--ink-mute)", marginBottom: 12, maxWidth: 720 }}>
        Showing the <strong style={{ color: "var(--ink)", fontWeight: 600 }}>{graph.includedCount} proposers</strong> with either a matched prior Catalyst / Treasury Fund 1 record
        or multiple current Treasury Fund 2 proposals. Ribbon width is ADA.
        Hover any link for the exact amount; click a proposer to open their profile.
      </div>
      <svg ref={svgRef} className="flow-svg"></svg>
      {hover && hover.kind === "link" && (
        <div style={{
          position: "absolute", bottom: 24, right: 32,
          background: "var(--paper)", border: "1px solid var(--rule)",
          borderRadius: 4, padding: "8px 12px", fontSize: 12,
          fontFamily: "var(--mono)", color: "var(--ink-mid)",
          boxShadow: "0 8px 24px -12px oklch(0.18 0.022 255 / 0.2)",
          pointerEvents: "none"
        }}>
          <div style={{ color: "var(--ink-mute)", fontSize: 10.5, textTransform: "uppercase", letterSpacing: "0.06em" }}>flow</div>
          <div style={{ marginTop: 2 }}>{hover.source} → {hover.target}</div>
          <div style={{ color: "var(--cardano)", marginTop: 2 }}>₳ {fmtAda(hover.value)}</div>
        </div>
      )}
    </div>
  );
}

window.FlowView = FlowView;
