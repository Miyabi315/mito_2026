from pathlib import Path

from backend.extraction.entities import extract_entities
from backend.extraction.events import extract_events
from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput


def test_extract_events_from_sample_record() -> None:
    text = Path("data/sample_records/sample_record_01.txt").read_text(encoding="utf-8")
    records = [MedicalRecordInput(record_id="sample_01", record_type="chart", text=text)]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    events = extract_events(normalized, entities=entities)

    assert len(events) == 2

    by_trigger = {event.trigger: event for event in events}
    assert set(by_trigger.keys()) == {"測定", "オーダー"}

    measured = by_trigger["測定"]
    assert measured.event_type == "performed"
    assert measured.time_text == "09:10"
    assert len(measured.actor_entity_ids) == 1
    assert measured.patient_entity_ids == []
    assert measured.evidence[0].line_index == 1

    ordered = by_trigger["オーダー"]
    assert ordered.event_type == "order"
    assert ordered.time_text == "09:20"
    assert len(ordered.actor_entity_ids) == 1
    assert ordered.patient_entity_ids == []
    assert ordered.evidence[0].line_index == 2


def test_extract_events_is_deterministic() -> None:
    records = [
        MedicalRecordInput(
            record_id="r1",
            record_type="nursing",
            text="看護師A 08:40 観察を実施\n医師B 09:00 指示",
        )
    ]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    first = extract_events(normalized, entities=entities)
    second = extract_events(normalized, entities=entities)

    assert first == second

