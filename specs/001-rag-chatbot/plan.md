# Implementation Plan: Integrated RAG Chatbot for Physical AI Book

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

## Summary

Design a Retrieval-Augmented Generation (RAG) chatbot that embeds into the Physical AI & Humanoid Robotics Docusaurus book, enabling students to ask questions about book content with two distinct modes: full-book retrieval and selected-text-only retrieval. The system orchestrates multiple specialized agent roles (Retrieval, Context Selection, Answer Synthesis, Citation & Guardrails) to deliver accurate, cited responses within 3 seconds for 95% of queries while maintaining strict boundaries to book content only.

**Architectural Approach**: Multi-agent orchestration pattern where each agent role has a single, well-defined responsibility. Request flows through a pipeline: user query → context selection → retrieval → answer synthesis → citation generation & guardrails → response delivery. Frontend integration uses embedded UI component within Docusaurus with session persistence via browser storage.

## Technical Context

**Language/Version**: Python 3.11+ (backend API), TypeScript/JavaScript (frontend integration)
**Primary Dependencies**:
- Backend: FastAPI (API framework), OpenAI Python SDK (LLM orchestration), Qdrant Client (vector search), Psycopg3 (Postgres driver)
- Frontend: React 18+ (Docusaurus requirement), Browser Storage API (session persistence)

**Storage**:
- Neon Serverless Postgres (conversation sessions, query metadata, analytics)
- Qdrant Cloud Free Tier (vector embeddings for book content chunks)
- Browser LocalStorage (session persistence, conversation history)

**Testing**:
- Backend: pytest (unit, integration), pytest-asyncio (async tests)
- Frontend: Jest + React Testing Library (UI components)
- E2E: Playwright (user journeys across full-book and selected-text modes)

**Target Platform**:
- Backend: Linux server (containerized deployment)
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge - last 2 years)
- Integration: Embedded within Docusaurus static site

**Project Type**: Web application (backend API + frontend integration component)

**Performance Goals**:
- 95% of queries answered within 3 seconds end-to-end
- Vector retrieval <500ms for 99th percentile
- Support 10 concurrent users initially (free tier constraints)
- Session persistence <100ms for conversation history restore

**Constraints**:
- Qdrant Cloud Free Tier: 1GB storage, 1M vectors (limits book content indexing granularity)
- OpenAI API: Rate limits and cost management (educational use case budget)
- No permanent user data storage (privacy constraint from spec)
- No external knowledge sources beyond book content
- Must deploy alongside existing Docusaurus site without separate complex infrastructure

**Scale/Scope**:
- Initial deployment: Single Physical AI book (~7 modules, ~50 chapters)
- Expected user base: 100-500 students during educational sessions
- Conversation history: Session-scoped only (no cross-device persistence)
- Query volume: ~1000 queries/day estimated

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 2+ Compliance

✅ **PASS - Interactive Backend Allowed**: Constitution Principle VI (MCP Server Development) states "Phase 2+: MCP development is IN SCOPE" and Phase 1 Constraints table lists "Interactive code execution | Requires backend | Phase 2+". This RAG chatbot is a Phase 2 feature with backend API, which is explicitly allowed.

✅ **PASS - External Services for Tooling**: OpenAI API, Qdrant Cloud, and Neon Postgres are used for project-relevant tooling (educational chatbot), which aligns with constitution allowing Phase 2+ enhancements.

✅ **PASS - Documentation Remains Primary**: The chatbot augments the Docusaurus book but does not replace documentation. Static HTML/CSS/JS from Phase 1 remains fully accessible even if chatbot services fail (per FR-012 graceful degradation).

✅ **PASS - Simplicity Principle**: Using managed services (Neon, Qdrant Cloud free tiers, OpenAI API) avoids premature infrastructure complexity. No custom vector databases, no self-hosted LLM orchestration.

### Potential Concerns (None)

