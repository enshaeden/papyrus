from __future__ import annotations

import datetime as dt
import html
import re
from typing import Iterable
from urllib.parse import quote


OBJECT_ID_PATTERN = re.compile(r"^kb-[a-z0-9]+(?:-[a-z0-9]+)*$")
DISPLAY_PLACEHOLDER_PATTERN = re.compile(r"<([A-Z0-9]+(?:_[A-Z0-9]+)*)>")

DISPLAY_TOKEN_REPLACEMENTS = {
    "COMPANY": "organization",
    "NAME": "",
    "ENDPOINT": "device",
    "SYSTEM": "system",
    "SERVICE": "service",
    "PROVIDER": "provider",
    "PLATFORM": "platform",
    "PORTAL": "portal",
    "REGION": "region",
    "OFFICE": "office",
    "SITE": "site",
    "ROOM": "room",
    "CATALOG": "catalog",
}

DISPLAY_TOKEN_ACRONYMS = {"AV", "HR", "IT", "VPN"}


def escape(value: object) -> str:
    return html.escape(sanitize_display_text("" if value is None else str(value)))


def sanitize_display_text(value: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        parts = [part for part in match.group(1).split("_") if part]
        while parts and len(parts[-1]) == 1:
            parts.pop()
        normalized: list[str] = []
        for part in parts:
            mapped = DISPLAY_TOKEN_REPLACEMENTS.get(part, part.lower())
            if not mapped:
                continue
            if part in DISPLAY_TOKEN_ACRONYMS:
                normalized.append(part)
            elif mapped.islower():
                normalized.append(mapped)
            else:
                normalized.append(mapped)
        if not normalized:
            return "internal reference"
        return " ".join(normalized)

    return DISPLAY_PLACEHOLDER_PATTERN.sub(replacement, value)


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", normalized)


def quoted_path(segment: str) -> str:
    return quote(segment, safe="")


def link(label: str, href: str, *, css_class: str = "") -> str:
    class_attr = f' class="{escape(css_class)}"' if css_class else ""
    return f'<a{class_attr} href="{escape(href)}">{escape(label)}</a>'


def join_html(items: Iterable[str], separator: str = "") -> str:
    return separator.join(item for item in items if item)


def render_list(items: list[str], *, css_class: str = "stack-list") -> str:
    if not items:
        return ""
    return f'<ul class="{escape(css_class)}">' + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def render_table(headers: list[str], rows: list[list[str]], *, table_id: str = "", css_class: str = "data-table") -> str:
    if not rows:
        return ""
    id_attr = f' id="{escape(table_id)}"' if table_id else ""
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    row_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        f'<table{id_attr} class="{escape(css_class)}"><thead><tr>{header_html}</tr></thead>'
        f"<tbody>{row_html}</tbody></table>"
    )


def render_definition_rows(rows: list[tuple[str, str]]) -> str:
    return "".join(
        f'<div class="meta-row"><dt>{escape(label)}</dt><dd>{value}</dd></div>'
        for label, value in rows
    )


def tone_for_trust(trust_state: str) -> str:
    return {
        "trusted": "approved",
        "weak_evidence": "warning",
        "stale": "warning",
        "suspect": "danger",
    }.get(trust_state, "muted")


def tone_for_review_state(revision_review_state: str | None) -> str:
    return {
        "approved": "approved",
        "in_review": "pending",
        "draft": "muted",
        "rejected": "danger",
        "superseded": "muted",
    }.get(str(revision_review_state or ""), "pending")


def tone_for_revision(revision_state: str) -> str:
    return tone_for_review_state(revision_state)


def tone_for_health(rank: int) -> str:
    if rank <= 0:
        return "approved"
    if rank == 1:
        return "warning"
    return "danger"


def risk_status(*, trust_state: str, safe_to_use: bool) -> tuple[str, str]:
    normalized = str(trust_state or "unknown")
    if normalized == "suspect":
        return "High", "danger"
    if not safe_to_use or normalized in {"weak_evidence", "stale"}:
        return "Review", "warning"
    return "Low", "approved"


def freshness_status(rank: int) -> tuple[str, str]:
    if rank <= 0:
        return "Current", "approved"
    if rank == 1:
        return "Due soon", "warning"
    return "Stale", "danger"


def review_state_status(revision_review_state: str | None) -> tuple[str, str]:
    normalized = str(revision_review_state or "unknown")
    return normalized.replace("_", " "), tone_for_review_state(normalized)


def format_timestamp(value: str | None) -> str:
    if not value:
        return "Unknown"
    try:
        timestamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return timestamp.strftime("%Y-%m-%d %H:%M")


def parse_multiline(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def parse_csvish(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
