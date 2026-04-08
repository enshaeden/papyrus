#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.interfaces.cli import search_main


def main() -> int:
    return search_main()


if __name__ == "__main__":
    raise SystemExit(main())
