from backend.extraction.types import MedicalRecordInput, NormalizedMedicalRecord


def normalize_records(records: list[MedicalRecordInput]) -> list[NormalizedMedicalRecord]:
    normalized: list[NormalizedMedicalRecord] = []
    for record in records:
        lines = [line.strip() for line in record.text.splitlines() if line.strip()]
        normalized.append(
            NormalizedMedicalRecord(
                record_id=record.record_id,
                record_type=record.record_type,
                lines=lines,
            )
        )
    return normalized

