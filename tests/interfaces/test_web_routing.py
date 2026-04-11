from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.app import Router
from papyrus.interfaces.web.http import Request


class WebRoutingTests(unittest.TestCase):
    def test_request_with_route_params_returns_new_request(self) -> None:
        request = Request(method="GET", path="/objects/kb-test", query={}, form={})
        routed = request.with_route_params({"object_id": "kb-test"})

        self.assertEqual(request.route_params, {})
        self.assertEqual(routed.route_value("object_id"), "kb-test")
        self.assertIsNot(request, routed)

    def test_router_match_returns_routed_request_without_mutation(self) -> None:
        router = Router()
        router.add(["GET"], "/objects/{object_id}", lambda request: request)
        request = Request(method="GET", path="/objects/kb-routing", query={}, form={})

        matched = router.match(request)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(request.route_params, {})
        self.assertEqual(matched.request.route_value("object_id"), "kb-routing")

    def test_router_match_preserves_method_not_allowed_behavior(self) -> None:
        router = Router()
        router.add(["GET"], "/objects/{object_id}", lambda request: request)
        request = Request(method="POST", path="/objects/kb-routing", query={}, form={})

        matched = router.match(request)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(matched.route.methods, ("__method_not_allowed__",))
        self.assertEqual(matched.request.route_value("object_id"), "kb-routing")


if __name__ == "__main__":
    unittest.main()
