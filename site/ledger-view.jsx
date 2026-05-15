/* ledger-view.jsx — sortable proposal table */
const { useState: useStateLV, useMemo: useMemoLV } = React;

function LedgerView({ proposals, threshold, selected, onOpenProposal }) {
  const [sort, setSort] = useStateLV({ key: "weight", dir: "desc" });

  const rows = useMemoLV(() => {
    const enriched = proposals.map(p => {
      const m = tieMetrics(p);
      return { p, m };
    });
    enriched.sort((a, b) => {
      let av, bv;
      switch (sort.key) {
        case "title":      av = a.p.title.toLowerCase(); bv = b.p.title.toLowerCase(); break;
        case "proposer":   av = a.p.proposer.toLowerCase(); bv = b.p.proposer.toLowerCase(); break;
        case "ada":        av = a.p.requested_ada; bv = b.p.requested_ada; break;
        case "priorAda":   av = a.m.priorAda; bv = b.m.priorAda; break;
        case "prior":      av = a.m.priorProjects; bv = b.m.priorProjects; break;
        case "peers":      av = a.m.peerProposals; bv = b.m.peerProposals; break;
        case "weight":     av = a.m.weight; bv = b.m.weight; break;
        default:           av = 0; bv = 0;
      }
      if (av == null) av = 0; if (bv == null) bv = 0;
      if (av < bv) return sort.dir === "asc" ? -1 : 1;
      if (av > bv) return sort.dir === "asc" ?  1 : -1;
      return 0;
    });
    return enriched;
  }, [proposals, sort]);

  const setSortKey = (k) => {
    setSort(s => s.key === k ? { key: k, dir: s.dir === "asc" ? "desc" : "asc" } : { key: k, dir: ["title", "proposer"].includes(k) ? "asc" : "desc" });
  };
  const Sh = ({ k, label, num }) => (
    <th className={"sortable " + (num ? "num" : "")} onClick={() => setSortKey(k)}>
      {label}
      {sort.key === k && <span className="sort-mark">{sort.dir === "asc" ? "↑" : "↓"}</span>}
    </th>
  );

  return (
    <div className="ledger-wrap">
      <div style={{ marginBottom: 14, display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--ink-mute)", letterSpacing: "0.04em" }}>
          {rows.length} {rows.length === 1 ? "row" : "rows"} · sorted by {sort.key} {sort.dir}
        </div>
        <div style={{ fontSize: 11.5, color: "var(--ink-faint)" }}>
          Click any row for full proposal + proposer profile.
        </div>
      </div>
      <table className="ledger">
        <thead>
          <tr>
            <Sh k="title"    label="Proposal" />
            <Sh k="proposer" label="Proposer" />
            <Sh k="ada"      label="Requested" num />
            <Sh k="prior"    label="Prior projects" num />
            <Sh k="priorAda" label="Prior ADA" num />
            <Sh k="peers"    label="Co-proposals" num />
            <th>Ties</th>
            <Sh k="weight"   label="Tie weight" num />
          </tr>
        </thead>
        <tbody>
          {rows.map(({ p, m }) => {
            const isSelected = selected?.kind === "proposal" && selected.id === p.id;
            const hi = m.priorProjects >= threshold || m.peerProposals > 1;
            return (
              <tr key={p.id}
                  className={(isSelected ? "selected " : "") + (hi ? "high-tie" : "")}
                  onClick={() => onOpenProposal(p.id)}>
                <td className="title-col">
                  <div className="t">{p.title}</div>
                  <div className="id">{p.id}</div>
                </td>
                <td className="proposer-col">
                  {p.proposer}
                  {p.entityType && <div className="ent">{p.entityType}</div>}
                </td>
                <td className="num">₳ {fmtAda(p.requested_ada)}</td>
                <td className="num">{m.priorProjects || <span style={{ color: "var(--ink-faint)" }}>—</span>}</td>
                <td className="num">{m.priorAda ? fmtAda(m.priorAda, { short: true }) : <span style={{ color: "var(--ink-faint)" }}>—</span>}</td>
                <td className="num">{m.peerProposals > 1 ? m.peerProposals : <span style={{ color: "var(--ink-faint)" }}>—</span>}</td>
                <td className="badges-col">
                  {m.catalystProjects > 0 && <span className="badge catalyst"><span className="dot"></span>{m.catalystProjects} Catalyst</span>}
                  {m.tf1Projects > 0 && <span className="badge tf1"><span className="dot"></span>{m.tf1Projects} TF1</span>}
                  {m.has2025 && <span className="badge b2025"><span className="dot"></span>2025 BP</span>}
                  {m.peerProposals > 1 && <span className="badge multi"><span className="dot"></span>{m.peerProposals}× TF2</span>}
                  {!m.catalystProjects && !m.tf1Projects && !m.has2025 && m.peerProposals === 1 && (
                    <span className="badge zero"><span className="dot"></span>no match</span>
                  )}
                </td>
                <td className="num">
                  <span style={{ fontFamily: "var(--mono)", fontSize: 12, color: hi ? "var(--tier-hi)" : "var(--ink-mid)" }}>
                    {m.weight.toFixed(1)}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

window.LedgerView = LedgerView;
