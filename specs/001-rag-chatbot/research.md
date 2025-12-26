# Research & Technology Decisions: RAG Chatbot

**Feature**: Integrated RAG Chatbot for Physical AI Book
**Date**: 2025-12-25
**Phase**: Phase 0 (Research)

## Research Questions Resolved

This document captures all technology decisions, rationale, and alternatives considered for the RAG chatbot architecture.

---

## 1. Vector Embedding Model Selection

### Decision
Use **OpenAI text-embedding-3-small** for book content and query embeddings.

### Rationale
- **Cost Efficiency**: text-embedding-3-small is significantly cheaper ($0.02/1M tokens) vs text-embedding-3-large ($0.13/1M tokens)
- **Performance**: 1536-dimensional embeddings provide sufficient semantic accuracy for educational content retrieval
- **Free Tier Compatibility**: Smaller embedding size (1536 vs 3072) allows indexing more book chunks within Qdrant's 1GB free tier
- **Retrieval Quality**: Benchmark studies show <2% accuracy difference for domain-specific QA tasks compared to larger models
- **Latency**: Smaller embedding models have lower API latency (~50ms vs ~100ms per batch)

### Alternatives Considered
| Model | Dimensions | Cost/1M Tokens | Why Rejected |
|-------|------------|----------------|--------------|
| text-embedding-3-large | 3072 | $0.13 | Higher cost, minimal accuracy gain for educational content, larger storage footprint |
| text-embedding-ada-002 | 1536 | $0.10 | Deprecated, replaced by text-embedding-3-small |
| Sentence-BERT (open-source) | 768 | Free (self-host) | Requires self-hosting infrastructure, breaks "managed services only" simplicity principle |
| Cohere Embed v3 | 1024 | $0.10 | Additional vendor dependency, no cost advantage |

### Validation Plan
- Index 10-chapter sample with text-embedding-3-small
- Run 50 test queries, measure retrieval accuracy (precision@5)
- If precision <70%, escalate to text-embedding-3-large

---

## 2. Book Content Chunking Strategy

### Decision
Use **paragraph-level chunking (~200-300 tokens)** with 50-token overlap between chunks.

### Rationale
- **Citation Granularity**: Paragraph-level chunks enable precise citations to specific concepts (vs entire sections)
- **Context Completeness**: 200-300 tokens provide enough context for LLM synthesis without overwhelming the prompt
- **Free Tier Fit**: Estimated 7 modules × 50 chapters × 10 paragraphs/chapter = ~3,500 chunks × 1536 dims = ~21MB embeddings (well under 1GB limit)
- **Retrieval Quality**: Paragraph-level semantic search balances specificity (not too broad) with context (not too granular)
- **Overlap Strategy**: 50-token overlap ensures concepts spanning paragraph boundaries aren't lost

### Alternatives Considered
| Strategy | Chunk Size | Why Rejected |
|----------|------------|--------------|
| Sentence-level | ~50 tokens | Too granular, citations would point to incomplete thoughts, higher vector count (risk free tier limits) |
| Section-level | ~500-800 tokens | Citations too broad ("see entire section"), harder to pinpoint specific concepts |
| Sliding window (100 tokens) | 100 tokens | Too many overlapping chunks, redundancy in retrieval results, inefficient storage |
| Semantic chunking (LLM-based) | Variable | Requires additional LLM calls for chunking, breaks "simplicity" principle, adds latency |

### Implementation Notes
- Use Docusaurus markdown structure to detect paragraph boundaries (double newlines)
- Store chunk metadata: `{chunk_id, module, chapter, section_id, paragraph_index, char_offset_start, char_offset_end}`
- If a paragraph exceeds 300 tokens, split at sentence boundaries

---

## 3. Session ID Generation Strategy

### Decision
Use **frontend-generated UUIDs** for session identification (no backend session table).

### Rationale
- **Simplicity**: No backend session management, no database table for session tracking
- **Privacy**: Session IDs are ephemeral, stored only in browser LocalStorage, never transmitted to backend beyond API calls
- **Stateless Backend**: FastAPI remains stateless for session management, easier to scale horizontally
- **Browser Native**: JavaScript `crypto.randomUUID()` provides secure, collision-resistant UUIDs

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| Backend-generated tokens (JWT) | Adds backend complexity (token signing/verification), requires session table, overkill for anonymous sessions |
| Cookie-based sessions | Requires backend cookie management, GDPR consent implications, less flexible than LocalStorage |
| IP-based identification | Not reliable (NAT, VPNs), privacy concerns, poor UX for mobile users |
| No session tracking | Breaks conversation history requirement (FR-007), cannot implement rate limiting per user |

### Implementation Notes
- Generate UUID on first chatbot interaction: `const sessionId = crypto.randomUUID()`
- Store in LocalStorage: `localStorage.setItem('chatbot_session_id', sessionId)`
- Include in all API requests: `{"session_id": sessionId, ...}`
- Backend uses session_id for rate limiting and analytics only (no persistent session state)

