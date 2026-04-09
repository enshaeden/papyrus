from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SectionType(str, Enum):
    TEXT = "text"
    LONG_TEXT = "long_text"
    STEPS = "steps"
    CHECKLIST = "checklist"
    METADATA = "metadata"
    REFERENCES = "references"
    RELATIONSHIPS = "relationships"


@dataclass(frozen=True)
class BlueprintSection:
    section_id: str
    display_name: str
    description: str
    section_type: SectionType
    required: bool = True
    fields: tuple[dict[str, Any], ...] = ()
    body_headings: tuple[str, ...] = ()
    validation_rules: dict[str, Any] = field(default_factory=dict)
    help_text: str = ""


@dataclass(frozen=True)
class Blueprint:
    blueprint_id: str
    display_name: str
    description: str
    sections: tuple[BlueprintSection, ...]
    required_sections: tuple[str, ...]
    ordering: tuple[str, ...]
    validation_rules: dict[str, Any] = field(default_factory=dict)
    evidence_requirements: dict[str, Any] = field(default_factory=dict)
    lifecycle_defaults: dict[str, Any] = field(default_factory=dict)

    def section(self, section_id: str) -> BlueprintSection:
        for section in self.sections:
            if section.section_id == section_id:
                return section
        raise KeyError(section_id)
