# Tasks: Integrated RAG Chatbot for Physical AI Book

**Input**: Design documents from `/specs/001-rag-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md

**Tests**: Not explicitly requested in specification - tasks focus on implementation only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `rag-chatbot/` (Python 3.11+, FastAPI)
- Frontend: `physical-ai-book/` (existing Docusaurus site with React/TypeScript)
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for backend and frontend integration

- [ ] T001 Create backend project structure: rag-chatbot/ with src/, tests/, scripts/ directories
- [ ] T002 Initialize Python project with pyproject.toml including FastAPI, OpenAI SDK, Qdrant client, Psycopg3 dependencies
- [ ] T003 [P] Create .env.example in rag-chatbot/ with placeholders for OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, POSTGRES_URL
- [ ] T004 [P] Configure linting (ruff) and formatting (black) in rag-chatbot/pyproject.toml
- [ ] T005 [P] Create rag-chatbot/README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create Postgres migration script rag-chatbot/scripts/migrate_db.py for book_content_chunks and query_analytics tables per data-model.md schema
- [ ] T007 Create Qdrant setup script rag-chatbot/scripts/setup_vector_db.py to initialize physical-ai-book-v1 collection with 1536-dim vectors
- [ ] T008 [P] Create settings configuration in rag-chatbot/src/config/settings.py using Pydantic BaseSettings for environment variables
- [ ] T009 [P] Create prompt templates in rag-chatbot/src/config/prompts.py with answer synthesis and guardrails prompts (declarative, non-code)
- [ ] T010 Create book content indexing script rag-chatbot/scripts/index_book_content.py to parse physical-ai-book/docs/, chunk paragraphs, generate embeddings, upsert to Qdrant and Postgres
- [ ] T011 [P] Create BookContentChunk model in rag-chatbot/src/models/content.py with Pydantic schema matching data-model.md
- [ ] T012 [P] Create Citation model in rag-chatbot/src/models/content.py with text, url, chunk_id fields
- [ ] T013 [P] Create Query model in rag-chatbot/src/models/query.py with QueryRequest and QueryResponse Pydantic schemas per openapi.yaml
- [ ] T014 [P] Create UserContext model in rag-chatbot/src/models/query.py for current_page_url, selected_text, session_id
- [ ] T015 Create storage service in rag-chatbot/src/services/storage.py with Qdrant and Postgres client initialization and health check functions
- [ ] T016 Create rate limiting middleware in rag-chatbot/src/api/middleware/rate_limit.py implementing sliding window (10 queries/min per session_id)
- [ ] T017 [P] Create error handling middleware in rag-chatbot/src/api/middleware/error_handling.py with structured error response formatting per openapi.yaml error taxonomy
- [ ] T018 Create FastAPI app initialization in rag-chatbot/src/api/main.py with CORS middleware, rate limiting, error handling
- [ ] T019 Create health check endpoint in rag-chatbot/src/api/routes/health.py implementing GET /v1/health per openapi.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 + 3 Combined - Full-Book Query with Citations (Priority: P1) 🎯 MVP

**Goal**: Enable students to ask questions about book content and receive synthesized answers with precise citations from multiple chapters

**Independent Test**: Ask "What is sensor fusion?" and verify response synthesizes information from Module 4 with clickable citations to specific sections

**User Stories Covered**:
- US1 (P1): Answer Questions Using Full Book Context
- US3 (P1): Receive Precise Source Citations

### Agent Implementation for US1+US3

- [ ] T020 [P] [US1] Create Context Selection Agent in rag-chatbot/src/agents/context_selection.py with scope determination logic (full-book vs selected-text)
- [ ] T021 [P] [US1] Create Retrieval Agent in rag-chatbot/src/agents/retrieval.py with Qdrant vector search for full-book mode and selected-text passthrough logic
- [ ] T022 [P] [US1] Create Answer Synthesis Agent in rag-chatbot/src/agents/synthesis.py with OpenAI API call to generate answer from retrieved chunks
- [ ] T023 [P] [US3] Create Citation & Guardrails Agent in rag-chatbot/src/agents/guardrails.py with citation generation from chunk metadata and boundary validation

### Service Layer for US1+US3

- [ ] T024 [US1] Create orchestrator service in rag-chatbot/src/services/orchestrator.py implementing 4-step pipeline: context selection → retrieval → synthesis → guardrails

### API Endpoint for US1+US3

- [ ] T025 [US1] Implement POST /v1/query endpoint in rag-chatbot/src/api/routes/query.py handling full-book mode queries with orchestrator pipeline integration

### Validation for US1+US3

- [ ] T026 [US1] Add query validation in POST /query to enforce token limits (1000 tokens), mode enum validation, required field checks
- [ ] T027 [US3] Add citation URL generation logic in guardrails agent to construct /docs/module-N/chapter#section-id links from chunk metadata
- [ ] T028 [US1] Add logging for query analytics in orchestrator: store session_id, query_text, mode, latencies, chunks_retrieved to query_analytics table

**Checkpoint**: At this point, the chatbot can answer full-book questions with citations - this is the MVP

---

## Phase 4: User Story 2 - Selected-Text Mode (Priority: P2)

**Goal**: Enable students to highlight text and ask questions constrained only to that selection

**Independent Test**: Select a paragraph about inverse kinematics, ask "What are the limitations?", verify response only references the selected text

### Extension for US2

- [ ] T029 [US2] Extend Context Selection Agent in rag-chatbot/src/agents/context_selection.py to validate selected_text exists, check min length (50 chars), handle stale selection
- [ ] T030 [US2] Extend Retrieval Agent in rag-chatbot/src/agents/retrieval.py to support selected-text passthrough (no vector search, use selected_text as single chunk)
- [ ] T031 [US2] Extend Answer Synthesis Agent in rag-chatbot/src/agents/synthesis.py to modify prompt for selected-text mode: "Answer based ONLY on this selected text:"
- [ ] T032 [US2] Update POST /v1/query endpoint in rag-chatbot/src/api/routes/query.py to handle mode=selected-text and extract selected_text from request body
- [ ] T033 [US2] Add selected-text validation in POST /query to require selected_text field when mode=selected-text, reject if mode mismatch

**Checkpoint**: Chatbot now supports both full-book and selected-text modes independently

---

## Phase 5: User Story 4 - Frontend Integration (Priority: P2)

**Goal**: Embed chatbot UI into Docusaurus site with session persistence and theme integration

**Independent Test**: Open chatbot, ask a question, navigate to different page, verify conversation history persists

### React Components for US4

- [ ] T034 [P] [US4] Create ChatbotPanel component in physical-ai-book/src/components/ChatbotPanel/ChatbotPanel.tsx with slide-in panel UI, message list, input field
- [ ] T035 [P] [US4] Create ChatInput component in physical-ai-book/src/components/ChatbotPanel/ChatInput.tsx with query submission, loading state, character count
- [ ] T036 [P] [US4] Create MessageList component in physical-ai-book/src/components/ChatbotPanel/MessageList.tsx to render query-response pairs with markdown formatting
- [ ] T037 [P] [US4] Create CitationLink component in physical-ai-book/src/components/ChatbotPanel/CitationLink.tsx to render clickable citations with module/chapter labels
- [ ] T038 [P] [US4] Create ModeToggle component in physical-ai-book/src/components/ChatbotPanel/ModeToggle.tsx to switch between full-book and selected-text modes

### React Hooks for US4

- [ ] T039 [P] [US4] Create useChatSession hook in physical-ai-book/src/hooks/useChatSession.ts for LocalStorage session management (save/load last 20 queries, 7-day expiry)
- [ ] T040 [P] [US4] Create useTextSelection hook in physical-ai-book/src/hooks/useTextSelection.ts to detect browser text selection, extract text, validate min length
- [ ] T041 [P] [US4] Create useChatbotAPI hook in physical-ai-book/src/hooks/useChatbotAPI.ts with fetch client for POST /v1/query, error handling, retry logic

### Theme Integration for US4

- [ ] T042 [US4] Create ChatbotIntegration wrapper in physical-ai-book/src/theme/ChatbotIntegration.tsx to integrate ChatbotPanel with Docusaurus theme context
- [ ] T043 [US4] Create Docusaurus Root.tsx in physical-ai-book/src/theme/Root.tsx to mount ChatbotIntegration globally across all pages
- [ ] T044 [US4] Add chatbot API URL configuration in physical-ai-book/docusaurus.config.ts customFields: {chatbotApiUrl: process.env.CHATBOT_API_URL || 'http://localhost:8000/v1'}
- [ ] T045 [US4] Add CSS styling for ChatbotPanel in physical-ai-book/src/css/custom.css with light/dark theme support using CSS variables

### Session Management for US4

- [ ] T046 [US4] Implement session UUID generation in useChatSession hook: generate on first load, persist in LocalStorage with key chatbot_session_id
- [ ] T047 [US4] Implement conversation history pruning in useChatSession hook: remove queries >7 days old, keep last 20 queries max, run on load
- [ ] T048 [US4] Add page navigation detection in ChatbotIntegration to clear selected_text context when page URL changes, reset mode to full-book

**Checkpoint**: Frontend chatbot is fully integrated with Docusaurus site and persists sessions

---

## Phase 6: User Story 5 - User Guidance (Priority: P3)

**Goal**: Provide clear guidance on chatbot capabilities and boundaries

**Independent Test**: Open chatbot for first time, verify welcome message explains full-book vs selected-text modes

### UI Enhancements for US5

- [ ] T049 [P] [US5] Add welcome message to ChatbotPanel component: "I can answer questions about the Physical AI book. Ask about any topic or select text for focused answers."
- [ ] T050 [P] [US5] Create Help dialog in physical-ai-book/src/components/ChatbotPanel/HelpDialog.tsx explaining mode differences with examples
- [ ] T051 [P] [US5] Add Help button to ChatbotPanel header triggering HelpDialog modal

### Guardrails for US5

- [ ] T052 [US5] Extend Citation & Guardrails Agent in rag-chatbot/src/agents/guardrails.py to detect ambiguous questions, suggest clarifying module choices
- [ ] T053 [US5] Add out-of-scope detection in guardrails agent: detect code generation requests, external topics, override answer with boundary message
- [ ] T054 [US5] Add boundary message templates in rag-chatbot/src/config/prompts.py for code generation, external topics, selected-text mismatch scenarios

**Checkpoint**: Users have clear guidance on chatbot usage and limitations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, deployment readiness

- [ ] T055 [P] Create Dockerfile in rag-chatbot/ for containerized deployment with Python 3.11, FastAPI, all dependencies
- [ ] T056 [P] Create docker-compose.yml in rag-chatbot/ for local development with backend, Postgres, Qdrant (or use cloud services)
- [ ] T057 [P] Add deployment instructions to rag-chatbot/README.md for Render/Railway deployment with environment variable setup
- [ ] T058 [P] Update physical-ai-book/README.md with chatbot integration documentation and local development setup
- [ ] T059 Add error message improvements in error_handling middleware: ensure all error codes have user-friendly messages matching openapi.yaml
- [ ] T060 Add performance logging in orchestrator service: log retrieval_latency_ms, synthesis_latency_ms, total_latency_ms for analytics
- [ ] T061 [P] Create re-indexing instructions in rag-chatbot/README.md for updating book content: run index_book_content.py when docs/ changes
- [ ] T062 [P] Add CORS configuration in FastAPI app for production Docusaurus domain in rag-chatbot/src/api/main.py
- [ ] T063 Validate quickstart.md instructions by running full setup from scratch: backend + frontend + indexing + query test
- [ ] T064 [P] Create GitHub Actions workflow in .github/workflows/rag-chatbot-ci.yml for backend: lint (ruff), format check (black), run pytest (when added)
- [ ] T065 [P] Add frontend build validation to GitHub Actions: npm run build in physical-ai-book/

**Checkpoint**: System is deployment-ready with documentation and CI/CD

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1+US3 (Phase 3)**: Depends on Foundational phase completion - No dependencies on other stories
- **US2 (Phase 4)**: Depends on Foundational phase completion - Extends US1 agents but independently testable
- **US4 (Phase 5)**: Depends on Foundational phase completion - Frontend integration, works with US1+US3 backend
- **US5 (Phase 6)**: Depends on US1+US3 and US4 completion - UI enhancements to existing components
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1+3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **THIS IS THE MVP**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 agents but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Frontend only, integrates with US1+US3 backend
- **User Story 5 (P3)**: Depends on US1+US3 and US4 - Adds guidance to existing UI

### Within Each User Story

- Models before services
- Services before endpoints
- Backend agents before orchestrator
- Core implementation before validation/logging
- Backend endpoint before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup tasks (Phase 1)**: T003, T004, T005 can run in parallel
- **Foundational tasks (Phase 2)**: T008, T009, T011, T012, T013, T014, T017 can run in parallel (different files)
- **US1+US3 agents (Phase 3)**: T020, T021, T022, T023 can run in parallel (4 separate agent files)
- **US4 components (Phase 5)**: T034, T035, T036, T037, T038 can run in parallel (separate component files)
- **US4 hooks (Phase 5)**: T039, T040, T041 can run in parallel (separate hook files)
- **US5 UI (Phase 6)**: T049, T050, T051 can run in parallel (different components)
- **Polish tasks (Phase 7)**: T055, T056, T057, T058, T061, T064, T065 can run in parallel

---

## Parallel Example: User Story 1+3 (MVP Phase)

```bash
# After Foundational phase completes, launch all 4 agents in parallel:
Task T020: "Context Selection Agent in rag-chatbot/src/agents/context_selection.py"
Task T021: "Retrieval Agent in rag-chatbot/src/agents/retrieval.py"
Task T022: "Answer Synthesis Agent in rag-chatbot/src/agents/synthesis.py"
Task T023: "Citation & Guardrails Agent in rag-chatbot/src/agents/guardrails.py"

