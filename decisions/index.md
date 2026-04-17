# Decision Index

`decisions/` is the authoritative governance source for current Papyrus behavior, architecture, and policy.

## Canonical Decisions

- [Role-scoped experience architecture](role-scoped-experience-architecture.md)
- [Layout contracts by surface](layout-contracts.md)
- [Knowledge workflows and lifecycle](knowledge-workflows-and-lifecycle.md)
- [Web UI component contracts](web-ui-component-contracts.md)

Use these records when changing:

- shared route structure
- role-conditioned visibility
- shared surface composition
- workflow and lifecycle boundaries
- visible UI ownership and presentation contracts

## Current Repository Contract Notes

- `pyproject.toml` and `requirements-dev.txt` are approved top-level engineering control files for formatter, lint, type-check, and CI reproducibility.
- `generated/route-map.json` and `generated/route-map.md` are derived artifacts. Regenerate them from the registered web routes instead of editing them by hand.
- Controlled taxonomy values and knowledge-object type identifiers referenced by active schemas, templates, runtime validation, authoring surfaces, or other authoritative repository contracts must not be removed or renamed except through one coordinated migration across those layers.