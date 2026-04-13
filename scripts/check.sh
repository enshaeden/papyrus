#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

"$ROOT_DIR/scripts/format.sh" --check
"$ROOT_DIR/scripts/lint.sh"
"$ROOT_DIR/scripts/typecheck.sh"
"$PYTHON_BIN" scripts/validate.py
"$PYTHON_BIN" scripts/build_route_map.py --check
"$PYTHON_BIN" -m unittest discover -s tests
"$ROOT_DIR/scripts/build_static_export.sh"
