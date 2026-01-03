# ChatKit Widget ↔ RAG Orchestration Integration Guide

**Document Type**: Integration Guide
**Phase**: 6 (Design Intelligence)
**Created**: 2025-12-26
**Status**: Design Specification (No Runtime Code)

---

## Overview

This guide documents how the ChatKit Widget integrates with the **RAG Orchestration Subagent** (`.claude/agents/rag-orchestration/`) for document-grounded question answering.

**Integration Pattern**: Event-Driven Architecture (Pattern 1)
**Communication**: Asynchronous event-based messaging
**Data Format**: JSON event payloads (defined in SKILL.md, mcp.json)

---

## Integration Architecture

```
┌─────────────────────┐
│  ChatKit Widget     │
│  (Frontend)         │
└──────────┬──────────┘
           │ user_message event
           ↓
┌─────────────────────┐
│  Event Bus          │
│  (Message Broker)   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  RAG Orchestration  │
│  Subagent           │
│  (Backend)          │
└──────────┬──────────┘
           │ agent_response event
           ↓
┌─────────────────────┐
│  ChatKit Widget     │
│  (Renders Answer)   │
└─────────────────────┘
```

**Key Design Principles**:
1. **Decoupling**: Widget doesn't call RAG API directly
2. **Event-Driven**: All communication via standardized events
3. **Asynchronous**: Widget doesn't block on RAG processing
4. **Resilient**: Circuit breaker for RAG API failures (Pattern 5)

---

## Event Flow: User Question → RAG Answer

### Step 1: User Submits Question

**Trigger**: User types question and presses Enter
**Widget State**: Idle → Typing → Processing

**Event Emitted**: `user_message`

```json
{
  "event": "user_message",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "anon-uuid-or-auth-session",
  "message": {
    "id": "msg-uuid",
    "type": "text",
    "content": "What is embodied intelligence?",
    "metadata": {
      "mode": "full-corpus",
      "selected_text": null,
      "context": {
        "current_page": "/docs/module-2-embodied/embodied-intelligence",
        "user_tier": "anonymous"
      }
    }
  }
}
```

**Required Fields**:
- `session_id` (UUID) - Anonymous: browser-generated, Authenticated: server-issued
- `message.content` (string, max 500 chars per FR-003)
- `metadata.mode` ("full-corpus" | "selected-text")
- `context.user_tier` ("anonymous" | "lightweight" | "full" | "premium")

---

### Step 2: RAG Orchestration Processes Query

**Subagent Location**: `.claude/agents/rag-orchestration/`

**Processing Pipeline** (4 steps):
1. **Context Selection**: Determine retrieval scope (full-corpus vs. selected-text)
2. **Retrieval**: Vector search in Qdrant (top-k chunks)
3. **Synthesis**: LLM generates answer from retrieved chunks
4. **Guardrails**: Validate answer boundaries, generate citations

**Timeout**: 10 seconds (FR-032)
**Fallback**: Circuit breaker after 3 failures → Offline FAQ (Pattern 5)

---

### Step 3: RAG Agent Returns Answer

**Trigger**: RAG agent completes synthesis
**Widget State**: Processing → Responding

**Event Emitted**: `agent_response`

```json
{
  "event": "agent_response",
  "timestamp": "2025-12-26T10:30:02.500Z",
  "session_id": "anon-uuid-or-auth-session",
  "message": {
    "id": "response-uuid",
    "type": "text",
    "content": "Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences...",
    "citations": [
      {
        "id": "citation-1",
        "module_id": "module-2-embodied",
        "chapter_id": "embodied-intelligence",
        "section_id": "definition",
        "url": "/docs/module-2-embodied/embodied-intelligence#definition",
        "excerpt": "Embodied intelligence is the idea that..."
      },
      {
        "id": "citation-2",
        "module_id": "module-2-embodied",
        "chapter_id": "sensorimotor-integration",
        "section_id": "perception-action-loop",
        "url": "/docs/module-2-embodied/sensorimotor-integration#perception-action-loop",
        "excerpt": "The perception-action loop enables..."
      }
    ],
    "metadata": {
      "mode": "full-corpus",
      "retrieval_count": 5,
      "synthesis_time_ms": 1200,
      "guardrails_passed": true
    }
  }
}
```

