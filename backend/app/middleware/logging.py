"""Request / response logging middleware."""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request and its response status / duration."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        logger.info(
            "[{request_id}] → {method} {path}",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1_000

        logger.info(
            "[{request_id}] ← {status} ({duration:.1f}ms)",
            request_id=request_id,
            status=response.status_code,
            duration=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response
