from __future__ import annotations

from papyrus.interfaces.web.routes import write_guided, write_object, write_search, write_submit


def register(router, runtime) -> None:
    write_object.register(router, runtime)
    write_search.register(router, runtime)
    write_guided.register(router, runtime)
    write_submit.register(router, runtime)
