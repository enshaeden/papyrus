"""Citation repository surface reserved for the relational runtime phase."""


class CitationRepository:
    def list_citations(self) -> list[object]:
        raise NotImplementedError("Citation repositories are introduced in a later phase.")

