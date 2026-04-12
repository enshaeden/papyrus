# Role and Visibility Matrix

Status: Approved
Owner: Product / UX / Architecture
Scope: Web UI, app UI, search visibility, object actions, governance exposure

## Roles
- Reader
- Operator
- Admin

## Global visibility rules
- Anything not explicitly granted to a role is absent from the UI for that role.
- Hidden means not rendered, not merely disabled.
- Search results must respect the same visibility constraints as navigation and direct routes.
- Production must not expose any role switcher or client-side mode switch capability.

## Experience matrix

| Surface / Capability | Reader | Operator | Admin | Notes |
|---|---:|---:|---:|---|
| Global search bar | Yes | Yes | Yes | Results filtered by role visibility |
| Account/system menu | Yes | Yes | Yes | Menu entries differ by role if needed |
| Dev-only role switcher | Dev only | Dev only | Dev only | Never in production |
| Left navigation | Reader-only items | Operator-only items | Admin-only items | No cross-role leakage |
| Reader tree navigation | Yes | Yes in Read | Optional inspect only | Admin may access object inspection separately |
| Read document view | Yes | Yes | Yes | Admin for inspection, not primary experience |
| Right contextual governance panel | Limited | Expanded | Expanded or admin-specific | Content differs by role |
| Flag for review action | Yes | Yes | Yes | Admin may also create flags if desired |
| View full flag details | No | Yes | Yes | Reader sees only their submission affordance |
| Resolve flag | No | Yes if authorised | Yes | Policy-controlled |
| Open object in Write | No | Yes | Optional override | Keep explicit if Admin inherits |
| Write workspace | No | Yes | Optional limited / full | Must be an explicit decision |
| Review queue | No | Yes | Yes | Admin may have oversight queue |
| Publish action | No | Conditional | Yes | Depends on publish policy |
| Templates | No | Read/use only if needed | Yes | Operators should not alter templates unless explicitly allowed |
| Schemas | No | No or limited inspect | Yes | Strong admin boundary |
| Users and roles admin | No | No | Yes | Admin-only |
| Spaces/access admin | No | No | Yes | Admin-only |
| Audit log | No | Limited object history | Yes | Distinguish local history from system audit |
| System settings | No | No | Yes | Admin-only |

## Reader pages

| Page / Panel / Action / Metadata | Reader visibility | Notes |
|---|---|---|
| Home / landing | Yes | Reader-specific, content-led |
| Tree navigation | Yes | Primary navigation model |
| Object read page | Yes | Primary task surface |
| Related objects | Yes | Safe linked discovery |
| Governance summary panel | Yes, limited | Owner, status, last review, scope |
| Flag submission dialog | Yes | Required comment |
| Full governance history | No | Too operational |
| Draft state | No | Hidden entirely |
| Review queues | No | Hidden entirely |
| Publish controls | No | Hidden entirely |

## Operator pages

| Page / Panel / Action / Metadata | Operator visibility | Notes |
|---|---|---|
| Read | Yes | Mirrors Reader document consumption |
| Write | Yes | Structured authoring workflow |
| Review | Yes | Queue-based work surface |
| Open in Write | Yes | From object read page |
| Validation panel | Yes | In Write |
| Version compare | Yes | In Write / Review |
| Flag queue | Yes | In Review |
| Resolve / reassign / escalate | Yes, policy-controlled | Review actions |
| Template usage | Yes | Use template, not necessarily modify |
| Template admin | No by default | Keep boundary clean |

## Admin pages

| Page / Panel / Action / Metadata | Admin visibility | Notes |
|---|---|---|
| Admin overview | Yes | Control-plane entry |
| Users and Roles | Yes | Admin-only |
| Spaces and Access | Yes | Admin-only |
| Templates | Yes | Admin-only by default |
| Schemas | Yes | Admin-only |
| Governance settings | Yes | Workflow and policy controls |
| Publishing controls | Yes | Release policy and override |
| Audit log | Yes | Full system audit |
| System settings | Yes | Admin-only |

## Explicit non-visibility rules
- Reader must never see Write, Review, Template, Schema, Admin, Publish, or User Management controls.
- Operator must never see User Management, Access Management, Schema Administration, or System Settings unless explicitly elevated.
- Admin must not inherit Operator workflows by accident. Any Admin access to Write or Review must be deliberate and documented.