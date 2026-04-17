# Route Map

Derived from the registered Papyrus web routes. Do not edit by hand.

| Methods | Pattern | Minimum Role | Owner |
| --- | --- | --- | --- |
| `GET` | `/` | `reader` | `papyrus.interfaces.web.routes.home.root_landing` |
| `GET` | `/admin` | `admin` | `papyrus.interfaces.web.routes.admin.admin_landing` |
| `GET` | `/admin/access` | `admin` | `papyrus.interfaces.web.routes.admin.access_page` |
| `GET` | `/admin/audit` | `admin` | `papyrus.interfaces.web.routes.manage.<lambda>` |
| `GET` | `/admin/overview` | `admin` | `papyrus.interfaces.web.routes.admin.overview_page` |
| `GET` | `/admin/schemas` | `admin` | `papyrus.interfaces.web.routes.admin.schemas_page` |
| `GET` | `/admin/settings` | `admin` | `papyrus.interfaces.web.routes.admin.settings_page` |
| `GET` | `/admin/spaces` | `admin` | `papyrus.interfaces.web.routes.admin.spaces_page` |
| `GET` | `/admin/templates` | `admin` | `papyrus.interfaces.web.routes.admin.templates_page` |
| `GET` | `/admin/users` | `admin` | `papyrus.interfaces.web.routes.admin.users_page` |
| `GET` | `/governance` | `operator` | `papyrus.interfaces.web.routes.dashboard.oversight_dashboard_page` |
| `GET` | `/governance/services` | `operator` | `papyrus.interfaces.web.routes.services.service_catalog_page` |
| `GET` | `/governance/services/{service_id}` | `operator` | `papyrus.interfaces.web.routes.services.service_detail_page` |
| `GET, POST` | `/import` | `operator` | `papyrus.interfaces.web.routes.ingest.ingest_list_page` |
| `GET` | `/import/{ingestion_id}` | `operator` | `papyrus.interfaces.web.routes.ingest.ingest_detail_page` |
| `GET, POST` | `/import/{ingestion_id}/review` | `operator` | `papyrus.interfaces.web.routes.ingest.ingest_review_page` |
| `GET` | `/read` | `reader` | `papyrus.interfaces.web.routes.queue.queue_page` |
| `GET` | `/read/object/{object_id}` | `reader` | `papyrus.interfaces.web.routes.objects.object_detail_page` |
| `GET` | `/read/object/{object_id}/revisions` | `operator` | `papyrus.interfaces.web.routes.objects.object_revision_history_page` |
| `GET` | `/review` | `operator` | `papyrus.interfaces.web.routes.manage.review_queue_page` |
| `GET` | `/review/activity` | `operator` | `papyrus.interfaces.web.routes.manage.audit_page` |
| `GET` | `/review/impact/object/{object_id}` | `operator` | `papyrus.interfaces.web.routes.impact.object_impact_page` |
| `GET` | `/review/impact/service/{service_id}` | `operator` | `papyrus.interfaces.web.routes.impact.service_impact_page` |
| `GET, POST` | `/review/object/{object_id}/archive` | `operator` | `papyrus.interfaces.web.routes.manage.object_archive_page` |
| `GET, POST` | `/review/object/{object_id}/evidence/revalidate` | `operator` | `papyrus.interfaces.web.routes.manage.evidence_revalidation_page` |
| `GET, POST` | `/review/object/{object_id}/supersede` | `operator` | `papyrus.interfaces.web.routes.manage.object_supersede_page` |
| `GET, POST` | `/review/object/{object_id}/suspect` | `operator` | `papyrus.interfaces.web.routes.manage.object_suspect_page` |
| `GET, POST` | `/review/object/{object_id}/{revision_id}` | `operator` | `papyrus.interfaces.web.routes.manage.review_decision_page` |
| `GET, POST` | `/review/object/{object_id}/{revision_id}/assign` | `operator` | `papyrus.interfaces.web.routes.manage.review_assignment_page` |
| `GET` | `/review/validation-runs` | `operator` | `papyrus.interfaces.web.routes.manage.validation_runs_page` |
| `GET, POST` | `/review/validation-runs/new` | `operator` | `papyrus.interfaces.web.routes.manage.validation_run_new_page` |
| `GET` | `/write` | `operator` | `papyrus.interfaces.web.routes.write_object.write_landing_page` |
| `GET` | `/write/citations/search` | `operator` | `papyrus.interfaces.web.routes.write_search.citation_search_endpoint` |
| `GET, POST` | `/write/new` | `operator` | `papyrus.interfaces.web.routes.write_object.create_primary_object_page` |
| `GET, POST` | `/write/object/{object_id}` | `operator` | `papyrus.interfaces.web.routes.write_guided.create_revision_page` |
| `POST` | `/write/object/{object_id}/start` | `operator` | `papyrus.interfaces.web.routes.write_guided.start_revision` |
| `GET, POST` | `/write/object/{object_id}/submit` | `operator` | `papyrus.interfaces.web.routes.write_submit.submit_revision_page` |
| `GET` | `/write/objects/search` | `operator` | `papyrus.interfaces.web.routes.write_search.related_object_search_endpoint` |
