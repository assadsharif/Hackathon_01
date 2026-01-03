"""
Retrieval Agent

Fetches relevant book content based on scope determined by Context Selection Agent.
Uses vector search for full-book mode, passes through selected text for selected-text mode.
"""

import time
from typing import List, Optional
from uuid import uuid4

from openai import OpenAI

from ..config.settings import Settings
from ..models.content import BookContentChunk, RetrievalResult
from ..services.storage import StorageService
from .context_selection import ContextSelectionResult


class RetrievalAgent:
    """
    Agent responsible for fetching relevant book content.

    Full-book mode: Query vector index (Qdrant) using semantic search
    Selected-text mode: Pass selected text directly as single "chunk"
    """

    def __init__(self, storage: StorageService, settings: Settings, openai_client: OpenAI):
        """
        Initialize retrieval agent.

        Args:
            storage: Storage service for database operations
            settings: Application settings
            openai_client: OpenAI client for generating embeddings
        """
        self.storage = storage
        self.settings = settings
        self.openai_client = openai_client

    async def retrieve(
        self,
        query: str,
        context_result: ContextSelectionResult,
    ) -> RetrievalResult:
        """
        Retrieve relevant book content based on context scope.

        Args:
            query: User's natural language question
            context_result: Result from context selection agent

        Returns:
            RetrievalResult with ranked chunks
        """
        start_time = time.time()

        if context_result.scope == "full-book":
            result = await self._retrieve_full_book(query)
        elif context_result.scope == "selected-text":
            result = await self._retrieve_selected_text(query, context_result)
        else:
            # Fallback to empty result
            result = RetrievalResult(
                chunks=[],
                retrieval_latency_ms=0,
                total_candidates=0,
                query_mode=context_result.scope,
            )

        # Update latency
        latency_ms = int((time.time() - start_time) * 1000)
        result.retrieval_latency_ms = latency_ms

        return result

    async def _retrieve_full_book(self, query: str) -> RetrievalResult:
        """
        Retrieve chunks using vector search across entire book.

        Args:
            query: User's question

        Returns:
            RetrievalResult with top-k chunks
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)

            # Search Qdrant for similar chunks
            result = await self.storage.search_similar_chunks(
                query_embedding=query_embedding,
                top_k=self.settings.chunk_retrieval_count,
                score_threshold=0.7,  # Cosine similarity threshold
            )

            return result

        except Exception as e:
            print(f"Error during full-book retrieval: {e}")
            return RetrievalResult(
                chunks=[],
                retrieval_latency_ms=0,
                total_candidates=0,
                query_mode="full-book",
            )

    async def _retrieve_selected_text(
        self,
        query: str,
        context_result: ContextSelectionResult,
    ) -> RetrievalResult:
        """
        Create synthetic chunk from selected text.

        Args:
            query: User's question
            context_result: Context with selected text content

        Returns:
            RetrievalResult with single synthetic chunk
        """
        selected_text = context_result.selected_text_content

        if not selected_text:
            return RetrievalResult(
                chunks=[],
                retrieval_latency_ms=0,
                total_candidates=0,
                query_mode="selected-text",
            )

        # Create synthetic chunk from selected text
        synthetic_chunk = BookContentChunk(
            chunk_id=uuid4(),
            module_number=0,  # Unknown module
            module_name="Selected Text",
            chapter_title="User Selection",
            section_id="selected-text",
            paragraph_index=0,
            char_offset_start=0,
            char_offset_end=len(selected_text),
            text_content=selected_text,
            token_count=self._estimate_token_count(selected_text),
        )

        return RetrievalResult(
            chunks=[synthetic_chunk],
            retrieval_latency_ms=0,
            total_candidates=1,
            query_mode="selected-text",
        )

    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI API.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536-dimensional)
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.settings.embedding_model,
            )
            return response.data[0].embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses simple heuristic: ~4 characters per token.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def _deduplicate_chunks(self, chunks: List[BookContentChunk]) -> List[BookContentChunk]:
        """
        Remove duplicate chunks from same section.

        Args:
            chunks: List of chunks

        Returns:
            Deduplicated list
        """
        seen_sections = set()
        deduplicated = []

        for chunk in chunks:
            section_key = (chunk.module_number, chunk.chapter_title, chunk.section_id)

            if section_key not in seen_sections:
                seen_sections.add(section_key)
                deduplicated.append(chunk)

        return deduplicated
