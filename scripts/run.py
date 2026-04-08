#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import threading
from pathlib import Path
from wsgiref.simple_server import make_server

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.application.commands import build_projection_command
from papyrus.application.demo_flow import DEMO_SOURCE_ROOT, build_operator_demo_runtime
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.interfaces.startup_guard import resolve_operator_source_root
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.web import app as web_app


def _reset_runtime_artifacts(database_path: Path, source_root: Path) -> None:
    for sibling in (
        database_path,
        database_path.with_name(database_path.name + "-shm"),
        database_path.with_name(database_path.name + "-wal"),
    ):
        if sibling.exists():
            sibling.unlink()
    if source_root != ROOT and source_root.exists():
        shutil.rmtree(source_root)


def _serve_in_thread(server, label: str) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, name=f"papyrus-{label}", daemon=True)
    thread.start()
    return thread


def main() -> int:
    parser = argparse.ArgumentParser(description="Start Papyrus in operator or demo mode with both local web and API surfaces.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Build the demo runtime, then start both local surfaces.")
    mode.add_argument("--operator", action="store_true", help="Rebuild the operator runtime, then start both local surfaces.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for both web and API servers.")
    parser.add_argument("--web-port", type=int, default=8080, help="Web port. Defaults to 8080.")
    parser.add_argument("--api-port", type=int, default=8081, help="API port. Defaults to 8081.")
    parser.add_argument("--db", default=None, help="Override the runtime SQLite database path.")
    parser.add_argument("--source-root", default=None, help="Override the source root used for writeback and evidence snapshots.")
    args = parser.parse_args()

    if args.demo:
        database_path = Path(args.db or ROOT / "build" / "demo-knowledge.db")
        source_root = Path(args.source_root or DEMO_SOURCE_ROOT)
        _reset_runtime_artifacts(database_path, source_root)
        build_operator_demo_runtime(database_path=database_path, source_root=source_root)
    else:
        try:
            database_path = Path(args.db or DB_PATH)
            source_root = resolve_operator_source_root(args.source_root)
            build_projection_command(database_path=database_path)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    web_server = make_server(
        args.host,
        args.web_port,
        web_app(
            database_path,
            source_root,
            allow_noncanonical_source_root=args.demo,
        ),
    )
    api_server = make_server(
        args.host,
        args.api_port,
        api_app(
            database_path,
            source_root,
            allow_noncanonical_source_root=args.demo,
        ),
    )
    web_thread = _serve_in_thread(web_server, "web")
    api_thread = _serve_in_thread(api_server, "api")

    mode_name = "demo" if args.demo else "operator"
    print(f"Papyrus {mode_name} mode is running.")
    print(f"Web: http://{args.host}:{args.web_port}")
    print(f"API: http://{args.host}:{args.api_port}")
    print(f"Runtime DB: {database_path}")
    print(f"Source root: {source_root}")
    try:
        web_thread.join()
        api_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down Papyrus.")
    finally:
        web_server.shutdown()
        api_server.shutdown()
        web_server.server_close()
        api_server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
