# Content Lifecycle

Papyrus uses a four-state lifecycle:

1. `draft`
2. `active`
3. `deprecated`
4. `archived`

## Draft

- Incomplete or under review.
- Not the preferred operational reference.
- Must still carry owner and review metadata.

## Active

- Approved for operational use.
- Must have current review metadata.
- Included in default navigation and default search results.

## Deprecated

- Still available temporarily but not preferred.
- Must include `replaced_by` or `retirement_reason`.
- Included in default navigation and default search results with lower preference than `active`.

## Archived

- Retained for history or audit purposes.
- Must live under `archive/knowledge/`.
- Must include `retirement_reason`.
- Excluded from default navigation and default search.

## Archival Rules

- Archive instead of silently overwriting or deleting retired source content.
- Preserve metadata and change history when moving an item to `archive/knowledge/`.
- If a replacement exists, declare it explicitly in `replaced_by`.
