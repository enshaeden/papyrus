# Sanitization Report

## Scope

- Reviewed all non-draft migrated source content selected into the KMDB seed set.
- Sanitized canonical articles, collection indexes, templates, taxonomies, decisions, architecture/governance docs, migration manifests, and generated site examples.
- Rebuilt derived site documentation from sanitized source content only.
- Regenerated migration manifests from the sanitized repository state without retaining reversible source mappings.

## Files Reviewed

- Total reviewed in scope: 224
- `README.md`: 1 file(s)
- `decisions`: 4 file(s)
- `docs`: 2 file(s)
- `docs/architecture`: 3 file(s)
- `docs/migration`: 1 file(s)
- `knowledge/access`: 2 file(s)
- `knowledge/applications`: 45 file(s)
- `knowledge/assets`: 48 file(s)
- `knowledge/governance`: 6 file(s)
- `knowledge/helpdesk`: 14 file(s)
- `knowledge/home`: 1 file(s)
- `knowledge/incidents`: 1 file(s)
- `knowledge/offboarding`: 1 file(s)
- `knowledge/onboarding`: 1 file(s)
- `knowledge/postmortems`: 1 file(s)
- `knowledge/runbooks`: 1 file(s)
- `knowledge/troubleshooting`: 46 file(s)
- `knowledge/user-lifecycle`: 27 file(s)
- `migration`: 4 file(s)
- `schemas`: 2 file(s)
- `taxonomies`: 9 file(s)
- `templates`: 4 file(s)

## Files Changed

- Total changed in scope: 219
- `README.md`: 1 file(s)
- `decisions`: 4 file(s)
- `docs/architecture`: 2 file(s)
- `docs/contributor-workflow.md`: 1 file(s)
- `docs/index.md`: 1 file(s)
- `docs/migration`: 1 file(s)
- `knowledge/access`: 2 file(s)
- `knowledge/applications`: 45 file(s)
- `knowledge/assets`: 48 file(s)
- `knowledge/governance`: 6 file(s)
- `knowledge/helpdesk`: 14 file(s)
- `knowledge/home`: 1 file(s)
- `knowledge/incidents`: 1 file(s)
- `knowledge/offboarding`: 1 file(s)
- `knowledge/onboarding`: 1 file(s)
- `knowledge/postmortems`: 1 file(s)
- `knowledge/runbooks`: 1 file(s)
- `knowledge/troubleshooting`: 46 file(s)
- `knowledge/user-lifecycle`: 27 file(s)
- `migration`: 4 file(s)
- `reports`: 2 file(s)
- `schemas`: 2 file(s)
- `scripts/kb_common.py`: 1 file(s)
- `taxonomies`: 2 file(s)
- `templates`: 4 file(s)

## Files Excluded

- No canonical seed files were excluded from the repository during this pass.
- No binary screenshots, embedded exports, or other non-text seed artifacts exist under `knowledge/`, `migration/`, or `generated/site_docs/` after this pass.

## Placeholder Categories Introduced

- Organization and people: `<COMPANY_NAME>`, `<ROLE_NAME>`, `<TEAM_NAME>`, `<PERSON_NAME>`, `<EMAIL_ADDRESS>`, `<PHONE_NUMBER>`, `<USERNAME>`, `<PASSWORD>`.
- Locations and assets: `<OFFICE_ADDRESS>`, `<SHIPPING_ADDRESS>`, `<OFFICE_SITE_A>` through `<OFFICE_SITE_D>`, `<REGION_A>` through `<REGION_D>`, `<ROOM_NAME_A>` through `<ROOM_NAME_O>`, `<ASSET_TAG>`, `<SERIAL_NUMBER>`.
- Systems and platforms: `<IDENTITY_PROVIDER>`, `<DIRECTORY_SERVICE>`, `<ENDPOINT_MANAGEMENT_PLATFORM>`, `<ENDPOINT_ENROLLMENT_PORTAL>`, `<COLLABORATION_PLATFORM>`, `<MESSAGING_PLATFORM>`, `<VIDEO_CONFERENCING_PLATFORM>`, `<REMOTE_SUPPORT_TOOL>`, `<REMOTE_WORKSPACE_PLATFORM>`, `<VPN_SERVICE>`, `<TICKETING_SYSTEM>`, `<KNOWLEDGE_PORTAL>`.
- Business application placeholders: `<APPLICATION_NAME>`, `<APPLICATION_CATALOG>`, `<BUSINESS_APPLICATION_A>` through `<BUSINESS_APPLICATION_D>`, `<CLOUD_PLATFORM>`, `<CREATIVE_PLATFORM>`, `<DEVELOPER_TOOL_SUITE>`, `<DIGITAL_ASSET_PLATFORM>`, `<PRODUCTIVITY_PLATFORM>`, `<REPORTING_PLATFORM>`, `<PASSWORD_MANAGER>`, `<PASSWORD_MANAGER_VAULT>`, `<PRINTER_MANAGEMENT_PLATFORM>`, `<SHIPPING_CARRIER>`.
- Network, routing, and provenance: `<INTERNAL_URL>`, `<SUPPORT_PORTAL_URL>`, `<REQUEST_FORM_URL>`, `<SUPPLIER_PORTAL_URL>`, `<HOSTNAME>`, `<IP_ADDRESS>`, `<IP_SUBNET>`, `<QUEUE_NAME>`, `<LOCATION_NAME>`, `<OUTAGE_TYPE>`, `<KNOWLEDGE_PORTAL_RECORD_ID>`, `<SOURCE_ARCHIVE_PATH>`, `<SOURCE_ARCHIVE_SHA256>`.

## Removed Content Categories

- Credential-like values, recovery material, and shared-secret examples.
- Internal URLs, internal domains, raw hostnames, IP addresses, and direct portal links.
- Personal names, direct contact details, office addresses, and other identifying location markers.
- Internal team labels, internal workflow names, and company-specific operating references that were not needed to preserve the procedure.
- Vendor names, product names, branded feature names, branded plan names, and branded admin-console language where detectable.
- Legacy export fragments such as raw record notes, copied source IDs, and malformed copied portal excerpts.

## Unresolved Manual Review

- No unresolved text findings remain in the validated source scope.
- Future imports should continue to exclude or replace screenshots, console captures, and other binary artifacts before they enter canonical seed content.
- Some procedures intentionally retain abstract placeholders for office sites, rooms, application names, and workflow variants. That is expected and is preferable to preserving identifying source values.
