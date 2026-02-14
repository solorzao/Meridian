import logging
from datetime import datetime

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler matching .NET ErrorHandlingMiddleware behavior."""
    if isinstance(exc, ValueError):
        status_code = 400
        error_message = str(exc)
    elif isinstance(exc, KeyError):
        status_code = 404
        error_message = str(exc)
    elif isinstance(exc, PermissionError):
        status_code = 401
        error_message = "Unauthorized"
    else:
        status_code = 500
        error_message = "An unexpected error occurred"
        logger.exception("Unhandled exception: %s", exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_message,
            "statusCode": status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