---

## 4. Rate Limiting Implementation

### Decision
Use **in-memory sliding window rate limiter** with Redis (optional) for production.

### Rationale
- **FR-011 Requirement**: Must limit to 10 queries/min per user
- **Stateless Backend**: In-memory limiter (Python dict with timestamps) works for single-instance MVP
- **Production Path**: Redis sliding window for multi-instance deployments (if needed)
- **Cost**: Redis not required for Phase 2 MVP, can use managed Redis free tier if scaling

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| Fixed window (reset every minute) | Allows burst of 10 queries at 0:59 + 10 at 1:00 = 20 queries in 2 seconds, not true rate limiting |
| Token bucket | More complex implementation, sliding window is simpler and sufficient for educational use case |
| API Gateway rate limiting (e.g., Nginx) | Requires infrastructure change, prefer application-level control for Phase 2 MVP |
| No rate limiting | Violates FR-011, risk of API cost overruns from abuse |

### Implementation Notes
- Middleware tracks: `{session_id: [(timestamp1, timestamp2, ...)]}`
- On each request: filter timestamps older than 60 seconds, count remaining
- If count ≥ 10, return 429 with retry-after header
- Cleanup: Remove session entries older than 1 hour to prevent memory leak

---

## 5. Deployment Strategy

### Decision
Use **single Docker container** with FastAPI + Postgres client + Qdrant client for Phase 2 MVP.

### Rationale
- **Simplicity**: Single container deployment to Render/Railway/Fly.io free tiers
- **Free Tier Fit**: No separate container orchestration needed (Kubernetes overkill)
- **Cost**: Managed Postgres (Neon) and Qdrant (cloud) are external, no self-hosting
- **Scaling Path**: If needed, can extract to microservices later (Orchestrator, Indexing separated)

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| Separate containers (API, Worker, DB) | Premature complexity for Phase 2, harder to deploy on free tiers |
| Serverless (AWS Lambda/Vercel) | Cold start latency conflicts with 3-second response goal, harder to manage stateful connections (Qdrant, Postgres) |
| Monorepo with frontend+backend | Docusaurus deployment is separate (static site), mixing breaks deployment independence |
| Self-hosted Qdrant + Postgres | Violates "managed services only" simplicity principle, operational overhead |

