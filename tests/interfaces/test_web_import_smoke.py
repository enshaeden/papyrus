from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


MODULES = (
    "papyrus.interfaces.web.app",
    "papyrus.interfaces.api",
    "papyrus.interfaces.web.rendering",
    "papyrus.interfaces.web.routes.home",
    "papyrus.interfaces.web.routes.dashboard",
    "papyrus.interfaces.web.routes.impact",
    "papyrus.interfaces.web.routes.objects",
    "papyrus.interfaces.web.routes.queue",
    "papyrus.interfaces.web.routes.services",
    "papyrus.interfaces.web.routes.write",
    "papyrus.interfaces.web.routes.write_guided",
    "papyrus.interfaces.web.routes.write_object",
    "papyrus.interfaces.web.routes.ingest",
    "papyrus.interfaces.web.presenters.governed_presenter",
    "papyrus.interfaces.web.presenters.home_presenter",
    "papyrus.interfaces.web.presenters.ingest_presenter",
    "papyrus.interfaces.web.presenters.object_presenter",
    "papyrus.interfaces.web.presenters.dashboard_presenter",
    "papyrus.interfaces.web.presenters.queue_presenter",
)


class WebImportSmokeTests(unittest.TestCase):
    def test_import_touched_web_modules(self) -> None:
        for module_name in MODULES:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)


if __name__ == "__main__":
    unittest.main()
