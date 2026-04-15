from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.substrate_checks import (
    validate_web_copy_policy,
    validate_web_copy_policy_source,
)


class WebCopyPolicyLintTests(unittest.TestCase):
    def test_repo_web_sources_pass_copy_policy_lint(self) -> None:
        issues = validate_web_copy_policy()
        self.assertEqual(
            [],
            [issue.render() for issue in issues],
            msg="\n".join(issue.render() for issue in issues),
        )

    def test_validator_flags_forbidden_page_header_and_header_adjacent_summary(self) -> None:
        source = """
def demo():
    return {
        "page_header": {
            "headline": "Home",
            "intro": "Decorative blurb",
        },
        "body_html": "<section><h2>Heading</h2><p class=\\"demo__summary\\">Decorative blurb</p></section>",
    }
"""
        issues = [
            issue.render()
            for issue in validate_web_copy_policy_source(ROOT / "tmp" / "demo_presenter.py", source)
        ]

        self.assertTrue(any("page_header field 'intro'" in issue for issue in issues))
        self.assertTrue(any("demo__summary" in issue for issue in issues))

    def test_validator_allows_explicit_state_critical_summary_exception(self) -> None:
        source = """
def demo():
    return "<section><h2>Progress</h2><p class=\\"ingest-progress__summary\\">Current focus</p></section>"
"""
        issues = validate_web_copy_policy_source(ROOT / "tmp" / "allowed_presenter.py", source)
        self.assertEqual([], issues)


if __name__ == "__main__":
    unittest.main()
