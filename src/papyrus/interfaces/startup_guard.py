from __future__ import annotations

import logging
from pathlib import Path

from papyrus.application.workspace import require_workspace_source_root
from papyrus.infrastructure.observability import get_logger, log_event
from papyrus.infrastructure.transactional_mutation import (
    MutationRecoveryError,
    TransactionalMutation,
)

LOGGER = get_logger(__name__)


def resolve_runtime_source_root(source_root: str | Path | None) -> Path | None:
    if source_root is None or not str(source_root).strip():
        log_event(LOGGER, logging.INFO, "runtime_source_root_not_configured")
        return None
    resolved = Path(source_root).resolve()
    log_event(
        LOGGER,
        logging.INFO,
        "runtime_source_root_resolved",
        requested_source_root=str(source_root),
        resolved_source_root=str(resolved),
    )
    return resolved


def prepare_workspace_source_root(
    source_root: str | Path | None,
    *,
    operation: str,
) -> Path:
    resolved = require_workspace_source_root(source_root, operation=operation)
    log_event(
        LOGGER,
        logging.INFO,
        "workspace_mutation_recovery_started",
        operation=operation,
        source_root=str(resolved),
    )
    try:
        TransactionalMutation.recover_pending_mutations(source_root=resolved)
    except MutationRecoveryError as exc:
        log_event(
            LOGGER,
            logging.ERROR,
            "workspace_mutation_recovery_failed",
            operation=operation,
            source_root=str(resolved),
            error=str(exc),
        )
        raise ValueError(str(exc)) from exc
    log_event(
        LOGGER,
        logging.INFO,
        "workspace_mutation_recovery_completed",
        operation=operation,
        source_root=str(resolved),
    )
    return resolved
