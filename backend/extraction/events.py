import hashlib
import re
from dataclasses import dataclass, field
from typing import Literal

from backend.extraction.entities import ExtractedEntity, extract_entities
from backend.extraction.types import NormalizedMedicalRecord

EventType = Literal["order", "instruction", "performed", "observation", "state_change"]

TIME_PATTERN = re.compile(r"\b([0-2]?\d:[0-5]\d)\b")
EVENT_RULES: tuple[tuple[re.Pattern[str], EventType], ...] = (
    (re.compile(r"(オーダー|処方|検査依頼|採血依頼|依頼)"), "order"),
    (re.compile(r"(指示|要請)"), "instruction"),
    (re.compile(r"(実施|施行|測定|投与|処置)"), "performed"),
    (re.compile(r"(観察|確認|評価|記録)"), "observation"),
    (re.compile(r"(改善|悪化|安定|発熱|低下|上昇)"), "state_change"),
)


@dataclass
class EventEvidence:
    record_id: str
    line_index: int
    text: str
    start_char: int
    end_char: int


@dataclass
class ExtractedEvent:
    event_id: str
    event_type: EventType
    trigger: str
    time_text: str | None
    actor_entity_ids: list[str]
    patient_entity_ids: list[str]
    evidence: list[EventEvidence] = field(default_factory=list)


def _make_event_id(
    record_id: str,
    line_index: int,
    event_type: EventType,
    trigger: str,
    start_char: int,
    end_char: int,
) -> str:
    source = f"{record_id}|{line_index}|{event_type}|{trigger}|{start_char}|{end_char}"
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
    return f"event_{digest}"


def _line_entity_ids(
    entities: list[ExtractedEntity],
) -> dict[tuple[str, int], dict[str, list[str]]]:
    line_map: dict[tuple[str, int], dict[str, list[str]]] = {}
    for entity in entities:
        bucket = "actors" if entity.entity_type == "staff" else "patients"
        for evidence in entity.evidence:
            line_key = (evidence.record_id, evidence.line_index)
            if line_key not in line_map:
                line_map[line_key] = {"actors": [], "patients": []}
            if entity.entity_id not in line_map[line_key][bucket]:
                line_map[line_key][bucket].append(entity.entity_id)
    for value in line_map.values():
        value["actors"].sort()
        value["patients"].sort()
    return line_map


def _extract_primary_event(
    line: str,
) -> tuple[EventType, str, int, int] | None:
    for pattern, event_type in EVENT_RULES:
        match = pattern.search(line)
        if match:
            trigger = match.group(1)
            return event_type, trigger, match.start(1), match.end(1)
    return None


def extract_events(
    records: list[NormalizedMedicalRecord],
    entities: list[ExtractedEntity] | None = None,
) -> list[ExtractedEvent]:
    if entities is None:
        entities = extract_entities(records)

    entities_by_line = _line_entity_ids(entities)
    events: list[ExtractedEvent] = []

    for record in records:
        for line_index, line in enumerate(record.lines):
            extracted = _extract_primary_event(line)
            if extracted is None:
                continue
            event_type, trigger, start_char, end_char = extracted
            line_key = (record.record_id, line_index)
            time_match = TIME_PATTERN.search(line)
            time_text = time_match.group(1) if time_match else None
            line_entity_map = entities_by_line.get(line_key, {"actors": [], "patients": []})

            events.append(
                ExtractedEvent(
                    event_id=_make_event_id(
                        record_id=record.record_id,
                        line_index=line_index,
                        event_type=event_type,
                        trigger=trigger,
                        start_char=start_char,
                        end_char=end_char,
                    ),
                    event_type=event_type,
                    trigger=trigger,
                    time_text=time_text,
                    actor_entity_ids=line_entity_map["actors"],
                    patient_entity_ids=line_entity_map["patients"],
                    evidence=[
                        EventEvidence(
                            record_id=record.record_id,
                            line_index=line_index,
                            text=line,
                            start_char=start_char,
                            end_char=end_char,
                        )
                    ],
                )
            )

    events.sort(key=lambda event: event.event_id)
    return events

