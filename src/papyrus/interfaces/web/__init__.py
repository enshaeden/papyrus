from __future__ import annotations


def main() -> int:
    from papyrus.interfaces.web.app import main as run_main

    return run_main()


__all__ = ["main"]
