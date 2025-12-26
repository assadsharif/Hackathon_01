"""
Answer Synthesis Agent

Generates natural language answers using retrieved content chunks and OpenAI LLM.
"""

import json
import time
from typing import List, Literal, Optional
from uuid import UUID

from openai import OpenAI
from pydantic import BaseModel, Field

from ..config.settings import Settings
from ..config.prompts import (
    SYNTHESIS_SYSTEM_PROMPT,
    SYNTHESIS_USER_TEMPLATE,
    format_chunks_for_synthesis,
    NO_INFORMATION_RESPONSE,
)
from ..models.content import BookContentChunk, RetrievalResult


class SynthesisResult(BaseModel):
    """Result from answer synthesis agent."""

    answer: str = Field(
        ...,
        description="Synthesized answer text",
    )

    chunk_ids_used: List[UUID] = Field(
        default_factory=list,
        description="Chunk IDs referenced in the answer",
    )

    confidence: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence level of the answer",
    )

    synthesis_latency_ms: int = Field(
        ...,
        description="Time spent generating answer",
        ge=0,
    )


class AnswerSynthesisAgent:
    """
    Agent responsible for generating natural language answers.

    Uses OpenAI GPT model to synthesize answers from retrieved book content chunks.
    """

    def __init__(self, openai_client: OpenAI, settings: Settings):
        """
        Initialize synthesis agent.

        Args:
            openai_client: OpenAI client
            settings: Application settings
        """
        self.openai_client = openai_client
        self.settings = settings

    async def synthesize(
        self,
        query: str,
        retrieval_result: RetrievalResult,
    ) -> SynthesisResult:
        """
        Synthesize answer from query and retrieved chunks.

        Args:
            query: User's question
            retrieval_result: Retrieved book content chunks

        Returns:
            SynthesisResult with answer and metadata
        """
        start_time = time.time()

        # Handle empty retrieval result
        if retrieval_result.is_empty:
            return self._create_no_information_response(start_time)

        # Generate answer using LLM
        try:
            result = await self._generate_answer(query, retrieval_result.chunks)
            latency_ms = int((time.time() - start_time) * 1000)
            result.synthesis_latency_ms = latency_ms
            return result

        except Exception as e:
            print(f"Error during synthesis: {e}")
            return self._create_error_response(start_time, str(e))

    async def _generate_answer(
        self,
        query: str,
        chunks: List[BookContentChunk],
    ) -> SynthesisResult:
        """
        Generate answer using OpenAI chat completion.

        Args:
            query: User's question
            chunks: Retrieved book content chunks

        Returns:
            SynthesisResult with answer
        """
        # Format chunks for prompt
        formatted_chunks = format_chunks_for_synthesis(
            [
                {
                    "chunk_id": str(chunk.chunk_id),
                    "text_content": chunk.text_content,
                    "module_name": chunk.module_name,
                    "chapter_title": chunk.chapter_title,
                }
                for chunk in chunks
            ]
        )

        # Construct user message
        user_message = SYNTHESIS_USER_TEMPLATE.format(
            query=query,
            chunks=formatted_chunks,
        )

        # Call OpenAI API
        try:
            response = self.openai_client.chat.completions.create(
                model=self.settings.chat_model,
                messages=[
                    {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,  # Lower temperature for more focused answers
                max_tokens=500,  # Limit response length
                timeout=self.settings.synthesis_timeout_seconds,
            )

            # Parse response
            answer_content = response.choices[0].message.content

            # Try to parse as JSON (expected format)
            try:
                answer_data = json.loads(answer_content)
                return SynthesisResult(
                    answer=answer_data.get("answer", answer_content),
                    chunk_ids_used=[
                        UUID(cid) for cid in answer_data.get("chunk_ids_used", [])
                    ],
                    confidence=answer_data.get("confidence", "medium"),
                    synthesis_latency_ms=0,  # Will be set by caller
                )
            except json.JSONDecodeError:
                # Fallback: use raw response as answer
                return SynthesisResult(
                    answer=answer_content,
                    chunk_ids_used=[chunk.chunk_id for chunk in chunks],
                    confidence="medium",
                    synthesis_latency_ms=0,
                )

        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")

    def _create_no_information_response(self, start_time: float) -> SynthesisResult:
        """Create response when no chunks were retrieved."""
        latency_ms = int((time.time() - start_time) * 1000)

        return SynthesisResult(
            answer=NO_INFORMATION_RESPONSE,
            chunk_ids_used=[],
            confidence="low",
            synthesis_latency_ms=latency_ms,
        )

    def _create_error_response(self, start_time: float, error: str) -> SynthesisResult:
        """Create response when synthesis fails."""
        latency_ms = int((time.time() - start_time) * 1000)

        return SynthesisResult(
            answer=f"I encountered an error while generating an answer: {error}",
            chunk_ids_used=[],
            confidence="low",
            synthesis_latency_ms=latency_ms,
        )

    def _extract_chunk_ids_from_answer(
        self,
        answer: str,
        available_chunks: List[BookContentChunk],
    ) -> List[UUID]:
        """
        Extract chunk IDs that were likely used in the answer.

        Fallback method when LLM doesn't return chunk_ids in JSON format.

        Args:
            answer: Generated answer text
            available_chunks: Chunks that were provided to LLM

        Returns:
            List of chunk IDs
        """
        # Simple heuristic: assume all chunks were used if we can't parse them
        return [chunk.chunk_id for chunk in available_chunks]
