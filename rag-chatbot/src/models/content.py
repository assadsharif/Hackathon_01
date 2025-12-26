"""
Content Data Models

Pydantic models for book content chunks and citations.
These models represent the core retrieval entities in the RAG system.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BookContentChunk(BaseModel):
    """
    A discrete paragraph-sized chunk of book content indexed for retrieval.

    Represents both the Postgres metadata and Qdrant vector payload.
    """

    chunk_id: UUID = Field(
        ...,
        description="Unique identifier for this chunk",
    )

    module_number: int = Field(
        ...,
        description="Module number in book (1-10)",
        ge=1,
        le=10,
    )

    module_name: str = Field(
        ...,
        description="Human-readable module name",
        max_length=255,
    )

    chapter_title: str = Field(
        ...,
        description="Chapter title",
        max_length=255,
    )

    section_id: str = Field(
        ...,
        description="Stable Docusaurus section ID (slug format)",
        max_length=255,
    )

    paragraph_index: int = Field(
        ...,
        description="0-based paragraph index within section",
        ge=0,
    )

    char_offset_start: int = Field(
        ...,
        description="Start character position in source file",
        ge=0,
    )

    char_offset_end: int = Field(
        ...,
        description="End character position in source file",
        gt=0,
    )

    text_content: str = Field(
        ...,
        description="Full paragraph text",
        min_length=1,
        max_length=2000,
    )

    token_count: int = Field(
        ...,
        description="Token count for this chunk (OpenAI tokenizer)",
        ge=50,
        le=400,
    )

    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when chunk was first indexed",
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when chunk was last updated",
    )

    # Optional: embedding vector (only populated when needed, not stored in Postgres)
    embedding_vector: Optional[list[float]] = Field(
        default=None,
        description="1536-dimensional embedding vector (from Qdrant)",
        exclude=True,  # Don't include in JSON serialization by default
    )

    @field_validator("section_id")
    @classmethod
    def validate_section_id(cls, v: str) -> str:
        """Validate section ID follows slug format."""
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError(
                f"section_id must be lowercase alphanumeric with hyphens only: {v}"
            )
        return v

    @field_validator("char_offset_end")
    @classmethod
    def validate_char_offsets(cls, v: int, info) -> int:
        """Validate end offset is greater than start offset."""
        if 'char_offset_start' in info.data:
            if v <= info.data['char_offset_start']:
                raise ValueError("char_offset_end must be greater than char_offset_start")
        return v

    @field_validator("text_content")
    @classmethod
    def validate_text_content(cls, v: str) -> str:
        """Validate text content is not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("text_content cannot be empty or whitespace-only")
        return v

    def to_qdrant_payload(self) -> dict:
        """
        Convert to Qdrant payload format.

        Returns:
            Dictionary suitable for Qdrant point payload
        """
        return {
            "chunk_id": str(self.chunk_id),
            "module_number": self.module_number,
            "module_name": self.module_name,
            "chapter_title": self.chapter_title,
            "section_id": self.section_id,
            "paragraph_index": self.paragraph_index,
            "text_content": self.text_content,
            "token_count": self.token_count,
        }

    @classmethod
    def from_qdrant_payload(cls, chunk_id: UUID, payload: dict) -> "BookContentChunk":
        """
        Create instance from Qdrant payload.

        Args:
            chunk_id: UUID of the chunk
            payload: Qdrant point payload

        Returns:
            BookContentChunk instance
        """
        return cls(
            chunk_id=chunk_id,
            module_number=payload['module_number'],
            module_name=payload['module_name'],
            chapter_title=payload['chapter_title'],
            section_id=payload['section_id'],
            paragraph_index=payload['paragraph_index'],
            char_offset_start=0,  # Not stored in Qdrant
            char_offset_end=len(payload['text_content']),
            text_content=payload['text_content'],
            token_count=payload['token_count'],
        )

    def generate_citation_url(self) -> str:
        """
        Generate Docusaurus URL for this chunk.

        Returns:
            URL string (e.g., "/docs/module-4/sensor-fusion#overview")
        """
        # Convert chapter title to URL slug
        chapter_slug = self.chapter_title.lower().replace(' ', '-').replace('&', 'and')
        # Remove special characters
        import re
        chapter_slug = re.sub(r'[^a-z0-9-]', '', chapter_slug)

        return f"/docs/module-{self.module_number}/{chapter_slug}#{self.section_id}"


class Citation(BaseModel):
    """
    A reference to a specific book section used in answer synthesis.

    Citations provide clickable links to the source material in the Docusaurus site.
    """

    text: str = Field(
        ...,
        description='Display text (e.g., "Module 5: Control Systems")',
        max_length=255,
    )

    url: str = Field(
        ...,
        description='Docusaurus link (e.g., "/docs/module-5/kinematics#inverse")',
    )

    chunk_id: Optional[UUID] = Field(
        default=None,
        description="Source chunk ID (for debugging and analytics)",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL starts with /docs/."""
        if not v.startswith("/docs/"):
            raise ValueError(f"Citation URL must start with /docs/: {v}")
        return v

    @field_validator("text")
    @classmethod
    def validate_text_format(cls, v: str) -> str:
        """Validate citation text follows expected format."""
        if not v.strip():
            raise ValueError("Citation text cannot be empty")

        # Recommended format: "Module N: Chapter Title" or "Module N: Section"
        # But we don't enforce this strictly to allow flexibility
        return v

    @classmethod
    def from_chunk(cls, chunk: BookContentChunk) -> "Citation":
        """
        Create citation from a book content chunk.

        Args:
            chunk: BookContentChunk instance

        Returns:
            Citation instance
        """
        text = f"Module {chunk.module_number}: {chunk.chapter_title}"
        url = chunk.generate_citation_url()

        return cls(
            text=text,
            url=url,
            chunk_id=chunk.chunk_id,
        )

    def to_markdown_link(self) -> str:
        """
        Convert citation to markdown link format.

        Returns:
            Markdown string: [text](url)
        """
        return f"[{self.text}]({self.url})"


class RetrievalResult(BaseModel):
    """
    Result from retrieval agent containing ranked chunks.

    Used internally in the orchestration pipeline.
    """

    chunks: list[BookContentChunk] = Field(
        default_factory=list,
        description="Ranked list of relevant chunks",
    )

    retrieval_latency_ms: int = Field(
        ...,
        description="Time spent retrieving chunks",
        ge=0,
    )

    total_candidates: int = Field(
        ...,
        description="Total number of chunks evaluated",
        ge=0,
    )

    query_mode: str = Field(
        ...,
        description="Retrieval mode used (full-book or selected-text)",
    )

    @property
    def chunk_count(self) -> int:
        """Number of chunks retrieved."""
        return len(self.chunks)

    @property
    def is_empty(self) -> bool:
        """Check if no chunks were retrieved."""
        return len(self.chunks) == 0
