from __future__ import annotations

from papyrus.domain.blueprints import Blueprint, BlueprintSection, SectionType


def _field(
    name: str,
    label: str,
    *,
    kind: str,
    required: bool = True,
    placeholder: str = "",
    hint: str = "",
    taxonomy: str | None = None,
    widget: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "label": label,
        "kind": kind,
        "required": required,
        "placeholder": placeholder,
        "hint": hint,
        "taxonomy": taxonomy,
        "widget": widget or {},
    }


COMMON_IDENTITY_SECTION = BlueprintSection(
    section_id="identity",
    display_name="Identity",
    description="Name the guidance and set the publishing details.",
    section_type=SectionType.METADATA,
    fields=(
        _field("object_id", "Reference code", kind="text", placeholder="Use lowercase words separated by hyphens"),
        _field("title", "Title", kind="text", placeholder="Name the guidance clearly"),
        _field(
            "canonical_path",
            "Publishing location",
            kind="text",
            placeholder="Where the published source will live in the knowledge library",
        ),
    ),
    help_text="Start with the title and publishing details before drafting the operational content.",
)

COMMON_STEWARDSHIP_SECTION = BlueprintSection(
    section_id="stewardship",
    display_name="Stewardship",
    description="Set ownership, review timing, and linked context.",
    section_type=SectionType.METADATA,
    fields=(
        _field("summary", "Summary", kind="long_text", placeholder="Summarize the outcome and when to use it."),
        _field("owner", "Owner", kind="text", placeholder="Team or person responsible"),
        _field("team", "Team", kind="select", taxonomy="teams"),
        _field("object_lifecycle_state", "Lifecycle state", kind="select", taxonomy="statuses"),
        _field("review_cadence", "Review cadence", kind="select", taxonomy="review_cadences"),
        _field("audience", "Audience", kind="select", taxonomy="audiences"),
        _field("systems", "Related systems", kind="list", required=False, placeholder="Add one related system per line."),
        _field(
            "tags",
            "Tags",
            kind="list",
            required=False,
            placeholder="One controlled tag per line.",
            widget={
                "type": "taxonomy_multi_select",
                "taxonomy": "tags",
                "placeholder": "Search controlled tags",
                "singular_label": "tag",
                "manual_entry_label": "Manual tag entry",
            },
        ),
        _field(
            "related_services",
            "Related services",
            kind="list",
            required=False,
            placeholder="One controlled service per line.",
            widget={
                "type": "taxonomy_multi_select",
                "taxonomy": "services",
                "placeholder": "Search related services",
                "singular_label": "service",
                "manual_entry_label": "Manual service entry",
            },
        ),
        _field(
            "related_object_ids",
            "Related guidance",
            kind="list",
            required=False,
            placeholder="Add one related guidance reference per line.",
            widget={
                "type": "object_search_multi_select",
                "placeholder": "Search related guidance",
                "singular_label": "related guidance item",
                "manual_entry_label": "Manual reference entry",
            },
        ),
        _field(
            "change_summary",
            "What changed",
            kind="text",
            required=False,
            placeholder="Summarize the change in one short line.",
        ),
    ),
    help_text="These details control accountability, review timing, and impact tracing.",
)

COMMON_EVIDENCE_SECTION = BlueprintSection(
    section_id="evidence",
    display_name="Evidence",
    description="Add the sources that support this draft before review.",
    section_type=SectionType.REFERENCES,
    fields=(
        _field(
            "citations",
            "Citations",
            kind="references",
            widget={
                "type": "citation_lookup",
                "slots": 3,
            },
        ),
    ),
    validation_rules={"minimum_items": 1},
    help_text="Every draft needs clear supporting sources before it goes to review.",
)

COMMON_RELATIONSHIP_SECTION = BlueprintSection(
    section_id="relationships",
    display_name="Relationships",
    description="Link related guidance and downstream dependencies.",
    section_type=SectionType.RELATIONSHIPS,
    required=False,
    fields=(
        _field("related_object_ids", "Related guidance", kind="list", required=False),
    ),
    help_text="These links make impact and follow-on work easier to review.",
)


