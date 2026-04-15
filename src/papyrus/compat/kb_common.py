from __future__ import annotations

from papyrus.application.impact_flow import (
    docs_knowledge_like_warnings,
    inverse_reference_graph,
    reference_graph,
)
from papyrus.application.impact_flow import (
    documents_missing_list_field as articles_missing_list_field,
)
from papyrus.application.impact_flow import (
    find_possible_duplicate_documents as find_possible_duplicate_articles,
)
from papyrus.application.impact_flow import (
    missing_owner_documents as missing_owner_articles,
)
from papyrus.application.impact_flow import (
    relationless_documents as relationless_articles,
)
from papyrus.application.validation_flow import (
    orphaned_files,
    validate_directory_contract,
    validate_docs_duplication,
    validate_field,
    validate_repository,
    validate_sanitization,
)
from papyrus.application.validation_flow import (
    validate_knowledge_documents as validate_articles,
)
from papyrus.domain.entities import (
    BrokenLink,
    DocsPlacementWarning,
    DuplicateCandidate,
    ValidationIssue,
)
from papyrus.domain.entities import (
    KnowledgeDocument as Article,
)
from papyrus.domain.policies import navigation_statuses, searchable_statuses, status_rank_map
from papyrus.infrastructure.markdown.parser import (
    collect_broken_markdown_links,
    extract_markdown_title,
    is_external_target,
    is_placeholder_target,
    resolve_local_link,
)
from papyrus.infrastructure.markdown.parser import (
    parse_knowledge_document as parse_article,
)
from papyrus.infrastructure.markdown.serializer import (
    date_to_iso,
    ensure_iso_date,
    json_dump,
    normalize_for_similarity,
    normalize_whitespace,
    parse_iso_date,
    render_change_log,
    render_list,
    render_reference,
    similarity_ratio,
    slugify,
)
from papyrus.infrastructure.paths import (
    ADDRESS_PATTERN,
    ARCHIVE_KNOWLEDGE_DIR,
    BARE_PLACEHOLDER_PATTERN,
    BRANDED_ADMIN_PATTERNS,
    BUILD_DIR,
    DATE_PATTERN,
    DB_PATH,
    DECISIONS_DIR,
    DOCS_DIR,
    DOCS_OPERATOR_LANGUAGE_PATTERNS,
    DOMAIN_PATTERN,
    EMAIL_PATTERN,
    FRONT_MATTER_PATTERN,
    GENERATED_DIR,
    GENERIC_BRAND_ALLOWLIST,
    IP_PATTERN,
    KNOWLEDGE_DIR,
    LEGACY_GENERATED_DOCS_DIR,
    LIKELY_BRANDED_PRODUCT_PATTERN,
    MARKDOWN_LINK_PATTERN,
    OPERATIONAL_HEADING_PATTERN,
    PHONE_PATTERN,
    PLACEHOLDER_PATTERN,
    POLICY_PATH,
    REPORTS_DIR,
    ROOT,
    TAXONOMY_DIR,
    TEMPLATE_DIR,
    relative_path,
)
from papyrus.infrastructure.paths import (
    ARTICLE_SCHEMA_PATH as SCHEMA_PATH,
)
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_article_paths,
    collect_decision_paths,
    collect_docs_source_paths,
    collect_root_markdown_paths,
    collect_sanitization_paths,
    load_articles,
    load_knowledge_documents,
    load_policy,
    load_schema,
    load_taxonomies,
    load_yaml_file,
)
from papyrus.infrastructure.repositories.knowledge_repo import (
    knowledge_source_roots as article_roots,
)
from papyrus.infrastructure.search.indexer import (
    fts5_available,
    summarize_for_search,
)
from papyrus.jobs.stale_scan import cadence_to_days
from papyrus.jobs.stale_scan import stale_documents as stale_articles

__all__ = [name for name in globals() if not name.startswith("_")]
