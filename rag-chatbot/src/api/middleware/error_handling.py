"""
Error Handling Middleware

Standardizes error responses across the API with consistent format.
Handles exceptions and converts them to user-friendly error messages.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import traceback


# Error code mapping
ERROR_CODES = {
    "RATE_LIMIT": {
        "status_code": 429,
        "message": "Rate limit exceeded. Please wait before trying again.",
    },
    "TIMEOUT": {
        "status_code": 504,
        "message": "Request timed out. Please try again.",
    },
    "SERVICE_UNAVAILABLE": {
        "status_code": 503,
        "message": "Service temporarily unavailable. Please try again later.",
    },
    "INVALID_INPUT": {
        "status_code": 400,
        "message": "Invalid input. Please check your request and try again.",
    },
    "NO_RESULTS": {
        "status_code": 200,  # Not an error, but no results found
        "message": "No relevant information found in the book content.",
    },
    "OUT_OF_SCOPE": {
        "status_code": 200,  # Not an error, but content is out of scope
        "message": "Your question is outside the scope of the Physical AI book.",
    },
    "INTERNAL_ERROR": {
        "status_code": 500,
        "message": "An internal error occurred. Please try again.",
    },
}


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware for standardized error responses.

    Catches exceptions and converts them to consistent JSON error responses.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Process request and handle any exceptions.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain

        Returns:
            Response or standardized error response
        """
        try:
            response = await call_next(request)
            return response

        except ValidationError as e:
            # Pydantic validation error
            return self._create_error_response(
                error_code="INVALID_INPUT",
                error_message=self._format_validation_error(e),
                status_code=400,
            )

        except TimeoutError:
            # Timeout error
            return self._create_error_response(
                error_code="TIMEOUT",
                error_message="Request timed out while processing your query.",
                status_code=504,
            )

        except ConnectionError:
            # Connection error to external services
            return self._create_error_response(
                error_code="SERVICE_UNAVAILABLE",
                error_message="Could not connect to required services. Please try again later.",
                status_code=503,
            )

        except Exception as e:
            # Unexpected error
            print(f"Unhandled exception: {e}")
            print(traceback.format_exc())

            return self._create_error_response(
                error_code="INTERNAL_ERROR",
                error_message="An unexpected error occurred. Please try again.",
                status_code=500,
            )

    def _create_error_response(
        self,
        error_code: str,
        error_message: str,
        status_code: int,
    ) -> JSONResponse:
        """
        Create standardized error response.

        Args:
            error_code: Error code constant
            error_message: User-friendly error message
            status_code: HTTP status code

        Returns:
            JSONResponse with error details
        """
        content = {
            "error_code": error_code,
            "error_message": error_message,
        }

        # Add retry_after for rate limit errors
        if error_code == "RATE_LIMIT":
            content["retry_after_seconds"] = 60

        return JSONResponse(
            status_code=status_code,
            content=content,
        )

    def _format_validation_error(self, error: ValidationError) -> str:
        """
        Format Pydantic validation error into user-friendly message.

        Args:
            error: Pydantic ValidationError

        Returns:
            Formatted error message
        """
        errors = error.errors()

        if not errors:
            return "Invalid input data."

        # Extract first error for simplicity
        first_error = errors[0]
        field = " -> ".join(str(loc) for loc in first_error['loc'])
        message = first_error['msg']

        return f"Invalid field '{field}': {message}"


def create_error_response_dict(
    error_code: str,
    custom_message: str | None = None,
) -> dict:
    """
    Helper function to create error response dictionary.

    Can be used in route handlers to return consistent error responses.

    Args:
        error_code: Error code from ERROR_CODES
        custom_message: Optional custom error message (overrides default)

    Returns:
        Dictionary suitable for JSONResponse

    Example:
        return JSONResponse(
            status_code=400,
            content=create_error_response_dict("INVALID_INPUT", "Query is too short")
        )
    """
    if error_code not in ERROR_CODES:
        error_code = "INTERNAL_ERROR"

    error_info = ERROR_CODES[error_code]
    message = custom_message or error_info["message"]

    response = {
        "error_code": error_code,
        "error_message": message,
    }

    # Add retry_after for rate limit errors
    if error_code == "RATE_LIMIT":
        response["retry_after_seconds"] = 60

    return response
