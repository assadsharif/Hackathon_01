"""
Citation & Guardrails Agent

Generates precise citations, enforces content boundaries, validates response quality.
"""

import re
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..config.prompts import (
    AMBIGUOUS_QUESTION_BOUNDARY,
    CODE_GENERATION_BOUNDARY,
    EXTERNAL_TOPICS_BOUNDARY,
    INSUFFICIENT_CONTEXT_BOUNDARY,
    LOW_CONFIDENCE_BOUNDARY,
    OUT_OF_SCOPE_RESPONSE,
    SELECTED_TEXT_MISMATCH_BOUNDARY,
)
from ..models.content import BookContentChunk, Citation
from ..services.storage import StorageService
from .synthesis import SynthesisResult


class GuardrailsResult(BaseModel):
    """Result from citation & guardrails agent."""

    status: Literal["pass", "warn", "block"] = Field(
        ...,
        description="Validation status",
    )

    final_answer: str = Field(
        ...,
        description="Final answer text (original or modified)",
    )

    citations: List[Citation] = Field(
        default_factory=list,
        description="Generated citations",
    )

    boundary_message: Optional[str] = Field(
        default=None,
        description="Optional boundary reminder message",
    )

    violations_detected: List[str] = Field(
        default_factory=list,
        description="List of violation types if any",
    )


