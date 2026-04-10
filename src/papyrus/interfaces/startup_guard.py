from __future__ import annotations

from pathlib import Path

from papyrus.infrastructure.transactional_mutation import MutationRecoveryError, TransactionalMutation
from papyrus.infrastructure.paths import ROOT


def resolve_operator_source_root(
    source_root: str | Path | None,
    *,
    allow_noncanonical: bool = False,
) -> Path:
    resolved = Path(source_root or ROOT).resolve()
    canonical_root = ROOT.resolve()
    if resolved != canonical_root and not allow_noncanonical:
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
    try:
        TransactionalMutation.recover_pending_mutations(source_root=resolved)
    except MutationRecoveryError as exc:
        raise ValueError(str(exc)) from exc
    return resolved