RUNBOOK_BLUEPRINT = Blueprint(
    blueprint_id="runbook",
    display_name="Runbook",
    description="Structured operational procedure with prerequisites, steps, recovery, and evidence.",
    sections=(
        COMMON_IDENTITY_SECTION,
        COMMON_STEWARDSHIP_SECTION,
        BlueprintSection(
            section_id="purpose",
            display_name="Purpose",
            description="When to use the runbook and what outcome it targets.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("use_when", "Use when", kind="long_text", placeholder="Explain the trigger and expected operator outcome."),
            ),
            body_headings=("Use When",),
        ),
        BlueprintSection(
            section_id="prerequisites",
            display_name="Prerequisites",
            description="Access, approvals, or setup required before running the procedure.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("prerequisites", "Prerequisites", kind="list", placeholder="One prerequisite per line."),
            ),
        ),
        BlueprintSection(
            section_id="procedure",
            display_name="Procedure",
            description="The ordered operational steps.",
            section_type=SectionType.STEPS,
            fields=(
                _field("steps", "Steps", kind="list", placeholder="One step per line."),
            ),
        ),
        BlueprintSection(
            section_id="verification",
            display_name="Verification",
            description="Checks that confirm the expected outcome.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("verification", "Verification", kind="list", placeholder="One verification check per line."),
            ),
        ),
        BlueprintSection(
            section_id="rollback",
            display_name="Rollback",
            description="Recovery actions when execution fails.",
            section_type=SectionType.STEPS,
            fields=(
                _field("rollback", "Rollback", kind="list", placeholder="One rollback action per line."),
            ),
        ),
        BlueprintSection(
            section_id="boundaries",
            display_name="Boundaries",
            description="Escalation boundaries and related knowledge notes.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field(
                    "boundaries_and_escalation",
                    "Boundaries and escalation",
                    kind="long_text",
                    placeholder="Explain where the runbook stops and escalation begins.",
                ),
                _field(
                    "related_knowledge_notes",
                    "Related knowledge notes",
                    kind="long_text",
                    required=False,
                    placeholder="Call out adjacent guidance or follow-on material.",
                ),
            ),
            body_headings=("Boundaries And Escalation", "Related Knowledge Notes"),
        ),
        COMMON_EVIDENCE_SECTION,
        COMMON_RELATIONSHIP_SECTION,
    ),
    required_sections=(
        "identity",
        "stewardship",
        "purpose",
        "prerequisites",
        "procedure",
        "verification",
        "rollback",
        "boundaries",
        "evidence",
    ),
    ordering=(
        "identity",
        "stewardship",
        "purpose",
        "prerequisites",
        "procedure",
        "verification",
        "rollback",
        "boundaries",
        "evidence",
        "relationships",
    ),
    validation_rules={"require_related_service": True},
    evidence_requirements={"minimum_citations": 1},
    lifecycle_defaults={"object_lifecycle_state": "draft", "review_cadence": "quarterly"},
)

