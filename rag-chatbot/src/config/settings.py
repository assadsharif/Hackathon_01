"""
Application Settings Configuration

Centralized configuration management using Pydantic BaseSettings.
All settings are loaded from environment variables with validation.
"""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated on startup. Missing required settings
    will raise a validation error with a clear error message.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for embeddings and chat completion",
        min_length=20,
    )

    # Qdrant Configuration
    qdrant_url: str = Field(
        ...,
        description="Qdrant Cloud URL (e.g., https://xxx.cloud.qdrant.io)",
    )
    qdrant_api_key: str = Field(
        ...,
        description="Qdrant API key for authentication",
        min_length=20,
    )
    qdrant_collection: str = Field(
        default="physical-ai-book-v1",
        description="Qdrant collection name for book embeddings",
    )

    # Postgres Configuration
    postgres_url: str = Field(
        ...,
        description="Neon Postgres connection string",
    )

    # API Server Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host address",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
        ge=1024,
        le=65535,
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Rate Limiting Configuration
    rate_limit_queries_per_minute: int = Field(
        default=10,
        description="Maximum queries per session per minute",
        ge=1,
        le=100,
    )

    # Performance Tuning
    chunk_retrieval_count: int = Field(
        default=5,
        description="Number of chunks to retrieve from Qdrant per query",
        ge=1,
        le=20,
    )
    retrieval_timeout_seconds: int = Field(
        default=2,
        description="Timeout for vector retrieval operations",
        ge=1,
        le=10,
    )
    synthesis_timeout_seconds: int = Field(
        default=2,
        description="Timeout for LLM synthesis operations",
        ge=1,
        le=10,
    )

    # CORS Configuration (T062 - Phase 7)
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins for frontend requests (comma-separated in .env). "
                    "For production, include your Docusaurus domain: https://assadsharif.github.io",
    )

    # OpenAI Model Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model for vector generation",
    )
    chat_model: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI chat model for answer synthesis",
    )
    embedding_dimensions: int = Field(
        default=1536,
        description="Embedding vector dimensions (text-embedding-3-small)",
    )

    # Chunking Configuration (for indexing script)
    default_chunk_size: int = Field(
        default=250,
        description="Default token count per chunk when indexing",
        ge=50,
        le=500,
    )
    default_chunk_overlap: int = Field(
        default=50,
        description="Token overlap between consecutive chunks",
        ge=0,
        le=100,
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard Python logging levels."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v_upper

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | List[str]) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("qdrant_url")
    @classmethod
    def validate_qdrant_url(cls, v: str) -> str:
        """Ensure Qdrant URL uses HTTPS for cloud deployment."""
        if not v.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid Qdrant URL: {v}. Must start with http:// or https://"
            )
        return v

    @field_validator("postgres_url")
    @classmethod
    def validate_postgres_url(cls, v: str) -> str:
        """Validate Postgres connection string format."""
        if not v.startswith("postgres://") and not v.startswith("postgresql://"):
            raise ValueError(
                f"Invalid Postgres URL: {v}. Must start with postgres:// or postgresql://"
            )
        return v

    @property
    def total_timeout_seconds(self) -> int:
        """Calculate total timeout for query processing pipeline."""
        return self.retrieval_timeout_seconds + self.synthesis_timeout_seconds + 1

    def get_database_pool_config(self) -> dict:
        """Get recommended database connection pool configuration."""
        return {
            "min_size": 2,
            "max_size": 10,
            "timeout": 30,
            "command_timeout": 60,
        }


# Singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get application settings singleton.

    Settings are loaded once on first call and cached for subsequent calls.
    This ensures consistent configuration across the application.

    Returns:
        Settings: Validated application settings

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience function for testing
def reset_settings() -> None:
    """Reset settings singleton (for testing purposes only)."""
    global _settings
    _settings = None
