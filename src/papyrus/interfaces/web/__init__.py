from __future__ import annotations

from typing import Any


def app(*args: Any, **kwargs: Any):
    from papyrus.interfaces.web.app import app as create_app

    return create_app(*args, **kwargs)


def main() -> int:
    from papyrus.interfaces.web.app import main as run_main

    return run_main()


__all__ = ["app", "main"]
