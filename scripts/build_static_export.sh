#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

"$ROOT_DIR/scripts/build.sh"
"$PYTHON_BIN" scripts/build_site_docs.py
"$PYTHON_BIN" scripts/validate.py

if [[ -x "$ROOT_DIR/.venv/bin/mkdocs" ]]; then
  "$ROOT_DIR/.venv/bin/mkdocs" build --strict
  "$PYTHON_BIN" scripts/validate.py --include-rendered-site
  exit 0
fi

if command -v mkdocs >/dev/null 2>&1; then
  mkdocs build --strict
  "$PYTHON_BIN" scripts/validate.py --include-rendered-site
  exit 0
fi

echo "mkdocs is not installed. Run scripts/bootstrap.sh first." >&2
exit 1
