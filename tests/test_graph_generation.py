from pathlib import Path

from backend.extraction.entities import extract_entities
from backend.extraction.events import extract_events
from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput
from backend.graph.generator import generate_care_graph


def test_generate_care_graph_from_sample_record() -> None:
    text = Path("data/sample_records/sample_record_01.txt").read_text(encoding="utf-8")
    records = [MedicalRecordInput(record_id="sample_01", record_type="chart", text=text)]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    events = extract_events(normalized, entities=entities)
    graph = generate_care_graph(entities=entities, events=events)

    assert len(graph.nodes) == 5
    assert len(graph.edges) == 2

    relation_set = {edge.relation for edge in graph.edges}
    assert relation_set == {"performed", "requested"}

    node_labels = {node.label for node in graph.nodes}
    assert "山田太郎" in node_labels
    assert "看護師A" in node_labels
    assert "医師B" in node_labels


def test_generate_care_graph_adds_responsible_edges_when_patient_appears_in_event_line() -> None:
    records = [
        MedicalRecordInput(
            record_id="r2",
            record_type="nursing",
            text="患者: 田中花子\n看護師C 患者: 田中花子 10:00 観察を実施",
        )
    ]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    events = extract_events(normalized, entities=entities)
    graph = generate_care_graph(entities=entities, events=events)

    relation_counts = {relation: 0 for relation in ("performed", "requested", "responsible")}
    for edge in graph.edges:
        relation_counts[edge.relation] = relation_counts.get(edge.relation, 0) + 1

    assert relation_counts["performed"] == 1
    assert relation_counts["responsible"] == 2

    event_to_patient = [
        edge for edge in graph.edges if edge.relation == "responsible" and edge.source.startswith("event_")
    ]
    assert len(event_to_patient) == 1


def test_generate_care_graph_is_deterministic() -> None:
    records = [
        MedicalRecordInput(
            record_id="r3",
            record_type="order",
            text="患者: 佐藤一郎\n医師E 11:20 CTオーダーを指示",
        )
    ]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    events = extract_events(normalized, entities=entities)

    first = generate_care_graph(entities=entities, events=events)
    second = generate_care_graph(entities=entities, events=events)

    assert first == second

