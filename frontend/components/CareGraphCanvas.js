import { useMemo } from "react";
import ReactFlow, { Background, Controls, MiniMap } from "reactflow";

const NODE_COLORS = {
  patient: "#ffecd2",
  staff: "#d9f2ef",
  event: "#ffe6c7"
};

const EDGE_COLORS = {
  responsible: "#14532d",
  performed: "#0f766e",
  requested: "#b45309"
};

function toFlowGraph(graph) {
  const byType = {
    patient: [],
    staff: [],
    event: []
  };

  for (const node of graph.nodes) {
    byType[node.node_type].push(node);
  }

  const withPosition = [];
  const patientX = 120;
  const staffX = 120;
  const eventX = 560;

  byType.patient.forEach((node, index) => {
    withPosition.push({
      id: node.node_id,
      type: "default",
      position: { x: patientX, y: 80 + index * 170 },
      data: {
        label: node.label,
        role: node.role,
        nodeType: node.node_type,
        evidence: node.evidence
      },
      style: {
        borderRadius: 14,
        border: "1px solid #d97706",
        background: NODE_COLORS.patient,
        width: 190,
        fontWeight: 600
      }
    });
  });

  byType.staff.forEach((node, index) => {
    withPosition.push({
      id: node.node_id,
      type: "default",
      position: { x: staffX, y: 380 + index * 170 },
      data: {
        label: node.label,
        role: node.role,
        nodeType: node.node_type,
        evidence: node.evidence
      },
      style: {
        borderRadius: 14,
        border: "1px solid #0f766e",
        background: NODE_COLORS.staff,
        width: 190,
        fontWeight: 600
      }
    });
  });

  byType.event.forEach((node, index) => {
    const meta = [node.event_type, node.time_text].filter(Boolean).join(" | ");
    withPosition.push({
      id: node.node_id,
      type: "default",
      position: { x: eventX, y: 120 + index * 170 },
      data: {
        label: `${node.label}${meta ? `\n${meta}` : ""}`,
        nodeType: node.node_type,
        evidence: node.evidence
      },
      style: {
        borderRadius: 10,
        border: "1px solid #7c2d12",
        background: NODE_COLORS.event,
        width: 230,
        whiteSpace: "pre-line"
      }
    });
  });

  const edges = graph.edges.map((edge) => ({
    id: edge.edge_id,
    source: edge.source,
    target: edge.target,
    label: edge.relation,
    animated: edge.relation === "requested",
    style: {
      stroke: EDGE_COLORS[edge.relation] || "#334155",
      strokeWidth: 2
    },
    labelStyle: {
      fill: "#0f172a",
      fontWeight: 700
    },
    data: {
      relation: edge.relation,
      eventId: edge.event_id,
      evidence: edge.evidence
    }
  }));

  return { nodes: withPosition, edges };
}

export default function CareGraphCanvas({ graph, onSelect }) {
  const flow = useMemo(() => {
    if (!graph) {
      return { nodes: [], edges: [] };
    }
    return toFlowGraph(graph);
  }, [graph]);

  if (!graph) {
    return <div className="empty-graph">Graph output will appear here.</div>;
  }

  return (
    <ReactFlow
      fitView
      nodes={flow.nodes}
      edges={flow.edges}
      onNodeClick={(_, node) => onSelect?.({ type: "node", data: node.data })}
      onEdgeClick={(_, edge) => onSelect?.({ type: "edge", data: edge.data })}
      proOptions={{ hideAttribution: true }}
    >
      <MiniMap pannable zoomable />
      <Controls />
      <Background gap={24} color="#cbd5e1" />
    </ReactFlow>
  );
}

