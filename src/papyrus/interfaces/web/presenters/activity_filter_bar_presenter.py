from __future__ import annotations

from papyrus.interfaces.web.urls import activity_url
from papyrus.interfaces.web.view_helpers import escape


def render_activity_filter_bar(*, role: str, object_id: str | None, selected_group: str) -> str:
    return (
        f'<form class="activity-filter-bar" method="get" action="{escape(activity_url(role))}" data-component="activity-filter-bar" data-surface="activity">'
        f'<input type="text" name="object_id" placeholder="Filter object ID" value="{escape(object_id or "")}" />'
        '<select name="group">'
        f'<option value=""{" selected" if not selected_group else ""}>All activity groups</option>'
        f'<option value="service_changes"{" selected" if selected_group == "service_changes" else ""}>Service changes</option>'
        f'<option value="evidence_degradation"{" selected" if selected_group == "evidence_degradation" else ""}>Evidence degradation</option>'
        f'<option value="validation_failures"{" selected" if selected_group == "validation_failures" else ""}>Validation failures</option>'
        f'<option value="manual_suspect_marks"{" selected" if selected_group == "manual_suspect_marks" else ""}>Manual suspect marks</option>'
        "</select>"
        '<button class="button button-primary" type="submit">Show activity</button>'
        "</form>"
    )
