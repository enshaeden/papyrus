from __future__ import annotations


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
