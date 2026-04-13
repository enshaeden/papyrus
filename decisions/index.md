# Decision Index

`decisions/` is the authoritative governance source for current Papyrus behavior, architecture, and policy.

## Canonical Decisions

- [Role-scoped experience architecture](role-scoped-experience-architecture.md)
- [Layout contracts by role](layout-contracts-by-role.md)
- [Knowledge workflows and lifecycle](knowledge-workflows-and-lifecycle.md)
- [Web UI component contracts](web-ui-component-contracts.md)

Use these records when changing routing, visibility, layouts, workflow boundaries, or lifecycle behavior.

## Current Repository Contract Notes

- `pyproject.toml` and `requirements-dev.txt` are approved top-level engineering control files for formatter, lint, type-check, and CI reproducibility.
- `generated/route-map.json` and `generated/route-map.md` are derived artifacts. Regenerate them from the registered web routes instead of editing them by hand.