# Then sequentially:
Task T024: "Orchestrator service" (depends on all agents)
Task T025: "POST /query endpoint" (depends on orchestrator)
Task T026-T028: "Validation and logging" (final touches)
```

---

## Parallel Example: User Story 4 (Frontend)

```bash
# Components can all run in parallel:
Task T034: "ChatbotPanel component"
Task T035: "ChatInput component"
Task T036: "MessageList component"
Task T037: "CitationLink component"
Task T038: "ModeToggle component"

# Hooks can all run in parallel:
Task T039: "useChatSession hook"
Task T040: "useTextSelection hook"
Task T041: "useChatbotAPI hook"
```

---

## Implementation Strategy

### MVP First (User Story 1+3 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T019) - **CRITICAL: This blocks everything**
3. Complete Phase 3: US1+US3 (T020-T028) - Full-book queries with citations
4. **STOP and VALIDATE**:
   - Run indexing script to populate book content
   - Start backend: `uvicorn src.api.main:app --reload`
   - Test query: `curl -X POST http://localhost:8000/v1/query -d '{"session_id":"...", "query":"What is sensor fusion?", "mode":"full-book"}'`
   - Verify response includes answer + citations
5. Deploy backend (if ready) or proceed to frontend

### Incremental Delivery

1. **Setup + Foundational (T001-T019)** → Foundation ready
2. **Add US1+US3 (T020-T028)** → Test independently → **MVP complete** (backend chatbot works via API)
3. **Add US2 (T029-T033)** → Test independently → Selected-text mode working
4. **Add US4 (T034-T048)** → Test independently → Frontend integrated, users can interact via UI
5. **Add US5 (T049-T054)** → Test independently → User guidance complete
6. **Polish (T055-T065)** → Deployment-ready, CI/CD configured

