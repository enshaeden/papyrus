# Route Map

Derived from the registered Papyrus web routes. Do not edit by hand.

| Methods | Pattern | Role Group | Owner |
| --- | --- | --- | --- |
| `GET` | `/` | `shared` | `papyrus.interfaces.web.routes.home.root_landing` |
| `GET` | `/admin` | `admin` | `papyrus.interfaces.web.routes.home.admin_landing` |
| `GET` | `/admin/audit` | `admin` | `papyrus.interfaces.web.routes.manage.audit_page` |
| `GET` | `/admin/governance` | `admin` | `papyrus.interfaces.web.routes.dashboard.oversight_dashboard_page` |
| `GET` | `/admin/impact/object/{object_id}` | `admin` | `papyrus.interfaces.web.routes.impact.object_impact_page` |
| `GET` | `/admin/impact/service/{service_id}` | `admin` | `papyrus.interfaces.web.routes.impact.service_impact_page` |
| `GET` | `/admin/inspect` | `admin` | `papyrus.interfaces.web.routes.queue.queue_page` |
| `GET` | `/admin/inspect/object/{object_id}` | `admin` | `papyrus.interfaces.web.routes.objects.object_detail_page` |
| `GET` | `/admin/inspect/object/{object_id}/revisions` | `admin` | `papyrus.interfaces.web.routes.objects.object_revision_history_page` |
| `GET` | `/admin/overview` | `admin` | `papyrus.interfaces.web.routes.home.home_page` |
| `GET` | `/admin/review` | `admin` | `papyrus.interfaces.web.routes.manage.review_queue_page` |
| `GET, POST` | `/admin/review/object/{object_id}/archive` | `admin` | `papyrus.interfaces.web.routes.manage.object_archive_page` |
| `GET, POST` | `/admin/review/object/{object_id}/evidence/revalidate` | `admin` | `papyrus.interfaces.web.routes.manage.evidence_revalidation_page` |
| `GET, POST` | `/admin/review/object/{object_id}/supersede` | `admin` | `papyrus.interfaces.web.routes.manage.object_supersede_page` |
| `GET, POST` | `/admin/review/object/{object_id}/suspect` | `admin` | `papyrus.interfaces.web.routes.manage.object_suspect_page` |
| `GET, POST` | `/admin/review/object/{object_id}/{revision_id}` | `admin` | `papyrus.interfaces.web.routes.manage.review_decision_page` |
| `GET, POST` | `/admin/review/object/{object_id}/{revision_id}/assign` | `admin` | `papyrus.interfaces.web.routes.manage.review_assignment_page` |
| `GET` | `/admin/services` | `admin` | `papyrus.interfaces.web.routes.services.service_catalog_page` |
| `GET` | `/admin/services/{service_id}` | `admin` | `papyrus.interfaces.web.routes.services.service_detail_page` |
| `GET` | `/admin/validation-runs` | `admin` | `papyrus.interfaces.web.routes.manage.validation_runs_page` |
| `GET, POST` | `/admin/validation-runs/new` | `admin` | `papyrus.interfaces.web.routes.manage.validation_run_new_page` |
| `GET` | `/operator` | `operator` | `papyrus.interfaces.web.routes.home.home_page` |
| `GET, POST` | `/operator/import` | `operator` | `papyrus.interfaces.web.routes.ingest.ingest_list_page` |
| `GET` | `/operator/import/{ingestion_id}` | `operator` | `papyrus.interfaces.web.routes.ingest.ingest_detail_page` |
| `GET, POST` | `/operator/import/{ingestion_id}/review` | `operator` | `papyrus.interfaces.web.routes.ingest.ingest_review_page` |
| `GET` | `/operator/read` | `operator` | `papyrus.interfaces.web.routes.queue.queue_page` |
| `GET` | `/operator/read/object/{object_id}` | `operator` | `papyrus.interfaces.web.routes.objects.object_detail_page` |
| `GET` | `/operator/read/object/{object_id}/revisions` | `operator` | `papyrus.interfaces.web.routes.objects.object_revision_history_page` |
| `GET` | `/operator/read/services` | `operator` | `papyrus.interfaces.web.routes.services.service_catalog_page` |
| `GET` | `/operator/read/services/{service_id}` | `operator` | `papyrus.interfaces.web.routes.services.service_detail_page` |
| `GET` | `/operator/review` | `operator` | `papyrus.interfaces.web.routes.manage.review_queue_page` |
| `GET` | `/operator/review/activity` | `operator` | `papyrus.interfaces.web.routes.manage.audit_page` |
| `GET` | `/operator/review/governance` | `operator` | `papyrus.interfaces.web.routes.dashboard.oversight_dashboard_page` |
| `GET` | `/operator/review/impact/object/{object_id}` | `operator` | `papyrus.interfaces.web.routes.impact.object_impact_page` |
| `GET` | `/operator/review/impact/service/{service_id}` | `operator` | `papyrus.interfaces.web.routes.impact.service_impact_page` |
| `GET, POST` | `/operator/review/object/{object_id}/archive` | `operator` | `papyrus.interfaces.web.routes.manage.object_archive_page` |
| `GET, POST` | `/operator/review/object/{object_id}/evidence/revalidate` | `operator` | `papyrus.interfaces.web.routes.manage.evidence_revalidation_page` |
| `GET, POST` | `/operator/review/object/{object_id}/supersede` | `operator` | `papyrus.interfaces.web.routes.manage.object_supersede_page` |
| `GET, POST` | `/operator/review/object/{object_id}/suspect` | `operator` | `papyrus.interfaces.web.routes.manage.object_suspect_page` |
| `GET, POST` | `/operator/review/object/{object_id}/{revision_id}` | `operator` | `papyrus.interfaces.web.routes.manage.review_decision_page` |
| `GET, POST` | `/operator/review/object/{object_id}/{revision_id}/assign` | `operator` | `papyrus.interfaces.web.routes.manage.review_assignment_page` |
| `GET` | `/operator/review/validation-runs` | `operator` | `papyrus.interfaces.web.routes.manage.validation_runs_page` |
| `GET, POST` | `/operator/review/validation-runs/new` | `operator` | `papyrus.interfaces.web.routes.manage.validation_run_new_page` |
| `GET, POST` | `/operator/write/advanced` | `operator` | `papyrus.interfaces.web.routes.write_object.create_advanced_object_page` |
| `GET` | `/operator/write/citations/search` | `operator` | `papyrus.interfaces.web.routes.write_search.citation_search_endpoint` |
| `GET, POST` | `/operator/write/new` | `operator` | `papyrus.interfaces.web.routes.write_object.create_primary_object_page` |
| `GET, POST` | `/operator/write/object/{object_id}` | `operator` | `papyrus.interfaces.web.routes.write_guided.create_revision_page` |
| `POST` | `/operator/write/object/{object_id}/start` | `operator` | `papyrus.interfaces.web.routes.write_guided.start_revision` |
| `GET, POST` | `/operator/write/object/{object_id}/submit` | `operator` | `papyrus.interfaces.web.routes.write_submit.submit_revision_page` |
| `GET` | `/operator/write/objects/search` | `operator` | `papyrus.interfaces.web.routes.write_search.related_object_search_endpoint` |
| `GET` | `/reader` | `reader` | `papyrus.interfaces.web.routes.home.reader_landing` |
| `GET` | `/reader/browse` | `reader` | `papyrus.interfaces.web.routes.queue.queue_page` |
| `GET` | `/reader/object/{object_id}` | `reader` | `papyrus.interfaces.web.routes.objects.object_detail_page` |
