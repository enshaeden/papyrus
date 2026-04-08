# Knowledge Object Lifecycle

Papyrus is moving from a single article lifecycle to a split model that separates object lifecycle, revision review state, and trust posture.

## Transition Note

Current canonical source files still carry the legacy four-state source status:

1. `draft`
2. `active`
3. `deprecated`
4. `archived`

That compatibility model remains in force until typed object schemas and review workflows are fully introduced.

## Target Lifecycle Model

### Knowledge Object Lifecycle

- `draft`: object exists but is not approved for operational reliance.
- `active`: current approved object for operational use.
- `deprecated`: still visible, but no longer preferred.
- `archived`: retained for history or audit and excluded from default operational views.

### Revision Review Lifecycle

- `draft`: editable working revision.
- `in_review`: submitted for formal review.
- `approved`: accepted revision and eligible to become current.
- `rejected`: review completed without approval.
- `superseded`: previously approved revision replaced by a newer approved revision.

### Trust Posture

Trust posture is orthogonal to lifecycle:

- `trusted`: approved and supported by healthy evidence.
- `suspect`: a dependency, citation, or related service change may have invalidated it.
- `stale`: review cadence has elapsed.
- `weak_evidence`: supporting citations are missing, broken, or degraded.

## Archival Rules

- Archive instead of silently overwriting or deleting retired source.
- Preserve object identity and revision history when archival support is added to the runtime model.
- If a replacement exists, record it explicitly instead of relying on implicit title succession.
