from pathlib import Path

from backend.extraction.entities import extract_entities
from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput


def test_extract_entities_from_sample_record_keeps_evidence() -> None:
    sample_path = Path("data/sample_records/sample_record_01.txt")
    text = sample_path.read_text(encoding="utf-8")
    records = [MedicalRecordInput(record_id="sample_01", record_type="chart", text=text)]

    normalized = normalize_records(records)
    entities = extract_entities(normalized)

    names = {entity.name for entity in entities}
    assert names == {"山田太郎", "看護師A", "医師B"}

    patient = next(entity for entity in entities if entity.name == "山田太郎")
    assert patient.entity_type == "patient"
    assert patient.role == "patient"
    assert patient.evidence[0].record_id == "sample_01"
    assert patient.evidence[0].line_index == 0
    assert patient.evidence[0].text == "患者: 山田太郎"

    nurse = next(entity for entity in entities if entity.name == "看護師A")
    assert nurse.entity_type == "staff"
    assert nurse.role == "nurse"
    assert nurse.evidence[0].line_index == 1
    assert "看護師A" in nurse.evidence[0].text

    doctor = next(entity for entity in entities if entity.name == "医師B")
    assert doctor.entity_type == "staff"
    assert doctor.role == "doctor"
    assert doctor.evidence[0].line_index == 2


def test_extract_entities_is_deterministic() -> None:
    records = [
        MedicalRecordInput(
            record_id="r1",
            record_type="chart",
            text="患者: 田中花子\n看護師C 10:00 観察\n医師D 10:30 指示",
        )
    ]

    normalized = normalize_records(records)
    first = extract_entities(normalized)
    second = extract_entities(normalized)

    assert first == second

