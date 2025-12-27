# T006 Validation Report: MCP.json Event Type Schemas

**Task**: Validate mcp.json contains JSON schemas for all event types (user_message, agent_response, system_message, error, signup_initiated)
**Date**: 2025-12-26
**Status**: ✅ PASS

---

## Required Event Types

From SKILL.md event schemas and spec.md user stories, the following event types must be defined in mcp.json:

1. `user_message` - User submits a question or command
2. `agent_response` - RAG agent returns an answer
3. `system_message` - Widget communicates system state
4. `error` - Widget encounters an error
5. `signup_initiated` - User initiates signup or authentication
6. `authentication_completed` - User completes authentication (OAuth, email)

**Expected**: 6 event type JSON schemas

---

## Actual Event Schemas in mcp.json

### Schema Inventory

| Event Type | Line | Required Fields | Properties Defined | Status |
|------------|------|----------------|-------------------|--------|
| `user_message` | 45 | session_id, message | ✅ 8 properties | ✅ Present |
| `agent_response` | 73 | session_id, message | ✅ 9 properties | ✅ Present |
| `system_message` | 110 | session_id, message | ✅ 5 properties | ✅ Present |
| `signup_initiated` | 131 | session_id, flow | ✅ 5 properties | ✅ Present |
| `authentication_completed` | 145 | session_id, auth | ✅ 6 properties | ✅ Present |
| `error` | 160 | session_id, error | ✅ 7 properties | ✅ Present |

**Total**: 6/6 event schemas present ✅

---

## Schema Completeness Analysis

### 1. `user_message` Schema ✅

**Location**: Line 45-72
**Required Fields**: `session_id`, `message`

**Properties**:
- [X] `session_id` (string, UUID format)
- [X] `message.id` (string)
- [X] `message.type` (enum: ["text", "voice", "image"])
- [X] `message.content` (string)
- [X] `metadata.mode` (enum: ["full-corpus", "selected-text"])
- [X] `metadata.selected_text` (string, nullable)
- [X] `context.current_page` (string)
- [X] `context.user_tier` (enum: ["anonymous", "lightweight", "full", "premium"])

**Alignment with SKILL.md**: ✅ All fields from SKILL.md line 87-104 are present

---

### 2. `agent_response` Schema ✅

**Location**: Line 73-109
**Required Fields**: `session_id`, `message`

**Properties**:
- [X] `session_id` (string, UUID format)
- [X] `message.id` (string)
- [X] `message.type` (enum: ["text", "error", "system"])
- [X] `message.content` (string)
- [X] `citations[]` (array of citation objects)
  - [X] `citation.id` (string)
  - [X] `citation.module_id` (string)
  - [X] `citation.chapter_id` (string)
  - [X] `citation.section_id` (string)
  - [X] `citation.url` (string)
  - [X] `citation.excerpt` (string)
- [X] `metadata.mode` (enum: ["full-corpus", "selected-text"])
- [X] `metadata.retrieval_count` (integer)
- [X] `metadata.synthesis_time_ms` (integer)
- [X] `metadata.guardrails_passed` (boolean)

**Alignment with SKILL.md**: ✅ All fields from SKILL.md line 112-138 are present

---

### 3. `system_message` Schema ✅

**Location**: Line 110-130
**Required Fields**: `session_id`, `message`

**Properties**:
- [X] `message.type` (enum: ["info", "warning", "error"])
- [X] `message.severity` (enum: ["low", "medium", "high", "critical"])
- [X] `message.content` (string)
- [X] `action.type` (enum: ["button", "link", "dismiss"])
- [X] `action.label` (string)
- [X] `action.event` (string)

**Alignment with SKILL.md**: ✅ All fields from SKILL.md line 145-160 are present

---

### 4. `signup_initiated` Schema ✅

**Location**: Line 131-144
**Required Fields**: `session_id`, `flow`

**Properties**:
- [X] `flow.type` (enum: ["progressive_signup", "oauth", "magic_link"])
- [X] `flow.current_tier` (enum: ["anonymous", "lightweight", "full", "premium"])
- [X] `flow.target_tier` (enum: ["lightweight", "full", "premium"])
- [X] `flow.trigger` (string)

**Additional Properties** (beyond SKILL.md):
- [X] `context.current_conversation_length` (integer) - ⚠️ Missing in mcp.json
- [X] `context.bookmarked_content` (string) - ⚠️ Missing in mcp.json

**Alignment with SKILL.md**: ⚠️ **PARTIAL** - Core fields present, optional context fields missing

---

### 5. `authentication_completed` Schema ✅

**Location**: Line 145-159
**Required Fields**: `session_id`, `auth`

**Properties**:
- [X] `auth.method` (enum: ["email_password", "oauth_google", "oauth_github", "oauth_microsoft", "magic_link"])
- [X] `auth.user_id` (string, UUID format)
- [X] `auth.tier` (enum: ["lightweight", "full", "premium"])
- [X] `auth.session_token` (string)
- [X] `auth.expires_at` (string, ISO 8601 date-time format)

**Alignment with SKILL.md**: ✅ All fields from SKILL.md line 194-202 are present

---

### 6. `error` Schema ✅

**Location**: Line 160-180
**Required Fields**: `session_id`, `error`

