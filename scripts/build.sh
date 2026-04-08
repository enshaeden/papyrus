#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

rm -rf "$ROOT_DIR/generated/site_docs" "$ROOT_DIR/site"

"$PYTHON_BIN" scripts/validate.py
"$PYTHON_BIN" scripts/build_index.py
