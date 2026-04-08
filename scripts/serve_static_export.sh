#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

"$ROOT_DIR/scripts/build_static_export.sh"

if [[ -x "$ROOT_DIR/.venv/bin/mkdocs" ]]; then
  exec "$ROOT_DIR/.venv/bin/mkdocs" serve -a 127.0.0.1:8000
fi

if command -v mkdocs >/dev/null 2>&1; then
  exec mkdocs serve -a 127.0.0.1:8000
fi

echo "mkdocs is not installed. Run scripts/bootstrap.sh first." >&2
exit 1
