"""Error format shared by the whole API: {"trace_id": "...", "message": "..."}."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Trace ids kept from the Go middleware
ROUTER_NOT_FOUND = "middlware-001"
REQUEST_INVALID = "middlware-003"


class AppError(Exception):
    """Raise from use cases / handlers to return a formatted error response."""

    def __init__(self, status_code: int, trace_id: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.trace_id = trace_id
        self.message = message


def error_response(status_code: int, trace_id: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"trace_id": trace_id, "message": message},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.status_code, exc.trace_id, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return error_response(exc.status_code, ROUTER_NOT_FOUND, "router not found")
        return error_response(exc.status_code, "http-error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"][1:]) or "body"
        return error_response(
            status.HTTP_400_BAD_REQUEST, REQUEST_INVALID, f"{field}: {first['msg']}"
        )
