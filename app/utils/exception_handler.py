import logging
import traceback
from datetime import datetime, timezone
from os import getenv
from typing import Any

from fastapi import HTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

DEBUG = getenv("DEBUG", "false").lower() in ("1", "true", "yes")

MAX_TRACEBACK_CHARS = int(getenv("MAX_TRACEBACK_CHARS", "10000"))


def _make_base_payload(request: Request, exc: Exception) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "path": request.url.path,
        "method": request.method,
        "type": type(exc).__name__,
        "message": str(exc) or repr(exc),
    }


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while handling request %s %s", request.method, request.url)

    if isinstance(exc, HTTPException):
        content = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "path": request.url.path,
            "method": request.method,
            "type": type(exc).__name__,
            "message": exc.detail if hasattr(exc, "detail") else str(exc),
        }
        return JSONResponse(status_code=exc.status_code, content=content)

    if isinstance(exc, RequestValidationError):
        content = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "path": request.url.path,
            "method": request.method,
            "type": type(exc).__name__,
            "message": "Validation error",
            "errors": exc.errors() if hasattr(exc, "errors") else None,
        }
        return JSONResponse(status_code=422, content=content)

    base = _make_base_payload(request, exc)

    if DEBUG:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        if len(tb) > MAX_TRACEBACK_CHARS:
            tb = tb[:MAX_TRACEBACK_CHARS] + "\n\n[truncated]"
        base["traceback"] = tb

    return JSONResponse(status_code=500, content=base)