No violations detected. The architecture respects:
- Phase 1 deliverables remain untouched (book content is static)
- Phase 2 backend is justified by educational chatbot use case
- External services are minimal and managed (free tiers)
- Complexity is bounded by using pre-built SDKs and cloud services

## Complexity Tracking

*Not applicable - no constitution violations to justify.*

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Technology decisions and rationale (Phase 0 output)
├── data-model.md        # Entity and state designs (Phase 1 output)
├── quickstart.md        # Developer setup guide (Phase 1 output)
├── contracts/           # API contracts (Phase 1 output)
│   ├── openapi.yaml     # REST API schema
│   └── events.yaml      # Frontend-backend event contracts
└── checklists/
    └── requirements.md  # Validation checklist (completed)
```

### Source Code (repository root)

```text
rag-chatbot/                      # Backend API service
├── src/
│   ├── agents/                   # Agent role implementations
│   │   ├── retrieval.py         # Retrieval Agent role
│   │   ├── context_selection.py # Context Selection Agent role
│   │   ├── synthesis.py         # Answer Synthesis Agent role
│   │   └── guardrails.py        # Citation & Guardrails Agent role
│   ├── api/                      # FastAPI endpoints
│   │   ├── routes/
│   │   │   ├── query.py         # POST /query endpoint
│   │   │   ├── session.py       # Session management endpoints
│   │   │   └── health.py        # Health check endpoint
│   │   └── middleware/
│   │       ├── rate_limit.py    # Rate limiting middleware
│   │       └── error_handling.py # Error response standardization
│   ├── models/                   # Data models
│   │   ├── query.py             # Query, Response models
│   │   ├── session.py           # ConversationSession model
│   │   └── content.py           # BookContentChunk, Citation models
│   ├── services/                 # Business logic
│   │   ├── orchestrator.py      # Main agent orchestration pipeline
│   │   ├── indexing.py          # Book content indexing service
│   │   └── storage.py           # Postgres and Qdrant abstraction
│   └── config/
│       ├── settings.py          # Environment-based configuration
│       └── prompts.py           # Agent prompt templates (non-code)
├── tests/
│   ├── unit/                    # Unit tests for agent roles
│   ├── integration/             # API endpoint integration tests
│   └── e2e/                     # End-to-end user journey tests
├── scripts/
│   ├── index_book_content.py   # One-time indexing of book content
│   └── migrate_db.py           # Database schema migrations
├── pyproject.toml              # Python dependencies
└── README.md

