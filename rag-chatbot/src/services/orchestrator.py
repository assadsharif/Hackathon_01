"""
Orchestrator Service

Coordinates the 4-agent pipeline for query processing:
1. Context Selection Agent → Determine retrieval scope
2. Retrieval Agent → Fetch relevant book content
3. Answer Synthesis Agent → Generate natural language answer
4. Citation & Guardrails Agent → Add citations and enforce boundaries
"""

import time
from uuid import UUID, uuid4

from openai import OpenAI

from ..agents.context_selection import ContextSelectionAgent
from ..agents.retrieval import RetrievalAgent
from ..agents.synthesis import AnswerSynthesisAgent
from ..agents.guardrails import CitationAndGuardrailsAgent
from ..config.settings import Settings
from ..models.query import QueryRequest, QueryResponse, QueryAnalytics
from ..services.storage import StorageService


class QueryOrchestrator:
    """
    Orchestrates the multi-agent pipeline for query processing.

    Pipeline Steps:
    1. Context Selection: Determine scope (full-book or selected-text)
    2. Retrieval: Fetch relevant chunks from Qdrant or use selected text
    3. Synthesis: Generate answer using OpenAI LLM
    4. Citation & Guardrails: Add citations and validate boundaries
    """

    def __init__(self, storage: StorageService, settings: Settings):
        """
        Initialize orchestrator with agents.

        Args:
            storage: Storage service for database operations
            settings: Application settings
        """
        self.storage = storage
        self.settings = settings

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

        # Initialize agents
        self.context_agent = ContextSelectionAgent()
        self.retrieval_agent = RetrievalAgent(storage, settings, self.openai_client)
        self.synthesis_agent = AnswerSynthesisAgent(self.openai_client, settings)
        self.guardrails_agent = CitationAndGuardrailsAgent(storage)

    async def process_query(self, request: QueryRequest) -> QueryResponse:
        """
        Process query through the 4-agent pipeline.

        Args:
            request: Query request from user

        Returns:
            QueryResponse with answer and citations
        """
        start_time = time.time()
        query_id = uuid4()

        try:
            # Step 1: Context Selection
            context_result = self.context_agent.determine_scope(request)

            # Check for context validation errors
            if context_result.validation_status == "error":
                return self._create_error_response(
                    request=request,
                    error_code="INVALID_INPUT",
                    error_message=context_result.message or "Invalid context",
                    latency_ms=int((time.time() - start_time) * 1000),
                )

            # Step 2: Retrieval
            retrieval_result = await self.retrieval_agent.retrieve(
                query=request.query,
                context_result=context_result,
            )

            # Step 3: Answer Synthesis
            synthesis_result = await self.synthesis_agent.synthesize(
                query=request.query,
                retrieval_result=retrieval_result,
            )

            # Step 4: Citation & Guardrails
            guardrails_result = await self.guardrails_agent.process(
                query=request.query,
                synthesis_result=synthesis_result,
                query_mode=request.mode,
            )

            # Calculate total latency
            total_latency_ms = int((time.time() - start_time) * 1000)

            # Create response
            response = QueryResponse(
                answer=guardrails_result.final_answer,
                citations=guardrails_result.citations,
                mode=request.mode,
                latency_ms=total_latency_ms,
                error_code=None,
                error_message=None,
            )

            # Store analytics
            await self._store_analytics(
                query_id=query_id,
                request=request,
                response=response,
                retrieval_latency_ms=retrieval_result.retrieval_latency_ms,
                synthesis_latency_ms=synthesis_result.synthesis_latency_ms,
                chunks_retrieved=retrieval_result.chunk_count,
                chunks_used=len(synthesis_result.chunk_ids_used),
            )

            return response

        except TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            return self._create_error_response(
                request=request,
                error_code="TIMEOUT",
                error_message="Request timed out. Please try again.",
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            print(f"Error processing query: {e}")
            return self._create_error_response(
                request=request,
                error_code="INTERNAL_ERROR",
                error_message="An error occurred while processing your question.",
                latency_ms=latency_ms,
            )

    def _create_error_response(
        self,
        request: QueryRequest,
        error_code: str,
        error_message: str,
        latency_ms: int,
    ) -> QueryResponse:
        """Create error response."""
        return QueryResponse(
            answer=error_message,
            citations=[],
            mode=request.mode,
            latency_ms=latency_ms,
            error_code=error_code,
            error_message=error_message,
        )

    async def _store_analytics(
        self,
        query_id: UUID,
        request: QueryRequest,
        response: QueryResponse,
        retrieval_latency_ms: int,
        synthesis_latency_ms: int,
        chunks_retrieved: int,
        chunks_used: int,
    ) -> None:
        """Store query analytics in Postgres."""
        try:
            analytics = QueryAnalytics(
                query_id=query_id,
                session_id=request.session_id,
                query_text=request.query,
                query_mode=request.mode,
                selected_text=request.selected_text,
                current_page_url=request.current_page_url,
                response_latency_ms=response.latency_ms,
                retrieval_latency_ms=retrieval_latency_ms,
                synthesis_latency_ms=synthesis_latency_ms,
                chunks_retrieved=chunks_retrieved,
                chunks_used=chunks_used,
                error_code=response.error_code,
            )

            await self.storage.store_query_analytics(analytics)

        except Exception as e:
            # Don't fail the request if analytics storage fails
            print(f"Failed to store analytics: {e}")
