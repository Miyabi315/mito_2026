import hashlib
import re
from dataclasses import dataclass, field
from typing import Literal

from backend.extraction.types import NormalizedMedicalRecord

EntityType = Literal["patient", "staff"]
EntityRole = Literal[
    "patient",
    "doctor",
    "nurse",
    "pharmacist",
    "therapist",
    "staff_unknown",
]

PATIENT_PATTERN = re.compile(r"(?:患者|Pt|Patient)\s*[:：]\s*([^\s、,。]+)")

STAFF_RULES: tuple[tuple[re.Pattern[str], EntityRole], ...] = (
    (re.compile(r"(看護師[^\s、,。]*)"), "nurse"),
    (re.compile(r"(医師[^\s、,。]*)"), "doctor"),
    (re.compile(r"(主治医[^\s、,。]*)"), "doctor"),
    (re.compile(r"(薬剤師[^\s、,。]*)"), "pharmacist"),
    (re.compile(r"(理学療法士[^\s、,。]*)"), "therapist"),
    (re.compile(r"(作業療法士[^\s、,。]*)"), "therapist"),
    (re.compile(r"(PT[^\s、,。]*)"), "therapist"),
    (re.compile(r"(OT[^\s、,。]*)"), "therapist"),
    (re.compile(r"(スタッフ[^\s、,。]*)"), "staff_unknown"),
)


@dataclass
class EntityEvidence:
    record_id: str
    line_index: int
    text: str
    start_char: int
    end_char: int


@dataclass
class ExtractedEntity:
    entity_id: str
    entity_type: EntityType
    role: EntityRole
    name: str
    evidence: list[EntityEvidence] = field(default_factory=list)


def _make_entity_id(entity_type: EntityType, role: EntityRole, name: str) -> str:
    source = f"{entity_type}|{role}|{name}"
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
    return f"{entity_type}_{digest}"


def extract_entities(records: list[NormalizedMedicalRecord]) -> list[ExtractedEntity]:
    entity_map: dict[tuple[EntityType, EntityRole, str], ExtractedEntity] = {}
    for record in records:
        for line_index, line in enumerate(record.lines):
            line_mentions: list[tuple[EntityType, EntityRole, str, int, int]] = []

            for match in PATIENT_PATTERN.finditer(line):
                name = match.group(1).strip()
                line_mentions.append(("patient", "patient", name, match.start(1), match.end(1)))

            for pattern, role in STAFF_RULES:
                for match in pattern.finditer(line):
                    name = match.group(1).strip()
                    line_mentions.append(("staff", role, name, match.start(1), match.end(1)))

            seen_in_line: set[tuple[EntityType, EntityRole, str, int, int]] = set()
            for entity_type, role, name, start_char, end_char in line_mentions:
                if not name:
                    continue
                mention_key = (entity_type, role, name, start_char, end_char)
                if mention_key in seen_in_line:
                    continue
                seen_in_line.add(mention_key)

                entity_key = (entity_type, role, name)
                if entity_key not in entity_map:
                    entity_map[entity_key] = ExtractedEntity(
                        entity_id=_make_entity_id(entity_type=entity_type, role=role, name=name),
                        entity_type=entity_type,
                        role=role,
                        name=name,
                    )

                entity_map[entity_key].evidence.append(
                    EntityEvidence(
                        record_id=record.record_id,
                        line_index=line_index,
                        text=line,
                        start_char=start_char,
                        end_char=end_char,
                    )
                )

    entities = sorted(entity_map.values(), key=lambda entity: entity.entity_id)
    for entity in entities:
        entity.evidence.sort(
            key=lambda item: (item.record_id, item.line_index, item.start_char, item.end_char)
        )
    return entities

