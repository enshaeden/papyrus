"""Validation repository surface reserved for the relational runtime phase."""


class ValidationRepository:
    def list_runs(self) -> list[object]:
        raise NotImplementedError("Validation repositories are introduced in a later phase.")

