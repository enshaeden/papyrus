from __future__ import annotations

from papyrus.domain.actor import Actor


DEFAULT_WEB_ACTOR = Actor(actor_id="local.operator", display_name="Local Operator", role_hint="operator")
WEB_ACTOR_OPTIONS = (
    DEFAULT_WEB_ACTOR,
    Actor(actor_id="local.reviewer", display_name="Local Reviewer", role_hint="reviewer"),
    Actor(actor_id="local.manager", display_name="Local Manager", role_hint="approver"),
    Actor(actor_id="papyrus-demo", display_name="Papyrus Demo", role_hint="demo"),
)


def flash_html_for_request(runtime, request) -> str:
    from papyrus.interfaces.web.presenters.form_presenter import FormPresenter

    presenter = FormPresenter(runtime.template_renderer)
    notice = request.query_value("notice").strip()
    if notice:
        return presenter.flash(title="Success", body=notice, tone="success")
    error = request.query_value("error").strip()
    if error:
        return presenter.flash(title="Attention", body=error, tone="warning")
    return ""


def actor_for_request(request) -> str:
    actor = request.cookie_value("papyrus_actor", DEFAULT_WEB_ACTOR.actor_id).strip()
    return actor or DEFAULT_WEB_ACTOR.actor_id
