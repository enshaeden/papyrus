from __future__ import annotations

import datetime as dt
import html
import re
from typing import Iterable
from urllib.parse import quote


OBJECT_ID_PATTERN = re.compile(r"^kb-[a-z0-9]+(?:-[a-z0-9]+)*$")


def escape(value: object) -> str:
    return html.escape("" if value is None else str(value))


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


def tone_for_approval(approval_state: str | None) -> str:
    return {
        "approved": "approved",
        "in_review": "pending",
        "draft": "muted",
        "rejected": "danger",
        "superseded": "muted",
    }.get(str(approval_state or ""), "pending")


def tone_for_revision(revision_state: str) -> str:
    return {
        "approved": "approved",
        "in_review": "pending",
        "draft": "muted",
        "rejected": "danger",
        "superseded": "muted",
    }.get(revision_state, "muted")


def tone_for_health(rank: int) -> str:
    if rank <= 0:
        return "approved"
    if rank == 1:
        return "warning"
    return "danger"


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