physical-ai-book/                # Existing Docusaurus site
├── src/
│   ├── components/
│   │   └── ChatbotPanel/       # New chatbot UI component
│   │       ├── ChatbotPanel.tsx
│   │       ├── ChatInput.tsx
│   │       ├── MessageList.tsx
│   │       ├── CitationLink.tsx
│   │       └── ModeToggle.tsx
│   ├── hooks/
│   │   ├── useChatSession.ts   # Session persistence hook
│   │   ├── useTextSelection.ts # Selected-text detection hook
│   │   └── useChatbotAPI.ts    # API client hook
│   └── theme/
│       └── ChatbotIntegration.tsx # Global chatbot integration wrapper
└── (existing Docusaurus structure)
```

**Structure Decision**: Web application pattern with separated backend and frontend integration. Backend API (`rag-chatbot/`) is a standalone Python service deployed separately. Frontend integration (`physical-ai-book/src/components/ChatbotPanel/`) embeds into existing Docusaurus site as a React component. This separation allows independent testing of agent orchestration logic and UI components.

## Architectural Design

### Agent Role Definitions

The system uses four conceptual agent roles, each with distinct responsibilities. These are architectural roles, not implementation classes.

#### 1. Context Selection Agent

**Responsibility**: Determine retrieval scope based on query mode (full-book vs selected-text) and validate context boundaries.

**Inputs**:
- User query text
- Query mode (full-book or selected-text)
- Selected text context (if mode is selected-text)
- Current page URL (for context)

**Outputs**:
- Retrieval scope decision (search full book index OR use selected text only)
- Validated context boundaries (character offsets for selected text)
- Context metadata (page URL, selection timestamp)

**Decision Logic**:
- If mode = full-book → scope = entire book vector index
- If mode = selected-text AND selection exists → scope = selected text only
- If mode = selected-text AND no selection → ERROR or fallback to full-book with user confirmation
- If selected text too short (<50 characters) → suggest full-book mode

**Failure Modes**:
- Stale selected text (user navigated away) → clear selection, default to full-book
- Selected text exceeds token limit → truncate with warning or reject

#### 2. Retrieval Agent

**Responsibility**: Fetch relevant book content based on scope determined by Context Selection Agent.

**Inputs**:
- User query (natural language question)
- Retrieval scope (full-book index OR selected text string)
- Number of chunks to retrieve (configurable, default 5-10)

**Outputs**:
- Ranked list of relevant book content chunks
- Each chunk includes: text content, source module, source chapter, section ID, relevance score
- Retrieval metadata (latency, total candidates evaluated)

**Decision Logic**:
- **Full-book mode**: Query vector index (Qdrant) using semantic search with query embedding
- **Selected-text mode**: No vector search; pass selected text directly as single "chunk" with synthetic metadata
- Apply relevance score threshold (e.g., >0.7 cosine similarity) to filter low-quality matches
- Deduplicate chunks from same section to avoid redundancy

**Failure Modes**:
- Vector database unavailable → return error, trigger graceful degradation (FR-012)
- No relevant chunks found (all scores <threshold) → return empty list, trigger "no information" response
- Timeout (>500ms) → return partial results or error

#### 3. Answer Synthesis Agent

**Responsibility**: Generate natural language answer using retrieved content chunks and query.

**Inputs**:
- User query
- Ranked list of relevant book content chunks
- Query mode (for response framing)

**Outputs**:
- Synthesized answer text
- List of chunk IDs used in synthesis (for citation mapping)
- Confidence score (optional, for future use)

**Decision Logic**:
- Construct prompt with: user question, retrieved chunks, instruction to synthesize from provided content only
- Submit to LLM (OpenAI API)
- Parse LLM response to extract answer text and identify which chunks were referenced
- If no chunks provided (retrieval failed) → generate "I don't have information on that topic" response

**Failure Modes**:
- LLM API unavailable → return error, trigger graceful degradation
- LLM response exceeds expected format → attempt parsing, fallback to generic error message
- Timeout (>2 seconds) → cancel request, return timeout error

#### 4. Citation & Guardrails Agent

**Responsibility**: Generate precise citations, enforce content boundaries, validate response quality.

**Inputs**:
- Synthesized answer text
- List of chunk IDs used in synthesis
- Book content chunk metadata (module, chapter, section IDs)

**Outputs**:
- Final response with embedded citation links
- Citation list (formatted as "[Module N: Chapter Title](URL#section-id)")
- Validation flags (boundary violations, hallucination detection)

**Decision Logic**:
- For each chunk ID used in synthesis:
  - Resolve to module name, chapter title, section ID from metadata
  - Generate Docusaurus URL with anchor: `/docs/module-N/chapter#section-id`
  - Format citation as markdown link
- Validate answer against guardrails:
  - Check for out-of-scope content (e.g., mentions of external topics not in book)
  - Detect code generation attempts (regex patterns for code blocks)
  - Flag ambiguous or uncertain language (e.g., "I think", "maybe") for review
- Inject boundary reminders if query was out-of-scope (e.g., "I can only answer based on book content")

**Failure Modes**:
- Missing chunk metadata → citation shows "Unknown Source" with warning
- Invalid section IDs (content moved) → link to chapter root instead of specific section
- Guardrail violation detected → override answer with boundary message

