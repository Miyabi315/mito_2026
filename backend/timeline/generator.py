from dataclasses import dataclass, field

from backend.extraction.entities import ExtractedEntity
from backend.extraction.events import ExtractedEvent


@dataclass
class TimelineEvidence:
    record_id: str
    line_index: int
    text: str
    start_char: int
    end_char: int


@dataclass
class TimelineEntry:
    timeline_id: str
    event_id: str
    event_type: str
    trigger: str
    time_text: str | None
    actor_entity_ids: list[str]
    patient_entity_ids: list[str]
    actor_names: list[str]
    patient_names: list[str]
    summary: str
    evidence: list[TimelineEvidence] = field(default_factory=list)


def _time_sort_key(time_text: str | None) -> tuple[int, int]:
    if not time_text:
        return (99, 99)
    hour_text, minute_text = time_text.split(":")
    return (int(hour_text), int(minute_text))


def generate_process_timeline(
    events: list[ExtractedEvent], entities: list[ExtractedEntity]
) -> list[TimelineEntry]:
    entity_name_map = {entity.entity_id: entity.name for entity in entities}
    entries: list[TimelineEntry] = []

    for event in events:
        actor_names = [entity_name_map[entity_id] for entity_id in event.actor_entity_ids]
        patient_names = [entity_name_map[entity_id] for entity_id in event.patient_entity_ids]

        evidence = [
            TimelineEvidence(
                record_id=item.record_id,
                line_index=item.line_index,
                text=item.text,
                start_char=item.start_char,
                end_char=item.end_char,
            )
            for item in event.evidence
        ]

        if actor_names:
            actor_text = ",".join(actor_names)
        else:
            actor_text = "unknown_actor"
        summary = f"{actor_text} {event.trigger}"

        entries.append(
            TimelineEntry(
                timeline_id=f"timeline_{event.event_id}",
                event_id=event.event_id,
                event_type=event.event_type,
                trigger=event.trigger,
                time_text=event.time_text,
                actor_entity_ids=event.actor_entity_ids,
                patient_entity_ids=event.patient_entity_ids,
                actor_names=actor_names,
                patient_names=patient_names,
                summary=summary,
                evidence=evidence,
            )
        )

    entries.sort(
        key=lambda entry: (
            _time_sort_key(entry.time_text),
            entry.evidence[0].record_id if entry.evidence else "",
            entry.evidence[0].line_index if entry.evidence else -1,
            entry.event_id,
        )
    )
    return entries
