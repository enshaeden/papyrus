# Papyrus

Papyrus is a local-first governed operational knowledge control plane for IT support and systems operations. Canonical knowledge stays in Markdown under `knowledge/` and `archive/knowledge/`; Papyrus builds a relational runtime on top of that source so operators can search, review, validate, and govern knowledge without turning generated output into the source of truth.

## Core Questions

- What is the current guidance?
- Why should we trust it?
- Who owns and reviewed it?
- What changed that may have invalidated it?
- What else is affected by this object or service?

## Use Modes

- `Read`: find the right runbook, known error, or service record and judge whether it is safe to use.
- `Write`: create or revise canonical knowledge, attach evidence, validate it, and hand it off for review.
- `Manage`: review queues, audit trust posture, inspect revision history, and track content health.

## Short Start

```bash
./scripts/bootstrap.sh
python3 scripts/serve_web.py
```

For terminal-first operator checks:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py dashboard --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
```

For a review/demo runtime with realistic workflow tension:

```bash
python3 scripts/demo_runtime.py
python3 scripts/serve_web.py --db build/demo-knowledge.db
python3 scripts/serve_api.py --db build/demo-knowledge.db
```

## Operator Docs

- Start here: [docs/getting-started.md](docs/getting-started.md)
- Read playbook: [docs/playbooks/read.md](docs/playbooks/read.md)
- Write playbook: [docs/playbooks/write.md](docs/playbooks/write.md)
- Manage playbook: [docs/playbooks/manage.md](docs/playbooks/manage.md)
- System model: [docs/reference/system-model.md](docs/reference/system-model.md)
- Operator readiness: [docs/reference/operator-readiness.md](docs/reference/operator-readiness.md)
- Decisions and rationale: [decisions/index.md](decisions/index.md)
