from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from email.parser import BytesParser
from email.policy import default
from typing import Any
from http.cookies import SimpleCookie
from urllib.parse import parse_qs


@dataclass(frozen=True)
class UploadedFile:
    field_name: str
    filename: str
    content_type: str
    body: bytes


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: dict[str, list[str]]
    form: dict[str, list[str]]
    json_body: dict[str, Any] | None = None
    route_params: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    files: dict[str, UploadedFile] = field(default_factory=dict)

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

    def cookie_value(self, name: str, default: str = "") -> str:
        return self.cookies.get(name, default)

    def uploaded_file(self, name: str) -> UploadedFile | None:
        return self.files.get(name)


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
    files: dict[str, UploadedFile] = {}
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
        elif content_type == "multipart/form-data":
            message = BytesParser(policy=default).parsebytes(
                b"Content-Type: " + str(environ.get("CONTENT_TYPE", "")).encode("utf-8") + b"\r\n\r\n" + raw_body
            )
            for part in message.iter_parts():
                if part.get_content_disposition() != "form-data":
                    continue
                field_name = str(part.get_param("name", header="content-disposition") or "")
                filename = part.get_filename()
                payload = part.get_payload(decode=True) or b""
                if filename:
                    files[field_name] = UploadedFile(
                        field_name=field_name,
                        filename=str(filename),
                        content_type=str(part.get_content_type() or "application/octet-stream"),
                        body=payload,
                    )
                else:
                    form.setdefault(field_name, []).append(payload.decode(part.get_content_charset() or "utf-8"))
        else:
            form = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)

    cookie = SimpleCookie()
    cookie.load(environ.get("HTTP_COOKIE", ""))
    cookies = {key: morsel.value for key, morsel in cookie.items()}

    return Request(
        method=method,
        path=path,
        query=query,
        form=form,
        json_body=json_body,
        cookies=cookies,
        files=files,
    )


def html_response(body: str, status: str = "200 OK", headers: list[tuple[str, str]] | None = None) -> Response:
    payload = body.encode("utf-8")
    return Response(
        status=status,
        body=payload,
        headers=[
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(payload))),
            ("Cache-Control", "no-store"),
            *(headers or []),
        ],
    )


def json_response(payload: object, status: str = "200 OK", headers: list[tuple[str, str]] | None = None) -> Response:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return Response(
        status=status,
        body=body,
        headers=[
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            *(headers or []),
        ],
    )


def redirect_response(
    location: str,
    status: str = "303 See Other",
    headers: list[tuple[str, str]] | None = None,
) -> Response:
    return Response(
        status=status,
        body=b"",
        headers=[
            ("Location", location),
            ("Content-Length", "0"),
            ("Cache-Control", "no-store"),
            *(headers or []),
        ],
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
