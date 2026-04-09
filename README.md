# Papyrus

Papyrus is a local-first operational knowledge control plane for IT support and systems operations. It keeps canonical knowledge in Markdown under `knowledge/` and `archive/knowledge/`, builds a relational runtime on top of that source, and guides people through the lifecycle of operational knowledge without turning generated output into the source of truth.

## Core Questions

- What is the current guidance?
- What should I do next?
- Is this safe to use right now?
- Why should we trust it?
- Who owns and reviewed it?
- What changed that may have invalidated it?
- What else is affected by this object or service?

## Use Modes

- `Read`: find the right runbook, known error, or service record and decide whether it is safe to use now.
- `Write`: create an object shell, draft or revise guidance, attach evidence, validate it, and submit it for review.
- `Review / Approvals`: inspect what changed, what evidence supports it, what is unresolved, and whether it should become canonical guidance.
- `Knowledge Health`: monitor stale guidance, weak evidence, suspect objects, and review pressure as stewardship work.
- `Services`: move from a service context into the right operational guidance path.
- `Activity / History`: understand what changed, what it affected, and what now needs review or revalidation.

## Short Start

```bash
./scripts/bootstrap.sh
python3 scripts/run.py --operator
```

Start at the web home page. Papyrus now opens on a lifecycle-guided landing page instead of dropping straight into a raw queue.

For terminal-first operator checks:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db
```

For a review/demo runtime with realistic workflow tension:

```bash
python3 scripts/run.py --demo
python3 scripts/run_scenario.py service-degradation
```

Writeback inspection and recovery remain explicit:

```bash
python3 scripts/source_sync.py preview --object kb-troubleshooting-vpn-connectivity
python3 scripts/source_sync.py writeback --object kb-troubleshooting-vpn-connectivity
python3 scripts/source_sync.py restore-last --object kb-troubleshooting-vpn-connectivity
python3 scripts/source_sync.py writeback-all
python3 scripts/ingest_event.py --type service_change --entity Remote\\ Access --payload payload.json
python3 scripts/operator_view.py activity --db build/knowledge.db --format json
python3 scripts/serve_web.py --db build/knowledge.db --source-root .
python3 scripts/serve_api.py --db build/knowledge.db --source-root .
```

Guardrail:
- `scripts/run.py --operator`, `scripts/serve_web.py`, and `scripts/serve_api.py` now reject non-canonical source roots unless you explicitly opt in with `--allow-noncanonical-source-root` on the direct web/API scripts.
- The same source-root check now runs inside `papyrus.interfaces.web.app(...)` and `papyrus.interfaces.api.app(...)`. Test or demo embeddings must opt in explicitly with `allow_noncanonical_source_root=True`.

## Operator Docs

- Start here: [docs/getting-started.md](docs/getting-started.md)
- Read playbook: [docs/playbooks/read.md](docs/playbooks/read.md)
- Write playbook: [docs/playbooks/write.md](docs/playbooks/write.md)
- Manage playbook: [docs/playbooks/manage.md](docs/playbooks/manage.md)
- System model: [docs/reference/system-model.md](docs/reference/system-model.md)
- Operator readiness: [docs/reference/operator-readiness.md](docs/reference/operator-readiness.md)
- Operator governance and decisions: [decisions/index.md](decisions/index.md)
