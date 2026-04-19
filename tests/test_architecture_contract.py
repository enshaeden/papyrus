from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureContractTests(unittest.TestCase):
    def test_domain_actor_keeps_audit_identity_only(self) -> None:
        actor_source = (ROOT / "src/papyrus/domain/actor.py").read_text(encoding="utf-8")

        for forbidden_token in (
            "landing_path",
            "page_behaviors",
            "show_context_rail",
            "copy_style",
            "action_labels",
            "columns",
        ):
            with self.subTest(forbidden_token=forbidden_token):
                self.assertNotIn(forbidden_token, actor_source)

    def test_application_read_models_do_not_define_presenter_shaped_article_sections(self) -> None:
        article_projection_path = ROOT / "src/papyrus/application/read_models/article_projection.py"
        self.assertFalse(article_projection_path.exists())
        legacy_web_projection_path = (
            ROOT / "src/papyrus/interfaces/web/view_models/article_projection.py"
        )
        self.assertFalse(legacy_web_projection_path.exists())

        forbidden_tokens = ('"eyebrow"', '"blocks"', '"show_context_rail"', '"section_id"')
        for path in sorted((ROOT / "src/papyrus/application/read_models").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            for forbidden_token in forbidden_tokens:
                with self.subTest(path=path.name, forbidden_token=forbidden_token):
                    self.assertNotIn(forbidden_token, source)

    def test_operator_api_does_not_define_role_prefixed_routes(self) -> None:
        api_source = (ROOT / "src/papyrus/interfaces/api.py").read_text(encoding="utf-8")

        for forbidden_token in ('"/reader/', '"/operator/', '"/admin/'):
            with self.subTest(forbidden_token=forbidden_token):
                self.assertNotIn(forbidden_token, api_source)


if __name__ == "__main__":
    unittest.main()
