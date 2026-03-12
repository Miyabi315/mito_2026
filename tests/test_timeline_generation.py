from pathlib import Path

from backend.extraction.entities import extract_entities
from backend.extraction.events import extract_events
from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput
from backend.timeline.generator import generate_process_timeline


def test_generate_timeline_from_sample_record() -> None:
    text = Path("data/sample_records/sample_record_01.txt").read_text(encoding="utf-8")
    records = [MedicalRecordInput(record_id="sample_01", record_type="chart", text=text)]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    events = extract_events(normalized, entities=entities)
    timeline = generate_process_timeline(events=events, entities=entities)

    assert len(timeline) == 2
    assert [entry.time_text for entry in timeline] == ["09:10", "09:20"]
    assert timeline[0].summary.startswith("看護師A")
    assert timeline[1].summary.startswith("医師B")
    assert timeline[0].evidence[0].line_index == 1


def test_generate_timeline_is_deterministic() -> None:
    records = [
        MedicalRecordInput(
            record_id="r4",
            record_type="nursing",
            text="看護師A 09:10 観察を実施\n医師B 09:20 指示",
        )
    ]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)
    events = extract_events(normalized, entities=entities)

    first = generate_process_timeline(events=events, entities=entities)
    second = generate_process_timeline(events=events, entities=entities)

    assert first == second

