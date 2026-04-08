#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import curated <KNOWLEDGE_PORTAL> seed content into the Papyrus source tree"
    )
    parser.add_argument("-zip", required=True, help="Path to the local <KNOWLEDGE_PORTAL> export zip")
    parser.add_argument("-root", default=None, help=argparse.SUPPRESS)
    parser.add_argument(
        "-overwrite",
        action="store_true",
        help="Allow overwriting existing generated seed files",
    )
    parser.add_argument(
        "-review-date",
        default=None,
        help="ISO date for last_reviewed and change log",
    )
    parser.parse_args()

    print(
        (
            "import_knowledge_portal.py is intentionally disabled. "
            "The checked-in implementation was syntactically corrupted and could not be "
            "verified or safely reconstructed from the repository state in this refactor pass."
        ),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
