from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.substrate_checks import (
    validate_documented_repository_paths,
    validate_documented_web_routes,
    validate_static_asset_references,
)
from papyrus.infrastructure.paths import (
    GENERATED_ROUTE_MAP_JSON_PATH,
    GENERATED_ROUTE_MAP_MARKDOWN_PATH,
)
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_repository_contract_paths,
)
from papyrus.jobs.route_map_build import check_route_map


class EngineeringSubstrateContractTests(unittest.TestCase):
    def _documentation_paths(self) -> list[Path]:
        return collect_repository_contract_paths()

    def test_documented_repository_paths_are_current(self) -> None:
        issues = validate_documented_repository_paths(self._documentation_paths())
        self.assertEqual(
            [],
            [issue.render() for issue in issues],
            msg="\n".join(issue.render() for issue in issues),
        )

    def test_documented_web_routes_are_current(self) -> None:
        issues = validate_documented_web_routes(self._documentation_paths())
        self.assertEqual(
            [],
            [issue.render() for issue in issues],
            msg="\n".join(issue.render() for issue in issues),
        )

    def test_static_asset_references_are_current(self) -> None:
        issues = validate_static_asset_references()
        self.assertEqual(
            [],
            [issue.render() for issue in issues],
            msg="\n".join(issue.render() for issue in issues),
        )

    def test_route_map_artifacts_are_current(self) -> None:
        findings = check_route_map(
            json_output=GENERATED_ROUTE_MAP_JSON_PATH,
            markdown_output=GENERATED_ROUTE_MAP_MARKDOWN_PATH,
        )
        self.assertEqual([], findings, msg="\n".join(findings))


if __name__ == "__main__":
    unittest.main()
