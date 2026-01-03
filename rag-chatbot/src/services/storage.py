"""
Storage Service

Provides abstractions for Postgres and Qdrant database operations.
Handles connection management, query execution, and data persistence.
"""

import asyncio
from typing import List, Optional
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, ScoredPoint, Filter, FieldCondition, MatchValue

from ..config.settings import Settings
from ..models.content import BookContentChunk, RetrievalResult
from ..models.query import QueryAnalytics


class StorageService:
    """
    Unified storage service for Postgres and Qdrant operations.

    Provides high-level methods for:
    - Retrieving book content chunks by vector similarity
    - Storing and querying analytics data
    - Health checks for dependent services
    """

    def __init__(self, settings: Settings):
        """
        Initialize storage service with configuration.

        Args:
            settings: Application settings
        """
        self.settings = settings

        # Qdrant client (synchronous)
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Postgres connection (will be managed per-request)
        self.postgres_url = settings.postgres_url

    def get_postgres_connection(self) -> psycopg.Connection:
        """
        Get a new Postgres connection.

        Returns:
            Postgres connection with dict_row factory

        Note:
            Caller is responsible for closing the connection.
        """
        conn = psycopg.connect(
            self.postgres_url,
            row_factory=dict_row,
        )
        return conn

    # ========================================================================
    # Vector Retrieval Operations
    # ========================================================================

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> RetrievalResult:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_embedding: Query embedding vector (1536-dimensional)
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            RetrievalResult with ranked chunks
        """
        import time
        start_time = time.time()

        try:
            # Search Qdrant
            search_results: List[ScoredPoint] = self.qdrant_client.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
            )

            # Convert to BookContentChunk objects
            chunks = []
            for result in search_results:
                chunk = BookContentChunk.from_qdrant_payload(
                    chunk_id=UUID(result.id),
                    payload=result.payload,
                )
                chunk.embedding_vector = result.vector  # Optional: include vector
                chunks.append(chunk)

            latency_ms = int((time.time() - start_time) * 1000)

            return RetrievalResult(
                chunks=chunks,
                retrieval_latency_ms=latency_ms,
                total_candidates=len(search_results),
                query_mode="full-book",
            )

        except Exception as e:
            # Return empty result on error
            latency_ms = int((time.time() - start_time) * 1000)
            return RetrievalResult(
                chunks=[],
                retrieval_latency_ms=latency_ms,
                total_candidates=0,
                query_mode="full-book",
            )

    async def get_chunk_by_id(self, chunk_id: UUID) -> Optional[BookContentChunk]:
        """
        Retrieve a single chunk by ID from Qdrant.

        Args:
            chunk_id: Chunk UUID

        Returns:
            BookContentChunk or None if not found
        """
        try:
            result = self.qdrant_client.retrieve(
                collection_name=self.settings.qdrant_collection,
                ids=[str(chunk_id)],
                with_payload=True,
                with_vectors=False,
            )

            if not result:
                return None

            point = result[0]
            chunk = BookContentChunk.from_qdrant_payload(
                chunk_id=UUID(point.id),
                payload=point.payload,
            )
            return chunk

        except Exception:
            return None

    async def get_chunks_by_ids(self, chunk_ids: List[UUID]) -> List[BookContentChunk]:
        """
        Retrieve multiple chunks by IDs from Qdrant.

        Args:
            chunk_ids: List of chunk UUIDs

        Returns:
            List of BookContentChunk objects
        """
        if not chunk_ids:
            return []

        try:
            results = self.qdrant_client.retrieve(
                collection_name=self.settings.qdrant_collection,
                ids=[str(cid) for cid in chunk_ids],
                with_payload=True,
                with_vectors=False,
            )

            chunks = []
            for point in results:
                chunk = BookContentChunk.from_qdrant_payload(
                    chunk_id=UUID(point.id),
                    payload=point.payload,
                )
                chunks.append(chunk)

            return chunks

        except Exception:
            return []

    # ========================================================================
    # Analytics Operations
    # ========================================================================

    async def store_query_analytics(self, analytics: QueryAnalytics) -> bool:
        """
        Store query analytics in Postgres.

        Args:
            analytics: QueryAnalytics record

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO query_analytics (
                            query_id, session_id, query_text, query_mode,
                            selected_text, current_page_url, response_latency_ms,
                            retrieval_latency_ms, synthesis_latency_ms,
                            chunks_retrieved, chunks_used, error_code, created_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        analytics.query_id,
                        analytics.session_id,
                        analytics.query_text,
                        analytics.query_mode,
                        analytics.selected_text,
                        analytics.current_page_url,
                        analytics.response_latency_ms,
                        analytics.retrieval_latency_ms,
                        analytics.synthesis_latency_ms,
                        analytics.chunks_retrieved,
                        analytics.chunks_used,
                        analytics.error_code,
                        analytics.created_at,
                    ))
                conn.commit()
            return True

        except Exception as e:
            print(f"Error storing analytics: {e}")
            return False

    async def get_session_query_count(
        self,
        session_id: UUID,
        minutes: int = 1
    ) -> int:
        """
        Get number of queries for a session in the last N minutes.

        Args:
            session_id: Session UUID
            minutes: Time window in minutes

        Returns:
            Query count
        """
        try:
            with self.get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*)
                        FROM query_analytics
                        WHERE session_id = %s
                          AND created_at > NOW() - INTERVAL '%s minutes'
                    """, (session_id, minutes))

                    result = cur.fetchone()
                    return result['count'] if result else 0

        except Exception:
            return 0

    # ========================================================================
    # Health Check Operations
    # ========================================================================

    async def check_qdrant_health(self) -> dict:
        """
        Check Qdrant service health.

        Returns:
            Dictionary with status and latency
        """
        import time

        try:
            start_time = time.time()
            collections = self.qdrant_client.get_collections()
            latency_ms = int((time.time() - start_time) * 1000)

            # Check if our collection exists
            collection_exists = any(
                c.name == self.settings.qdrant_collection
                for c in collections.collections
            )

            if not collection_exists:
                return {
                    "status": "unhealthy",
                    "latency_ms": latency_ms,
                    "error": f"Collection {self.settings.qdrant_collection} not found",
                }

            return {
                "status": "healthy",
                "latency_ms": latency_ms,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": 0,
                "error": str(e),
            }

    async def check_postgres_health(self) -> dict:
        """
        Check Postgres service health.

        Returns:
            Dictionary with status and latency
        """
        import time

        try:
            start_time = time.time()

            with self.get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()

            latency_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "healthy",
                "latency_ms": latency_ms,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": 0,
                "error": str(e),
            }

    async def check_all_services_health(self) -> dict:
        """
        Check health of all dependent services.

        Returns:
            Dictionary with status for each service
        """
        # Run health checks in parallel
        qdrant_health, postgres_health = await asyncio.gather(
            self.check_qdrant_health(),
            self.check_postgres_health(),
        )

        return {
            "qdrant": qdrant_health,
            "postgres": postgres_health,
        }

    # ========================================================================
    # Utility Methods
    # ========================================================================

    async def get_collection_stats(self) -> dict:
        """
        Get statistics about the Qdrant collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_info = self.qdrant_client.get_collection(
                collection_name=self.settings.qdrant_collection
            )

            return {
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status,
            }

        except Exception as e:
            return {
                "error": str(e),
            }

    def close(self) -> None:
        """
        Close all connections and cleanup resources.

        Note:
            This should be called when shutting down the application.
        """
        # Qdrant client doesn't require explicit cleanup
        pass


# ============================================================================
# Singleton Factory
# ============================================================================

_storage_service: Optional[StorageService] = None


def get_storage_service(settings: Settings) -> StorageService:
    """
    Get or create storage service singleton.

    Args:
        settings: Application settings

    Returns:
        StorageService instance
    """
    global _storage_service

    if _storage_service is None:
        _storage_service = StorageService(settings)

    return _storage_service


def reset_storage_service() -> None:
    """Reset storage service singleton (for testing purposes only)."""
    global _storage_service

    if _storage_service is not None:
        _storage_service.close()
        _storage_service = None
