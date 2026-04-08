# System Model

Use this page when you need the minimum shared model behind Papyrus. Each rule is defined once here so operators do not have to reconstruct the system from multiple architecture notes.

## Operating Boundary

Papyrus has one authoritative layer and two derived layers:

- Canonical source: Markdown knowledge under `knowledge/` and `archive/knowledge/`
- Runtime: rebuildable relational state used for validation, search, reporting, revision history, trust, and governance views
- Export: approved-content publication output under `generated/` and `site/`

If these layers disagree, canonical source wins and the runtime or export must be rebuilt.

## Reference

| Topic | What It Is | Why It Exists | What Breaks If Misunderstood |
| --- | --- | --- | --- |
| Knowledge object model | Papyrus treats runbooks, known errors, and service records as first-class knowledge objects with stable identity. | Stable identity lets the runtime track revisions, relationships, services, and evidence over time. | Duplicate or forked objects fragment history, trust, and ownership. |
| Revision lifecycle | Revisions move independently of object lifecycle so draft, in-review, approved, rejected, and superseded states can be tracked cleanly. | Review decisions apply to a revision, not to an abstract file snapshot. | Review history becomes ambiguous and operators cannot tell which version was approved. |
| Object lifecycle | Source objects still use `draft`, `active`, `deprecated`, and `archived` lifecycle states. | Lifecycle answers whether the object should appear in normal operational use. | Deprecated or archived guidance may be treated as current, or active guidance may disappear from the wrong views. |
| Trust model | Trust posture is separate from lifecycle and can degrade to `suspect`, `stale`, or `weak_evidence`. | Operators need to know whether current guidance is safe to rely on, not just whether it exists. | Active objects may be used even when evidence is broken, ownership is unclear, or upstream change invalidated them. |
| Citation model | Citations are runtime-tracked evidence records tied to claims and targets, not passive front matter decoration. | Evidence needs to stay inspectable, degradable, and auditable as targets change. | Broken, vague, or migration-era citations can be mistaken for healthy evidence. |
| Variant modeling | Shared procedures should live once, while site or room differences stay in overview pages, access pages, or narrowly scoped exceptions. | A single base procedure reduces drift and keeps local deltas visible without forking the workflow body. | Operators update one site copy and assume the family changed everywhere, leaving hidden divergence in sibling articles. |
| Validation and reporting | Validation enforces schema, taxonomy, metadata, link, citation, and repository rules; reporting exposes stale, duplicate, broken, isolated, or suspect content. | Papyrus depends on controlled structure and visible drift signals. | Invalid or low-quality knowledge enters the corpus and governance problems stay hidden. |
| Runtime versus source of truth | The runtime is a rebuildable projection of canonical source plus governance state. | Search, trust, queue, and impact views need relational state without making generated data authoritative. | People patch derived state by hand or trust stale runtime output over source. |
| Export model | Static export is an approval-gated publication surface for approved knowledge only. | Publishing and browseability are useful, but they are not the operational control plane. | Draft or unreviewed material leaks into published output, or operators mistake export pages for the live governance surface. |

## Commands That Exercise The Model

```bash
python3 scripts/validate.py
python3 scripts/build_index.py
python3 scripts/report_stale.py
python3 scripts/report_content_health.py --section citation-health --section suspect-objects
python3 scripts/serve_web.py
python3 scripts/serve_api.py
./scripts/build_static_export.sh
```

## Practical Rules

- Edit canonical knowledge in `knowledge/` or `archive/knowledge/`.
- Prefer one canonical procedure plus linked site deltas over copy-based regional variants.
- Do not patch generated files in `generated/`, `build/`, or `site/`.
- Validate before treating a revision as ready.
- Use queue, trust, revision, service, and impact views to govern runtime posture.
- Use the static export for approved publication, not for live review or trust decisions.
