from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WEB_TEST_GLOBS = (
    "tests/test_web_*.py",
    "tests/interfaces/test_*_ui.py",
    "tests/test_interface_surfaces.py",
    "tests/test_surface_conformance.py",
    "tests/test_operator_readiness.py",
)
EXCLUDED_FILES = {
    "web_assertions.py",
    "test_web_semantic_hook_contract.py",
}
FORBIDDEN_HOOK_TOKENS = (
    "data-surface",
    "data-component",
    "data-action-id",
)


def iter_web_test_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in WEB_TEST_GLOBS:
        files.update(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(path for path in files if path.name not in EXCLUDED_FILES)


class WebSemanticHookContractTests(unittest.TestCase):
    def test_web_facing_tests_route_semantic_hook_checks_through_helper(self) -> None:
        target_files = iter_web_test_files()
        self.assertTrue(target_files, msg="expected at least one web-facing test file")

        violations: list[str] = []
        for path in target_files:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            for line_number, line in enumerate(lines, start=1):
                for token in FORBIDDEN_HOOK_TOKENS:
                    if token in line:
                        relative_path = path.relative_to(ROOT)
                        violations.append(
                            f"{relative_path}:{line_number} contains raw semantic hook token {token!r}"
                        )

        self.assertFalse(
            violations,
            msg=(
                "web-facing tests should use tests/web_assertions.py instead of raw semantic hook strings:\n"
                + "\n".join(violations)
            ),
        )