KNOWN_ERROR_BLUEPRINT = Blueprint(
    blueprint_id="known_error",
    display_name="Known Error",
    description="Diagnosed issue pattern with signals, checks, mitigations, and escalation criteria.",
    sections=(
        COMMON_IDENTITY_SECTION,
        COMMON_STEWARDSHIP_SECTION,
        BlueprintSection(
            section_id="diagnosis",
            display_name="Diagnosis",
            description="Symptoms, scope, and cause.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("symptoms", "Symptoms", kind="list", placeholder="One observable symptom per line."),
                _field("scope", "Scope", kind="long_text", placeholder="Define the affected boundary."),
                _field("cause", "Cause", kind="long_text", placeholder="Describe the diagnosed cause."),
            ),
        ),
        BlueprintSection(
            section_id="diagnostic_checks",
            display_name="Diagnostic Checks",
            description="Checks used to confirm the pattern.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("diagnostic_checks", "Diagnostic checks", kind="list", placeholder="One check per line."),
            ),
        ),
        BlueprintSection(
            section_id="mitigations",
            display_name="Mitigations",
            description="Containment or workaround steps.",
            section_type=SectionType.STEPS,
            fields=(
                _field("mitigations", "Mitigations", kind="list", placeholder="One mitigation per line."),
                _field(
                    "permanent_fix_status",
                    "Permanent fix status",
                    kind="select",
                    taxonomy="permanent_fix_status",
                ),
            ),
        ),
        BlueprintSection(
            section_id="escalation",
            display_name="Escalation",
            description="Detection, escalation threshold, and supporting notes.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("detection_notes", "Detection notes", kind="long_text"),
                _field("escalation_threshold", "Escalation threshold", kind="long_text"),
                _field("evidence_notes", "Evidence notes", kind="long_text", required=False),
            ),
            body_headings=("Detection Notes", "Escalation Threshold", "Evidence Notes"),
        ),
        COMMON_EVIDENCE_SECTION,
        COMMON_RELATIONSHIP_SECTION,
    ),
    required_sections=(
        "identity",
        "stewardship",
        "diagnosis",
        "diagnostic_checks",
        "mitigations",
        "escalation",
        "evidence",
    ),
    ordering=(
        "identity",
        "stewardship",
        "diagnosis",
        "diagnostic_checks",
        "mitigations",
        "escalation",
        "evidence",
        "relationships",
    ),
    validation_rules={"require_related_service": True},
    evidence_requirements={"minimum_citations": 1},
    lifecycle_defaults={"object_lifecycle_state": "draft", "review_cadence": "after_change"},
)

SERVICE_RECORD_BLUEPRINT = Blueprint(
    blueprint_id="service_record",
    display_name="Service Record",
    description="Support-facing description of a service, its dependencies, support paths, and failure modes.",
    sections=(
        COMMON_IDENTITY_SECTION,
        COMMON_STEWARDSHIP_SECTION,
        BlueprintSection(
            section_id="service_profile",
            display_name="Service Profile",
            description="What the service is and how critical it is.",
            section_type=SectionType.METADATA,
            fields=(
                _field("service_name", "Service name", kind="text"),
                _field("service_criticality", "Service criticality", kind="select", taxonomy="service_criticality"),
                _field("scope_notes", "Scope", kind="long_text"),
            ),
            body_headings=("Scope",),
        ),
        BlueprintSection(
            section_id="dependencies",
            display_name="Dependencies",
            description="Systems and service dependencies.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("dependencies", "Dependencies", kind="list", placeholder="One dependency per line."),
            ),
        ),
        BlueprintSection(
            section_id="support_entrypoints",
            display_name="Support Entrypoints",
            description="How operators and support flows reach the service team.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("support_entrypoints", "Support entrypoints", kind="list", placeholder="One entrypoint per line."),
            ),
        ),
        BlueprintSection(
            section_id="failure_modes",
            display_name="Failure Modes",
            description="Common operational failure patterns.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("common_failure_modes", "Common failure modes", kind="list", placeholder="One failure mode per line."),
            ),
        ),
        BlueprintSection(
            section_id="operations",
            display_name="Operational Notes",
            description="Support posture, caveats, and related service knowledge.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("operational_notes", "Operational notes", kind="long_text"),
                _field("evidence_notes", "Evidence notes", kind="long_text", required=False),
                _field("related_runbooks", "Related runbooks", kind="list", required=False),
                _field("related_known_errors", "Related known errors", kind="list", required=False),
            ),
            body_headings=("Operational Notes", "Evidence Notes"),
        ),
        COMMON_EVIDENCE_SECTION,
        COMMON_RELATIONSHIP_SECTION,
    ),
    required_sections=(
        "identity",
        "stewardship",
        "service_profile",
        "dependencies",
        "support_entrypoints",
        "failure_modes",
        "operations",
        "evidence",
    ),
    ordering=(
        "identity",
        "stewardship",
        "service_profile",
        "dependencies",
        "support_entrypoints",
        "failure_modes",
        "operations",
        "evidence",
        "relationships",
    ),
    validation_rules={"require_dependencies": True},
    evidence_requirements={"minimum_citations": 1},
    lifecycle_defaults={"object_lifecycle_state": "draft", "review_cadence": "quarterly"},
)

