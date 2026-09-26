"""FastAPI application entrypoint.

Wires:
- ``GET /health`` — liveness check
- ``/api/runs`` router — list, tearsheet, trades
- CORS for ``QUANT_CORS_ORIGINS`` (comma-separated; default "*" for local dev)
- Global exception handlers that shape every error as §4.4's ``ApiError``
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from quant.api.routers.runs import router as runs_router

app = FastAPI(title="Quant Research Platform", version="0.1.0")

# --- CORS --------------------------------------------------------------

_default_origins = "*"
_raw_origins = os.environ.get("QUANT_CORS_ORIGINS", _default_origins)
_allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers -----------------------------------------------------------

app.include_router(runs_router)

# --- Exception handlers ------------------------------------------------


def _api_error(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {"code": code, "message": message, "details": details}
        },
    )


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Convert router-raised HTTPExceptions into §4.4 ApiError shape.

    Routers raise HTTPException with detail shaped as
    {"error": {"code", "message", "details"}}. If the detail already has
    that shape, unwrap it. Otherwise wrap the raw detail as a generic
    message with code derived from the HTTP status.
    """
    detail = exc.detail
    if (
        isinstance(detail, dict)
        and "error" in detail
        and isinstance(detail["error"], dict)
    ):
        payload = detail["error"]
        return _api_error(
            status_code=exc.status_code,
            code=str(payload.get("code", "INTERNAL")),
            message=str(payload.get("message", "")),
            details=payload.get("details"),
        )
    return _api_error(
        status_code=exc.status_code,
        code=_default_code_for_status(exc.status_code),
        message=str(detail) if detail else "",
        details=None,
    )


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Shape FastAPI's 422 validation errors as ApiError."""
    return _api_error(
        status_code=422,
        code="VALIDATION",
        message="request validation failed",
        details=exc.errors(),
    )


def _default_code_for_status(status_code: int) -> str:
    if status_code == 404:
        return "NOT_FOUND"
    if status_code == 422:
        return "VALIDATION"
    if status_code == 500:
        return "INTERNAL"
    return "HTTP_ERROR"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
