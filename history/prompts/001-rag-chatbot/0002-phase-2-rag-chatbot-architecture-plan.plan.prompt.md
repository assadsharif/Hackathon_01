---
id: 0002
title: Phase 2 RAG Chatbot Architecture Plan
stage: plan
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: assad
command: /sp.plan
labels: ["architecture", "multi-agent", "rag", "phase-2", "design"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/plan.md
  - specs/001-rag-chatbot/research.md
  - specs/001-rag-chatbot/data-model.md
  - specs/001-rag-chatbot/contracts/openapi.yaml
  - specs/001-rag-chatbot/contracts/events.yaml
  - specs/001-rag-chatbot/quickstart.md
tests:
  - Architecture design validates against spec requirements (all FR/SC covered)
  - Agent role separation verified (no overlapping responsibilities)
  - Data model supports all user scenarios
---

## Prompt

You are executing /sp.plan for PHASE 2.

Input:
Approved /sp.specify
Updated SKILL.md

Objective:
Design the system architecture for the RAG chatbot.

Plan must include:
- Conceptual agent roles (no implementation)
  - Retrieval Agent
  - Context-Selection Agent
  - Answer Synthesis Agent
  - Citation & Guardrails Agent
- Data flow between components
- Separation of concerns
- How selected-text queries differ from global queries
- Failure handling at design level
- Future extensibility to multi-modal inputs

Rules:
- No code
- No pseudo-code
- No SDK usage
- No agent instructions
- Agents are roles, not implementations

Deliverable:
A clean architectural plan suitable for /sp.tasks.
Stop after planning.

## Response snapshot

Created comprehensive architectural plan with Phase 0 (research) and Phase 1 (design) artifacts:

**Plan.md (477 lines)**: Complete system architecture with:
- **Agent Roles**: 4 conceptual agents (Context Selection, Retrieval, Answer Synthesis, Citation & Guardrails) with inputs/outputs/decision-logic/failure-modes
- **Data Flow**: ASCII diagram showing frontend → backend pipeline → response with all orchestration steps
- **Separation of Concerns**: Table defining what each component does and does NOT handle
- **Mode Differences**: Full comparison table (Full-Book vs Selected-Text) covering 8 aspects
- **Failure Handling**: 8 failure scenarios with detection/handling/UX strategies
- **Multi-Modal Extensibility**: 4 future extension points (image, voice, video, code snippets) with impact analysis
- **Risk Analysis**: 5 technical risks + 3 operational risks with mitigations
- **Constitution Check**: Passed all gates (Phase 2+ backend allowed, managed services, simplicity preserved)

**Research.md (10 decisions)**: Technology choices with rationale/alternatives:
1. Embedding Model: text-embedding-3-small (cost vs accuracy trade-off)
2. Chunking Strategy: Paragraph-level ~250 tokens with 50-token overlap
3. Session IDs: Frontend UUIDs (stateless backend)
4. Rate Limiting: In-memory sliding window (Redis path for scaling)
5. Deployment: Single Docker container (managed services)
6. Conversation History: Last 20 Q&A pairs or 7-day expiry
7. API Protocol: REST JSON (not WebSockets/GraphQL)
8. Testing: Unit → Integration → E2E three-tier
9. Indexing: Manual script for Phase 2, automate in Phase 3
10. Error Handling: Structured error codes with graceful degradation

**Data-Model.md**: Complete entity schemas with:
- **Postgres Tables**: book_content_chunks (metadata), query_analytics (30-day retention)
- **Qdrant Collection**: physical-ai-book-v1 (1536-dim vectors, HNSW index)
- **LocalStorage Schema**: Conversation history (20 queries, 7-day expiry)
- **6 Entities**: BookContentChunk, Query, Response, Citation, ConversationSession, UserContext
- **Validation Rules**: 50+ constraints across all entities
- **Relationships Diagram**: Entity interactions and data flow
- **Migration Strategy**: Zero-downtime collection versioning

**Contracts/openapi.yaml**: Full REST API specification with:
- **POST /v1/query**: Submit chatbot query (full-book or selected-text mode)
- **GET /v1/health**: Service health check with dependency status
- **5 Response Codes**: 200 (success), 400 (invalid), 429 (rate-limit), 503 (unavailable), 504 (timeout)
- **Error Taxonomy**: 6 error codes with user messages and details
- **Request/Response Schemas**: Fully typed with examples for all scenarios

**Contracts/events.yaml**: Frontend-backend event lifecycle with:
- **10 Frontend Events**: Panel open, query submit, response receive, text selection, navigation, theme toggle, etc.
- **6 Backend Events**: Query receive, context select, retrieval, synthesis, guardrails, response send
- **6 Error Events**: Rate limit, timeout, service unavailable, invalid input, no results, out-of-scope
- **State Machine**: Chatbot panel states (closed → idle → loading → error/success)

**Quickstart.md**: Complete developer setup guide with:
- **Prerequisites**: Software + API keys (OpenAI, Qdrant, Neon)
- **8 Setup Steps**: Clone, backend setup, indexing, run API, frontend integration, testing, workflow, deployment
- **Troubleshooting**: 8 common issues with solutions
- **Next Steps**: Links to architecture docs and resources

## Outcome

- ✅ Impact: Complete architecture ready for `/sp.tasks` - all design artifacts created (6 files, 2000+ lines)
- 🧪 Tests: Architecture validated against spec (all 20 FRs covered, all 12 SCs addressable, 4 agent roles clean separation)
- 📁 Files: Created plan.md, research.md, data-model.md, openapi.yaml, events.yaml, quickstart.md
- 🔁 Next prompts: `/sp.tasks` to generate actionable implementation tasks from this plan
- 🧠 Reflection: Successfully maintained design-only approach (no code/pseudo-code). Agent roles are conceptual with clear boundaries. Multi-modal extensibility designed without breaking current architecture. All open questions documented for implementation phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning phases completed successfully
- Graders run and results (PASS/FAIL): Constitution Check PASS (4/4 gates), Spec Coverage PASS (20 FRs mapped to plan), Data Model Validation PASS (all entities support user scenarios)
- Prompt variant (if applicable): N/A - first planning iteration
- Next experiment (smallest change to try): Proceed to task generation to validate that plan provides sufficient detail for actionable implementation tasks