**Required Fields**:
- `message.content` (string) - Synthesized answer
- `citations[]` (array) - Source attributions (Stable-ID pattern)
- `metadata.guardrails_passed` (boolean) - Boundary validation result

---

### Step 4: Widget Renders Answer

**Trigger**: Widget consumes `agent_response` event
**Widget State**: Responding → Idle

**Rendering Steps**:
1. Display answer text with markdown formatting
2. Render citations as inline superscript numbers [1], [2]
3. Make citations clickable (navigate to source URL)
4. Append message to conversation history
5. Save conversation to browser LocalStorage (anonymous) or server (authenticated)

---

## Error Handling & Resilience

### Error Scenario 1: RAG API Timeout

**Condition**: No `agent_response` received within 10 seconds (FR-032)

**Widget Behavior**:
1. Widget state: Processing → Error
2. Emit `error` event:

```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:10.000Z",
  "session_id": "anon-uuid",
  "error": {
    "code": "RAG_API_TIMEOUT",
    "message": "The chatbot is taking longer than expected. Please try again.",
    "severity": "recoverable",
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 1000
    }
  }
}
```

3. Display user-friendly error message
4. Show "Retry" button
5. User clicks retry → Error → Idle → Typing → Processing (retry)

---

### Error Scenario 2: Circuit Breaker Opens

**Condition**: 3 consecutive RAG API failures (FR-033, Pattern 5)

**Widget Behavior**:
1. Circuit breaker state: OPEN (60-second cooldown)
2. Widget switches to **offline FAQ fallback**:

```json
{
  "event": "system_message",
  "timestamp": "2025-12-26T10:30:15.000Z",
  "session_id": "anon-uuid",
  "message": {
    "type": "warning",
    "severity": "medium",
    "content": "⚠ Network unavailable. Showing cached answers from FAQ.",
    "action": null
  }
}
```

3. Widget queries local FAQ cache (static JSON file)
4. Display cached answer with disclaimer: "⚠ Offline mode: Limited to cached content"
5. After 60 seconds, circuit breaker transitions to HALF-OPEN (retry next query)

**Offline FAQ Structure** (design-level):
```json
{
  "faq": [
    {
      "question": "What is embodied intelligence?",
      "answer": "Embodied intelligence is the theory that...",
      "source": "/docs/module-2-embodied/embodied-intelligence"
    }
  ]
}
```

---

### Error Scenario 3: Guardrails Failure

**Condition**: `guardrails_passed: false` in `agent_response`

**Widget Behavior**:
1. RAG agent detected out-of-scope question
2. Agent returns boundary message:

```json
{
  "message": {
    "content": "This question is outside the book's scope. I can only answer questions about Physical AI and Humanoid Robotics topics covered in the documentation.",
    "citations": [],
    "metadata": {
      "guardrails_passed": false
    }
  }
}
```

3. Widget displays boundary message to user
4. No citations rendered (empty citations array)
5. Conversation continues normally (no error state)

---

## Integration Points with Existing Artifacts

### 1. RAG Orchestration Subagent

**Location**: `.claude/agents/rag-orchestration/`

**Consumes**: `user_message` events
**Emits**: `agent_response`, `error` events

**Contract**: Event schemas defined in `.claude/skills/chatkit-widget/SKILL.md` lines 82-224

---

### 2. RAG Chatbot Skill

**Location**: `.claude/skills/rag-chatbot/SKILL.md`

**Provides**:
- Dual-mode retrieval logic (full-corpus vs. selected-text)
- Citation rendering patterns (Stable-ID system)
- Guardrails boundary enforcement

**Pattern Alignment**: ChatKit Pattern 1 (Event-Driven) + RAG Chatbot orchestration

---

### 3. Better-Auth MCP

**Location**: `.claude/mcp/better-auth/`