### Data Flow Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│  Frontend (Docusaurus Site)                                         │
│  ┌────────────────┐     ┌──────────────────┐                       │
│  │ User selects   │────▶│ useTextSelection │                       │
│  │ text (optional)│     │ hook             │                       │
│  └────────────────┘     └──────────────────┘                       │
│         │                        │                                  │
│         │                        ▼                                  │
│         │                ┌─────────────────┐                       │
│         │                │ ChatbotPanel    │                       │
│         │                │ Component       │                       │
│         │                └────────┬────────┘                       │
│         │                         │                                 │
│         │                         ▼                                 │
│         │                ┌─────────────────┐                       │
│         └───────────────▶│ useChatbotAPI   │                       │
│                          │ hook            │                       │
│                          └────────┬────────┘                       │
│                                   │                                 │
│                                   │ POST /query                     │
│                                   │ {query, mode, selection}        │
└───────────────────────────────────┼─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Backend API (FastAPI)                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │ Rate Limiting Middleware (FR-011: 10 queries/min)             ││
│  └──────────────────────┬─────────────────────────────────────────┘│
│                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Orchestrator Service (Pipeline Coordinator)                  │  │
│  │                                                               │  │
│  │  Step 1: Context Selection Agent                             │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │ Input: query, mode, selection                        │   │  │
│  │  │ Output: scope (full-book | selected-text)            │   │  │
│  │  │ Validate: selection exists if mode=selected-text     │   │  │
│  │  └──────────────────────┬───────────────────────────────┘   │  │
│  │                         ▼                                     │  │
│  │  Step 2: Retrieval Agent                                     │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │ IF scope=full-book:                                  │   │  │
│  │  │   → Query Qdrant vector index                        │   │  │
│  │  │   → Return top 5-10 chunks by cosine similarity      │   │  │
│  │  │ IF scope=selected-text:                              │   │  │
│  │  │   → Use selection as single chunk                    │   │  │
│  │  │ Output: [BookContentChunk, ...]                      │   │  │
│  │  └──────────────────────┬───────────────────────────────┘   │  │
│  │                         ▼                                     │  │
│  │  Step 3: Answer Synthesis Agent                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │ Construct LLM prompt:                                │   │  │
│  │  │   - User query                                       │   │  │
│  │  │   - Retrieved chunks                                 │   │  │
│  │  │   - Instruction: answer from provided content only   │   │  │
│  │  │ Call OpenAI API                                      │   │  │
│  │  │ Output: answer_text, chunk_ids_used                  │   │  │
│  │  └──────────────────────┬───────────────────────────────┘   │  │
│  │                         ▼                                     │  │
│  │  Step 4: Citation & Guardrails Agent                         │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │ For each chunk_id:                                   │   │  │
│  │  │   → Resolve module, chapter, section ID             │   │  │
│  │  │   → Generate URL: /docs/module/chapter#section      │   │  │
│  │  │ Validate answer:                                     │   │  │
│  │  │   → Check for out-of-scope content                  │   │  │
│  │  │   → Detect code generation attempts                 │   │  │
│  │  │   → Enforce boundary messages if needed             │   │  │
│  │  │ Output: final_response with citations               │   │  │
│  │  └──────────────────────┬───────────────────────────────┘   │  │
│  │                         ▼                                     │  │
│  │  ┌─────────────────────────────────────────────────────┐    │  │
│  │  │ Store in Postgres:                                  │    │  │
│  │  │   - ConversationSession (session_id, query, response)│   │  │
│  │  │   - Analytics (query pattern, retrieval latency)    │    │  │
│  │  └──────────────────────┬──────────────────────────────┘    │  │
│  └────────────────────────┼────────────────────────────────────┘  │
│                           ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Response JSON:                                             │  │
│  │ {                                                          │  │
│  │   "answer": "...",                                         │  │
│  │   "citations": [{"text": "Module 5", "url": "..."}],      │  │
│  │   "mode": "full-book",                                     │  │
│  │   "latency_ms": 2500                                       │  │
│  │ }                                                          │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Frontend (Docusaurus Site)                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ ChatbotPanel receives response                             │   │
│  │   → Render answer text with markdown                       │   │
│  │   → Render clickable citation links                        │   │
│  │   → Store in session history (LocalStorage)                │   │
│  │   → Update UI state (loading → display)                    │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Separation of Concerns

