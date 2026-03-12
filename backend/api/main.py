from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from backend.extraction.entities import ExtractedEntity, extract_entities
from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput


class RecordInputPayload(BaseModel):
    record_id: str
    record_type: Literal["chart", "nursing", "order", "other"]
    text: str


class NormalizeRequest(BaseModel):
    records: list[RecordInputPayload]


app = FastAPI(title="Care Graph Prototype API")


def _to_medical_record_inputs(request: NormalizeRequest) -> list[MedicalRecordInput]:
    return [
        MedicalRecordInput(
            record_id=record.record_id,
            record_type=record.record_type,
            text=record.text,
        )
        for record in request.records
    ]


def _serialize_entities(entities: list[ExtractedEntity]) -> list[dict[str, object]]:
    return [
        {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type,
            "role": entity.role,
            "name": entity.name,
            "evidence": [
                {
                    "record_id": evidence.record_id,
                    "line_index": evidence.line_index,
                    "text": evidence.text,
                    "start_char": evidence.start_char,
                    "end_char": evidence.end_char,
                }
                for evidence in entity.evidence
            ],
        }
        for entity in entities
    ]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/records/normalize")
def normalize(request: NormalizeRequest) -> dict[str, list[dict[str, object]]]:
    inputs = _to_medical_record_inputs(request)
    normalized = normalize_records(inputs)
    return {
        "normalized_records": [
            {
                "record_id": record.record_id,
                "record_type": record.record_type,
                "lines": record.lines,
            }
            for record in normalized
        ]
    }


@app.post("/extraction/entities")
def entities(request: NormalizeRequest) -> dict[str, list[dict[str, object]]]:
    inputs = _to_medical_record_inputs(request)
    normalized = normalize_records(inputs)
    extracted = extract_entities(normalized)
    return {"entities": _serialize_entities(extracted)}
