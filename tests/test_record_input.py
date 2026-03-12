from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput


def test_normalize_records_trims_and_drops_empty_lines() -> None:
    records = [
        MedicalRecordInput(
            record_id="r1",
            record_type="chart",
            text="  患者: 山田太郎 \n\n 看護記録: 安静  ",
        )
    ]

    normalized = normalize_records(records)

    assert len(normalized) == 1
    assert normalized[0].record_id == "r1"
    assert normalized[0].record_type == "chart"
    assert normalized[0].lines == ["患者: 山田太郎", "看護記録: 安静"]

