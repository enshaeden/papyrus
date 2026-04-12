from __future__ import annotations

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.view_helpers import escape


def render_ingest_upload(
    *,
    components: ComponentPresenter,
    forms: FormPresenter,
    errors: list[str] | None,
    allow_web_ingest_local_paths: bool,
) -> str:
    local_path_html = (
        forms.field(
            field_id="source_path",
            label="Local source file",
            control_html=forms.input(field_id="source_path", name="source_path", value="", placeholder="/absolute/path/to/file.md"),
            hint="Use an absolute path on this computer. Use this only in a trusted local session.",
        )
        if allow_web_ingest_local_paths
        else (
            '<div class="ingest-upload__notice">'
            "<p><strong>Local source file unavailable</strong></p>"
            "<p>This session accepts uploaded files only.</p>"
            "<p>Start the app with <code>--allow-web-ingest-local-paths</code> if you intentionally want to read a file from this same computer.</p>"
            "</div>"
        )
    )
    error_html = (
        '<div class="ingest-upload__errors">'
        + "".join(f"<p>{escape(item)}</p>" for item in errors or [])
        + "</div>"
        if errors
        else ""
    )
    return (
        '<section class="ingest-upload" data-component="ingest-upload" data-surface="ingest">'
        '<p class="ingest-upload__kicker">Import</p>'
        "<h2>Upload document</h2>"
        f"{error_html}"
        '<form class="governed-form" method="post" enctype="multipart/form-data">'
        + forms.field(
            field_id="upload",
            label="File upload",
            control_html='<input id="upload" name="upload" type="file" accept=".md,.markdown,.docx,.pdf" data-component="form-control" data-control-type="file" />',
            hint="Upload Markdown, DOCX, or PDF. Text-based PDFs work best and may still need cleanup after import.",
        )
        + local_path_html
        + forms.button(label="Import document", action_id="start-ingestion")
        + "</form></section>"
    )
