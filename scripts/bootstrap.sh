#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

"$ROOT_DIR/scripts/build.sh"

echo "bootstrap complete"
echo "run ./scripts/serve.sh to start the local site server"
