#!/usr/bin/env python3
from __future__ import annotations

import sys


def main() -> int:
    print(
        (
            "import_knowledge_portal.py is retired and unsupported. "
            "See decisions/index.md for the retirement rationale and use "
            "migration/seed-plan.yml, migration/import-manifest.yml, and "
            "docs/migration/seed-migration-rationale.md as the maintained migration record. "
            "Use scripts/validate_migration.py to verify the current seed state."
        ),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
