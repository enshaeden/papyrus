#!/usr/bin/env python3
from __future__ import annotations

import sys

from kb_common import load_articles, validate_repository


def main() -> int:
    try:
        issues = validate_repository()
        article_count = len(load_articles())
    except Exception as exc:  # pragma: no cover - exercised via CLI tests
        print(f"validation setup failed: {exc}", file=sys.stderr)
        return 1

    if issues:
        for issue in issues:
            print(issue.render(), file=sys.stderr)
        print(f"validation failed with {len(issues)} issue(s)", file=sys.stderr)
        return 1

    print(f"validated {article_count} article(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
