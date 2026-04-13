from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_DIR = ROOT / "knowledge"
ARCHIVE_KNOWLEDGE_DIR = ROOT / "archive" / "knowledge"
DOCS_DIR = ROOT / "docs"
DECISIONS_DIR = ROOT / "decisions"
TEMPLATE_DIR = ROOT / "templates"
GENERATED_DIR = ROOT / "generated"
GENERATED_SITE_DOCS_DIR = GENERATED_DIR / "site_docs"
GENERATED_ROUTE_MAP_JSON_PATH = GENERATED_DIR / "route-map.json"
GENERATED_ROUTE_MAP_MARKDOWN_PATH = GENERATED_DIR / "route-map.md"
LEGACY_GENERATED_DOCS_DIR = DOCS_DIR / "generated"
REPORTS_DIR = ROOT / "reports"
ARTICLE_SCHEMA_PATH = ROOT / "schemas" / "article.yml"
OBJECT_SCHEMA_DIR = ROOT / "schemas" / "knowledge_objects"
POLICY_PATH = ROOT / "schemas" / "repository_policy.yml"
TAXONOMY_DIR = ROOT / "taxonomies"
BUILD_DIR = ROOT / "build"
SITE_DIR = ROOT / "site"
DB_PATH = BUILD_DIR / "knowledge.db"
SYSTEM_DESIGN_DOCS_SITE_ROOT = Path("system-design-docs")
GENERATED_SITE_INDEX_PATHS = (
    "index.md",
    "knowledge/index.md",
    "knowledge/start-here.md",
    "knowledge/support.md",
    "knowledge/explorer.md",
    "knowledge/tree.md",
    "knowledge/by-type.md",
    "knowledge/by-audience.md",
    "knowledge/by-service.md",
    "knowledge/by-system.md",
    "knowledge/by-tag.md",
    "knowledge/by-team.md",
    "knowledge/by-lifecycle.md",
    "archive/index.md",
)
GENERATED_SITE_ASSET_PATHS = (
    "system-design-docs/assets/site.css",
    "system-design-docs/assets/knowledge-explorer.js",
)
GENERATED_ROUTE_MAP_PATHS = (
    "generated/route-map.json",
    "generated/route-map.md",
)
FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PLACEHOLDER_PATTERN = re.compile(r"^<[A-Z0-9_]+>$")
BARE_PLACEHOLDER_PATTERN = re.compile(r"^[A-Z0-9_]+$")
HTML_HREF_PATTERN = re.compile(r"""href=["']([^"']+)["']""", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+\d{1,3}[ -]?)?(?:\(\d{3}\)|\d{3})[ -]\d{3}[ -]\d{4}\b")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+[A-Za-z0-9][A-Za-z0-9 .'-]{1,40}\s"
    r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl)\b",
    re.IGNORECASE,
)
DOMAIN_PATTERN = re.compile(
    r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\.(?:com|net|org|io|local|internal|corp|lan|private)\b",
    re.IGNORECASE,
)
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|token|client[_ -]?secret|password|passphrase|recovery[_ -]?code)\b"
        r"[^\n]{0,20}[:=][ \t]*['\"]?[A-Za-z0-9/_+=.-]{8,}"
    ),
]
BRANDED_ADMIN_PATTERNS = [
    re.compile(r"\badmin console\b", re.IGNORECASE),
    re.compile(r"\badmin center\b", re.IGNORECASE),
]
LIKELY_BRANDED_PRODUCT_PATTERN = re.compile(
    r"\b(?:[A-Z][a-z0-9]+(?:[ -][A-Z][a-z0-9]+){0,2})\s"
    r"(?:Platform|Suite|Portal|Cloud|Workspace|Center|Console|Directory)\b"
)
OPERATIONAL_HEADING_PATTERN = re.compile(
    r"^#{1,6}\s+(Prerequisites|Steps|Verification|Rollback)\b",
    re.IGNORECASE | re.MULTILINE,
)
DOCS_OPERATOR_LANGUAGE_PATTERNS = (
    (
        "standard operating procedure",
        re.compile(r"\b(?:standard operating procedure|SOP)\b", re.IGNORECASE),
    ),
    ("runbook", re.compile(r"\brunbook\b", re.IGNORECASE)),
    ("troubleshooting", re.compile(r"\btroubleshooting\b", re.IGNORECASE)),
    (
        "service desk or operator language",
        re.compile(r"\b(?:service desk|help ?desk|on-call|operator)\b", re.IGNORECASE),
    ),
    (
        "procedural phrasing",
        re.compile(
            r"\b(?:before you begin|follow these steps|perform the following steps|to verify|"
            r"verification steps|rollback steps|escalate to)\b",
            re.IGNORECASE,
        ),
    ),
)
GENERIC_BRAND_ALLOWLIST = {
    "Asset",
    "Business",
    "Cloud",
    "Collaboration",
    "Conferencing",
    "Content",
    "Creative",
    "Developer",
    "Desk",
    "Disconnect",
    "Device",
    "Digital",
    "Directory",
    "Documentation",
    "Endpoint",
    "Enabled",
    "Enrollment",
    "HR",
    "Helpdesk",
    "Identity",
    "Instant",
    "Internal",
    "Knowledge",
    "License",
    "Management",
    "Messaging",
    "Multi-Factor",
    "Migration",
    "New",
    "Password",
    "Printer",
    "Productivity",
    "Remote",
    "Reporting",
    "Seed",
    "Self",
    "Service",
    "Shipping",
    "Support",
    "Ticketing",
    "Video",
    "Workflow",
    "Workspace",
    "Application",
    "Admin",
    "And",
    "VPN",
    "Workplace",
    "Label",
    "Network",
    "Software",
}


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()
