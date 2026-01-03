"""
Query Endpoint

Handles POST /v1/query requests for chatbot queries.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from ...config.settings import Settings, get_settings
from ...services.storage import StorageService, get_storage_service
from ...services.orchestrator import QueryOrchestrator
from ...models.query import QueryRequest, QueryResponse


router = APIRouter()
logger = logging.getLogger(__name__)


def get_orchestrator(
    settings: Settings = Depends(get_settings),
    storage: StorageService = Depends(lambda: get_storage_service(get_settings())),
) -> QueryOrchestrator:
    """
    Dependency to get orchestrator instance.

    Args:
        settings: Application settings
        storage: Storage service

    Returns:
        QueryOrchestrator instance
    """
    return QueryOrchestrator(storage=storage, settings=settings)


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Submit Chatbot Query",
    description="Submit a question to the RAG chatbot (full-book or selected-text mode)",
)
async def submit_query(
    request: QueryRequest,
    orchestrator: QueryOrchestrator = Depends(get_orchestrator),
) -> QueryResponse:
    """
    Process a chatbot query through the multi-agent pipeline.

    **Request Body:**
    - `session_id`: UUID for session tracking
    - `query`: User's natural language question (1-5000 chars)
    - `mode`: "full-book" or "selected-text"
    - `selected_text`: Required if mode="selected-text"
    - `current_page_url`: Optional page context

    **Response:**
    - `answer`: Synthesized answer text
    - `citations`: List of source citations
    - `mode`: Echo of query mode
    - `latency_ms`: Total response time
    - `error_code`: Set if request failed
    - `error_message`: User-friendly error message

    **Query Modes:**

    **Full-book mode:**
    - Searches entire book using vector similarity
    - Returns answer with citations from relevant chapters
    - Best for: General questions, concept explanations

    **Selected-text mode:**
    - Answers based ONLY on highlighted text
    - Returns answer constrained to selection
    - Best for: Understanding specific passages

    **Error Codes:**
    - `RATE_LIMIT`: Too many queries (wait before retrying)
    - `TIMEOUT`: Request took too long
    - `SERVICE_UNAVAILABLE`: Database connection failed
    - `INVALID_INPUT`: Invalid request parameters
    - `NO_RESULTS`: No relevant book content found
    - `OUT_OF_SCOPE`: Question outside book scope
    - `INTERNAL_ERROR`: Unexpected error

    **Example Request (Full-book):**
    ```json
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "query": "What is sensor fusion?",
      "mode": "full-book",
      "current_page_url": "/docs/module-4/perception"
    }
    ```

    **Example Request (Selected-text):**
    ```json
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "query": "Explain this concept in simpler terms",
      "mode": "selected-text",
      "selected_text": "Inverse kinematics calculates joint angles...",
      "current_page_url": "/docs/module-5/control"
    }
    ```

    **Example Response:**
    ```json
    {
      "answer": "Sensor fusion is the process of combining data...",
      "citations": [
        {
          "text": "Module 4: Perception Systems",
          "url": "/docs/module-4/sensor-fusion#overview"
        }
      ],
      "mode": "full-book",
      "latency_ms": 2350
    }
    ```
    """
    logger.info(
        f"Query received: session={request.session_id}, mode={request.mode}, "
        f"query_length={len(request.query)}"
    )

    try:
        # Process query through orchestrator
        response = await orchestrator.process_query(request)

        logger.info(
            f"Query processed: session={request.session_id}, latency={response.latency_ms}ms, "
            f"citations={response.citation_count}, error={response.error_code}"
        )

        return response

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your question.",
        )