| Component | Responsibility | Does NOT Handle |
|-----------|----------------|-----------------|
| **Context Selection Agent** | Determine retrieval scope, validate selection boundaries | Does NOT perform retrieval or answer synthesis |
| **Retrieval Agent** | Fetch relevant content from vector index or selected text | Does NOT synthesize answers or generate citations |
| **Answer Synthesis Agent** | Generate natural language response from retrieved chunks | Does NOT validate boundaries or create citation links |
| **Citation & Guardrails Agent** | Generate citations, enforce content boundaries | Does NOT perform retrieval or LLM calls |
| **Orchestrator Service** | Coordinate agent pipeline, handle errors, manage state | Does NOT contain agent-specific logic (delegates to agents) |
| **Frontend ChatbotPanel** | UI rendering, session persistence, text selection detection | Does NOT perform retrieval or answer generation (calls API) |

### Full-Book vs Selected-Text Mode Differences

| Aspect | Full-Book Mode | Selected-Text Mode |
|--------|----------------|-------------------|
| **Context Selection** | Scope = entire vector index (all book chunks) | Scope = selected text only (single "chunk") |
| **Retrieval** | Vector similarity search in Qdrant (semantic) | No search; use selected text as-is |
| **Retrieved Chunks** | Top 5-10 ranked by relevance score | Single chunk = selected text |
| **Answer Synthesis Prompt** | "Answer using these relevant book sections..." | "Answer based ONLY on this selected text..." |
| **Citation Sources** | Multiple chapters/modules (cross-reference possible) | Single source (current page/section) |
| **Boundary Validation** | Check for out-of-book topics | Check for question-selection mismatch |
| **User Feedback** | "Based on the Physical AI book..." | "Based on your selected text..." |
| **Failure if No Context** | "No relevant information found in book" | "Your question doesn't relate to selected text. Search full book?" |

### Failure Handling (Design Level)

| Failure Scenario | Detection | Handling Strategy | User Experience |
|------------------|-----------|-------------------|-----------------|
| **Vector DB Unavailable** | Qdrant client raises connection error | Orchestrator catches error, skips retrieval step, returns degraded response | "Chatbot temporarily unavailable. Please try again later." Book remains accessible (FR-012). |
| **LLM API Timeout** | OpenAI client timeout (>2s) | Cancel request, log timeout, return timeout message | "Request took too long. Please try a simpler question or try again." |
| **Rate Limit Exceeded** | Middleware detects >10 queries/min from session ID | Return 429 status before pipeline starts | "Please wait a moment before asking another question." |
| **Empty Retrieval Results** | Retrieval Agent returns empty list (no chunks >threshold) | Answer Synthesis Agent generates "no information" response | "I don't have information on that topic in the book." |
| **Out-of-Scope Query** | Guardrails Agent detects non-book content (e.g., code gen request) | Override answer with boundary message | "I can explain concepts from the book but cannot write code or provide information outside this material." |
| **Stale Selected Text** | Context Selection Agent detects selection timestamp >5min or different page URL | Clear selection, prompt user to re-select or use full-book mode | "Selected text has expired. Searching full book instead..." |
| **Invalid Section ID** | Citation Agent cannot resolve chunk metadata to valid URL | Link to chapter root instead of specific section | Citation shows "[Module 5: Control](URL)" without #section anchor |
| **Browser Storage Disabled** | Frontend session persistence fails on write | Continue without session history, show notice | "Conversation history won't persist (browser storage disabled)." |

### Future Extensibility to Multi-Modal Inputs

**Current Scope (Phase 2)**: Text-only queries and text-only book content.

**Future Extension Points** (design considerations, not implemented):

