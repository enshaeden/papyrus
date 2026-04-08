#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.interfaces.cli import report_content_health_main


def main() -> int:
    return report_content_health_main()


if __name__ == "__main__":
    raise SystemExit(main())
