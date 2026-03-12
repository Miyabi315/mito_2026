import hashlib
from dataclasses import dataclass, field
from typing import Literal

from backend.extraction.entities import ExtractedEntity
from backend.extraction.events import ExtractedEvent

NodeType = Literal["patient", "staff", "event"]
EdgeRelation = Literal["responsible", "performed", "requested"]

ACTOR_EVENT_RELATION: dict[str, EdgeRelation] = {
    "order": "requested",
    "instruction": "requested",
    "performed": "performed",
    "observation": "performed",
    "state_change": "responsible",
}


@dataclass
class GraphEvidence:
    record_id: str
    line_index: int
    text: str
    start_char: int
    end_char: int


@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    label: str
    role: str | None = None
    event_type: str | None = None
    time_text: str | None = None
    trigger: str | None = None
    evidence: list[GraphEvidence] = field(default_factory=list)


@dataclass
class GraphEdge:
    edge_id: str
    source: str
    target: str
    relation: EdgeRelation
    event_id: str | None = None
    evidence: list[GraphEvidence] = field(default_factory=list)


@dataclass
class CareGraph:
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def _to_graph_evidence(items: list[object]) -> list[GraphEvidence]:
    return [
        GraphEvidence(
            record_id=item.record_id,
            line_index=item.line_index,
            text=item.text,
            start_char=item.start_char,
            end_char=item.end_char,
        )
        for item in items
    ]


def _make_edge_id(
    source: str, target: str, relation: EdgeRelation, event_id: str | None
) -> str:
    source_text = f"{source}|{target}|{relation}|{event_id or ''}"
    digest = hashlib.sha1(source_text.encode("utf-8")).hexdigest()[:12]
    return f"edge_{digest}"


def generate_care_graph(
    entities: list[ExtractedEntity], events: list[ExtractedEvent]
) -> CareGraph:
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    edge_keys: set[tuple[str, str, EdgeRelation, str | None]] = set()

    for entity in entities:
        nodes.append(
            GraphNode(
                node_id=entity.entity_id,
                node_type=entity.entity_type,
                label=entity.name,
                role=entity.role,
                evidence=_to_graph_evidence(entity.evidence),
            )
        )

    for event in events:
        nodes.append(
            GraphNode(
                node_id=event.event_id,
                node_type="event",
                label=f"{event.event_type}: {event.trigger}",
                event_type=event.event_type,
                time_text=event.time_text,
                trigger=event.trigger,
                evidence=_to_graph_evidence(event.evidence),
            )
        )

        actor_relation = ACTOR_EVENT_RELATION[event.event_type]
        for actor_id in event.actor_entity_ids:
            actor_edge_key = (actor_id, event.event_id, actor_relation, event.event_id)
            if actor_edge_key not in edge_keys:
                edge_keys.add(actor_edge_key)
                edges.append(
                    GraphEdge(
                        edge_id=_make_edge_id(
                            source=actor_id,
                            target=event.event_id,
                            relation=actor_relation,
                            event_id=event.event_id,
                        ),
                        source=actor_id,
                        target=event.event_id,
                        relation=actor_relation,
                        event_id=event.event_id,
                        evidence=_to_graph_evidence(event.evidence),
                    )
                )

        for patient_id in event.patient_entity_ids:
            patient_edge_key = (event.event_id, patient_id, "responsible", event.event_id)
            if patient_edge_key not in edge_keys:
                edge_keys.add(patient_edge_key)
                edges.append(
                    GraphEdge(
                        edge_id=_make_edge_id(
                            source=event.event_id,
                            target=patient_id,
                            relation="responsible",
                            event_id=event.event_id,
                        ),
                        source=event.event_id,
                        target=patient_id,
                        relation="responsible",
                        event_id=event.event_id,
                        evidence=_to_graph_evidence(event.evidence),
                    )
                )

            for actor_id in event.actor_entity_ids:
                responsible_edge_key = (actor_id, patient_id, "responsible", event.event_id)
                if responsible_edge_key in edge_keys:
                    continue
                edge_keys.add(responsible_edge_key)
                edges.append(
                    GraphEdge(
                        edge_id=_make_edge_id(
                            source=actor_id,
                            target=patient_id,
                            relation="responsible",
                            event_id=event.event_id,
                        ),
                        source=actor_id,
                        target=patient_id,
                        relation="responsible",
                        event_id=event.event_id,
                        evidence=_to_graph_evidence(event.evidence),
                    )
                )

    nodes.sort(key=lambda node: node.node_id)
    edges.sort(key=lambda edge: edge.edge_id)
    return CareGraph(nodes=nodes, edges=edges)

