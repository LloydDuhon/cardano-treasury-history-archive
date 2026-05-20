/* findings-view.jsx — review queue for prior-work overlap findings */
const { useState: useStateFV, useMemo: useMemoFV } = React;

function confidenceRank(confidence) {
  return ({ high: 0, medium: 1, low: 2 })[confidence] ?? 9;
}

function shortText(text, limit = 150) {
  if (!text) return "";
  return text.length > limit ? text.slice(0, limit - 1).trimEnd() + "…" : text;
}

function buildFindingRows(proposals) {
  const proposalById = new Map(proposals.map(p => [p.id, p]));
  const rows = [];
  for (const proposal of proposals) {
    for (const finding of workOverlapFor(proposal.id)) {
      rows.push({
        key: `${proposal.id}:${finding.historical_source}:${finding.historical_project_id}`,
        proposal,
        finding
      });
    }
  }
  rows.sort((a, b) => {
    const ac = confidenceRank(a.finding.match_confidence);
    const bc = confidenceRank(b.finding.match_confidence);
    if (ac !== bc) return ac - bc;
    if (a.finding.work_overlap_percent !== b.finding.work_overlap_percent) {
      return b.finding.work_overlap_percent - a.finding.work_overlap_percent;
    }
    return a.proposal.title.localeCompare(b.proposal.title);
  });
  return rows.filter(row => proposalById.has(row.proposal.id));
}

function FindingsView({ proposals, onOpenProposal }) {
  const [selectedKey, setSelectedKey] = useStateFV(null);
  const [show, setShow] = useStateFV("all");
  const allRows = useMemoFV(() => buildFindingRows(proposals), [proposals]);
  const rows = useMemoFV(
    () => allRows.filter(row => show === "all" || row.finding.match_confidence === show),
    [allRows, show]
  );
  const selected = rows.find(row => row.key === selectedKey) || rows[0] || null;
  const counts = allRows.reduce((acc, row) => {
    const c = row.finding.match_confidence;
    acc[c] = (acc[c] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="findings-view">
      <div className="findings-list">
        <div className="findings-toolbar">
          <div>
            <div className="findings-title">Similarity findings</div>
            <div className="findings-sub">
              {rows.length} shown · {counts.high || 0} high · {counts.medium || 0} medium
            </div>
          </div>
          <div className="findings-controls">
            <div className="segmented" aria-label="Finding confidence filter">
              {[
                ["high", "High"],
                ["medium", "Medium"],
                ["all", "All"]
              ].map(([value, label]) => (
                <button
                  key={value}
                  className={show === value ? "active" : ""}
                  onClick={() => setShow(value)}
                >
                  {label}
                </button>
              ))}
            </div>
            <div className="findings-note">AI Matched rows are screening results.</div>
          </div>
        </div>

        {rows.length === 0 ? (
          <div className="findings-empty">No similarity findings in the current filter.</div>
        ) : (
          <div className="finding-cards">
            {rows.map(row => {
              const f = row.finding;
              const isSelected = selected?.key === row.key;
              return (
                <button
                  key={row.key}
                  className={"finding-card " + (isSelected ? "selected" : "")}
                  onClick={() => setSelectedKey(row.key)}
                >
                  <div className="finding-card-top">
                    <span className={"confidence " + f.match_confidence}>{f.match_confidence}</span>
                    <span className={"review-chip " + (f.adjudication_source === "Human Reviewed" ? "human" : "ai")}>
                      {f.adjudication_source}
                    </span>
                    <span className="finding-percent">{f.work_overlap_percent}%</span>
                  </div>
                  <div className="finding-current">{row.proposal.title}</div>
                  <div className="finding-history">{f.historical_title}</div>
                  <div className="finding-meta">
                    <span>{f.historical_source}</span>
                    <span>rank {f.retrieval_rank}</span>
                    <span>funding {f.previously_funded_relevance}</span>
                  </div>
                  {f.overlap_evidence && <div className="finding-excerpt">{shortText(f.overlap_evidence)}</div>}
                </button>
              );
            })}
          </div>
        )}
      </div>

      <FindingDetail row={selected} onOpenProposal={onOpenProposal} />
    </div>
  );
}

function FindingDetail({ row, onOpenProposal }) {
  if (!row) {
    return (
      <div className="finding-detail empty">
        Select a finding to review the evidence.
      </div>
    );
  }
  const { proposal, finding: f } = row;
  return (
    <div className="finding-detail">
      <div className="finding-detail-head">
        <div className="kind">Selected finding</div>
        <h2>{proposal.title}</h2>
        <button className="open-proposal" onClick={() => onOpenProposal(proposal.id)}>Open proposal</button>
      </div>

      <div className="finding-score-row">
        <span className={"confidence " + f.match_confidence}>{f.match_confidence}</span>
        <span>{f.work_overlap_percent}% current-work overlap</span>
        <span>{f.overlap_type}</span>
        <span className={"review-chip " + (f.adjudication_source === "Human Reviewed" ? "human" : "ai")}>{f.adjudication_source}</span>
      </div>

      <div className="finding-detail-section">
        <h3>Historical candidate</h3>
        <div className="detail-title">{f.historical_title}</div>
        <div className="detail-meta">
          <span className={"src " + sourceKey(f.historical_source)}>{f.historical_source}</span>
          <span>{f.historical_project_id}</span>
          {fundNumber(f.historical_project_id) && <span>{fundNumber(f.historical_project_id)}</span>}
          <span>{statusLabel(f.historical_status)}</span>
        </div>
      </div>

      <div className="finding-detail-grid">
        <div>
          <div className="l">Previously proposed</div>
          <div className="v">{f.previously_proposed ? "Yes" : "No"}</div>
        </div>
        <div>
          <div className="l">Previously funded relevance</div>
          <div className="v">{f.previously_funded_relevance}</div>
        </div>
        <div>
          <div className="l">Proposer relationship</div>
          <div className="v">{f.same_or_related_proposer}</div>
        </div>
        <div>
          <div className="l">Amount</div>
          <div className="v">{f.amount_original || "—"}</div>
        </div>
      </div>

      <EvidenceBlock label="Overlap evidence" value={f.overlap_evidence} />
      <EvidenceBlock label="Funding evidence" value={f.funding_evidence} />
      <EvidenceBlock label="Relationship evidence" value={f.relationship_evidence} />
      {f.review_notes && <EvidenceBlock label="Review notes" value={f.review_notes} />}

      <div className="finding-detail-footer">
        <span>Retrieval rank {f.retrieval_rank} · score {f.retrieval_score?.toFixed?.(3) || "—"}</span>
        <ExternalLink href={f.source_url}>Open source ↗</ExternalLink>
      </div>
    </div>
  );
}

function EvidenceBlock({ label, value }) {
  if (!value) return null;
  return (
    <div className="finding-detail-section">
      <h3>{label}</h3>
      <p>{value}</p>
    </div>
  );
}

window.FindingsView = FindingsView;
