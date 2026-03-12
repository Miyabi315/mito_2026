from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.extraction.entities import ExtractedEntity, extract_entities
from backend.extraction.events import ExtractedEvent, extract_events
from backend.extraction.input import normalize_records
from backend.extraction.types import MedicalRecordInput
from backend.graph.generator import CareGraph, generate_care_graph
from backend.timeline.generator import TimelineEntry, generate_process_timeline


class RecordInputPayload(BaseModel):
    record_id: str
    record_type: Literal["chart", "nursing", "order", "other"]
    text: str


class NormalizeRequest(BaseModel):
    records: list[RecordInputPayload]


app = FastAPI(title="Care Graph Prototype API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def _serialize_events(events: list[ExtractedEvent]) -> list[dict[str, object]]:
    return [
        {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "trigger": event.trigger,
            "time_text": event.time_text,
            "actor_entity_ids": event.actor_entity_ids,
            "patient_entity_ids": event.patient_entity_ids,
            "evidence": [
                {
                    "record_id": evidence.record_id,
                    "line_index": evidence.line_index,
                    "text": evidence.text,
                    "start_char": evidence.start_char,
                    "end_char": evidence.end_char,
                }
                for evidence in event.evidence
            ],
        }
        for event in events
    ]


def _serialize_graph(graph: CareGraph) -> dict[str, list[dict[str, object]]]:
    return {
        "nodes": [
            {
                "node_id": node.node_id,
                "node_type": node.node_type,
                "label": node.label,
                "role": node.role,
                "event_type": node.event_type,
                "time_text": node.time_text,
                "trigger": node.trigger,
                "evidence": [
                    {
                        "record_id": evidence.record_id,
                        "line_index": evidence.line_index,
                        "text": evidence.text,
                        "start_char": evidence.start_char,
                        "end_char": evidence.end_char,
                    }
                    for evidence in node.evidence
                ],
            }
            for node in graph.nodes
        ],
        "edges": [
            {
                "edge_id": edge.edge_id,
                "source": edge.source,
                "target": edge.target,
                "relation": edge.relation,
                "event_id": edge.event_id,
                "evidence": [
                    {
                        "record_id": evidence.record_id,
                        "line_index": evidence.line_index,
                        "text": evidence.text,
                        "start_char": evidence.start_char,
                        "end_char": evidence.end_char,
                    }
                    for evidence in edge.evidence
                ],
            }
            for edge in graph.edges
        ],
    }


def _serialize_timeline(entries: list[TimelineEntry]) -> dict[str, list[dict[str, object]]]:
    return {
        "timeline": [
            {
                "timeline_id": entry.timeline_id,
                "event_id": entry.event_id,
                "event_type": entry.event_type,
                "trigger": entry.trigger,
                "time_text": entry.time_text,
                "actor_entity_ids": entry.actor_entity_ids,
                "patient_entity_ids": entry.patient_entity_ids,
                "actor_names": entry.actor_names,
                "patient_names": entry.patient_names,
                "summary": entry.summary,
                "evidence": [
                    {
                        "record_id": evidence.record_id,
                        "line_index": evidence.line_index,
                        "text": evidence.text,
                        "start_char": evidence.start_char,
                        "end_char": evidence.end_char,
                    }
                    for evidence in entry.evidence
                ],
            }
            for entry in entries
        ]
    }


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


@app.post("/extraction/events")
def events(request: NormalizeRequest) -> dict[str, list[dict[str, object]]]:
    inputs = _to_medical_record_inputs(request)
    normalized = normalize_records(inputs)
    extracted_entities = extract_entities(normalized)
    extracted_events = extract_events(normalized, entities=extracted_entities)
    return {"events": _serialize_events(extracted_events)}


@app.post("/graph/care")
def care_graph(request: NormalizeRequest) -> dict[str, list[dict[str, object]]]:
    inputs = _to_medical_record_inputs(request)
    normalized = normalize_records(inputs)
    extracted_entities = extract_entities(normalized)
    extracted_events = extract_events(normalized, entities=extracted_entities)
    graph = generate_care_graph(entities=extracted_entities, events=extracted_events)
    return _serialize_graph(graph)


@app.post("/timeline/process")
def process_timeline(request: NormalizeRequest) -> dict[str, list[dict[str, object]]]:
    inputs = _to_medical_record_inputs(request)
    normalized = normalize_records(inputs)
    extracted_entities = extract_entities(normalized)
    extracted_events = extract_events(normalized, entities=extracted_entities)
    timeline = generate_process_timeline(events=extracted_events, entities=extracted_entities)
    return _serialize_timeline(timeline)
