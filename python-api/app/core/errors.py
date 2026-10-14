"""Error format shared by the whole API: {"trace_id": "...", "message": "..."}."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    DomainError,
    InvalidRequestError,
    NotFoundError,
)

logger = logging.getLogger(__name__)

# Trace ids kept from the Go middleware
ROUTER_NOT_FOUND = "middlware-001"
JWT_AUTH_ERROR = "middlware-002"
REQUEST_INVALID = "middlware-003"
INTERNAL_ERROR = "internal-error"

DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidRequestError: status.HTTP_400_BAD_REQUEST,
}


class ErrorResponse(BaseModel):
    """Error body, used for the OpenAPI docs."""

    trace_id: str
    message: str


class AppError(Exception):
    """Raise from handlers to return a formatted error response."""

    def __init__(self, status_code: int, trace_id: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.trace_id = trace_id
        self.message = message


@contextmanager
def domain_errors(trace_id: str) -> Iterator[None]:
    """Turn DomainErrors raised inside the block into AppErrors carrying `trace_id`."""
    try:
        yield
    except DomainError as exc:
        status_code = DOMAIN_ERROR_STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
        raise AppError(status_code, trace_id, str(exc)) from exc


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

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=exc)
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, INTERNAL_ERROR, "internal server error"
        )
