from dataclasses import dataclass
from typing import Literal

RecordType = Literal["chart", "nursing", "order", "other"]


@dataclass(frozen=True)
class MedicalRecordInput:
    record_id: str
    record_type: RecordType
    text: str


@dataclass(frozen=True)
class NormalizedMedicalRecord:
    record_id: str
    record_type: RecordType
    lines: list[str]

