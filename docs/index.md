# System & Design Docs

This area explains how the Papyrus knowledge system works. It is for repository architecture, schema behavior, generator design, taxonomy design, workflow design, and contributor guidance. It is not the source of truth for operator-facing procedures.

## Use The Right Area

- For operational procedures, troubleshooting, runbooks, SOPs, and support references, use the [Knowledge Base](../knowledge/home/index.md).
- For repository, schema, taxonomy, generator, and workflow documentation, use `docs/`.
- For durable structural rationale and tradeoffs, use [Governance & Decisions](../decisions/index.md).

## What Belongs Here

- Repository architecture and directory contract
- Schema and taxonomy behavior
- Site-generator and indexing design
- Contributor workflow and placement rules
- Migration and system-level implementation notes

## What Does Not Belong Here

- Canonical operational procedures
- Troubleshooting steps intended for day-to-day support execution
- SOP content duplicated from `knowledge/`

If a page in `docs/` starts reading like operator guidance, review the placement rubric in [contributor-workflow.md](contributor-workflow.md) and run:

```bash
python3 scripts/report_content_health.py --section knowledge-like-docs
```

## Start Here

- [Contributor Workflow](contributor-workflow.md)
- [Information Architecture](architecture/information-architecture.md)
- [Content Lifecycle](architecture/content-lifecycle.md)
- [Governance Policy](architecture/governance.md)
- [Knowledge Discovery Improvement Plan](knowledge-discovery-improvement-plan.md)
- [Seed Migration Rationale](migration/seed-migration-rationale.md)
