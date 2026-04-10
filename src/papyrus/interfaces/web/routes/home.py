from __future__ import annotations

from papyrus.application.queries import event_history, knowledge_queue, manage_queue, service_catalog
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.governed_presenter import projection_use_guidance
from papyrus.interfaces.web.presenters.home_presenter import present_home_page
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request


def register(router, runtime) -> None:
    def home_page(request: Request):
        actor_id = actor_for_request(request)
        read_queue = knowledge_queue(limit=12, database_path=runtime.database_path)
        manage = manage_queue(database_path=runtime.database_path)
        services = service_catalog(database_path=runtime.database_path)
        events = event_history(limit=8, database_path=runtime.database_path)
        page = present_home_page(
            runtime.template_renderer,
            actor_id=actor_id,
            counts={
                "read_ready": sum(
                    1
                    for item in read_queue
                    if bool(projection_use_guidance(item.get("ui_projection")).get("safe_to_use"))
                ),
                "drafts": len(manage["draft_items"]),
                "review_required": len(manage["review_required"]),
                "needs_revalidation": len(manage["needs_revalidation"]),
                "needs_attention": len(manage["needs_attention"]),
                "weak_evidence": len(manage["weak_evidence_items"]),
                "stale": len(manage["stale_items"]),
                "services": len(services),
                "recent_activity": len(events),
            },
            events=events,
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_id,
                current_path=request.path,
                **page,
            )
        )

    router.add(["GET"], "/", home_page)
