# Runtime Role Context and Access Resolution

Scope: Request-scoped role context, local runtime role selection, route access enforcement, and dev-only experience switching

## Purpose

This record defines how Papyrus establishes and uses role context at runtime.

Use it when changing:

- request entrypoints
- web runtime role selection
- route guards
- visibility enforcement
- navigation generation
- search visibility
- local development role switching
- future authentication or authorization integration

This record exists because Papyrus uses one production shell and one shared route space.
Shared routes require a canonical non-path source of role context.
Path prefixes, route namespaces, or template branching must not be the authority for runtime role identity.

## Decision

Papyrus MUST resolve a canonical request-scoped role context for every interactive runtime request.

That context is the authority for:

- route access
- navigation visibility
- action visibility
- panel visibility
- related-link visibility
- search visibility
- workflow control visibility

Papyrus MUST NOT infer the active production role from path prefix alone.

Papyrus MAY continue to support development-only actor or role switching, but that mechanism is not production authority and must not define production route architecture.

## Core rules

- Production role context is request-scoped.
- Production role context is resolved before route handling and template composition.
- Route identity is canonical and shared.
- Role controls what is visible and what is allowed on a route.
- Direct access to a route or action that is not allowed for the resolved role MUST fail closed.
- Templates, presenters, and page-local helpers MUST consume canonical request context rather than independently inferring role from URL shape.
- Path prefixes may remain temporarily during migration, but they are not the governing source of role identity.
- Development switching is allowed only as a local/runtime convenience and must be explicitly marked as non-production.
- Future authentication or persistent user-role assignment may replace the local role source without changing the request-context contract.

## Canonical request context model

Each request MUST resolve an access context with at least:

- `principal_id`
- `role`
- `capabilities`
- `is_dev_switchable`
- `role_source`

### Required semantics

- `principal_id`
  - Identifies the current actor, user, or local runtime principal when known.
  - In local development, this may be a synthetic value.
- `role`
  - One of the canonical production roles: `Reader`, `Operator`, `Admin`.
- `capabilities`
  - Derived permissions for the current request.
  - Capability evaluation may initially be coarse and role-based.
- `is_dev_switchable`
  - Indicates whether the current runtime allows dev-only role switching.
- `role_source`
  - Records how the role was established, such as `session`, `dev_override`, `config_default`, or future `identity_provider`.

## Resolution order for local runtime

Until Papyrus ships a production authentication and authorization system, local runtime MUST resolve role context in this order:

1. explicit dev-only session role selection, if enabled
2. explicit dev-only request override, if enabled for local runtime
3. configured local default role
4. safe fallback role

### Safe fallback role

The safe fallback role MUST be `Reader` unless an explicit local-development configuration intentionally chooses a higher default for operator development.

A higher default MAY be permitted in local development, but it must be clearly configuration-driven and not silently inferred.

## Production stance

Production runtime MUST NOT expose user-facing role switching.

Production runtime MUST obtain role context from the authenticated principal and access policy layer once that exists.

Until that system exists, Papyrus should treat local role resolution as a development/runtime mechanism only.

## Capability model

Papyrus does not need full RBAC to satisfy this contract.

The minimum required model is:

- canonical production role
- derived request capabilities
- route and action minimum-role declarations
- fail-closed enforcement

Capabilities may initially map directly from role.
A finer-grained policy layer may be added later without changing the shared-route model.

## Route and action enforcement

Each route MUST declare a minimum visible role.

Each sensitive action MUST declare a minimum permitted role.

Each search result type and related-link type MUST declare a minimum visible role.

Enforcement MUST occur before render or action execution.

If the current request role is insufficient:

- navigation entry is absent
- search result is absent
- related link is absent
- control is absent
- direct access fails closed

Hidden means absent, not disabled, unless a later decision explicitly requires visible-but-disabled affordances for a narrowly defined reason.

## Navigation and presentation rules

Navigation generation MUST derive from:

- canonical shared route definitions
- resolved request role
- route visibility contracts

Navigation MUST NOT derive from:

- separate role-owned route trees
- path-prefix inference
- page-local ad hoc role checks

Templates and presenters MUST read the resolved request context from a canonical request-scoped source.

They MUST NOT treat URL prefix as the authority for deciding what role is active.

## Search and discovery rules

Global search, command surfaces, recent destinations, related links, and recommendation surfaces MUST use the resolved request role and capability set.

A user MUST NOT receive discoverable access to destinations they cannot open.

Search filtering is an access rule, not only a presentation choice.

## Development-only switching rules

Papyrus MAY provide a dev-only role switcher for local runtime.

If present, it MUST follow these rules:

- clearly marked development-only
- never the production authority model
- does not justify separate production route trees
- writes to a canonical local role source such as session state
- resolves through the same request-context mechanism used by ordinary requests

Development actors such as `local.operator`, `local.reviewer`, and `local.manager` MAY remain as convenience inputs during transition, but they MUST resolve into canonical production roles and MUST NOT define permanent production experience architecture.

## Migration rules

During migration from path-owned experience routing to shared-route role-conditioned access:

- introduce canonical request-scoped role resolution first
- move route guards to request-context enforcement
- move navigation and template visibility to request-context consumption
- remove path-prefix role inference as governing logic
- retain temporary compatibility shims only where needed to avoid breaking local workflows
- do not preserve route duplication once shared canonical routes are in place

## Implementation guidance

Papyrus SHOULD implement a dedicated request access context type and resolver.

Typical local-runtime components include:

- access context dataclass
- role resolver
- request bootstrap or middleware hook
- route guard helper
- visibility helper layer consuming request context
- dev-only switch endpoint or session setter when enabled

Preferred shape:

- resolve once per request
- attach to request context
- consume everywhere from that context
- keep role selection separate from route identity

## Consequences

### Positive

- aligns runtime with shared-route architecture
- prevents path naming from becoming de facto authorization
- gives Codex and maintainers one canonical model to implement against
- creates a clean bridge to future authn/authz work
- reduces drift between routes, templates, nav, and search

### Trade-offs

- requires request bootstrap changes
- may require route-definition metadata updates
- may force cleanup of older actor/path assumptions
- may expose inconsistencies in existing AGENTS, tests, and route maps

## Repository alignment actions

When adopting this decision, update as needed:

- runtime entrypoints
- request bootstrap/middleware
- route guard helpers
- visibility helpers
- navigation generation
- search projection
- related-link projection
- web templates and presenters
- AGENTS files that still prescribe role-owned route groups
- tests that assume role comes from path structure

## Non-goals

This record does not require:

- a full enterprise RBAC system
- external identity provider integration
- per-user persistent administration UI
- complete capability decomposition on day one

It establishes the minimum correct runtime contract needed for shared-route role-conditioned access.
