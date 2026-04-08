"""Audit repository surface reserved for the relational runtime phase."""


class AuditRepository:
    def list_events(self) -> list[object]:
        raise NotImplementedError("Audit repositories are introduced in a later phase.")