Each phase adds value without breaking previous phases.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together (T001-T019)**
2. Once Foundational is done:
   - **Developer A**: User Story 1+3 backend (T020-T028)
   - **Developer B**: User Story 4 frontend (T034-T048) - can start in parallel with A
   - **Developer C**: User Story 2 selected-text (T029-T033) - can start after A completes agents, or work on polish tasks
3. **Developer A** then adds User Story 5 (T049-T054) after frontend is ready
4. **All developers** work on Polish tasks (T055-T065) in parallel

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 14 tasks
- **Phase 3 (US1+US3 - MVP)**: 9 tasks
- **Phase 4 (US2)**: 5 tasks
- **Phase 5 (US4)**: 15 tasks
- **Phase 6 (US5)**: 6 tasks
- **Phase 7 (Polish)**: 11 tasks

**Total**: 65 tasks

**Parallel Opportunities**: 25 tasks marked [P] can run concurrently with other tasks in their phase

**MVP Scope**: Phases 1-3 (28 tasks) deliver working backend chatbot with full-book queries and citations

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability (US1, US2, US3, US4, US5)
- **US1 and US3 are combined** in Phase 3 because citations are integral to answering queries (can't separate them)
- **Each user story should be independently testable** at its checkpoint
- **No tests explicitly requested** in spec - tasks focus on implementation only (tests can be added later if needed)
- **Commit after each task** or logical group for incremental progress
- **Stop at any checkpoint** to validate story independently before proceeding
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence
