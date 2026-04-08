from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_path() -> None:
    src_path = Path(__file__).resolve().parent.parent / "src"
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
