"""Service repository surface reserved for the relational runtime phase."""


class ServiceRepository:
    def list_services(self) -> list[object]:
        raise NotImplementedError("Service repositories are introduced in a later phase.")

