from __future__ import annotations

import logging
from pathlib import Path

from papyrus.infrastructure.observability import get_logger, log_event
from papyrus.infrastructure.paths import ROOT
from papyrus.infrastructure.transactional_mutation import (
    MutationRecoveryError,
    TransactionalMutation,
)

LOGGER = get_logger(__name__)


def resolve_operator_source_root(
    source_root: str | Path | None,
    *,
    allow_noncanonical: bool = False,
) -> Path:
    resolved = Path(source_root or ROOT).resolve()
    canonical_root = ROOT.resolve()
    log_event(
        LOGGER,
        logging.INFO,
        "operator_source_root_resolved",
        requested_source_root=str(source_root or ROOT),
        resolved_source_root=str(resolved),
        canonical_source_root=str(canonical_root),
        allow_noncanonical=allow_noncanonical,
    )
    if resolved != canonical_root and not allow_noncanonical:
        log_event(
            LOGGER,
            logging.ERROR,
            "operator_source_root_rejected",
            resolved_source_root=str(resolved),
            canonical_source_root=str(canonical_root),
        )
        raise ValueError(
            f"operator mode requires the canonical source root {canonical_root}; "
            f"use --demo or pass --allow-noncanonical-source-root for sandboxed roots"
        )
    return resolved


def prepare_operator_source_root(
    source_root: str | Path | None,
    *,
    allow_noncanonical: bool = False,
) -> Path:
    resolved = resolve_operator_source_root(
        source_root,
        allow_noncanonical=allow_noncanonical,
    )
    log_event(
        LOGGER,
        logging.INFO,
        "operator_mutation_recovery_started",
        source_root=str(resolved),
    )
    try:
        TransactionalMutation.recover_pending_mutations(source_root=resolved)
    except MutationRecoveryError as exc:
        log_event(
            LOGGER,
            logging.ERROR,
            "operator_mutation_recovery_failed",
            source_root=str(resolved),
            error=str(exc),
        )
        raise ValueError(str(exc)) from exc
    log_event(
        LOGGER,
        logging.INFO,
        "operator_mutation_recovery_completed",
        source_root=str(resolved),
    )
    return resolved
