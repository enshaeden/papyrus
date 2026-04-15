#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

SOURCE_ROOT="${PAPYRUS_SOURCE_ROOT:-}"
if [[ "${1:-}" == "--source-root" ]]; then
  if [[ $# -lt 2 ]]; then
    echo "--source-root requires a path" >&2
    exit 1
  fi
  SOURCE_ROOT="$2"
fi

if [[ -n "$SOURCE_ROOT" ]]; then
  "$PYTHON_BIN" scripts/validate.py --source-root "$SOURCE_ROOT"
  "$PYTHON_BIN" scripts/build_index.py --source-root "$SOURCE_ROOT"
else
  "$PYTHON_BIN" scripts/validate.py
fi
"$PYTHON_BIN" scripts/build_route_map.py