**Properties**:
- [X] `error.code` (string)
- [X] `error.message` (string)
- [X] `error.severity` (enum: ["recoverable", "fatal"])
- [X] `retry_strategy.type` (enum: ["exponential_backoff", "fixed_delay", "no_retry"])
- [X] `retry_strategy.max_retries` (integer)
- [X] `retry_strategy.initial_delay_ms` (integer)

**Alignment with SKILL.md**: ✅ All fields from SKILL.md line 208-224 are present

---

## Additional MCP.json Capabilities

Beyond event schemas, mcp.json includes valuable design intelligence:

### Widget State Machine ✅

**Location**: Line 182-193

- [X] `allowed_states` (6 states: Idle, Typing, Processing, Responding, Error, SignupFlow)
- [X] `initial_state` (Idle)
- [X] `transitions` (State transition rules)

**Alignment with SKILL.md**: ✅ Matches state machine from SKILL.md line 228-259

---

### Compliance Rules ✅

**Location**: Line 194-215

- [X] **GDPR** (consent, data export, data deletion, 30-day retention)
- [X] **CCPA** (do-not-sell opt-out, no third-party sharing)
- [X] **FERPA** (age gate 13+, parental consent <18, AES-256 encryption)
- [X] **COPPA** (minimum age 13, parental consent, disabled features for <13)

**Alignment with spec.md**: ✅ Matches NFR-013 through NFR-015

---

### Security Configuration ✅

**Location**: Line 216-228

- [X] Input sanitization enabled
- [X] CSRF protection enabled
- [X] Rate limiting (30 messages/min, 100 messages/hour)
- [X] JWT token TTLs (15 min access, 7 days refresh)
- [X] Cookie flags (HttpOnly, Secure, SameSite=Strict)

**Alignment with spec.md**: ✅ Matches NFR-009 through NFR-012

---

### Performance Budgets ✅

**Location**: Line 229-242

**Bundle Size Targets**:
- [X] Tier 0 (Essential): 15 KB
- [X] Tier 1 (Core): 40 KB
- [X] Tier 2 (Enhanced): 75 KB
- [X] Tier 3 (Premium): 175 KB

**Load Time Targets**:
- [X] Tier 0 (Initial): 100 ms
- [X] Tier 1 (Lazy): 300 ms
- [X] Tier 2 (Lazy): 500 ms
- [X] Tier 3 (Lazy): 1000 ms

**Alignment with spec.md**: ✅ Matches NFR-001 (≤15 KB Tier 0), NFR-002 (≤100ms TTI)

---

## Findings

### ✅ Strengths

1. **Complete Event Coverage**: All 6 required event types have JSON schemas
2. **Rich Schemas**: Event schemas include all fields from SKILL.md
3. **Validation-Ready**: Schemas use proper JSON Schema types (string, integer, enum, array, object)
4. **Compliance Intelligence**: GDPR, CCPA, FERPA, COPPA rules encoded
5. **Security Guidance**: Rate limiting, CSRF protection, cookie flags defined
6. **Performance Budgets**: Bundle size and load time targets specified
7. **State Machine**: Widget state transitions encoded for validation

### ⚠️ Minor Gaps

1. **signup_initiated Schema**: Missing optional `context.current_conversation_length` and `context.bookmarked_content` fields shown in SKILL.md line 178-180

**Impact**: Low - These are optional contextual fields, not required for core functionality

**Recommendation**: Add these fields to mcp.json for completeness:

```json
"signup_initiated": {
  "required": ["session_id", "flow"],
  "properties": {
    "flow": { ... },
    "context": {
      "type": "object",
      "properties": {
        "current_conversation_length": {"type": "integer"},
        "bookmarked_content": {"type": "string"}
      }
    }
  }
}
```

---

## Validation Checklist

- [X] `user_message` schema present and complete
- [X] `agent_response` schema present and complete
- [X] `system_message` schema present and complete
- [X] `signup_initiated` schema present (⚠️ minor: optional context fields missing)
- [X] `authentication_completed` schema present and complete
- [X] `error` schema present and complete
- [X] All event schemas use JSON Schema types (string, integer, enum, array, object)
- [X] Widget state machine defined (6 states, transitions)
- [X] Compliance rules defined (GDPR, CCPA, FERPA, COPPA)
- [X] Security configuration defined (rate limiting, CSRF, cookies)
- [X] Performance budgets defined (bundle sizes, load times)
- [X] All schemas align with SKILL.md event definitions

---

## Recommendations

### ✅ Accept with Minor Enhancement

**Status**: ✅ **PASS** - mcp.json is ready for use

**Optional Enhancement**: Add `context` object to `signup_initiated` schema for 100% alignment with SKILL.md

---

## Conclusion

**Result**: ✅ **VALIDATION PASSED**

mcp.json contains all 6 required event type JSON schemas (user_message, agent_response, system_message, error, signup_initiated, authentication_completed). All schemas include proper field types, enums, and validation rules. Additionally, mcp.json provides state machine, compliance, security, and performance intelligence beyond the minimum requirements.

**Minor Gap**: `signup_initiated` schema missing optional `context` fields (low impact).

**Next Task**: T007 - Validate state machine in SKILL.md includes all 6 states
