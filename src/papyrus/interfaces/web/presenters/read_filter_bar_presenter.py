from __future__ import annotations

from papyrus.interfaces.web.urls import search_url
from papyrus.interfaces.web.view_helpers import escape


def render_read_filter_bar(
    *, role: str, query: str, selected_type: str, selected_trust: str, selected_review_state: str
) -> str:
    return (
        f'<form class="read-filter-bar" method="get" action="{escape(search_url(role))}" data-component="read-filter-bar" data-surface="read-queue">'
        '<div class="read-filter-bar__search">'
        f'<input type="search" name="query" placeholder="Search by title, path, service, or summary" value="{escape(query)}" />'
        '<button class="button button-primary" type="submit">Search</button>'
        "</div>"
        '<div class="read-filter-bar__row">'
        '<label><span>Type</span><select name="object_type">'
        f'<option value=""{" selected" if not selected_type else ""}>All</option>'
        f'<option value="runbook"{" selected" if selected_type == "runbook" else ""}>Runbook</option>'
        f'<option value="known_error"{" selected" if selected_type == "known_error" else ""}>Known error</option>'
        f'<option value="service_record"{" selected" if selected_type == "service_record" else ""}>Service record</option>'
        f'<option value="policy"{" selected" if selected_type == "policy" else ""}>Policy</option>'
        f'<option value="system_design"{" selected" if selected_type == "system_design" else ""}>System design</option>'
        "</select></label>"
        '<label><span>Trust</span><select name="trust">'
        f'<option value=""{" selected" if not selected_trust else ""}>Any</option>'
        f'<option value="trusted"{" selected" if selected_trust == "trusted" else ""}>Trusted</option>'
        f'<option value="weak_evidence"{" selected" if selected_trust == "weak_evidence" else ""}>Weak evidence</option>'
        f'<option value="stale"{" selected" if selected_trust == "stale" else ""}>Stale</option>'
        f'<option value="suspect"{" selected" if selected_trust == "suspect" else ""}>Suspect</option>'
        "</select></label>"
        '<label><span>Review</span><select name="review_state">'
        f'<option value=""{" selected" if not selected_review_state else ""}>Any</option>'
        f'<option value="approved"{" selected" if selected_review_state == "approved" else ""}>Approved</option>'
        f'<option value="in_review"{" selected" if selected_review_state == "in_review" else ""}>In review</option>'
        f'<option value="draft"{" selected" if selected_review_state == "draft" else ""}>Draft</option>'
        f'<option value="rejected"{" selected" if selected_review_state == "rejected" else ""}>Rejected</option>'
        "</select></label>"
        "</div></form>"
    )
