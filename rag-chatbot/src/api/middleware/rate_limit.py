"""
Rate Limiting Middleware

Implements sliding window rate limiting per session to prevent abuse.
Tracks query counts using Postgres analytics table.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import UUID
import json

from ...config.settings import get_settings
from ...services.storage import get_storage_service


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.

    Limits queries per session based on settings.rate_limit_queries_per_minute.
    Queries are tracked using the query_analytics table in Postgres.
    """

    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.storage = get_storage_service(self.settings)

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce rate limits.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain

        Returns:
            Response or rate limit error
        """
        # Only apply rate limiting to /v1/query endpoint
        if not request.url.path.startswith("/v1/query"):
            return await call_next(request)

        # Extract session_id from request body
        session_id = await self._extract_session_id(request)

        if session_id is None:
            # Can't rate limit without session_id, allow request
            return await call_next(request)

        # Check rate limit
        try:
            query_count = await self.storage.get_session_query_count(
                session_id=session_id,
                minutes=1,
            )

            if query_count >= self.settings.rate_limit_queries_per_minute:
                # Rate limit exceeded
                return JSONResponse(
                    status_code=429,
                    content={
                        "error_code": "RATE_LIMIT",
                        "error_message": (
                            f"Rate limit exceeded. Maximum {self.settings.rate_limit_queries_per_minute} "
                            f"queries per minute allowed. Please wait before submitting another query."
                        ),
                        "retry_after_seconds": 60,
                    },
                )

        except Exception as e:
            # If rate limit check fails, allow request (fail open)
            print(f"Rate limit check failed: {e}")

        # Proceed with request
        response = await call_next(request)
        return response

    async def _extract_session_id(self, request: Request) -> UUID | None:
        """
        Extract session_id from request body.

        Args:
            request: FastAPI request object

        Returns:
            Session UUID or None if not found
        """
        try:
            # Read body
            body_bytes = await request.body()

            # Parse JSON
            if body_bytes:
                body = json.loads(body_bytes.decode('utf-8'))
                session_id_str = body.get('session_id')

                if session_id_str:
                    return UUID(session_id_str)

        except Exception:
            pass

        return None
