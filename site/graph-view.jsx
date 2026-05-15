/* graph-view.jsx — funding graph (proposers and funding sources, sized by matched history) */
const { useRef: useRefGV, useEffect: useEffectGV, useMemo: useMemoGV, useState: useStateGV } = React;

function GraphView({ proposals, threshold, labelMode, highlightHighTies, showZeroHistory, selected, onOpenProposal, onOpenProposer }) {
  const wrapRef = useRefGV(null);
  const svgRef  = useRefGV(null);
  const [hover, setHover] = useStateGV(null);

  /* Build node + link graph from currently filtered proposals */
  const graph = useMemoGV(() => {
    const proposerSet = new Map(); // canonical name -> meta
    for (const p of proposals) {
      const name = p.proposer;
      if (!proposerSet.has(name)) {
        const m = tieMetrics(p);
        proposerSet.set(name, {
          id: "P:" + name, type: "proposer", name,
          currentProposals: 1,
          requestedAda: p.requested_ada,
          priorProjects: m.priorProjects,
          priorAda: m.priorAda,
          catalystProjects: m.catalystProjects,
          tf1Projects: m.tf1Projects,
          has2025: m.has2025,
          weight: m.weight,
          proposalIds: [p.id]
        });
      } else {
        const e = proposerSet.get(name);
        e.currentProposals += 1;
        e.requestedAda += p.requested_ada;
        e.proposalIds.push(p.id);
      }
    }

    /* Skip zero-history proposers if toggled */
    if (!showZeroHistory) {
      for (const [k, v] of proposerSet) {
        if (v.priorProjects === 0 && !v.has2025 && v.currentProposals === 1) proposerSet.delete(k);
      }
    }

    /* Source anchor nodes */
    const sources = [
      { id: "S:catalyst", type: "source", key: "catalyst", name: "Project Catalyst",     fx: null, fy: null, fillVar: "var(--src-catalyst)" },
      { id: "S:tf1",      type: "source", key: "tf1",      name: "Treasury Fund 1",      fx: null, fy: null, fillVar: "var(--src-tf1)" },
      { id: "S:b2025",    type: "source", key: "b2025",    name: "2025 Budget Process",  fx: null, fy: null, fillVar: "var(--src-2025)" }
    ];

    const nodes = [...sources, ...proposerSet.values()];
    const links = [];
    for (const p of proposerSet.values()) {
      if (p.catalystProjects > 0) links.push({ source: p.id, target: "S:catalyst", weight: p.catalystProjects, key: "catalyst" });
      if (p.tf1Projects > 0)      links.push({ source: p.id, target: "S:tf1",      weight: p.tf1Projects,      key: "tf1" });
      if (p.has2025)              links.push({ source: p.id, target: "S:b2025",    weight: 1,                  key: "b2025" });
    }
    return { nodes, links };
  }, [proposals, showZeroHistory]);

  /* d3-force simulation */
  useEffectGV(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const wrap = wrapRef.current;
    const W = wrap.clientWidth, H = wrap.clientHeight;

    /* Fixed anchor positions for source hubs (triangle around center) */
    const cx = W / 2, cy = H / 2;
    const r = Math.min(W, H) * 0.36;
    const anchorPos = {
      "S:catalyst": [cx - r * 0.85, cy + r * 0.45],   // bottom-left
      "S:tf1":      [cx + r * 0.85, cy + r * 0.45],   // bottom-right
      "S:b2025":    [cx,             cy - r * 0.75]    // top
    };
    graph.nodes.forEach(n => {
      if (n.type === "source") { n.fx = anchorPos[n.id][0]; n.fy = anchorPos[n.id][1]; }
    });

    /* Node radius scale */
    const radius = (n) => {
      if (n.type === "source") return 38;
      const base = Math.sqrt(1 + (n.priorProjects || 0) + (n.currentProposals || 0) * 2.2 + (n.has2025 ? 1 : 0));
      return 7 + base * 4.2;
    };

    const linkScale = d3.scaleLinear()
      .domain([0, d3.max(graph.links, l => l.weight) || 1])
      .range([0.8, 9]);

    /* Force sim — precompute statically (no animation, robust to throttled rAF) */
    const sim = d3.forceSimulation(graph.nodes)
      .force("link", d3.forceLink(graph.links).id(d => d.id).distance(l => 110 + 60 / Math.sqrt(l.weight)).strength(l => 0.25 + Math.min(1, l.weight / 20)))
      .force("charge", d3.forceManyBody().strength(d => d.type === "source" ? -1400 : -260))
      .force("center", d3.forceCenter(cx, cy).strength(0.04))
      .force("collide", d3.forceCollide().radius(d => radius(d) + 6).strength(0.9))
      .stop();
    /* Tick to convergence */
    for (let i = 0; i < 360; i++) sim.tick();
    /* Clamp proposer nodes within viewport (label-safe margin) */
    const pad = 130;
    graph.nodes.forEach(n => {
      if (n.type !== "proposer") return;
      n.x = Math.max(pad, Math.min(W - pad, n.x));
      n.y = Math.max(40, Math.min(H - 40, n.y));
    });

    /* Render links */
    const linkSel = svg.append("g").attr("class", "links").selectAll("path")
      .data(graph.links).enter()
      .append("path")
      .attr("class", "node-link")
      .attr("fill", "none")
      .attr("stroke", d => `var(--src-${d.key})`)
      .attr("stroke-width", d => linkScale(d.weight));

    /* Source halo (light fill ring) */
    const sourceG = svg.append("g").selectAll("g").data(graph.nodes.filter(n => n.type === "source")).enter()
      .append("g").attr("class", "source-node");
    sourceG.append("circle")
      .attr("r", 60)
      .attr("fill", d => d.fillVar)
      .attr("fill-opacity", 0.06)
      .attr("stroke", "none");
    sourceG.append("circle")
      .attr("r", d => radius(d))
      .attr("fill", "var(--paper)")
      .attr("stroke", d => d.fillVar)
      .attr("stroke-width", 1.5);
    sourceG.append("text")
      .attr("text-anchor", "middle").attr("dy", "0.35em")
      .attr("font-family", "var(--mono)").attr("font-size", 10).attr("font-weight", 600)
      .attr("fill", d => d.fillVar)
      .attr("paint-order", "stroke")
      .attr("stroke", "var(--paper-soft)")
      .attr("stroke-width", 4)
      .attr("stroke-linejoin", "round")
      .style("text-transform", "uppercase").style("letter-spacing", "0.06em")
      .each(function(d) {
        const parts = d.name.split(" ");
        const mid = Math.ceil(parts.length / 2);
        d3.select(this).append("tspan").attr("x", 0).attr("dy", "-0.5em").text(parts.slice(0, mid).join(" "));
        d3.select(this).append("tspan").attr("x", 0).attr("dy", "1.1em").text(parts.slice(mid).join(" "));
      });

    /* Proposer nodes */
    const propNodes = graph.nodes.filter(n => n.type === "proposer");
    const propG = svg.append("g").selectAll("g").data(propNodes).enter()
      .append("g")
      .attr("class", d => "gnode " + (highlightHighTies && d.priorProjects >= threshold ? "high-tie" : "") + (selected?.kind === "proposer" && selected.id === d.name ? " selected" : ""))
      .style("cursor", "pointer")
      .on("click", (e, d) => onOpenProposer(d.name))
      .on("mouseenter", (e, d) => setHover(d))
      .on("mouseleave", () => setHover(null));

    /* Selection ring */
    propG.append("circle").attr("class", "ring")
      .attr("r", d => radius(d) + 4);

    /* Core circle */
    propG.append("circle").attr("class", "core")
      .attr("r", d => radius(d))
      .attr("fill", d => {
        if (d.priorProjects === 0 && !d.has2025) return "var(--paper)";
        if (d.tf1Projects > 0 && d.tf1Projects >= d.catalystProjects) return "oklch(0.52 0.10 200 / 0.7)";
        return "oklch(0.50 0.14 264 / 0.7)";
      })
      .attr("stroke", d => {
        if (d.priorProjects === 0 && !d.has2025) return "var(--ink-faint)";
        return "var(--ink)";
      })
      .attr("stroke-width", d => d.priorProjects === 0 ? 1 : 1.2);

    /* Multi-proposal badge (small circle with number) */
    propG.filter(d => d.currentProposals > 1).each(function(d) {
      const g = d3.select(this);
      g.append("circle").attr("class", "badge-bg")
        .attr("r", 9)
        .attr("cx", radius(d) * 0.72)
        .attr("cy", -radius(d) * 0.72);
      g.append("text").attr("class", "badge")
        .attr("x", radius(d) * 0.72)
        .attr("y", -radius(d) * 0.72)
        .attr("dy", "0.35em")
        .text(d.currentProposals);
    });

    /* Labels */
    function shouldLabel(d) {
      if (labelMode === "off") return false;
      if (labelMode === "all") return true;
      return (
        d.priorProjects >= 20 ||
        d.currentProposals > 1 ||
        (selected?.kind === "proposer" && selected.id === d.name)
      );
    }

    const labelSel = propG.append("text")
      .attr("class", d => "node-label proposer" + (d.weight > 4 ? " hub" : ""))
      .attr("text-anchor", "middle")
      .attr("dy", d => radius(d) + 12)
      .style("display", d => shouldLabel(d) ? null : "none")
      .text(d => d.name.length > 22 ? d.name.slice(0, 21) + "…" : d.name);

    /* Curved path between proposer and source */
    function linkPath(d) {
      const s = d.source, t = d.target;
      const dx = t.x - s.x, dy = t.y - s.y;
      const dr = Math.sqrt(dx*dx + dy*dy) * 1.4;
      return `M${s.x},${s.y}A${dr},${dr} 0 0,1 ${t.x},${t.y}`;
    }

    sim.on("tick", () => {
      window.__simTicks = (window.__simTicks || 0) + 1;
      linkSel.attr("d", linkPath);
      propG.attr("transform", d => `translate(${d.x},${d.y})`);
      sourceG.attr("transform", d => `translate(${d.x},${d.y})`);
    });
    /* Apply final positions immediately */
    linkSel.attr("d", linkPath);
    propG.attr("transform", d => `translate(${d.x},${d.y})`);
    sourceG.attr("transform", d => `translate(${d.x},${d.y})`);
    window.__sim = sim;

    /* drag — manually re-tick on each drag event since the sim is stopped */
    function applyAll() {
      linkSel.attr("d", linkPath);
      propG.attr("transform", d => `translate(${d.x},${d.y})`);
      sourceG.attr("transform", d => `translate(${d.x},${d.y})`);
    }
    propG.call(d3.drag()
      .on("start", (e, d) => { d.fx = d.x; d.fy = d.y; })
      .on("drag",  (e, d) => { d.fx = e.x; d.fy = e.y; d.x = e.x; d.y = e.y;
                               for (let i = 0; i < 8; i++) sim.tick();
                               applyAll(); })
      .on("end",   (e, d) => { d.fx = null; d.fy = null; })
    );

    /* Resize observer — recompute static layout */
    const ro = new ResizeObserver(() => {
      const W2 = wrap.clientWidth, H2 = wrap.clientHeight;
      if (W2 < 50 || H2 < 50) return;
      const cx2 = W2 / 2, cy2 = H2 / 2;
      const r2 = Math.min(W2, H2) * 0.36;
      const pos = {
        "S:catalyst": [cx2 - r2 * 0.85, cy2 + r2 * 0.45],
        "S:tf1":      [cx2 + r2 * 0.85, cy2 + r2 * 0.45],
        "S:b2025":    [cx2,             cy2 - r2 * 0.75]
      };
      graph.nodes.forEach(n => {
        if (n.type === "source") { n.fx = pos[n.id][0]; n.fy = pos[n.id][1]; }
      });
      sim.force("center", d3.forceCenter(cx2, cy2).strength(0.04));
      for (let i = 0; i < 120; i++) sim.tick();
      applyAll();
    });
    ro.observe(wrap);

    return () => { sim.stop(); ro.disconnect(); };
  }, [graph, threshold, labelMode, highlightHighTies, selected]);

  /* Stats overlay */
  const summary = useMemoGV(() => {
    const proposerNodes = graph.nodes.filter(n => n.type === "proposer");
    const overThresh = proposerNodes.filter(n => n.priorProjects >= threshold).length;
    return {
      proposers: proposerNodes.length,
      withHistory: proposerNodes.filter(n => n.priorProjects > 0).length,
      overThresh,
      linkCount: graph.links.length
    };
  }, [graph, threshold]);

  return (
    <div className="graph-stage" ref={wrapRef}>
      <svg ref={svgRef}></svg>
      <div className="graph-overlay-tl">
        <h4>Each circle is a proposer.</h4>
        <div className="small">
          Area = prior projects + current TF2 proposals. Edge thickness = matched record count.
          A numeral marks proposers with multiple current proposals. Drag any node; click for profile.
        </div>
      </div>
      <div className="graph-overlay-br">
        {summary.proposers} proposers · {summary.withHistory} with history · {summary.overThresh} ≥ threshold
      </div>
      {hover && (
        <div style={{
          position: "absolute",
          left: 14, bottom: 60,
          background: "var(--paper)",
          border: "1px solid var(--rule)",
          borderRadius: 4,
          padding: "10px 14px",
          minWidth: 240,
          maxWidth: 320,
          fontSize: 12,
          color: "var(--ink-mid)",
          pointerEvents: "none",
          boxShadow: "0 8px 24px -12px oklch(0.18 0.022 255 / 0.2)"
        }}>
          <div style={{ fontWeight: 600, color: "var(--ink)", marginBottom: 4 }}>{hover.name}</div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--ink-mute)", lineHeight: 1.7 }}>
            {hover.currentProposals} current proposal{hover.currentProposals !== 1 ? "s" : ""} · ₳ {fmtAda(hover.requestedAda, { short: true })} requested<br />
            {hover.priorProjects > 0 ? <>
              {hover.priorProjects} prior project{hover.priorProjects !== 1 ? "s" : ""} · ₳ {fmtAda(hover.priorAda, { short: true })} matched<br />
              {hover.catalystProjects > 0 && <><span style={{ color: "var(--src-catalyst)" }}>● </span>Catalyst: {hover.catalystProjects}{"  "}</>}
              {hover.tf1Projects > 0 && <><span style={{ color: "var(--src-tf1)" }}>● </span>TF1: {hover.tf1Projects}</>}
            </> : <>No matched prior funding</>}
            {hover.has2025 && <><br /><span style={{ color: "var(--src-2025)" }}>● </span>Bridged to 2025 BP</>}
          </div>
          <div style={{ marginTop: 6, fontSize: 11, color: "var(--cardano)" }}>Click for full profile →</div>
        </div>
      )}
    </div>
  );
}

window.GraphView = GraphView;
