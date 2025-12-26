# Data Model: RAG Chatbot

**Feature**: Integrated RAG Chatbot for Physical AI Book
**Date**: 2025-12-25
**Phase**: Phase 1 (Data Model Design)

## Overview

This document defines all entities, relationships, validation rules, and state transitions for the RAG chatbot system. Entities are categorized by storage location: **Postgres** (relational metadata), **Qdrant** (vector embeddings), and **Browser LocalStorage** (session data).

---

## Entity Catalog

| Entity | Storage | Purpose | Lifespan |
|--------|---------|---------|----------|
| `BookContentChunk` | Qdrant + Postgres | Indexed book content for retrieval | Permanent (until re-indexed) |
| `Query` | Postgres (analytics only) | User question metadata | 30 days (analytics retention) |
| `Response` | Transient (API response) | Chatbot answer with citations | Request-scoped only |
| `ConversationSession` | Browser LocalStorage | Session history for UI | 7 days or 20 queries |
| `Citation` | Transient (embedded in Response) | Source reference link | Request-scoped only |
| `UserContext` | Transient (API request) | Current page, selection, mode | Request-scoped only |

---

## Storage Schema

### Postgres Schema

#### Table: `book_content_chunks`

Stores metadata for each indexed book chunk (text content stored in Qdrant, metadata here for citation generation).

```sql
CREATE TABLE book_content_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_number INT NOT NULL,                  -- e.g., 1 for "Module 1: Introduction"
    module_name VARCHAR(255) NOT NULL,           -- e.g., "Introduction to Physical AI"
    chapter_title VARCHAR(255) NOT NULL,         -- e.g., "What is Physical AI?"
    section_id VARCHAR(255) NOT NULL,            -- Docusaurus frontmatter ID (stable)
    paragraph_index INT NOT NULL,                -- 0-based paragraph within section
    char_offset_start INT NOT NULL,              -- Character offset in source file
    char_offset_end INT NOT NULL,
    text_content TEXT NOT NULL,                  -- Full paragraph text (for reference)
    token_count INT NOT NULL,                    -- For chunk size validation
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(module_number, chapter_title, section_id, paragraph_index)
);

CREATE INDEX idx_chunks_module ON book_content_chunks(module_number);
CREATE INDEX idx_chunks_section ON book_content_chunks(section_id);
```

**Validation Rules**:
- `module_number` ∈ [1, 10] (Physical AI book has 7 modules, allow room for expansion)
- `paragraph_index` ≥ 0
- `token_count` ∈ [50, 400] (chunk size constraints)
- `section_id` must match Docusaurus frontmatter format: `[a-z0-9-]+`
- `text_content` non-empty

---

#### Table: `query_analytics`

