from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, quote, unquote
from wsgiref.simple_server import make_server

from papyrus.application.queries import (
    KnowledgeObjectNotFoundError,
    RuntimeUnavailableError,
    ServiceNotFoundError,
    impact_view_for_object,
    impact_view_for_service,
    knowledge_object_detail,
    knowledge_queue,
    revision_history,
    service_detail,
    trust_dashboard,
)
from papyrus.infrastructure.paths import DB_PATH


def _escape(value: object) -> str:
    return html.escape("" if value is None else str(value))


def _link(label: str, href: str) -> str:
    return f'<a href="{_escape(href)}">{_escape(label)}</a>'


def _html_response(start_response, status: str, body: str) -> list[bytes]:
    payload = body.encode("utf-8")
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(payload))),
        ("Cache-Control", "no-store"),
    ]
    start_response(status, headers)
    return [payload]


def _redirect_response(start_response, location: str) -> list[bytes]:
    start_response("302 Found", [("Location", location), ("Content-Length", "0")])
    return [b""]


def _badge(label: str, value: object, tone: str = "neutral") -> str:
    return (
        f'<span class="badge badge-{_escape(tone)}">'
        f'<span class="badge-label">{_escape(label)}</span>'
        f'<span class="badge-value">{_escape(value)}</span>'
        "</span>"
    )


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return '<p class="empty">None.</p>'
    head_html = "".join(f"<th>{_escape(header)}</th>" for header in headers)
    row_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{row_html}</tbody></table>"


def _list_card(title: str, items: list[str]) -> str:
    if not items:
        content = '<p class="empty">None.</p>'
    else:
        content = "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"
    return f'<section class="card"><h2>{_escape(title)}</h2>{content}</section>'