1. **Image-Based Questions** (e.g., "Explain this diagram"):
   - **Change**: Add image upload to ChatbotPanel UI
   - **Context Selection Agent**: Accept image + query, extract text via OCR or use vision model
   - **Retrieval Agent**: Support multi-modal embeddings (CLIP-style) for image-text matching
   - **Impact**: Minimal changes to orchestrator pipeline; agents remain modular

2. **Voice Input** (e.g., speech-to-text):
   - **Change**: Add audio capture to frontend, transcribe to text via Web Speech API or OpenAI Whisper
   - **Impact**: No backend changes needed; voice input converts to text before API call

3. **Video/Animation Content in Book** (future Phase 3+):
   - **Change**: Index video transcripts and keyframes as additional chunks
   - **Retrieval Agent**: Support video timestamp citations
   - **Citation Agent**: Generate citations with video timestamps (e.g., "Module 5 Video at 2:34")

4. **Code Snippet Questions** (e.g., "Explain this ROS code"):
   - **Guardrails Agent**: Relax code generation boundary to allow code *explanation* (not generation)
   - **Answer Synthesis Agent**: Include code snippet in context for explanation
   - **Impact**: Requires updated guardrail rules, no architectural changes

**Design Principle for Extensibility**: Agent roles remain stable; modality-specific logic is encapsulated within each agent. Adding new input modalities requires updating Context Selection and Retrieval agents, not the entire pipeline.

## Risk Analysis

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Qdrant Free Tier Limits Exceeded** | Medium | High | Monitor vector count, chunk book content at optimal granularity (paragraph-level, not sentence-level). Implement chunk count alert. |
| **OpenAI API Costs Exceed Budget** | Medium | Medium | Implement strict rate limiting (10 queries/min), use GPT-3.5-turbo for synthesis (cheaper than GPT-4), cache common queries. |
| **Citation Links Break After Book Restructure** | Low | Medium | Use stable section IDs (Docusaurus frontmatter), not URL-based references. Test citation stability in restructure scenarios. |
| **Slow Query Response (>3s)** | Medium | High | Profile pipeline steps, optimize vector search (reduce chunk retrieval count if needed), implement timeout guardrails. |
| **Hallucination (Answer Not in Book)** | Medium | High | Strong guardrail prompts ("only use provided content"), post-synthesis validation, user-facing citations for verification. |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Book Content Updates Require Re-Indexing** | High | Medium | Automate re-indexing script, implement versioning for vector index, allow graceful index swap (no downtime per SC-011). |
| **External Service Outage (OpenAI/Qdrant)** | Low | High | Graceful degradation (FR-012): show error message, keep book accessible, implement health checks. |
| **Session Data Loss (Browser Clear)** | Medium | Low | Expected behavior per spec (session-only persistence). Provide export conversation feature in future. |

## Open Questions for Implementation Phase

1. **Vector Embedding Model**: Use OpenAI text-embedding-3-small (cheaper, sufficient) or text-embedding-3-large (higher accuracy)? → Recommend small initially, benchmark retrieval quality.

2. **Chunk Size for Book Content**: Paragraph-level (~200 tokens) or section-level (~500 tokens)? → Test both, balance between granular citations and context completeness.

3. **Session ID Generation**: Use frontend UUID or backend-generated session tokens? → Recommend frontend UUID (simpler, no backend session table needed initially).

4. **Deployment Strategy**: Single container (FastAPI + Postgres + Qdrant clients) or separate services? → Recommend single container for Phase 2 MVP, separate if scaling needed.

5. **Conversation History Depth**: Store last N queries in LocalStorage? → Recommend last 20 queries or 7-day expiry, whichever is lower.

## Next Steps

1. **Phase 0 Complete**: Create `research.md` with technology decisions (embedding model, chunk size, deployment approach)
2. **Phase 1 Complete**: Create `data-model.md`, `contracts/`, `quickstart.md`
3. **Ready for `/sp.tasks`**: Generate actionable tasks from this plan once Phase 1 artifacts are complete