Stores query metadata for analytics (not for conversation history; that's browser-only).

```sql
CREATE TABLE query_analytics (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,                    -- Frontend-generated UUID
    query_text TEXT NOT NULL,
    query_mode VARCHAR(50) NOT NULL,             -- 'full-book' or 'selected-text'
    selected_text TEXT,                          -- NULL if mode=full-book
    current_page_url TEXT,                       -- For context tracking
    response_latency_ms INT NOT NULL,            -- Total pipeline latency
    retrieval_latency_ms INT,                    -- Time spent in Retrieval Agent
    synthesis_latency_ms INT,                    -- Time spent in LLM
    chunks_retrieved INT,                        -- Number of chunks returned by retrieval
    chunks_used INT,                             -- Number of chunks cited in answer
    error_code VARCHAR(50),                      -- NULL if successful, error code otherwise
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CHECK (query_mode IN ('full-book', 'selected-text')),
    CHECK (response_latency_ms >= 0),
    CHECK (chunks_retrieved >= 0),
    CHECK (chunks_used >= 0 AND chunks_used <= chunks_retrieved)
);

CREATE INDEX idx_analytics_session ON query_analytics(session_id);
CREATE INDEX idx_analytics_created ON query_analytics(created_at);
CREATE INDEX idx_analytics_mode ON query_analytics(query_mode);

-- Retention policy: Delete records older than 30 days
-- (Implement as scheduled job or trigger)
```

**Validation Rules**:
- `query_mode` must be `'full-book'` or `'selected-text'`
- If `query_mode = 'selected-text'`, `selected_text` must not be NULL
- `response_latency_ms` ≥ `retrieval_latency_ms + synthesis_latency_ms` (sanity check)
- `error_code` ∈ {NULL, 'RATE_LIMIT', 'TIMEOUT', 'SERVICE_UNAVAILABLE', 'INVALID_INPUT', 'NO_RESULTS', 'OUT_OF_SCOPE'}

---

### Qdrant Collection Schema

#### Collection: `physical-ai-book-v1`

Stores vector embeddings for book content chunks.

**Collection Config**:
```json
{
  "collection_name": "physical-ai-book-v1",
  "vector_config": {
    "size": 1536,
    "distance": "Cosine"
  }
}
```

**Point Schema**:
```json
{
  "id": "chunk_id (UUID as string)",
  "vector": [0.123, -0.456, ...],  // 1536-dimensional embedding
  "payload": {
    "chunk_id": "UUID",
    "module_number": 1,
    "module_name": "Introduction to Physical AI",
    "chapter_title": "What is Physical AI?",
    "section_id": "what-is-physical-ai",
    "paragraph_index": 0,
    "text_content": "Physical AI refers to...",
    "token_count": 245
  }
}
```

**Indexing Strategy**:
- HNSW index (default) for fast approximate nearest neighbor search
- `m`: 16 (connections per layer)
- `ef_construct`: 100 (construction-time accuracy)
- `ef`: 128 (search-time accuracy)

**Validation Rules**:
- `id` must match `chunk_id` in Postgres `book_content_chunks` table
- `vector` must be 1536-dimensional (text-embedding-3-small output)
- `payload` must include all fields for citation generation (no missing keys)

---

### Browser LocalStorage Schema

#### Key: `chatbot_session_id`

Stores session UUID.

**Schema**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### Key: `chatbot_conversation_history`

Stores conversation query-response pairs.

**Schema**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "queries": [
    {
      "query": "What is sensor fusion?",
      "mode": "full-book",
      "answer": "Sensor fusion is the process of...",
      "citations": [
        {"text": "Module 4: Perception Systems", "url": "/docs/module-4/sensor-fusion#overview"}
      ],
      "timestamp": "2025-12-25T10:30:00Z"
    },
    {
      "query": "Explain this passage",
      "mode": "selected-text",
      "selected_text": "Inverse kinematics calculates...",
      "answer": "This passage describes...",
      "citations": [
        {"text": "Module 5: Control Systems", "url": "/docs/module-5/kinematics#inverse"}
      ],
      "timestamp": "2025-12-25T10:32:15Z"
    }
  ]
}
```

**Validation Rules**:
- `queries` array max length: 20 (enforced by frontend)
- `timestamp` must be ISO 8601 format
- Queries older than 7 days are pruned on load
- If mode = `'selected-text'`, `selected_text` field must exist

---

## Entity Definitions

### 1. BookContentChunk

**Description**: A discrete paragraph-sized chunk of book content indexed for retrieval.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `chunk_id` | UUID | Primary key, unique | Unique identifier for chunk |
| `module_number` | Integer | 1-10 | Module number in book |
| `module_name` | String | Max 255 chars | Human-readable module name |
| `chapter_title` | String | Max 255 chars | Chapter title |
| `section_id` | String | Max 255 chars, slug format | Stable Docusaurus section ID |
| `paragraph_index` | Integer | ≥ 0 | 0-based paragraph index within section |
| `char_offset_start` | Integer | ≥ 0 | Start character position in source file |
| `char_offset_end` | Integer | > char_offset_start | End character position |
| `text_content` | String | 50-2000 chars | Full paragraph text |
| `token_count` | Integer | 50-400 | Token count for chunk (OpenAI tokenizer) |
| `embedding_vector` | Float[] | Length 1536 | Vector embedding (stored in Qdrant) |

**Relationships**:
- **Many chunks → One module**: Each chunk belongs to one module
- **Many chunks → One chapter**: Each chunk belongs to one chapter
- **Many chunks → One section**: Each chunk belongs to one section

**State Transitions**:
- **Created**: Chunk indexed during initial book indexing
- **Updated**: Chunk re-indexed when book content changes
- **Deleted**: Chunk removed if section deleted from book (orphan cleanup)

**Validation Rules**:
1. `text_content` must not be empty or whitespace-only
2. `token_count` must match actual tokenization of `text_content` (±5% tolerance)
3. `section_id` must exist in Docusaurus site structure (validated during indexing)
4. `paragraph_index` must be unique within (module, chapter, section) tuple

---

### 2. Query

**Description**: A user's natural language question submitted to the chatbot. Stored for analytics only (not conversation history).

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `query_id` | UUID | Primary key | Unique identifier |
| `session_id` | UUID | Foreign key to session | Session this query belongs to |
| `query_text` | String | 1-5000 chars | User's question |
| `query_mode` | Enum | 'full-book' \| 'selected-text' | Retrieval mode |
| `selected_text` | String | Optional, max 10000 chars | User-highlighted text (if mode=selected-text) |
| `current_page_url` | String | Valid URL | Current documentation page |
| `timestamp` | DateTime | ISO 8601 | When query was submitted |

**Validation Rules**:
1. `query_text` must not be empty
2. If `query_mode = 'selected-text'`, `selected_text` must not be NULL
3. `current_page_url` must be a valid URL matching `/docs/*` pattern
4. `timestamp` must be ≤ current server time (reject future timestamps)

---

### 3. Response

**Description**: The chatbot's synthesized answer with citations. Transient (exists only in API response).

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `answer` | String | 0-2000 chars | Synthesized answer text (empty if error) |
| `citations` | Citation[] | 0-10 items | List of source citations |
| `mode` | Enum | 'full-book' \| 'selected-text' | Echo of query mode |
| `latency_ms` | Integer | ≥ 0 | Total response time in milliseconds |
| `error_code` | String | Optional | Error code if request failed |
| `error_message` | String | Optional | User-friendly error message |

**Validation Rules**:
1. If `error_code` is not NULL, `answer` should contain error explanation
2. `citations` must not contain duplicate URLs
3. `latency_ms` must be < 5000ms (enforced by timeout)
4. If `answer` is empty, `error_code` must be set

---

### 4. Citation

**Description**: A reference to a specific book section used in answer synthesis.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `text` | String | Max 255 chars | Display text (e.g., "Module 5: Control Systems") |
| `url` | String | Valid URL | Docusaurus link (e.g., "/docs/module-5/kinematics#inverse") |
| `chunk_id` | UUID | References BookContentChunk | Source chunk (for debugging) |

**Validation Rules**:
1. `url` must be a valid relative URL starting with `/docs/`
2. `url` must include section anchor (`#section-id`) if available
3. `text` must follow format: "Module N: Chapter Title" or "Module N: Section"
4. `chunk_id` must exist in `book_content_chunks` table

---

### 5. ConversationSession

**Description**: A browser session containing conversation history. Stored in LocalStorage only.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `session_id` | UUID | Unique | Frontend-generated session UUID |
| `queries` | Array<QueryResponsePair> | Max 20 items | List of query-response pairs |
| `created_at` | DateTime | ISO 8601 | Session start time |
| `last_activity` | DateTime | ISO 8601 | Last query timestamp |

**QueryResponsePair**:
```typescript
{
  query: string;
  mode: 'full-book' | 'selected-text';
  selected_text?: string;
  answer: string;
  citations: Citation[];
  timestamp: string; // ISO 8601
}
```

**Validation Rules**:
1. `queries` array length ≤ 20 (trim oldest when exceeding)
2. Queries older than 7 days are pruned on session load
3. Total LocalStorage size for session < 500KB (enforce pruning if exceeded)

**State Transitions**:
- **Created**: On first chatbot interaction (UUID generated)
- **Active**: User is actively asking questions
- **Idle**: No activity for >10 minutes (session still valid)
- **Expired**: >7 days since `last_activity` (pruned on load)

---

### 6. UserContext

**Description**: Metadata about user's current state in the documentation. Transient (exists only in API request).

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `current_page_url` | String | Valid URL | Current documentation page |
| `active_theme` | Enum | 'light' \| 'dark' | Current Docusaurus theme |
| `selected_text` | String | Optional, max 10000 chars | Text highlighted by user |
| `selection_start` | Integer | ≥ 0 | Character offset start |
| `selection_end` | Integer | > selection_start | Character offset end |
| `session_id` | UUID | References session | Current session UUID |

**Validation Rules**:
1. `current_page_url` must match `/docs/module-*` or `/docs/Part-*` pattern
2. If `selected_text` exists, `selection_start` and `selection_end` must be valid
3. `selection_end - selection_start` must equal length of `selected_text`
4. `selected_text` must not be empty or whitespace-only

---

## Relationships Diagram

```text
┌─────────────────────────┐
│  BookContentChunk       │
│  (Postgres + Qdrant)    │
│                         │
│  - chunk_id (PK)        │
│  - module_number        │
│  - chapter_title        │
│  - section_id           │
│  - text_content         │
│  - embedding_vector     │
└───────────┬─────────────┘
            │
            │ Referenced by (N:1)
            │
            ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  Citation               │◀───────┤  Response               │
│  (Transient)            │ N:1    │  (Transient)            │
│                         │         │                         │
│  - chunk_id (FK)        │         │  - answer               │
│  - text                 │         │  - citations[]          │
│  - url                  │         │  - latency_ms           │
└─────────────────────────┘         └───────────┬─────────────┘
                                                 │
                                                 │ Generated from (1:1)
                                                 │
                                                 ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  Query                  │────────▶│  QueryAnalytics         │
│  (Transient API input)  │ 1:1    │  (Postgres)             │
│                         │         │                         │
│  - query_text           │         │  - query_id (PK)        │
│  - query_mode           │         │  - session_id           │
│  - selected_text        │         │  - response_latency_ms  │
└───────────┬─────────────┘         └─────────────────────────┘
            │
            │ Part of (N:1)
            │
            ▼
┌─────────────────────────┐
│  ConversationSession    │
│  (Browser LocalStorage) │
│                         │
│  - session_id (PK)      │
│  - queries[]            │
│  - created_at           │
│  - last_activity        │
└───────────┬─────────────┘
            │
            │ Contains (1:1)
            │
            ▼
┌─────────────────────────┐
│  UserContext            │
│  (Transient API input)  │
│                         │
│  - session_id (FK)      │
│  - current_page_url     │
│  - selected_text        │
└─────────────────────────┘
```

---

## Data Flow

### Indexing Flow (One-Time Setup)

```text
1. Book Markdown Files
   ↓
2. Chunking Script (scripts/index_book_content.py)
   - Parse markdown, extract paragraphs
   - Generate embeddings via OpenAI API
   ↓
3. Postgres Insert: book_content_chunks (metadata)
   ↓
4. Qdrant Insert: physical-ai-book-v1 (vectors + payload)
```

### Query Flow (Runtime)

```text
1. User submits query + mode + selection (if applicable)
   ↓
2. Frontend sends: POST /api/v1/query
   {session_id, query, mode, selection, current_page_url}
   ↓
3. Backend Pipeline:
   a. Context Selection Agent → determines scope
   b. Retrieval Agent → fetches BookContentChunks from Qdrant
   c. Answer Synthesis Agent → calls OpenAI API
   d. Citation Agent → resolves chunk_ids to Citations via Postgres
   ↓
4. Backend stores: query_analytics (Postgres)
   ↓
5. Backend returns: Response {answer, citations, latency_ms}
   ↓
6. Frontend appends to ConversationSession (LocalStorage)
   ↓
7. Frontend renders answer + citations in UI
```

---

## Migration Strategy

### Initial Schema Creation

1. **Postgres**: Run SQL migrations to create `book_content_chunks` and `query_analytics` tables
2. **Qdrant**: Create collection `physical-ai-book-v1` via Python SDK
3. **Indexing**: Run `scripts/index_book_content.py` to populate both Postgres and Qdrant

### Schema Evolution (Future)

- **Adding Fields**: Add nullable columns to Postgres tables, backfill with default values
- **Re-indexing**: Create new Qdrant collection (`physical-ai-book-v2`), populate, swap collection name in config
- **Breaking Changes**: Use collection versioning to allow zero-downtime migration

---

## Data Retention Policies

| Data Type | Retention Period | Cleanup Mechanism |
|-----------|------------------|-------------------|
| `book_content_chunks` | Indefinite (until re-indexed) | Manual cleanup when book content deleted |
| `query_analytics` | 30 days | Scheduled job deletes records where `created_at < NOW() - INTERVAL '30 days'` |
| `ConversationSession` | 7 days or 20 queries | Frontend prunes on load |
| Transient entities (Query, Response, UserContext) | Request-scoped only | Garbage collected after response sent |

---

## Next Steps

1. **Implement Postgres migrations** using Alembic or raw SQL
2. **Implement Qdrant collection setup** in `scripts/setup_vector_db.py`
3. **Create data models** in `rag-chatbot/src/models/` as Pydantic schemas
4. **Validate data model** against API contracts in `contracts/` (next artifact)
