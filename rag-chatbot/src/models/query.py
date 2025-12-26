"""
Query Data Models

Pydantic models for query requests, responses, and user context.
These models define the API contract between frontend and backend.
"""

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .content import Citation


class UserContext(BaseModel):
    """
    Metadata about user's current state in the documentation.

    Transient model that exists only in API requests.
    """

    current_page_url: str = Field(
        ...,
        description="Current documentation page URL",
    )

    active_theme: Optional[Literal["light", "dark"]] = Field(
        default="light",
        description="Current Docusaurus theme",
    )

    selected_text: Optional[str] = Field(
        default=None,
        description="Text highlighted by user (if mode=selected-text)",
        max_length=10000,
    )

    selection_start: Optional[int] = Field(
        default=None,
        description="Character offset start of selection",
        ge=0,
    )

    selection_end: Optional[int] = Field(
        default=None,
        description="Character offset end of selection",
        ge=0,
    )

    session_id: UUID = Field(
        ...,
        description="Current session UUID (from browser LocalStorage)",
    )

    @field_validator("current_page_url")
    @classmethod
    def validate_page_url(cls, v: str) -> str:
        """Validate page URL matches expected pattern."""
        if not (v.startswith("/docs/") or v.startswith("/Part-")):
            raise ValueError(
                f"Invalid page URL: {v}. Must start with /docs/ or /Part-"
            )
        return v

    @field_validator("selected_text")
    @classmethod
    def validate_selected_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate selected text is not empty or whitespace-only."""
        if v is not None:
            if not v.strip():
                raise ValueError("selected_text cannot be empty or whitespace-only")
        return v

    @field_validator("selection_end")
    @classmethod
    def validate_selection_offsets(cls, v: Optional[int], info) -> Optional[int]:
        """Validate selection offsets are consistent."""
        if v is not None and 'selection_start' in info.data:
            start = info.data.get('selection_start')
            if start is not None and v <= start:
                raise ValueError("selection_end must be greater than selection_start")

            # Validate selection length matches text length
            if 'selected_text' in info.data and info.data['selected_text'] is not None:
                expected_length = v - start
                actual_length = len(info.data['selected_text'])
                if abs(expected_length - actual_length) > 5:  # Allow small tolerance
                    raise ValueError(
                        f"Selection offsets ({expected_length}) don't match "
                        f"selected_text length ({actual_length})"
                    )
        return v


class QueryRequest(BaseModel):
    """
    Request payload for POST /v1/query endpoint.

    Represents a user's question submitted to the chatbot.
    """

    session_id: UUID = Field(
        ...,
        description="Frontend-generated session UUID",
    )

    query: str = Field(
        ...,
        description="User's natural language question",
        min_length=1,
        max_length=5000,
    )

    mode: Literal["full-book", "selected-text"] = Field(
        ...,
        description="Retrieval mode: full-book or selected-text",
    )

    selected_text: Optional[str] = Field(
        default=None,
        description="User-highlighted text (required if mode=selected-text)",
        max_length=10000,
    )

    current_page_url: Optional[str] = Field(
        default=None,
        description="Current documentation page URL",
    )

    user_context: Optional[UserContext] = Field(
        default=None,
        description="Additional user context metadata",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("query cannot be empty or whitespace-only")
        return v

    @field_validator("selected_text")
    @classmethod
    def validate_selected_text_mode(cls, v: Optional[str], info) -> Optional[str]:
        """Validate selected_text is provided when mode=selected-text."""
        if 'mode' in info.data and info.data['mode'] == 'selected-text':
            if v is None or not v.strip():
                raise ValueError(
                    "selected_text is required and cannot be empty when mode=selected-text"
                )
        return v


class QueryResponse(BaseModel):
    """
    Response payload for POST /v1/query endpoint.

    Contains the synthesized answer with citations and performance metrics.
    """

    answer: str = Field(
        ...,
        description="Synthesized answer text (empty if error)",
        max_length=2000,
    )

    citations: list[Citation] = Field(
        default_factory=list,
        description="List of source citations (max 10)",
        max_length=10,
    )

    mode: Literal["full-book", "selected-text"] = Field(
        ...,
        description="Echo of query mode from request",
    )

    latency_ms: int = Field(
        ...,
        description="Total response time in milliseconds",
        ge=0,
        lt=5000,  # Enforce 5-second timeout
    )

    error_code: Optional[str] = Field(
        default=None,
        description="Error code if request failed",
    )

    error_message: Optional[str] = Field(
        default=None,
        description="User-friendly error message",
    )

    @field_validator("citations")
    @classmethod
    def validate_citations(cls, v: list[Citation]) -> list[Citation]:
        """Validate citations don't contain duplicates."""
        urls = [c.url for c in v]
        if len(urls) != len(set(urls)):
            raise ValueError("citations cannot contain duplicate URLs")
        return v

    @field_validator("answer")
    @classmethod
    def validate_answer_with_error(cls, v: str, info) -> str:
        """Validate answer is empty if error_code is set."""
        if 'error_code' in info.data and info.data['error_code'] is not None:
            # If there's an error, answer should contain error explanation
            if not v:
                raise ValueError("answer must contain error explanation when error_code is set")
        return v

    @property
    def is_error(self) -> bool:
        """Check if response contains an error."""
        return self.error_code is not None

    @property
    def citation_count(self) -> int:
        """Number of citations in response."""
        return len(self.citations)


