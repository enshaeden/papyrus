from __future__ import annotations

import argparse
import logging
import shutil
import threading
from pathlib import Path
from wsgiref.simple_server import make_server

from papyrus.application.demo_flow import DEMO_SOURCE_ROOT, build_operator_demo_runtime
from papyrus.application.role_visibility import normalize_role, role_from_actor_id
from papyrus.domain.actor import default_actor_id, default_actor_id_for_role
from papyrus.infrastructure.observability import get_logger, log_event
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.web.app import app as web_app
from papyrus.interfaces.web.urls import home_url

LOGGER = get_logger(__name__)


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
    parser = argparse.ArgumentParser(
        description="Start Papyrus in operator or demo mode with lifecycle-guided web and API surfaces."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--demo",
        action="store_true",
        help="Build the demo runtime, then start both local surfaces.",
    )
    mode.add_argument(
        "--operator",
        action="store_true",
        help="Start both local operator surfaces against the selected runtime database.",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Bind host for both web and API servers."
    )
    parser.add_argument("--web-port", type=int, default=8080, help="Web port. Defaults to 8080.")
    parser.add_argument("--api-port", type=int, default=8081, help="API port. Defaults to 8081.")
    parser.add_argument("--db", default=None, help="Override the runtime SQLite database path.")
    parser.add_argument(
        "--source-root",
        default=None,
        help="Workspace source root for source-backed authoring, ingest, and writeback operations.",
    )
    parser.add_argument(
        "--allow-web-ingest-local-paths",
        action="store_true",
        help="Allow the /ingest web form to read an absolute local file path from the machine running Papyrus.",
    )
    identity = parser.add_mutually_exclusive_group()
    identity.add_argument(
        "--actor",
        default=None,
        help="Local actor id for the web runtime role context. Defaults to the local operator actor.",
    )
    identity.add_argument(
        "--role",
        default=None,
        help="Local role for the web runtime role context. Use reader, operator, or admin.",
    )
    args = parser.parse_args()
    selected_actor_id = (
        args.actor or default_actor_id_for_role(args.role or "") or default_actor_id()
    )
    selected_role = normalize_role(args.role or role_from_actor_id(selected_actor_id))

    if args.demo:
        database_path = Path(args.db or ROOT / "build" / "demo-knowledge.db")
        source_root = Path(args.source_root or DEMO_SOURCE_ROOT)
        log_event(
            LOGGER,
            logging.INFO,
            "runtime_cli_demo_started",
            database_path=str(database_path),
            source_root=str(source_root),
            actor_id=selected_actor_id,
            role=selected_role,
        )
        _reset_runtime_artifacts(database_path, source_root)
        build_operator_demo_runtime(database_path=database_path, source_root=source_root)
    else:
        database_path = Path(args.db or DB_PATH)
        source_root = Path(args.source_root).resolve() if args.source_root else None
        log_event(
            LOGGER,
            logging.INFO,
            "runtime_cli_operator_started",
            database_path=str(database_path),
            source_root=str(source_root) if source_root is not None else None,
            actor_id=selected_actor_id,
            role=selected_role,
        )

    web_server = make_server(
        args.host,
        args.web_port,
        web_app(
            database_path,
            source_root,
            allow_web_ingest_local_paths=args.allow_web_ingest_local_paths,
            default_actor_id=selected_actor_id,
            default_role=selected_role,
        ),
    )
    api_server = make_server(
        args.host,
        args.api_port,
        api_app(
            database_path,
            source_root,
        ),
    )
    web_thread = _serve_in_thread(web_server, "web")
    api_thread = _serve_in_thread(api_server, "api")

    mode_name = "demo" if args.demo else "operator"
    log_event(
        LOGGER,
        logging.INFO,
        "runtime_cli_servers_ready",
        mode=mode_name,
        web_url=f"http://{args.host}:{args.web_port}",
        api_url=f"http://{args.host}:{args.api_port}",
        database_path=str(database_path),
        source_root=str(source_root),
        actor_id=selected_actor_id,
        role=selected_role,
    )
    print(f"Papyrus {mode_name} mode is running.")
    print(f"Home: http://{args.host}:{args.web_port}{home_url(selected_role)}")
    print(f"Web: http://{args.host}:{args.web_port}")
    print(f"API: http://{args.host}:{args.api_port}")
    print(f"Runtime DB: {database_path}")
    print(f"Source root: {source_root}")
    print(f"Web role context: {selected_role} ({selected_actor_id})")
    print(
        f"Local web root / redirects to {home_url(selected_role)}. Rebuild the runtime separately with `python3 scripts/build_index.py --source-root /path/to/workspace` when source-backed data must change."
    )
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
