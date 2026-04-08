from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: dict[str, list[str]]
    form: dict[str, list[str]]
    json_body: dict[str, Any] | None = None
    route_params: dict[str, str] = field(default_factory=dict)

    def query_value(self, name: str, default: str = "") -> str:
        values = self.query.get(name)
        if not values:
            return default
        return values[0]

    def query_values(self, name: str) -> list[str]:
        return list(self.query.get(name, []))

    def form_value(self, name: str, default: str = "") -> str:
        values = self.form.get(name)
        if not values:
            return default
        return values[0]

    def form_values(self, name: str) -> list[str]:
        return list(self.form.get(name, []))

    def route_value(self, name: str, default: str = "") -> str:
        return self.route_params.get(name, default)


@dataclass(frozen=True)
class Response:
    status: str
    body: bytes
    headers: list[tuple[str, str]]

    def as_wsgi(self, start_response) -> list[bytes]:
        start_response(self.status, self.headers)
        return [self.body]


def request_from_environ(environ: dict[str, Any]) -> Request:
    method = str(environ.get("REQUEST_METHOD", "GET")).upper()
    path = environ.get("PATH_INFO", "/") or "/"
    query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    form: dict[str, list[str]] = {}
    json_body: dict[str, Any] | None = None

    content_length_raw = environ.get("CONTENT_LENGTH") or "0"
    try:
        content_length = max(int(content_length_raw), 0)
    except ValueError:
        content_length = 0
    raw_body = environ["wsgi.input"].read(content_length) if content_length else b""

    if raw_body:
        content_type = str(environ.get("CONTENT_TYPE", "")).split(";", 1)[0].strip().lower()
        if content_type == "application/json":
            loaded = json.loads(raw_body.decode("utf-8"))
            if isinstance(loaded, dict):
                json_body = loaded
        else:
            form = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)

    return Request(
        method=method,
        path=path,
        query=query,
        form=form,
        json_body=json_body,
    )


def html_response(body: str, status: str = "200 OK") -> Response:
    payload = body.encode("utf-8")
    return Response(
        status=status,
        body=payload,
        headers=[
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(payload))),
            ("Cache-Control", "no-store"),
        ],
    )


def json_response(payload: object, status: str = "200 OK") -> Response:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return Response(
        status=status,
        body=body,
        headers=[
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ],
    )


def redirect_response(location: str, status: str = "303 See Other") -> Response:
    return Response(
        status=status,
        body=b"",
        headers=[("Location", location), ("Content-Length", "0"), ("Cache-Control", "no-store")],
    )


def static_response(payload: bytes, content_type: str, status: str = "200 OK") -> Response:
    return Response(
        status=status,
        body=payload,
        headers=[
            ("Content-Type", content_type),
            ("Content-Length", str(len(payload))),
            ("Cache-Control", "public, max-age=300"),
        ],
    )