POLICY_BLUEPRINT = Blueprint(
    blueprint_id="policy",
    display_name="Policy",
    description="Governed policy with scope, controls, exceptions, and evidence.",
    sections=(
        COMMON_IDENTITY_SECTION,
        COMMON_STEWARDSHIP_SECTION,
        BlueprintSection(
            section_id="policy_scope",
            display_name="Scope",
            description="Purpose and scope of the policy.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("policy_scope", "Policy scope", kind="long_text"),
            ),
            body_headings=("Policy Scope",),
        ),
        BlueprintSection(
            section_id="controls",
            display_name="Controls",
            description="Control statements or mandatory requirements.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("controls", "Controls", kind="list", placeholder="One control per line."),
            ),
        ),
        BlueprintSection(
            section_id="exceptions",
            display_name="Exceptions",
            description="Exceptions, waivers, or boundary conditions.",
            section_type=SectionType.LONG_TEXT,
            required=False,
            fields=(
                _field("exceptions", "Exceptions", kind="long_text"),
            ),
            body_headings=("Exceptions",),
        ),
        COMMON_EVIDENCE_SECTION,
        COMMON_RELATIONSHIP_SECTION,
    ),
    required_sections=("identity", "stewardship", "policy_scope", "controls", "evidence"),
    ordering=("identity", "stewardship", "policy_scope", "controls", "exceptions", "evidence", "relationships"),
    evidence_requirements={"minimum_citations": 1},
    lifecycle_defaults={"object_lifecycle_state": "draft", "review_cadence": "annual"},
)

SYSTEM_DESIGN_BLUEPRINT = Blueprint(
    blueprint_id="system_design",
    display_name="System Design",
    description="Operational system design with architecture, dependencies, interfaces, failure modes, and support notes.",
    sections=(
        COMMON_IDENTITY_SECTION,
        COMMON_STEWARDSHIP_SECTION,
        BlueprintSection(
            section_id="architecture",
            display_name="Architecture",
            description="High-level architecture and design intent.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("architecture", "Architecture", kind="long_text"),
            ),
            body_headings=("Architecture",),
        ),
        BlueprintSection(
            section_id="dependencies",
            display_name="Dependencies",
            description="Internal and external dependencies.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("dependencies", "Dependencies", kind="list"),
            ),
        ),
        BlueprintSection(
            section_id="interfaces",
            display_name="Interfaces",
            description="Key interfaces, integrations, and entrypoints.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("interfaces", "Interfaces", kind="list"),
            ),
        ),
        BlueprintSection(
            section_id="failure_modes",
            display_name="Failure Modes",
            description="Known failure or degradation modes.",
            section_type=SectionType.CHECKLIST,
            fields=(
                _field("common_failure_modes", "Failure modes", kind="list"),
            ),
        ),
        BlueprintSection(
            section_id="operations",
            display_name="Operations",
            description="Operational notes, escalation, and follow-on guidance.",
            section_type=SectionType.LONG_TEXT,
            fields=(
                _field("operational_notes", "Operational notes", kind="long_text"),
                _field("support_entrypoints", "Support entrypoints", kind="list", required=False),
            ),
            body_headings=("Operational Notes",),
        ),
        COMMON_EVIDENCE_SECTION,
        COMMON_RELATIONSHIP_SECTION,
    ),
    required_sections=(
        "identity",
        "stewardship",
        "architecture",
        "dependencies",
        "interfaces",
        "failure_modes",
        "operations",
        "evidence",
    ),
    ordering=(
        "identity",
        "stewardship",
        "architecture",
        "dependencies",
        "interfaces",
        "failure_modes",
        "operations",
        "evidence",
        "relationships",
    ),
    evidence_requirements={"minimum_citations": 1},
    lifecycle_defaults={"object_lifecycle_state": "draft", "review_cadence": "after_change"},
)


BLUEPRINTS = (
    RUNBOOK_BLUEPRINT,
    KNOWN_ERROR_BLUEPRINT,
    SERVICE_RECORD_BLUEPRINT,
    POLICY_BLUEPRINT,
    SYSTEM_DESIGN_BLUEPRINT,
)
