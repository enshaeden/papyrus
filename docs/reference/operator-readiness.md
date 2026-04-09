# Operator Readiness

This document records the v1.5 lifecycle-guided pass. Papyrus remains a governed local-first operational knowledge control plane, but the product framing now emphasizes guided work, next actions, lifecycle progression, and stewardship instead of presenting governance metadata as the primary experience.

## What This Pass Accomplished

- Reframed the product model around the lifecycle of operational knowledge:
  - draft
  - revise
  - review
  - approve
  - use
  - revalidate
  - supersede or archive
- Added a real home page with:
  - primary work areas
  - outstanding work counts
  - recent activity
  - actor-specific next actions
- Changed top-level navigation to:
  - `Read`
  - `Write`
  - `Review / Approvals`
  - `Knowledge Health`
  - `Services`
  - `Activity / History`
- Reworked read surfaces so object detail and search results answer:
  - what this is
  - when to use it
  - whether it is safe now
  - what changed recently
  - what to do next if it is not safe or current
- Reworked write surfaces so guided authoring shows:
  - progress through the draft flow
  - required versus optional work
  - validation blockers versus warnings
  - lifecycle context and publication outcome
- Reworked review and manage surfaces so stewardship work is grouped as:
  - ready for review
  - needs decision
  - needs revalidation
  - weak evidence
  - recently changed
  - superseded guidance still in view
- Added source-sync preview and conflict detection so canonical publication is inspectable before approval or explicit apply.
- Added source-sync recovery through journaled mutation rollback and governed backup restoration.
- Reframed event and impact history around operational consequences instead of raw payload inspection.
- Expanded local actor handling with registry-backed display names, role hints, default actor selection, explicit actor propagation, and self-approval prevention.
- Aligned CLI language with the lifecycle-guided model so queue, health, review, object detail, activity, and validation output describe next actions instead of only raw state.

## Product Decisions

- Governance remains visible as a guardrail, not the lead headline on every primary screen.
- Read surfaces lead with safe use, freshness, service context, and recent change.
- Write surfaces lead with progress and readiness to submit.
- Review surfaces lead with decision support and downstream effect.
- Knowledge health is separate from approval work.
- Activity and history explain what happened, what it affected, and what should happen next.
- Source sync is explicit, inspectable, and recoverable, but Papyrus only claims safety within the configured canonical roots and local ingest allowlist.
- Actor attribution is lightweight and local-first. This pass does not introduce enterprise authentication.

## Recovery And Inspection

- Inspect a pending or approved writeback:

```bash
python3 scripts/source_sync.py preview --object <object_id>
```

- Apply explicit source writeback:

```bash
python3 scripts/source_sync.py writeback --object <object_id>
```

- Restore the most recent backed-up canonical state:

```bash
python3 scripts/source_sync.py restore-last --object <object_id>
```

- Review recent operational consequences:

```bash
python3 scripts/operator_view.py activity --db build/knowledge.db
```

## Current Boundary

In scope after this pass:

- lifecycle-guided web UX
- lifecycle-aligned CLI wording
- stewardship-oriented review and knowledge-health surfaces
- inspectable writeback preview, conflict detection, and recovery
- consequence-oriented event and impact presentation
- lightweight local actor accountability

Still deferred after this pass:

- enterprise auth and RBAC
- realtime collaboration
- notifications and subscriptions
- advanced diffs
- external integrations
- connectors to external systems
- LLM, AI, embeddings, or vector infrastructure

## Dependencies And Operational Risk

- No new third-party dependencies were introduced.
- Source of truth remains canonical Markdown under `knowledge/` and `archive/knowledge/`.
- Derived output remains non-authoritative.
- Governed mutation policy now terminates in `papyrus.domain.lifecycle`, `papyrus.application.policy_authority`, and `papyrus.infrastructure.transactional_mutation`. CLI, API, and web actions call those flows instead of each surface owning path or lifecycle checks.
- Some read surfaces still expose compatibility aliases such as `status` and `approval_state` alongside the explicit lifecycle fields. Those aliases are not the authoritative mutation contract.

## Rollback Reference

- If the runtime is unavailable, rebuild it with `python3 scripts/build_index.py`.
- If a revision should not become canonical, do not bypass the workflow; use rejection or do not approve it.
- If canonical writeback needs recovery after approval, use `scripts/source_sync.py restore-last` so the restore is recorded in audit history.
