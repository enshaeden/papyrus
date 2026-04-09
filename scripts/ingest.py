#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.application.ingestion_flow import ingest_file
from papyrus.infrastructure.paths import DB_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a local Markdown, DOCX, or PDF file into the Papyrus import workbench.")
    parser.add_argument("file", help="Path to the source file.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    args = parser.parse_args()

    result = ingest_file(file_path=Path(args.file), database_path=Path(args.db))
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