class QueryAnalytics(BaseModel):
    """
    Analytics record for query performance and usage tracking.

    Stored in Postgres query_analytics table.
    """

    query_id: UUID = Field(
        ...,
        description="Unique identifier for this query",
    )

    session_id: UUID = Field(
        ...,
        description="Frontend-generated session UUID",
    )

    query_text: str = Field(
        ...,
        description="User's question",
    )

    query_mode: Literal["full-book", "selected-text"] = Field(
        ...,
        description="Retrieval mode used",
    )

    selected_text: Optional[str] = Field(
        default=None,
        description="User-highlighted text (NULL if mode=full-book)",
    )

    current_page_url: Optional[str] = Field(
        default=None,
        description="Current documentation page",
    )

    response_latency_ms: int = Field(
        ...,
        description="Total pipeline latency",
        ge=0,
    )

    retrieval_latency_ms: Optional[int] = Field(
        default=None,
        description="Time spent in Retrieval Agent",
        ge=0,
    )

    synthesis_latency_ms: Optional[int] = Field(
        default=None,
        description="Time spent in LLM synthesis",
        ge=0,
    )

    chunks_retrieved: Optional[int] = Field(
        default=None,
        description="Number of chunks returned by retrieval",
        ge=0,
    )

    chunks_used: Optional[int] = Field(
        default=None,
        description="Number of chunks cited in answer",
        ge=0,
    )

    error_code: Optional[str] = Field(
        default=None,
        description="Error code if request failed",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when query was submitted",
    )

    @field_validator("chunks_used")
    @classmethod
    def validate_chunks_used(cls, v: Optional[int], info) -> Optional[int]:
        """Validate chunks_used <= chunks_retrieved."""
        if v is not None and 'chunks_retrieved' in info.data:
            retrieved = info.data.get('chunks_retrieved')
            if retrieved is not None and v > retrieved:
                raise ValueError(
                    f"chunks_used ({v}) cannot exceed chunks_retrieved ({retrieved})"
                )
        return v


class HealthCheckResponse(BaseModel):
    """
    Response payload for GET /v1/health endpoint.

    Provides service health status and dependent service availability.
    """

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Overall service health status",
    )

    version: str = Field(
        ...,
        description="API version",
    )

    services: dict[str, dict] = Field(
        default_factory=dict,
        description="Status of dependent services (qdrant, postgres, openai)",
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp",
    )

    @property
    def is_healthy(self) -> bool:
        """Check if service is fully healthy."""
        return self.status == "healthy"

    @property
    def is_degraded(self) -> bool:
        """Check if service is degraded but operational."""
        return self.status == "degraded"
