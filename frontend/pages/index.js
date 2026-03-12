import { useState } from "react";

import CareGraphCanvas from "../components/CareGraphCanvas";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

const INITIAL_RECORD = [
  "患者: 山田太郎",
  "看護師A 09:10 バイタル測定を実施",
  "医師B 09:20 採血オーダーを指示"
].join("\n");

export default function HomePage() {
  const [recordText, setRecordText] = useState(INITIAL_RECORD);
  const [graph, setGraph] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [selected, setSelected] = useState(null);
  const [errorText, setErrorText] = useState("");
  const [loading, setLoading] = useState(false);

  async function buildGraph() {
    setLoading(true);
    setErrorText("");
    try {
      const requestBody = JSON.stringify({
        records: [
          {
            record_id: "input_01",
            record_type: "chart",
            text: recordText
          }
        ]
      });
      const requestOptions = {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: requestBody
      };

      const [graphResponse, timelineResponse] = await Promise.all([
        fetch(`${API_BASE}/graph/care`, requestOptions),
        fetch(`${API_BASE}/timeline/process`, requestOptions)
      ]);

      if (!graphResponse.ok) {
        throw new Error(`graph_request_failed_${graphResponse.status}`);
      }
      if (!timelineResponse.ok) {
        throw new Error(`timeline_request_failed_${timelineResponse.status}`);
      }

      const graphPayload = await graphResponse.json();
      const timelinePayload = await timelineResponse.json();

      setGraph(graphPayload);
      setTimeline(timelinePayload.timeline || []);
      setSelected(null);
    } catch (error) {
      setGraph(null);
      setTimeline([]);
      setSelected(null);
      setErrorText(`Graph request failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-root">
      <header className="hero">
        <h1>Care Graph Prototype</h1>
        <p>
          Medical text input -&gt; entity/event extraction -&gt; deterministic care graph
        </p>
      </header>

      <section className="layout-grid">
        <section className="panel input-panel">
          <h2>Record Input</h2>
          <label htmlFor="record-text" className="small-label">
            Paste chart/nursing/order text
          </label>
          <textarea
            id="record-text"
            value={recordText}
            onChange={(event) => setRecordText(event.target.value)}
          />
          <div className="row">
            <button type="button" onClick={buildGraph} disabled={loading}>
              {loading ? "Building..." : "Build Care Graph"}
            </button>
            <span className="api-hint">API: {API_BASE}/graph/care</span>
          </div>
          {errorText && <p className="error">{errorText}</p>}
        </section>

        <section className="panel graph-panel">
          <h2>Care Graph</h2>
          <div className="graph-canvas">
            <CareGraphCanvas graph={graph} onSelect={setSelected} />
          </div>
        </section>

        <section className="panel evidence-panel">
          <h2>Evidence</h2>
          {!selected && <p className="muted">Click a node or edge to inspect evidence.</p>}
          {selected && (
            <div className="evidence-list">
              <p className="small-label">
                {selected.type === "node" ? "Node" : "Edge"} selected
              </p>
              {(selected.data.evidence || []).map((item, index) => (
                <article className="evidence-card" key={`${item.record_id}-${item.line_index}-${index}`}>
                  <p className="meta">
                    {item.record_id} / line {item.line_index}
                  </p>
                  <p>{item.text}</p>
                  <p className="meta">
                    span: {item.start_char}-{item.end_char}
                  </p>
                </article>
              ))}
            </div>
          )}

          <h2 className="timeline-title">Process Timeline</h2>
          {timeline.length === 0 && <p className="muted">No timeline entries yet.</p>}
          {timeline.length > 0 && (
            <div className="timeline-list">
              {timeline.map((entry) => (
                <article className="timeline-card" key={entry.timeline_id}>
                  <p className="meta">
                    {entry.time_text || "--:--"} / {entry.event_type}
                  </p>
                  <p>{entry.summary}</p>
                  {entry.evidence[0] && (
                    <p className="meta">
                      {entry.evidence[0].record_id} line {entry.evidence[0].line_index}
                    </p>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
