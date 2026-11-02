import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

from gaitmate_api.config import settings
from gaitmate_api.logging_config import configure_logging, log_event
from gaitmate_api.responses import ApiError, ApiResponse, ErrorDetail, ErrorResponse


class HealthData(BaseModel):
    status: str = "ok"
    service: str = "gaitmate-api"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


def _request_id(request: Request) -> str:
    return str(request.state.request_id)


def _log_path(request: Request) -> str:
    route_path = getattr(request.scope.get("route"), "path", None)
    return route_path if isinstance(route_path, str) else "<unmatched>"


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ApiError(code=code, message=message, details=details),
        request_id=_request_id(request),
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True),
        headers={"X-Request-ID": _request_id(request)},
    )


def create_app() -> FastAPI:
    configure_logging()
    api = FastAPI(title="GaitMate API", version="0.1.0")

    @api.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.request_id = str(uuid4())
        started = monotonic()
        try:
            response = await call_next(request)
        except Exception as exc:
            log_event(
                logging.ERROR,
                "request_failed",
                request_id=_request_id(request),
                method=request.method,
                path=_log_path(request),
                status_code=500,
                duration_ms=round((monotonic() - started) * 1000, 2),
                exception_type=type(exc).__name__,
            )
            return _error_response(request, 500, "INTERNAL_ERROR", "Internal server error")
        response.headers["X-Request-ID"] = _request_id(request)
        log_event(
            logging.INFO,
            "request_completed",
            request_id=_request_id(request),
            method=request.method,
            path=_log_path(request),
            status_code=response.status_code,
            duration_ms=round((monotonic() - started) * 1000, 2),
        )
        return response

    api.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.web_origin],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID"],
    )

    @api.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(part) for part in error["loc"]),
                message=str(error["msg"]),
                type=str(error["type"]),
            )
            for error in exc.errors()
        ]
        return _error_response(
            request, 422, "VALIDATION_ERROR", "Request validation failed", details
        )

    @api.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        codes = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
        }
        code = codes.get(exc.status_code, "HTTP_ERROR")
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return _error_response(request, exc.status_code, code, message)

    @api.get("/api/v1/health", response_model=ApiResponse[HealthData])
    def health() -> ApiResponse[HealthData]:
        return ApiResponse(data=HealthData())

    return api


app = create_app()
