from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput


class RecordInputPayload(BaseModel):
    record_id: str
    record_type: Literal["chart", "nursing", "order", "other"]
    text: str


class NormalizeRequest(BaseModel):
    records: list[RecordInputPayload]


app = FastAPI(title="Care Graph Prototype API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/records/normalize")
def normalize(request: NormalizeRequest) -> dict[str, list[dict[str, object]]]:
    inputs = [
        MedicalRecordInput(
            record_id=record.record_id,
            record_type=record.record_type,
            text=record.text,
        )
        for record in request.records
    ]
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