**Provides**:
- User authentication (tier determination)
- Session management (session_id generation)

**Integration**: When user upgrades from anonymous → authenticated, session_id changes from browser-generated to server-issued

---

## Rate Limiting (Privacy-Compliant)

**Anonymous Users** (Tier 0): 10 messages/minute (NFR-012, mcp.json line 220)
**Authenticated Users** (Tier 1+): 30 messages/minute (mcp.json line 220)

**Rate Limit Enforcement**:
- Widget tracks message count per minute (browser-side counter)
- When limit exceeded, emit `system_message`:

```json
{
  "message": {
    "type": "info",
    "severity": "low",
    "content": "You've reached the rate limit (10 questions/min). Create a free account for unlimited questions.",
    "action": {
      "type": "button",
      "label": "Sign Up",
      "event": "signup_triggered"
    }
  }
}
```

- User can click "Sign Up" → Triggers Progressive Signup flow (Pattern 3)

---

## Testing Strategy (Phase 7+ Implementation)

### Unit Tests (Widget)
1. Test `user_message` event emission on question submit
2. Test `agent_response` event consumption and rendering
3. Test error event handling (timeout, circuit breaker)
4. Test citation link generation (Stable-ID → URL)

### Integration Tests (Widget ↔ RAG Agent)
1. End-to-end Q&A flow (submit question → receive answer)
2. Timeout handling (mock RAG API delay >10s)
3. Circuit breaker activation (3 consecutive failures)
4. Guardrails rejection (out-of-scope question)
5. Dual-mode switching (full-corpus → selected-text)

### Contract Tests
1. Validate `user_message` payload matches mcp.json schema
2. Validate `agent_response` payload matches mcp.json schema
3. Validate citation objects have all required fields (Stable-ID pattern)

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| RAG API Response Time (p95) | ≤3 seconds | NFR-003 |
| Widget Event Emission Latency | ≤50ms | Pattern 2 (Progressive Loading) |
| Citation Rendering Time (100 citations) | ≤100ms | Pattern 4 (Citation-Aware) |
| Offline FAQ Lookup | ≤10ms | Pattern 5 (Graceful Degradation) |

---

## Security Considerations

1. **Input Sanitization**: Widget MUST sanitize user input before emitting `user_message` (XSS prevention, NFR-009)
2. **HTTPS Only**: All RAG API requests MUST use HTTPS (NFR-011)
3. **Session Token Security**: Authenticated session_id MUST use HttpOnly, Secure, SameSite=Strict cookies (FR-023)
4. **No Message Content Logging**: Widget MUST NOT log message content for anonymous users (FR-039)

---

## Deployment Checklist

- [ ] RAG Orchestration Subagent deployed and reachable
- [ ] Event bus (WebSocket or HTTP) configured
- [ ] Circuit breaker thresholds configured (3 failures, 60s cooldown)
- [ ] Offline FAQ cache pre-populated (static JSON file)
- [ ] Rate limiting enforced (10 msg/min anonymous, 30 msg/min authenticated)
- [ ] Citation URL template configured (base URL + Stable-ID pattern)
- [ ] Error messages tested (timeout, circuit breaker, guardrails)
- [ ] Performance validated (p95 latency ≤3s)

---

## References

- **Event Schemas**: `.claude/skills/chatkit-widget/SKILL.md` lines 76-224
- **Pattern 1 (Event-Driven)**: `.claude/skills/chatkit-widget/patterns.md` lines 24-126
- **Pattern 4 (Citations)**: `.claude/skills/chatkit-widget/patterns.md` lines 419-556
- **Pattern 5 (Degradation)**: `.claude/skills/chatkit-widget/patterns.md` lines 557-747
- **RAG Chatbot Skill**: `.claude/skills/rag-chatbot/SKILL.md`
- **MCP JSON Schemas**: `.claude/mcp/chatkit/mcp.json` lines 44-181

---

**Last Updated**: 2025-12-26
**Status**: Design Specification Complete ✅
**Next Step**: Implement widget event emitters and RAG agent event consumers (Phase 7+)