def _page(title: str, body: str, *, active: str) -> str:
    navigation = [
        ("Queue", "/queue", "queue"),
        ("Trust Dashboard", "/dashboard/trust", "dashboard"),
    ]
    nav_html = "".join(
        f'<a class="nav-link{" is-active" if key == active else ""}" href="{href}">{_escape(label)}</a>'
        for label, href, key in navigation
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(title)} | Papyrus</title>
  <style>
    :root {{
      --paper: #f5f1e8;
      --ink: #1f2622;
      --muted: #5d675f;
      --line: #d8cfbe;
      --panel: rgba(255, 252, 246, 0.9);
      --accent: #365c4f;
      --accent-soft: #dfe9e3;
      --warn: #7a4f24;
      --warn-soft: #f3e2cd;
      --danger: #7f2f2f;
      --danger-soft: #f4dada;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(54, 92, 79, 0.12), transparent 32rem),
        linear-gradient(180deg, #faf6ee 0%, var(--paper) 100%);
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .shell {{ max-width: 1200px; margin: 0 auto; padding: 1.5rem; }}
    .hero {{
      display: flex;
      gap: 1rem;
      justify-content: space-between;
      align-items: end;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--line);
      padding-bottom: 1rem;
    }}
    .hero h1 {{ margin: 0; font-size: clamp(2rem, 4vw, 3rem); line-height: 1; }}
    .hero p {{ margin: 0.5rem 0 0; color: var(--muted); max-width: 48rem; }}
    .nav {{ display: flex; gap: 0.6rem; flex-wrap: wrap; }}
    .nav-link {{
      padding: 0.65rem 0.9rem;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.5);
    }}
    .nav-link.is-active {{
      background: var(--accent);
      color: #f8f6f1;
      border-color: var(--accent);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1rem 1.1rem;
      box-shadow: 0 16px 40px rgba(42, 48, 45, 0.06);
    }}
    .card h2, .card h3 {{ margin-top: 0; }}
    .badge {{
      display: inline-flex;
      gap: 0.5rem;
      padding: 0.35rem 0.6rem;
      border-radius: 999px;
      font-size: 0.9rem;
      border: 1px solid var(--line);
      margin: 0.1rem 0.35rem 0.1rem 0;
      background: white;
    }}
    .badge-warning {{ background: var(--warn-soft); border-color: #dfc8a8; }}
    .badge-danger {{ background: var(--danger-soft); border-color: #ddb0b0; }}
    .badge-accent {{ background: var(--accent-soft); border-color: #bdd1c7; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.96rem;
    }}
    th, td {{
      text-align: left;
      padding: 0.65rem 0.55rem;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    ul {{ padding-left: 1.1rem; }}
    pre {{
      overflow-x: auto;
      white-space: pre-wrap;
      background: #f8f4eb;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1rem;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.9rem;
    }}
    .meta {{ color: var(--muted); margin-bottom: 1rem; }}
    .empty {{ color: var(--muted); }}
    .split {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 1rem;
    }}
    @media (max-width: 840px) {{
      .hero {{ align-items: start; flex-direction: column; }}
      .split {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div>
        <h1>{_escape(title)}</h1>
        <p>Local-first governed operational knowledge control plane.</p>
      </div>
      <nav class="nav">{nav_html}</nav>
    </header>
    {body}
  </main>
</body>
</html>"""


def _render_queue_page(items: list[dict[str, Any]]) -> str:
    cards = [
        _badge("Items", len(items), "accent"),
        _badge("Approval Pending", sum(1 for item in items if item["approval_state"] != "approved"), "warning"),
        _badge("Weak Evidence", sum(1 for item in items if item["citation_health_rank"] > 0), "danger"),
    ]
    rows = [
        [
            (
                f"{_link(item['title'], f'/objects/{quote(item['object_id'])}')}"
                f'<div class="meta">{_escape(item["object_id"])}</div>'
            ),
            _escape(item["object_type"]),
            _escape(item["trust_state"]),
            _escape(item["approval_state"]),
            _escape(", ".join(item["reasons"])),
            _escape(item["path"]),
        ]
        for item in items
    ]
    body = f"""
    <section class="card">
      <div>{''.join(cards)}</div>
      <h2>Knowledge Queue</h2>
      <p class="meta">Queue entries are ordered by approval state, trust posture, evidence quality, freshness, and ownership clarity.</p>
      {_table(["Title", "Type", "Trust", "Approval", "Reasons", "Path"], rows)}
    </section>
    """
    return _page("Knowledge Queue", body, active="queue")


def _render_object_detail_page(detail: dict[str, Any]) -> str:
    item = detail["object"]
    current_revision = detail["current_revision"]
    summary_badges = "".join(
        [
            _badge("Trust", item["trust_state"], "warning" if item["trust_state"] != "trusted" else "accent"),
            _badge("Approval", item["approval_state"] or "unknown", "warning" if item["approval_state"] != "approved" else "accent"),
            _badge("Citation Health", item["citation_health_rank"], "warning" if item["citation_health_rank"] > 0 else "accent"),
            _badge("Freshness", item["freshness_rank"], "warning" if item["freshness_rank"] > 0 else "accent"),
        ]
    )
    services = [
        _link(service["service_name"], f"/services/{quote(service['service_id'])}")
        for service in detail["related_services"]
    ]
    outbound = [
        f"{_escape(rel['relationship_type'])}: {_link(rel['title'], f'/objects/{quote(rel['object_id'])}')}"
        for rel in detail["outbound_relationships"]
    ]
    inbound = [
        f"{_escape(rel['relationship_type'])}: {_link(rel['title'], f'/objects/{quote(rel['object_id'])}')}"
        for rel in detail["inbound_relationships"]
    ]
    citations = [
        (
            f"<strong>{_escape(citation['source_title'])}</strong> | "
            f"{_escape(citation['source_ref'])} | "
            f"status={_escape(citation['validity_status'])}"
        )
        for citation in detail["citations"]
    ]
    audit = [
        f"{_escape(event['occurred_at'])} | {_escape(event['event_type'])} | actor={_escape(event['actor'])}"
        for event in detail["audit_events"]
    ]
    metadata_rows = [
        [_escape("Owner"), _escape(item["owner"])],
        [_escape("Team"), _escape(item["team"])],
        [_escape("Status"), _escape(item["status"])],
        [_escape("Path"), _escape(item["canonical_path"])],
        [_escape("Review Cadence"), _escape(item["review_cadence"])],
        [_escape("Last Reviewed"), _escape(item["last_reviewed"])],
        [_escape("Tags"), _escape(", ".join(item["tags"]))],
        [_escape("Systems"), _escape(", ".join(item["systems"]))],
    ]
    current_revision_html = (
        f"<p class='meta'>Current revision #{current_revision['revision_number']} | state={_escape(current_revision['revision_state'])}</p>"
        f"<pre>{_escape(current_revision['body_markdown'])}</pre>"
        if current_revision is not None
        else '<p class="empty">No current revision.</p>'
    )
    body = f"""
    <section class="card">
      <p class="meta">{_escape(item['object_type'])} | {_escape(item['object_id'])}</p>
      <h2>{_escape(item['title'])}</h2>
      <p>{_escape(item['summary'])}</p>
      <div>{summary_badges}</div>
      <p class="meta">
        {_link("Revision History", f"/objects/{quote(item['object_id'])}/revisions")} |
        {_link("Impact View", f"/impact/object/{quote(item['object_id'])}")}
      </p>
    </section>
    <div class="split">
      <section class="card">
        <h2>Current Revision</h2>
        {current_revision_html}
      </section>
      <section class="card">
        <h2>Metadata</h2>
        {_table(["Field", "Value"], metadata_rows)}
      </section>
    </div>
    <div class="grid">
      {_list_card("Related Services", services)}
      {_list_card("Outbound Relationships", outbound)}
      {_list_card("Inbound Relationships", inbound)}
      {_list_card("Citations", citations)}
    </div>
    <section class="card">
      <h2>Recent Audit Events</h2>
      {'<ul>' + ''.join(f'<li>{item}</li>' for item in audit) + '</ul>' if audit else '<p class="empty">None.</p>'}
    </section>
    """
    return _page(item["title"], body, active="queue")


def _render_revision_history_page(history: dict[str, Any]) -> str:
    object_info = history["object"]
    rows = [
        [
            _escape(revision["revision_number"]),
            _escape(revision["revision_state"]),
            _escape(revision["change_summary"] or ""),
            _escape(
                ", ".join(
                    f"{status}={count}" for status, count in revision["citations"].items() if count
                )
            ),
            _escape(
                "; ".join(
                    f"{assignment['reviewer']} ({assignment['state']})"
                    for assignment in revision["review_assignments"]
                )
            ),
            _escape("current" if revision["is_current"] else ""),
        ]
        for revision in history["revisions"]
    ]
    audit_items = [
        f"{_escape(event['occurred_at'])} | {_escape(event['event_type'])} | actor={_escape(event['actor'])}"
        for event in history["audit_events"]
    ]
    body = f"""
    <section class="card">
      <p class="meta">{_escape(object_info['object_id'])}</p>
      <h2>{_link(object_info['title'], f"/objects/{quote(object_info['object_id'])}")}</h2>
      <p class="meta">Revision history for {_escape(object_info['canonical_path'])}</p>
      {_table(["Revision", "State", "Change Summary", "Citations", "Review Assignments", "Current"], rows)}
    </section>
    {_list_card("Audit Trail", audit_items)}
    """
    return _page(f"{object_info['title']} Revision History", body, active="queue")


def _render_service_detail_page(detail: dict[str, Any]) -> str:
    service = detail["service"]
    linked_objects = [
        f"{_link(item['title'], f'/objects/{quote(item['object_id'])}')} | trust={_escape(item['trust_state'])}"
        for item in detail["linked_objects"]
    ]
    metadata_rows = [
        [_escape("Service Name"), _escape(service["service_name"])],
        [_escape("Status"), _escape(service["status"])],
        [_escape("Criticality"), _escape(service["service_criticality"])],
        [_escape("Source"), _escape(service["source"])],
        [_escape("Owner"), _escape(service["owner"] or "")],
        [_escape("Team"), _escape(service["team"] or "")],
    ]
    canonical_object = (
        _link(detail["canonical_object"]["title"], f"/objects/{quote(detail['canonical_object']['object_id'])}")
        if detail["canonical_object"] is not None
        else "None"
    )
    body = f"""
    <section class="card">
      <p class="meta">{_escape(service['service_id'])}</p>
      <h2>{_escape(service['service_name'])}</h2>
      <p class="meta">
        {_link("Impact View", f"/impact/service/{quote(service['service_id'])}")}
      </p>
    </section>
    <div class="split">
      <section class="card">
        <h2>Service Record</h2>
        {_table(["Field", "Value"], metadata_rows + [[_escape("Canonical Object"), canonical_object]])}
      </section>
      <section class="card">
        <h2>Operational Notes</h2>
        <p><strong>Support Entrypoints:</strong> {_escape(', '.join(service['support_entrypoints']) or 'None')}</p>
        <p><strong>Dependencies:</strong> {_escape(', '.join(service['dependencies']) or 'None')}</p>
        <p><strong>Common Failure Modes:</strong> {_escape(', '.join(service['common_failure_modes']) or 'None')}</p>
      </section>
    </div>
    {_list_card("Linked Knowledge Objects", linked_objects)}
    """
    return _page(service["service_name"], body, active="queue")


def _render_trust_dashboard_page(dashboard: dict[str, Any]) -> str:
    summary_cards = f"""
    <div class="grid">
      <section class="card"><h2>Objects</h2><p>{_escape(dashboard['object_count'])}</p></section>
      <section class="card"><h2>Trust States</h2><p>{_escape(', '.join(f'{key}={value}' for key, value in sorted(dashboard['trust_counts'].items())) )}</p></section>
      <section class="card"><h2>Approval States</h2><p>{_escape(', '.join(f'{key}={value}' for key, value in sorted(dashboard['approval_counts'].items())) )}</p></section>
      <section class="card"><h2>Evidence</h2><p>{_escape(', '.join(f'{key}={value}' for key, value in sorted(dashboard['evidence_counts'].items())) )}</p></section>
    </div>
    """
    queue_rows = [
        [
            _link(item["title"], f"/objects/{quote(item['object_id'])}"),
            _escape(item["trust_state"]),
            _escape(item["approval_state"]),
            _escape(", ".join(item["reasons"])),
        ]
        for item in dashboard["queue"][:20]
    ]
    validation_rows = [
        [
            _escape(item["completed_at"]),
            _escape(item["run_type"]),
            _escape(item["status"]),
            _escape(item["finding_count"]),
        ]
        for item in dashboard["validation_runs"]
    ]
    body = f"""
    {summary_cards}
    <div class="split">
      <section class="card">
        <h2>Priority Queue</h2>
        {_table(["Title", "Trust", "Approval", "Reasons"], queue_rows)}
      </section>
      <section class="card">
        <h2>Recent Validation Runs</h2>
        {_table(["Completed", "Run Type", "Status", "Findings"], validation_rows)}
      </section>
    </div>
    """
    return _page("Trust Dashboard", body, active="dashboard")


def _render_impact_page(impact: dict[str, Any]) -> str:
    entity = impact["entity"]
    if impact["entity_type"] == "knowledge_object":
        body = f"""
        <section class="card">
          <p class="meta">{_escape(entity['object_id'])}</p>
          <h2>{_link(entity['title'], f"/objects/{quote(entity['object_id'])}")}</h2>
          <p class="meta">Impact is calculated from inbound relationships, current citation dependents, and related services.</p>
        </section>
        <div class="grid">
          {_list_card("Impacted Objects", [f"{_link(item['title'], f'/objects/{quote(item['object_id'])}')} | trust={_escape(item['trust_state'])}" for item in impact['impacted_objects']])}
          {_list_card("Inbound Relationships", [f"{_escape(item['relationship_type'])}: {_link(item['title'], f'/objects/{quote(item['object_id'])}')}" for item in impact['inbound_relationships']])}
          {_list_card("Citation Dependents", [f"{_link(item['title'], f'/objects/{quote(item['object_id'])}')} | citation={_escape(item['citation_status'])}" for item in impact['citation_dependents']])}
          {_list_card("Related Services", [_link(item['service_name'], f"/services/{quote(item['service_id'])}") for item in impact['related_services']])}
        </div>
        """
        return _page(f"Impact: {entity['title']}", body, active="dashboard")

    body = f"""
    <section class="card">
      <p class="meta">{_escape(entity['service_id'])}</p>
      <h2>{_link(entity['service_name'], f"/services/{quote(entity['service_id'])}")}</h2>
      <p class="meta">Impact is calculated from current knowledge objects linked to this service.</p>
    </section>
    {_list_card("Impacted Objects", [f"{_link(item['title'], f'/objects/{quote(item['object_id'])}')} | trust={_escape(item['trust_state'])}" for item in impact['impacted_objects']])}
    """
    return _page(f"Impact: {entity['service_name']}", body, active="dashboard")


def _render_error_page(title: str, detail: str, status: str, *, active: str) -> str:
    body = f"""
    <section class="card">
      <h2>{_escape(title)}</h2>
      <p>{_escape(detail)}</p>
      <p class="meta">HTTP status: {_escape(status)}</p>
    </section>
    """
    return _page(title, body, active=active)


def app(database_path: str | Path = DB_PATH) -> Callable:
    resolved_database_path = Path(database_path)

    def application(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/") or "/"
        query = parse_qs(environ.get("QUERY_STRING", ""))
        if method != "GET":
            return _html_response(
                start_response,
                "405 Method Not Allowed",
                _render_error_page("Method Not Allowed", "Only GET is supported.", "405", active="queue"),
            )

        try:
            if path == "/":
                return _redirect_response(start_response, "/queue")

            if path == "/queue":
                limit = int(query.get("limit", ["100"])[0])
                return _html_response(
                    start_response,
                    "200 OK",
                    _render_queue_page(knowledge_queue(limit=limit, database_path=resolved_database_path)),
                )

            if path == "/dashboard/trust":
                return _html_response(
                    start_response,
                    "200 OK",
                    _render_trust_dashboard_page(trust_dashboard(database_path=resolved_database_path)),
                )

            if path.startswith("/objects/"):
                parts = [unquote(part) for part in path.strip("/").split("/")]
                if len(parts) == 2:
                    return _html_response(
                        start_response,
                        "200 OK",
                        _render_object_detail_page(
                            knowledge_object_detail(parts[1], database_path=resolved_database_path)
                        ),
                    )
                if len(parts) == 3 and parts[2] == "revisions":
                    return _html_response(
                        start_response,
                        "200 OK",
                        _render_revision_history_page(
                            revision_history(parts[1], database_path=resolved_database_path)
                        ),
                    )

            if path.startswith("/services/"):
                service_id = unquote(path.removeprefix("/services/"))
                return _html_response(
                    start_response,
                    "200 OK",
                    _render_service_detail_page(service_detail(service_id, database_path=resolved_database_path)),
                )

            if path.startswith("/impact/object/"):
                object_id = unquote(path.removeprefix("/impact/object/"))
                return _html_response(
                    start_response,
                    "200 OK",
                    _render_impact_page(impact_view_for_object(object_id, database_path=resolved_database_path)),
                )

            if path.startswith("/impact/service/"):
                service_id = unquote(path.removeprefix("/impact/service/"))
                return _html_response(
                    start_response,
                    "200 OK",
                    _render_impact_page(impact_view_for_service(service_id, database_path=resolved_database_path)),
                )

            return _html_response(
                start_response,
                "404 Not Found",
                _render_error_page("Not Found", f"No route for {path}", "404", active="queue"),
            )
        except RuntimeUnavailableError as exc:
            return _html_response(
                start_response,
                "503 Service Unavailable",
                _render_error_page("Runtime Unavailable", str(exc), "503", active="queue"),
            )
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError) as exc:
            return _html_response(
                start_response,
                "404 Not Found",
                _render_error_page("Not Found", str(exc), "404", active="queue"),
            )
        except Exception as exc:  # pragma: no cover - exercised through interface integration tests
            return _html_response(
                start_response,
                "500 Internal Server Error",
                _render_error_page("Internal Error", str(exc), "500", active="queue"),
            )

    return application


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Papyrus operator web interface over WSGI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8080, help="Bind port. Defaults to 8080.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    args = parser.parse_args()

    with make_server(args.host, args.port, app(args.db)) as server:
        print(f"Papyrus web interface listening on http://{args.host}:{args.port}")
        server.serve_forever()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
