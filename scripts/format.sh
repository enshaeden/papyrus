#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

ARGS=()
if [[ "${1:-}" == "--check" ]]; then
  ARGS+=(--check)
fi

if [[ ${#ARGS[@]} -gt 0 ]]; then
  "$PYTHON_BIN" -m ruff format "${ARGS[@]}" .
  exit 0
fi

"$PYTHON_BIN" -m ruff format .
