from __future__ import annotations

from pathlib import Path

from papyrus.infrastructure.observability import get_logger
from papyrus.infrastructure.paths import ROOT

LOGGER = get_logger(__name__)


class WorkspaceSourceRequiredError(ValueError):
    """Raised when a workspace-scoped source operation is invoked without a source root."""


def require_workspace_source_root(
    source_root: str | Path | None,
    *,
    operation: str,
) -> Path:
    if source_root is None or not str(source_root).strip():
        raise WorkspaceSourceRequiredError(
            f"{operation} requires a workspace source root; read-only runtime can start without one, "
            "but source-backed operations must run against a workspace."
        )
    return Path(source_root).resolve()


def repository_workspace_root() -> Path:
    """Return the repository workspace root for repo-scoped tooling."""
    return ROOT.resolve()
