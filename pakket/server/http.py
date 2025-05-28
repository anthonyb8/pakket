from enum import Enum
from dataclasses import dataclass
import inspect
from typing import Any, Callable, Dict
import re
import json
from urllib.parse import urlparse, parse_qs
from pydantic import ValidationError, create_model
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
    PUT = "PUT"
    DELETE = "DELETE"

    @staticmethod
    def from_str(s: str) -> "HttpMethod":
        match s:
            case "GET":
                return HttpMethod.GET
            case "POST":
                return HttpMethod.POST
            case "PUT":
                return HttpMethod.PUT
            case "DELETE":
                return HttpMethod.DELETE
            case _:
                raise ValueError(f"Unknown HTTP method: {s}")


@dataclass
class HttpRequest:
    method: HttpMethod
    headers: Dict[str, str]
    path: str
    query: Dict[str, Any]
    body: Dict[str, Any]

    def match_path(self, template: str):
        """Matches template path to user passed path."""
        pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", template)
        match = re.fullmatch(pattern, self.path)
        if match:
            path_args = match.groupdict()
            return {**path_args, **self.query, **self.body}

        return None

    @staticmethod
    def from_bytes(raw: bytes) -> "HttpRequest":
        """Construct HttpRequest from the raw message bytes."""
        # Split Head and Body
        head, _, body = raw.partition(b"\r\n\r\n")
        header_str = head.decode("utf-8", errors="replace")
        head_lines = header_str.splitlines()

        # Start Line
        method, url, _ = head_lines[0].split(" ")
        parsed = urlparse(url)
        query_params = {}
        for k, v in parse_qs(parsed.query).items():
            if len(v) == 1:
                query_params[k] = v[0]

        # Headers
        headers = {}
        for line in head_lines[1:]:
            if not line.strip():
                continue
            key, value = line.split(":", 1)
            headers[key.lower()] = value

        # Body
        body_str = body.decode("utf-8", errors="replace")
        body = json.loads(body_str) if body_str else {}

        return HttpRequest(
            HttpMethod.from_str(method),
            headers,
            parsed.path,
            query_params,
            body,
        )


@dataclass
class HttpResponse(Message):
    statuscode: StatusCode
    headers: Dict[str, str]
    body: bytes

    def to_bytes(self) -> bytes:
        """Convert to bytes ready for transportation."""
        msg = b""
        status_code, status_text = self.statuscode.value
        msg += f"HTTP/1.1 {status_code} {status_text}\r\n".encode("utf-8")

        for k, v in self.headers.items():
            msg += f"{k}: {v}\r\n".encode("utf-8")
        msg += b"\r\n"
        return msg + self.body

    @staticmethod
    def ok(data: Any, code: StatusCode = StatusCode.OK) -> "HttpResponse":
        raw = json.dumps({"status": "ok", "data": data}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(raw)),
        }
        return HttpResponse(code, headers, raw)

    @staticmethod
    def error(msg: str, code: StatusCode) -> "HttpResponse":
        body = json.dumps({"status": "error", "error": msg}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
        }
        return HttpResponse(code, headers, body)


def validate_data(func: Callable, data: dict) -> dict:
    """
    Valdates date against a funcs expected arguement types.

    Return:
        - pydantic.BaseModel
    """
    fields = {}

    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        annotation = (
            param.annotation if param.annotation is not inspect._empty else Any
        )
        default = param.default if param.default is not inspect._empty else ...
        fields[name] = (annotation, default)

    model = create_model("ValidationModel", **fields)

    try:
        validated = model.model_validate(data)
        return dict(validated)
    except ValidationError as e:
        raise (e)


class Router(Service):
    def __init__(self):
        self.routes = {}

    def add_route(self, method: HttpMethod, path: str, func: Callable):
        """Add new routes to instance."""
        self.routes.setdefault(method, []).append((path, func))

    def route(self, request: HttpRequest) -> HttpResponse:
        """Route request to proper endpoint and calls handler."""
        method_routes = self.routes.get(request.method, [])

        for temp, func in method_routes:
            args = request.match_path(temp)
            if args:
                try:
                    data = validate_data(func, args)
                    return func(**data)
                except Exception as e:
                    return HttpResponse.error(str(e), StatusCode.BAD_REQUEST)

        return HttpResponse.error("Bad endpoint", StatusCode.NOT_FOUND)

    def call(self, msg: bytes) -> Message:
        """Main entry point, recieves request msg in raw bytes."""
        http_req = HttpRequest.from_bytes(msg)
        http_response = self.route(http_req)
        return http_response

    def get(self, path: str):
        """Convenient way to add a GET path with decorator"""

        def decorator(func):
            self.add_route(HttpMethod.GET, path, func)
            return func

        return decorator

    def post(self, path: str):
        """Convenient way to add a POST path with decorator"""

        def decorator(func):
            self.add_route(HttpMethod.POST, path, func)
            return func

        return decorator

    def put(self, path: str):
        """Convenient way to add a PUT path with decorator"""

        def decorator(func):
            self.add_route(HttpMethod.PUT, path, func)
            return func

        return decorator

    def delete(self, path: str):
        """Convenient way to add a DELETE path with decorator"""

        def decorator(func):
            self.add_route(HttpMethod.DELETE, path, func)
            return func

        return decorator
