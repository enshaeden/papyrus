from __future__ import annotations

from papyrus.interfaces.web.http import Request, redirect_response
from papyrus.interfaces.web.urls import home_url


def register(router, runtime) -> None:
    def root_landing(_: Request):
        return redirect_response(home_url(runtime.default_role))

    router.add(["GET"], "/", root_landing, minimum_visible_role="reader")