class CitationAndGuardrailsAgent:
    """
    Agent responsible for citation generation and content boundary enforcement.

    Validates that answers stay within book content boundaries and generates
    precise citations to source material.
    """

    def __init__(self, storage: StorageService):
        """
        Initialize citation & guardrails agent.

        Args:
            storage: Storage service for retrieving chunk metadata
        """
        self.storage = storage

    async def process(
        self,
        query: str,
        synthesis_result: SynthesisResult,
        query_mode: str,
    ) -> GuardrailsResult:
        """
        Process synthesis result to add citations and enforce guardrails.

        Args:
            query: Original user query
            synthesis_result: Result from synthesis agent
            query_mode: Query mode (full-book or selected-text)

        Returns:
            GuardrailsResult with citations and validation status
        """
        # Check guardrails
        violations = self._check_guardrails(synthesis_result.answer, query)

        # Block response if violations detected
        if violations:
            return self._create_blocked_response(violations)

        # Generate citations
        citations = await self._generate_citations(synthesis_result.chunk_ids_used)

        # Add boundary reminder if confidence is low
        boundary_message = None
        if synthesis_result.confidence == "low":
            boundary_message = (
                "Note: I have limited information on this topic in the book content."
            )

        # Determine status
        status = "warn" if boundary_message else "pass"

        return GuardrailsResult(
            status=status,
            final_answer=synthesis_result.answer,
            citations=citations,
            boundary_message=boundary_message,
            violations_detected=[],
        )

    async def _generate_citations(self, chunk_ids: List[UUID]) -> List[Citation]:
        """
        Generate citations from chunk IDs.

        Args:
            chunk_ids: List of chunk UUIDs used in answer

        Returns:
            List of Citation objects
        """
        if not chunk_ids:
            return []

        # Retrieve chunks from storage
        chunks = await self.storage.get_chunks_by_ids(chunk_ids)

        # Generate citations
        citations = []
        seen_citations = set()  # Deduplicate by URL

        for chunk in chunks:
            citation = Citation.from_chunk(chunk)

            # Deduplicate by URL
            if citation.url not in seen_citations:
                seen_citations.add(citation.url)
                citations.append(citation)

        return citations[:10]  # Limit to 10 citations

    def _check_guardrails(self, answer: str, query: str) -> List[str]:
        """
        Check answer against content boundary guardrails.

        Args:
            answer: Synthesized answer text
            query: Original user query

        Returns:
            List of violation types (empty if no violations)
        """
        violations = []

        # Check for code generation
        if self._contains_code(answer):
            violations.append("code_generation")

        # Check for out-of-scope content (enhanced - T053)
        if self._is_out_of_scope_enhanced(answer, query):
            violations.append("out_of_scope")

        # Check for ambiguous questions (T052)
        if self._is_ambiguous_question(query):
            violations.append("ambiguous_question")

        # Check for uncertain language (potential hallucination)
        if self._contains_uncertain_language(answer):
            violations.append("uncertain_language")

        return violations

    def _contains_code(self, text: str) -> bool:
        """
        Detect if text contains code blocks or code generation.

        Args:
            text: Text to check

        Returns:
            True if code detected
        """
        # Check for code blocks (markdown or plain)
        code_patterns = [
            r'```[\s\S]*?```',  # Markdown code blocks
            r'`[^`]+`',  # Inline code
            r'def\s+\w+\s*\(',  # Python function definitions
            r'function\s+\w+\s*\(',  # JavaScript function definitions
            r'class\s+\w+\s*[\({]',  # Class definitions
        ]

        for pattern in code_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _is_out_of_scope(self, answer: str, query: str) -> bool:
        """
        Detect if answer discusses topics outside Physical AI book scope.

        Args:
            answer: Synthesized answer
            query: Original query

        Returns:
            True if out of scope
        """
        # Out-of-scope topic keywords
        out_of_scope_keywords = [
            "medical advice",
            "legal advice",
            "financial advice",
            "current events",
            "news",
            "stock market",
            "cryptocurrency",
        ]

        answer_lower = answer.lower()

        for keyword in out_of_scope_keywords:
            if keyword in answer_lower:
                return True

        return False

    def _contains_uncertain_language(self, text: str) -> bool:
        """
        Detect uncertain language that may indicate hallucination.

        Args:
            text: Text to check

        Returns:
            True if uncertain language detected
        """
        uncertain_phrases = [
            r'\bI think\b',
            r'\bI believe\b',
            r'\bmaybe\b',
            r'\bperhaps\b',
            r'\bprobably\b',
            r'\bmight be\b',
            r'\bcould be\b',
        ]

        text_lower = text.lower()

        for pattern in uncertain_phrases:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _is_ambiguous_question(self, query: str) -> bool:
        """
        T052: Detect if a question is too broad/ambiguous and needs clarification.

        Ambiguous questions are very general and could relate to multiple modules
        or require significant context to answer properly.

        Args:
            query: User query text

        Returns:
            True if question is ambiguous and needs clarification
        """
        query_lower = query.lower()

        # Very general question patterns
        ambiguous_patterns = [
            r'^(what|how|why|when|where)\s+(is|are|do|does)\s+(robots?|humanoids?|ai)(\s+work)?\??$',
            r'^tell me about (robots?|humanoids?|ai|physical ai)\??$',
            r'^explain (robots?|humanoids?|ai|physical ai)\??$',
            r'^(what|how)\s+(is|are)\s+physical ai\??$',
            r'^(what|how)\s+(is|are)\s+embodied intelligence\??$',
        ]

        for pattern in ambiguous_patterns:
            if re.search(pattern, query_lower):
                return True

        # Extremely short queries (less than 5 words, excluding very specific terms)
        words = query_lower.split()
        if len(words) <= 3 and not any(
            term in query_lower
            for term in [
                "sensor fusion",
                "inverse kinematics",
                "pid control",
                "slam",
                "reinforcement learning",
                "neural network",
                "computer vision",
            ]
        ):
            # Short and vague questions like "how robots work?"
            return True

        return False

    def _is_out_of_scope_enhanced(self, answer: str, query: str) -> bool:
        """
        T053: Enhanced out-of-scope detection for topics outside the book.

        Detects questions about:
        - Code generation requests
        - External/unrelated topics
        - Implementation details for production systems
        - Current events, specific companies/products

        Args:
            answer: Synthesized answer
            query: Original query

        Returns:
            True if out of scope
        """
        query_lower = query.lower()
        answer_lower = answer.lower()

        # Code generation request patterns
        code_request_patterns = [
            r'\b(write|create|generate|implement|code|program)\s+(a|an|the)?\s*(function|class|script|program|code)',
            r'\bshow me (the )?(code|implementation)',
            r'\bgive me (the )?(code|implementation)',
            r'\b(python|javascript|c\+\+|java|rust)\s+(code|function|class)',
        ]

        for pattern in code_request_patterns:
            if re.search(pattern, query_lower):
                return True

        # External topics (expanded list - T053)
        external_topics = [
            "medical advice",
            "legal advice",
            "financial advice",
            "investment",
            "stock market",
            "cryptocurrency",
            "bitcoin",
            "current events",
            "latest news",
            "recent developments",
            "what happened",
            "breaking news",
            "today's",
            "this week",
            "this month",
            "2024",  # Specific years indicate current events
            "2025",
        ]

        # Check both query and answer for out-of-scope keywords
        for keyword in external_topics:
            if keyword in query_lower or keyword in answer_lower:
                return True

        # Detect questions about specific companies/products not in academic context
        commercial_patterns = [
            r'\b(boston dynamics|tesla|google|amazon|microsoft)\s+(product|robot|system)',
            r'\bhow (much|expensive)\s+(is|are|does|do)',  # Pricing questions
            r'\bwhere (can i|to)\s+(buy|purchase|get)',  # Commercial queries
        ]

        for pattern in commercial_patterns:
            if re.search(pattern, query_lower):
                return True

        return False

    def _create_blocked_response(self, violations: List[str]) -> GuardrailsResult:
        """
        Create blocked response when violations detected.

        Uses boundary message templates from T054.

        Args:
            violations: List of violation types

        Returns:
            GuardrailsResult with blocked status
        """
        # Determine appropriate boundary message (T054 templates)
        if "code_generation" in violations:
            boundary_message = CODE_GENERATION_BOUNDARY
        elif "ambiguous_question" in violations:
            boundary_message = AMBIGUOUS_QUESTION_BOUNDARY
        elif "out_of_scope" in violations:
            boundary_message = EXTERNAL_TOPICS_BOUNDARY
        elif "uncertain_language" in violations:
            boundary_message = LOW_CONFIDENCE_BOUNDARY
        else:
            boundary_message = OUT_OF_SCOPE_RESPONSE

        return GuardrailsResult(
            status="block",
            final_answer=boundary_message,
            citations=[],
            boundary_message=boundary_message,
            violations_detected=violations,
        )
