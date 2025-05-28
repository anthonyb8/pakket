from enum import Enum
from dataclasses import dataclass
from typing import Callable, Dict, List
import re
import json
from urllib.parse import urlparse, parse_qs
from .base import Service, Message


class StatusCode(Enum):
    OK = (200, "OK")
    CREATED = (201, "Created")
    NO_CONTENT = (204, "No Content")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    NOT_IMPLEMENTED = (501, "Not Implemented")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    @staticmethod
    def from_str(s: str) -> "HttpMethod":
        match s:
            case "GET":
                return HttpMethod.GET
            case "POST":
                return HttpMethod.POST
            case "UPDATE":
                return HttpMethod.UPDATE
            case "DELETE":
                return HttpMethod.DELETE
            case _:
                raise ValueError(f"Unknown HTTP method: {s}")


@dataclass
class HttpRequest:
    method: HttpMethod
    headers: Dict[str, str]
    path: str
    query: Dict[str, List[str]]
    body: str

    @property
    def args(self) -> dict:
        # Try to parse JSON body
        try:
            parsed_body = json.loads(self.body) if self.body else {}
            if not isinstance(parsed_body, dict):
                parsed_body = {}
        except json.JSONDecodeError:
            parsed_body = {}

        # Merge body and query
        return {**self.query, **parsed_body}

    @staticmethod
    def from_bytes(raw: bytes) -> "HttpRequest":
        # Split Head and Body
        head, _, body = raw.partition(b"\r\n\r\n")
        header_str = head.decode("utf-8", errors="replace")
        head_lines = header_str.splitlines()

        # Start Line
        method, url, version = head_lines[0].split(" ")
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)  # convert to dict

        # Headers
        headers = {}
        for line in head_lines[1:]:
            if not line.strip():
                continue
            key, value = line.split(":", 1)
            headers[key.lower()] = value

        # Body
        charset = "utf-8"
        body_str = body.decode(charset, errors="replace")

        return HttpRequest(
            HttpMethod.from_str(method),
            headers,
            parsed.path,
            query_params,
            body_str,
        )


@dataclass
class HttpResponse(Message):
    statuscode: StatusCode
    headers: Dict[str, str]
    body: bytes

    def to_bytes(self) -> bytes:
        msg = b""
        status_code, status_text = self.statuscode.value
        msg += f"HTTP/1.1 {status_code} {status_text}\r\n".encode("utf-8")

        for k, v in self.headers.items():
            msg += f"{k}: {v}\r\n".encode("utf-8")
        msg += b"\r\n"
        return msg + self.body

    @staticmethod
    def error(msg: str, code: StatusCode) -> "HttpResponse":
        return HttpResponse(
            statuscode=code,
            headers={
                "Content-Type": "text/plain",
                "Content-Length": str(len(msg)),
            },
            body=msg.encode("utf-8"),
        )


def match_path(template: str, actual: str):
    pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", template)
    match = re.fullmatch(pattern, actual)
    if match:
        return match.groupdict()
    return None


class Http(Service):
    def __init__(self):
        self.routes = {}

    def add_route(self, method: HttpMethod, path: str, func: Callable):
        self.routes.setdefault(method, []).append((path, func))

    def route(self, request: HttpRequest) -> HttpResponse:
        method_routes = self.routes.get(request.method, [])

        for temp, func in method_routes:
            path_params = match_path(temp, request.path)
            if path_params:
                path_params.update(request.args)
                try:
                    return func(**path_params)
                except Exception as e:
                    return HttpResponse.error(str(e), StatusCode.BAD_REQUEST)

        return HttpResponse.error("Bad endpoint", StatusCode.NOT_FOUND)

    def call(self, msg: bytes) -> Message:
        http_req = HttpRequest.from_bytes(msg)
        http_response = self.route(http_req)
        return http_response

    def get(self, path: str):
        def decorator(func):
            self.add_route(HttpMethod.GET, path, func)
            return func

        return decorator

    def post(self, path: str):
        def decorator(func):
            self.add_route(HttpMethod.POST, path, func)
            return func

        return decorator

    def update(self, path: str):
        def decorator(func):
            self.add_route(HttpMethod.UPDATE, path, func)
            return func

        return decorator

    def delete(self, path: str):
        def decorator(func):
            self.add_route(HttpMethod.DELETE, path, func)
            return func

        return decorator