### Implementation Notes
- `Dockerfile` with Python 3.11, install FastAPI, OpenAI SDK, Qdrant client, Psycopg3
- Environment variables: `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `POSTGRES_URL`
- Health check endpoint: `/health` returns status of Qdrant/Postgres connections
- Deploy to Render free tier initially (750 hours/month), migrate to Railway if needed

---

## 6. Conversation History Depth

### Decision
Store **last 20 query-response pairs** OR **7-day expiry**, whichever is lower, in browser LocalStorage.

### Rationale
- **Storage Limit**: LocalStorage has ~5-10MB limit per domain; 20 Q&A pairs ≈ 50KB (safe margin)
- **User Experience**: 20 queries provide sufficient scrollback for educational sessions
- **Privacy**: 7-day expiry ensures stale conversations don't persist indefinitely
- **Performance**: Retrieving 20 items from LocalStorage is instant (<10ms)

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| Store all conversation history | Risks hitting LocalStorage limits, privacy concerns (long-term data retention) |
| No history limit | Same as above |
| 50 Q&A pairs | Higher storage footprint, most users won't scroll beyond 20 anyway |
| Backend-stored history | Requires user authentication (out of scope per spec), violates "no permanent user data" constraint |

### Implementation Notes
- LocalStorage schema: `{session_id: {queries: [{q, a, timestamp, citations}, ...]}}`
- On startup: Filter queries older than 7 days, keep last 20
- On new query: Append to array, trim if length >20, update LocalStorage
- Export feature (future): Allow user to download conversation as JSON/Markdown

---

## 7. Frontend-Backend Event Contracts

### Decision
Use **REST API with JSON payloads** (not WebSockets or GraphQL).

### Rationale
- **Simplicity**: REST is standard, well-documented, no special client libraries needed
- **Request-Response Pattern**: Chatbot interactions are request-response (not real-time streaming)
- **Caching**: HTTP caching headers can optimize repeated queries (future optimization)
- **Testing**: Easier to test with standard HTTP tools (Postman, curl, pytest)

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| WebSockets | Overkill for request-response pattern, requires persistent connections (harder to deploy/scale) |
| GraphQL | Adds complexity (schema, resolvers), REST is sufficient for single query endpoint |
| gRPC | Requires proto definitions, not browser-friendly, overkill for simple API |
| Server-Sent Events (SSE) | Useful for streaming responses (future), but not needed for Phase 2 MVP |

### Implementation Notes
- Endpoint: `POST /api/v1/query`
- Request: `{"session_id": "uuid", "query": "...", "mode": "full-book | selected-text", "selection": "..." (optional)}`
- Response: `{"answer": "...", "citations": [{text, url}], "mode": "...", "latency_ms": 2500}`
- Error responses: `{"error": "...", "code": "RATE_LIMIT | TIMEOUT | SERVICE_UNAVAILABLE"}`

---

## 8. Testing Strategy

### Decision
Three-tier testing: **Unit (agents) → Integration (API) → E2E (user journeys)**.

### Rationale
- **Agent Unit Tests**: Validate each agent role independently (mocked dependencies)
- **API Integration Tests**: Test orchestrator pipeline with real Qdrant/Postgres (test DB)
- **E2E Tests**: Playwright tests for full user journeys (full-book mode, selected-text mode)
- **Coverage Goal**: 80% code coverage minimum for production readiness

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| Unit tests only | Misses integration failures (e.g., Qdrant connection issues) |
| E2E tests only | Slow, brittle, hard to debug failures, insufficient coverage |
| Manual testing only | Not repeatable, doesn't scale, risk of regressions |

### Implementation Notes
- Unit: pytest with mocked OpenAI API, Qdrant, Postgres
- Integration: pytest-asyncio with test Qdrant collection, test Postgres DB
- E2E: Playwright with headless browser, test against deployed staging environment
- CI/CD: Run unit+integration on every PR, E2E on merge to main

---

## 9. Book Content Indexing Automation

### Decision
Use **manual one-time indexing script** for Phase 2, automate re-indexing trigger in future.

### Rationale
- **Phase 2 Scope**: Book content is stable, updates are infrequent
- **Simplicity**: Run `python scripts/index_book_content.py` when book updates
- **Future**: Trigger re-indexing via webhook on Docusaurus build completion (Phase 3)

### Alternatives Considered
| Strategy | Why Rejected |
|----------|--------------|
| Auto-index on every Docusaurus build | Requires tight coupling, breaks deployment independence |
| Scheduled re-indexing (cron) | Wasteful if content hasn't changed, harder to test |
| Real-time indexing (on page save) | Complex, requires Docusaurus plugin, overkill for Phase 2 |

### Implementation Notes
- Script reads Markdown files from `physical-ai-book/docs/`
- Parses frontmatter (module, chapter), chunks paragraphs, generates embeddings
- Upserts to Qdrant collection: `physical-ai-book-v1`
- Stores metadata in Postgres: `{chunk_id, module, chapter, section_id, char_offsets}`
- Versioning: Use collection names with version suffix (`v1`, `v2`) for zero-downtime swaps

---

## 10. Error Handling Best Practices

### Decision
Use **structured error responses** with error codes, user-friendly messages, and internal logs.

### Rationale
- **User Experience**: Clear error messages help users understand what went wrong
- **Debugging**: Error codes and internal logs enable quick debugging
- **Graceful Degradation**: FR-012 requires book remains accessible even if chatbot fails

### Error Code Taxonomy
| Code | Meaning | User Message | Action |
|------|---------|--------------|--------|
| `RATE_LIMIT` | 10 queries/min exceeded | "Please wait before asking another question." | Return 429, include retry-after header |
| `TIMEOUT` | Response took >3 seconds | "Request took too long. Try a simpler question." | Cancel LLM call, return partial results if available |
| `SERVICE_UNAVAILABLE` | Qdrant/OpenAI/Postgres down | "Chatbot temporarily unavailable. Try again later." | Return 503, book remains accessible |
| `INVALID_INPUT` | Query too long, invalid mode | "Please shorten your question to under 1000 words." | Return 400 with specific validation error |
| `NO_RESULTS` | No relevant chunks found | "I don't have information on that topic in the book." | Return 200 with empty answer, suggest rephrasing |
| `OUT_OF_SCOPE` | Query outside book content | "I can only answer based on the Physical AI book content." | Return 200 with boundary message |

### Implementation Notes
- Log all errors to structured logger (JSON format) with: `{timestamp, session_id, error_code, query, stack_trace}`
- Frontend displays user-friendly message, logs full error to console for debugging
- Implement retry logic for transient failures (Qdrant timeout → retry once after 1s)

---

## Summary

All technology decisions prioritize **simplicity, cost efficiency, and alignment with Phase 2 constraints**:

- **Embedding Model**: text-embedding-3-small (cost-effective, sufficient accuracy)
- **Chunking**: Paragraph-level with 50-token overlap (granular citations, free tier fit)
- **Sessions**: Frontend UUIDs (stateless backend, privacy-first)
- **Rate Limiting**: In-memory sliding window (simple MVP, Redis path for scaling)
- **Deployment**: Single Docker container (managed services for Postgres/Qdrant)
- **History Depth**: Last 20 Q&A pairs or 7-day expiry (LocalStorage friendly)
- **API**: REST JSON (standard, simple, testable)
- **Testing**: Unit → Integration → E2E (comprehensive coverage)
- **Indexing**: Manual script for Phase 2 (automate in Phase 3)
- **Error Handling**: Structured codes with graceful degradation

**Next Phase**: Create `data-model.md`, `contracts/`, and `quickstart.md` (Phase 1 outputs).
