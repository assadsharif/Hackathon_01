"""
Context Selection Agent

Determines retrieval scope based on query mode (full-book vs selected-text)
and validates context boundaries.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..models.query import QueryRequest, UserContext


class ContextSelectionResult(BaseModel):
    """Result from context selection agent."""

    scope: Literal["full-book", "selected-text"] = Field(
        ...,
        description="Determined retrieval scope",
    )

    validation_status: Literal["valid", "error", "warning"] = Field(
        ...,
        description="Validation status of the context",
    )

    message: Optional[str] = Field(
        default=None,
        description="Optional user-facing message",
    )

    selected_text_content: Optional[str] = Field(
        default=None,
        description="Validated selected text content (if mode=selected-text)",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


class ContextSelectionAgent:
    """
    Agent responsible for determining retrieval scope based on query mode.

    Decision Rules:
    - If mode=full-book: Always use full book retrieval scope
    - If mode=selected-text AND selection exists: Use ONLY the selected text
    - If mode=selected-text AND selection is missing/empty: Return ERROR
    - If selected text is too short (<50 characters): Suggest switching to full-book mode
    """

    MIN_SELECTION_LENGTH = 50  # Minimum characters for meaningful selected text

    def determine_scope(self, request: QueryRequest) -> ContextSelectionResult:
        """
        Determine retrieval scope based on query request.

        Args:
            request: Query request with mode and optional selection

        Returns:
            ContextSelectionResult with scope and validation status
        """
        # Full-book mode is straightforward
        if request.mode == "full-book":
            return self._handle_full_book_mode(request)

        # Selected-text mode requires validation
        elif request.mode == "selected-text":
            return self._handle_selected_text_mode(request)

        else:
            # Invalid mode (should be caught by Pydantic validation)
            return ContextSelectionResult(
                scope="full-book",  # Fallback to full-book
                validation_status="error",
                message=f"Invalid query mode: {request.mode}",
                metadata={"fallback": True},
            )

    def _handle_full_book_mode(self, request: QueryRequest) -> ContextSelectionResult:
        """Handle full-book mode query."""
        return ContextSelectionResult(
            scope="full-book",
            validation_status="valid",
            message=None,
            metadata={
                "current_page": request.current_page_url,
                "selection_length": 0,
            },
        )

    def _handle_selected_text_mode(self, request: QueryRequest) -> ContextSelectionResult:
        """Handle selected-text mode query with validation."""
        # Check if selected text exists
        if not request.selected_text or not request.selected_text.strip():
            return ContextSelectionResult(
                scope="selected-text",
                validation_status="error",
                message=(
                    "Selected-text mode requires highlighted text. "
                    "Please select text on the page or switch to full-book mode."
                ),
                metadata={
                    "error_type": "missing_selection",
                },
            )

        selected_text = request.selected_text.strip()
        selection_length = len(selected_text)

        # Check if selection is too short
        if selection_length < self.MIN_SELECTION_LENGTH:
            return ContextSelectionResult(
                scope="selected-text",
                validation_status="warning",
                message=(
                    f"Your selection is very short ({selection_length} characters). "
                    f"Consider selecting more text or switching to full-book mode for better results."
                ),
                selected_text_content=selected_text,
                metadata={
                    "selection_length": selection_length,
                    "warning_type": "short_selection",
                },
            )

        # Validate selection length is reasonable (not too long)
        MAX_SELECTION_LENGTH = 5000
        if selection_length > MAX_SELECTION_LENGTH:
            # Truncate with warning
            truncated_text = selected_text[:MAX_SELECTION_LENGTH]
            return ContextSelectionResult(
                scope="selected-text",
                validation_status="warning",
                message=(
                    f"Your selection was very long ({selection_length} characters) and has been "
                    f"truncated to {MAX_SELECTION_LENGTH} characters. Consider selecting a smaller "
                    f"section for more focused answers."
                ),
                selected_text_content=truncated_text,
                metadata={
                    "selection_length": selection_length,
                    "truncated_to": MAX_SELECTION_LENGTH,
                    "warning_type": "long_selection",
                },
            )

        # Selection is valid
        return ContextSelectionResult(
            scope="selected-text",
            validation_status="valid",
            message=None,
            selected_text_content=selected_text,
            metadata={
                "selection_length": selection_length,
                "current_page": request.current_page_url,
            },
        )

    def validate_context(self, user_context: Optional[UserContext]) -> bool:
        """
        Validate user context metadata.

        Args:
            user_context: Optional user context

        Returns:
            True if valid, False otherwise
        """
        if user_context is None:
            return True  # Context is optional

        # Validate selection offsets match text length
        if user_context.selected_text:
            if user_context.selection_start is not None and user_context.selection_end is not None:
                expected_length = user_context.selection_end - user_context.selection_start
                actual_length = len(user_context.selected_text)

                # Allow small tolerance for whitespace differences
                if abs(expected_length - actual_length) > 10:
                    return False

        return True
