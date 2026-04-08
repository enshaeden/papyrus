from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from papyrus.interfaces.web.rendering import PageRenderer


@dataclass(frozen=True)
class WebRuntime:
    database_path: Path
    page_renderer: PageRenderer
    taxonomies: dict[str, dict[str, Any]]

    @property
    def template_renderer(self):
        return self.page_renderer.template_renderer
