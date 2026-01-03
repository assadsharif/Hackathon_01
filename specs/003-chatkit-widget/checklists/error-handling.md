# Error Handling Checklist: Complete Error Taxonomy

**Feature**: ChatKit Widget Integration
**User Story**: US5 - Offline Mode & Graceful Degradation (P3)
**Task**: T047 - Create comprehensive error handling checklist with complete error code taxonomy
**Date**: 2025-12-26
**Gap Addressed**: T042 validation found error event schema exists but error code taxonomy not explicit

---

## Overview

This checklist provides a **complete error code taxonomy** for ChatKit Widget, covering all error types (network, validation, authentication, guardrails) with standardized codes, severities, and retry strategies.

**Problem Solved**: The validation report (T041-T044) identified that while error events exist in SKILL.md, there was no explicit error code taxonomy. This checklist fills that gap.

---

## Table of Contents

1. [Error Code Taxonomy](#error-code-taxonomy)
2. [Network Errors](#network-errors)
3. [Validation Errors](#validation-errors)
4. [Authentication Errors](#authentication-errors)
5. [Guardrail Errors](#guardrail-errors)
6. [System Errors](#system-errors)
7. [Error Severity Levels](#error-severity-levels)
8. [Retry Strategies](#retry-strategies)
9. [Error Message Templates](#error-message-templates)
10. [Error Handling Checklist](#error-handling-checklist)

---

## Error Code Taxonomy

### Complete Error Code List

| Error Code | Category | Subtype | Severity | Retry Strategy | HTTP Status |
|------------|----------|---------|----------|----------------|-------------|
| `NETWORK_UNREACHABLE` | Network | network_error | recoverable | exponential_backoff | N/A |
| `NETWORK_TIMEOUT` | Network | timeout | recoverable | exponential_backoff | N/A |
| `RAG_API_TIMEOUT` | Network | timeout | recoverable | exponential_backoff | 504 |
| `RAG_API_UNAVAILABLE` | Network | server_error | recoverable | exponential_backoff | 503 |
| `RAG_API_500` | Network | server_error | recoverable | exponential_backoff | 500 |
| `RAG_API_502` | Network | proxy_error | recoverable | exponential_backoff | 502 |
| `RAG_API_404` | Network | not_found | fatal | none | 404 |
| `INVALID_INPUT` | Validation | validation_error | fatal | none | 400 |
| `RATE_LIMIT_EXCEEDED` | Validation | rate_limit | recoverable | wait_and_retry | 429 |
| `SESSION_EXPIRED` | Authentication | auth_error | recoverable | re_authenticate | 401 |
| `INVALID_CREDENTIALS` | Authentication | auth_error | fatal | none | 401 |
| `OAUTH_TIMEOUT` | Authentication | timeout | recoverable | manual_retry | N/A |
| `OAUTH_CANCELLED` | Authentication | user_cancelled | fatal | none | N/A |
| `OUT_OF_SCOPE` | Guardrails | guardrails | warning | none | 200 |
| `CODE_GENERATION_BLOCKED` | Guardrails | guardrails | warning | none | 200 |
| `LOW_CONFIDENCE` | Guardrails | guardrails | warning | none | 200 |
| `CIRCUIT_BREAKER_OPEN` | System | circuit_breaker | recoverable | wait_for_cooldown | N/A |
| `WIDGET_INITIALIZATION_FAILED` | System | critical | fatal | reload_page | N/A |
| `INDEXEDDB_ERROR` | System | storage_error | recoverable | fallback_localstorage | N/A |

**Total Error Codes**: 19 (comprehensive coverage)

---

## Network Errors

### 1. NETWORK_UNREACHABLE

**Description**: Client has no internet connection (DNS failure, network adapter disabled).

**When Triggered**:
- User is offline (airplane mode)
- Network adapter disabled
- DNS resolution fails
- Corporate firewall blocks all traffic

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "NETWORK_UNREACHABLE",
    "message": "You appear to be offline. Check your internet connection and try again.",
    "severity": "recoverable",
    "subtype": "network_error",
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 1000
    },
    "fallback": {
      "tier": 3,
      "source": "static_faq"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ You appear to be offline
Check your internet connection and try again.

[Use Offline FAQ]  [Retry]
```

**Retry Strategy**: Exponential backoff (1s, 2s, 4s delays)

**Fallback**: Static FAQ (Tier 3)

**Circuit Breaker**: Counts toward failure threshold (increments count)

---

### 2. NETWORK_TIMEOUT

**Description**: Network request initiated but no response received within timeout period.

**When Triggered**:
- Slow network connection (mobile 2G/3G)
- High network latency (>5s round trip)
- Intermediate proxy timeout

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:05.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "NETWORK_TIMEOUT",
    "message": "The connection is taking longer than expected. This might be due to a slow network.",
    "severity": "recoverable",
    "subtype": "timeout",
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 1000
    },
    "fallback": {
      "tier": 2,
      "source": "cached_response"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Connection Timeout
The connection is taking longer than expected.

[Try Cached Answer]  [Retry]
```

**Retry Strategy**: Exponential backoff (1s, 2s, 4s delays)

**Fallback**: Cached response (Tier 2) → Static FAQ (Tier 3)

**Circuit Breaker**: Counts toward failure threshold

---

### 3. RAG_API_TIMEOUT

**Description**: RAG API request sent but no response within 5-second timeout.

**When Triggered**:
- RAG API backend overloaded (high query volume)
- Database query slow (>5s)
- Model inference slow (large context window)

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:05.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RAG_API_TIMEOUT",
    "message": "The chatbot is taking longer than expected. Please try again.",
    "severity": "recoverable",
    "subtype": "timeout",
    "http_status": 504,
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 1000
    },
    "fallback": {
      "tier": 2,
      "source": "cached_response"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ The chatbot is taking longer than expected
This might be due to high server load. Try again in a moment.

[Try Cached Answer]  [Retry]
```

**Retry Strategy**: Exponential backoff (1s, 2s, 4s delays)

**Fallback**: Cached response (Tier 2) → Static FAQ (Tier 3)

**Circuit Breaker**: Counts toward failure threshold

---

### 4. RAG_API_UNAVAILABLE (503)

**Description**: RAG API backend is temporarily unavailable (maintenance, deployment, crash).

**When Triggered**:
- Backend deployment in progress
- Backend crashed (unhandled exception)
- Database unavailable

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RAG_API_UNAVAILABLE",
    "message": "The chatbot service is temporarily unavailable. We're working to restore it.",
    "severity": "recoverable",
    "subtype": "server_error",
    "http_status": 503,
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 2000
    },
    "fallback": {
      "tier": 3,
      "source": "static_faq"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Service Temporarily Unavailable
We're working to restore the chatbot service. Try offline answers in the meantime.

[Use Offline FAQ]  [Retry in 2s]
```

**Retry Strategy**: Exponential backoff (2s, 4s, 8s delays) - longer delays for 503

**Fallback**: Static FAQ (Tier 3)

**Circuit Breaker**: Counts toward failure threshold

---

### 5. RAG_API_500 (Internal Server Error)

**Description**: RAG API backend encountered an unhandled exception.

**When Triggered**:
- Bug in RAG API code
- Unhandled edge case (malformed query)
- Database connection pool exhausted

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RAG_API_500",
    "message": "Something went wrong on our end. Please try rephrasing your question.",
    "severity": "recoverable",
    "subtype": "server_error",
    "http_status": 500,
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 2,
      "initial_delay_ms": 1000
    },
    "fallback": {
      "tier": 3,
      "source": "static_faq"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Something went wrong on our end
Try rephrasing your question or use offline answers.

[Use Offline FAQ]  [Rephrase Question]
```

**Retry Strategy**: Exponential backoff (1s, 2s delays) - fewer retries for 500

**Fallback**: Static FAQ (Tier 3)

**Circuit Breaker**: Counts toward failure threshold

---

### 6. RAG_API_502 (Bad Gateway)

**Description**: Proxy/load balancer cannot reach RAG API backend.

**When Triggered**:
- Load balancer health check fails
- Backend process crashed
- Network partition between proxy and backend

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RAG_API_502",
    "message": "Unable to reach the chatbot service. Please try again shortly.",
    "severity": "recoverable",
    "subtype": "proxy_error",
    "http_status": 502,
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 1000
    }
  }
}
```

**User-Facing Message**: Same as RAG_API_UNAVAILABLE (503)

**Retry Strategy**: Exponential backoff (1s, 2s, 4s delays)

**Circuit Breaker**: Counts toward failure threshold

---

### 7. RAG_API_404 (Not Found)

**Description**: RAG API endpoint does not exist (configuration error, wrong URL).

**When Triggered**:
- Widget misconfigured (wrong API endpoint URL)
- API endpoint moved/deprecated
- Typo in API endpoint path

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RAG_API_404",
    "message": "The chatbot service could not be found. This is a configuration error.",
    "severity": "fatal",
    "subtype": "not_found",
    "http_status": 404,
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**:
```
❌ Configuration Error
The chatbot service could not be found. Please contact support.

[Use Offline FAQ]  [Contact Support]
```

**Retry Strategy**: None (fatal error, requires admin fix)

**Fallback**: Static FAQ (Tier 3) only

**Circuit Breaker**: Does NOT count toward failure threshold (configuration error, not service failure)

---

## Validation Errors

### 8. INVALID_INPUT

**Description**: User input is invalid (empty, too long, contains banned characters).

**When Triggered**:
- Empty message submitted
- Message exceeds 2000 character limit
- Message contains only whitespace/newlines

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Your question is too short. Please enter at least 3 characters.",
    "severity": "fatal",
    "subtype": "validation_error",
    "http_status": 400,
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Invalid Question
Your question must be 3-2000 characters. Please try again.

[Clear Input]
```

**Retry Strategy**: None (user must fix input)

**Circuit Breaker**: Does NOT count toward failure threshold

---

### 9. RATE_LIMIT_EXCEEDED

**Description**: User exceeded rate limit (too many requests in time window).

**When Triggered**:
- Anonymous user: 15 messages in 30 minutes
- Tier 1 user: 50 messages in 24 hours
- Tier 2 user: 200 messages in 24 hours

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You've reached the 15-message limit for anonymous users. Sign up to get 50 messages per day.",
    "severity": "recoverable",
    "subtype": "rate_limit",
    "http_status": 429,
    "retry_strategy": {
      "type": "wait_and_retry",
      "retry_after_seconds": 1800
    },
    "upgrade_prompt": {
      "current_tier": 0,
      "next_tier": 1,
      "action": "signup_initiated"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Message Limit Reached
You've reached the 15-message limit for anonymous users.

Sign up (free) to get 50 messages per day!

[Sign Up with Google]  [Sign Up with Email]
```

**Retry Strategy**: Wait and retry (30 minutes for anonymous users)

**Circuit Breaker**: Does NOT count toward failure threshold

---

## Authentication Errors

### 10. SESSION_EXPIRED

**Description**: User's authentication session expired (JWT access token expired).

**When Triggered**:
- Access token TTL exceeded (15 minutes)
- Refresh token TTL exceeded (7 days)
- User logged out on another device

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "SESSION_EXPIRED",
    "message": "Your session has expired. Please log in again.",
    "severity": "recoverable",
    "subtype": "auth_error",
    "http_status": 401,
    "retry_strategy": {
      "type": "re_authenticate"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Session Expired
Your session has expired. Log in to continue.

[Log In]  [Continue as Guest]
```

**Retry Strategy**: Re-authenticate (automatic refresh token attempt, then manual login)

**Circuit Breaker**: Does NOT count toward failure threshold

---

### 11. INVALID_CREDENTIALS

**Description**: User provided incorrect email/password during login.

**When Triggered**:
- Incorrect password
- Email not found in database
- Account disabled

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect email or password. Please try again.",
    "severity": "fatal",
    "subtype": "auth_error",
    "http_status": 401,
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**:
```
❌ Incorrect Email or Password
Please check your credentials and try again.

[Forgot Password?]  [Try Again]
```

**Retry Strategy**: None (user must provide correct credentials)

**Circuit Breaker**: Does NOT count toward failure threshold

---

### 12. OAUTH_TIMEOUT

**Description**: OAuth flow did not complete within 10-second timeout.

**When Triggered**:
- User closed OAuth popup without completing
- OAuth provider slow (Google/GitHub timeout)
- Network timeout during OAuth redirect

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:10.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "OAUTH_TIMEOUT",
    "message": "Authentication timed out. Please try again.",
    "severity": "recoverable",
    "subtype": "timeout",
    "retry_strategy": {
      "type": "manual_retry"
    },
    "oauth_provider": "google"
  }
}
```

**User-Facing Message**:
```
⚠️ Authentication Timeout
The OAuth flow timed out. Try again or use email signup.

[Retry with Google]  [Use Email Instead]
```

**Retry Strategy**: Manual retry (user clicks "Try Again")

**Circuit Breaker**: Does NOT count toward failure threshold (separate from RAG API)

---

### 13. OAUTH_CANCELLED

**Description**: User cancelled OAuth flow (closed popup, clicked "Cancel").

**When Triggered**:
- User closed OAuth popup before granting consent
- User clicked "Cancel" on OAuth consent screen

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:05.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "OAUTH_CANCELLED",
    "message": "OAuth authentication cancelled.",
    "severity": "fatal",
    "subtype": "user_cancelled",
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**: No error shown (silent, expected user behavior)

**Retry Strategy**: None (user intentionally cancelled)

**Circuit Breaker**: Does NOT count toward failure threshold

---

## Guardrail Errors

### 14. OUT_OF_SCOPE

**Description**: User question is outside the book's coverage (detected by RAG orchestration).

**When Triggered**:
- Question about Python programming (not Physical AI)
- Question about cooking recipes
- Question about weather

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "OUT_OF_SCOPE",
    "message": "This question is outside the book's coverage. I can only answer questions about Physical AI and Humanoid Robotics.",
    "severity": "warning",
    "subtype": "guardrails",
    "http_status": 200,
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Out of Scope
This question is outside the book's coverage. I can only answer questions about Physical AI and Humanoid Robotics.

[Rephrase Question]  [See Topics]
```

**Retry Strategy**: None (valid response, not a failure)

**Circuit Breaker**: Does NOT count toward failure threshold

---

### 15. CODE_GENERATION_BLOCKED

**Description**: User requested code generation, which is blocked by guardrails.

**When Triggered**:
- Question: "Write Python code for inverse kinematics"
- Question: "Generate ROS 2 launch file"

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "CODE_GENERATION_BLOCKED",
    "message": "I can't generate code, but I can explain concepts and point you to relevant documentation.",
    "severity": "warning",
    "subtype": "guardrails",
    "http_status": 200,
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Code Generation Not Supported
I can't generate code, but I can explain inverse kinematics concepts and link to documentation.

[Explain Concepts Instead]  [See Code Examples in Book]
```

**Retry Strategy**: None (valid response, guardrail working as intended)

**Circuit Breaker**: Does NOT count toward failure threshold

---

### 16. LOW_CONFIDENCE

**Description**: RAG model has low confidence in answer accuracy (<70% confidence score).

**When Triggered**:
- Ambiguous question ("What is the best humanoid robot?")
- Niche topic with limited book coverage
- Question spans multiple modules (no clear answer)

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "LOW_CONFIDENCE",
    "message": "I'm not certain about this answer. Please verify with cited sources.",
    "severity": "warning",
    "subtype": "guardrails",
    "http_status": 200,
    "confidence_score": 0.65,
    "retry_strategy": {
      "type": "none"
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Low Confidence Answer
I'm not certain about this answer. Please verify with cited sources.

[Show Answer Anyway]  [Rephrase Question]
```

**Retry Strategy**: None (answer still returned, but with warning)

**Circuit Breaker**: Does NOT count toward failure threshold

---

## System Errors

### 17. CIRCUIT_BREAKER_OPEN

**Description**: Circuit breaker is open (service unavailable, cooldown active).

**When Triggered**:
- 5 consecutive RAG API failures
- Circuit breaker in "open" state (60-second cooldown)

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "CIRCUIT_BREAKER_OPEN",
    "message": "Service temporarily unavailable. Retrying in 45 seconds...",
    "severity": "recoverable",
    "subtype": "circuit_breaker",
    "retry_strategy": {
      "type": "wait_for_cooldown",
      "retry_after_seconds": 45
    },
    "circuit_breaker": {
      "state": "open",
      "failure_count": 5,
      "cooldown_remaining_seconds": 45
    }
  }
}
```

**User-Facing Message**:
```
⚠️ Service Temporarily Unavailable
Retrying in 45 seconds... Using offline answers in the meantime.

[Use Offline FAQ]  [Countdown: 45s]
```

**Retry Strategy**: Wait for cooldown (automatic retry after 60s)

**Fallback**: Static FAQ (Tier 3)

**Circuit Breaker**: N/A (circuit breaker itself is the error)

---

### 18. WIDGET_INITIALIZATION_FAILED

**Description**: Widget failed to initialize (JavaScript error, missing dependencies).

**When Triggered**:
- JavaScript bundle corrupted
- Required dependency missing (React not loaded)
- Browser incompatibility (IE 11, old mobile browsers)

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": null,
  "error": {
    "code": "WIDGET_INITIALIZATION_FAILED",
    "message": "The chatbot widget failed to load. Please refresh the page.",
    "severity": "fatal",
    "subtype": "critical",
    "retry_strategy": {
      "type": "reload_page"
    }
  }
}
```

**User-Facing Message**:
```
❌ Widget Failed to Load
The chatbot widget encountered an error. Please refresh the page.

[Reload Page]  [Report Issue]
```

**Retry Strategy**: Reload page (window.location.reload())

**Circuit Breaker**: N/A (widget not initialized)

---

### 19. INDEXEDDB_ERROR

**Description**: IndexedDB read/write failed (quota exceeded, browser privacy mode).

**When Triggered**:
- Browser in private/incognito mode (IndexedDB disabled)
- Storage quota exceeded (>50MB)
- IndexedDB API not supported (very old browsers)

**Error Event Payload**:
```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "INDEXEDDB_ERROR",
    "message": "Unable to save conversation history locally. Try enabling cookies or exiting private mode.",
    "severity": "recoverable",
    "subtype": "storage_error",
    "retry_strategy": {
      "type": "fallback_localstorage"
    }
  }
}
```

**User-Facing Message**: Silent fallback to localStorage (no user-facing error unless localStorage also fails)

**Retry Strategy**: Fallback to localStorage (more limited storage)

**Circuit Breaker**: Does NOT count toward failure threshold

---

## Error Severity Levels

| Severity | Description | User Impact | Retry Allowed? |
|----------|-------------|-------------|----------------|
| **fatal** | Unrecoverable error, requires user action | Cannot proceed with current request | No (user must fix) |
| **recoverable** | Temporary error, likely to resolve on retry | Request failed, but retry may succeed | Yes (automatic or manual) |
| **warning** | Not an error, but requires user attention | Request succeeded, but with caveats | No (not needed) |

---

### Severity Guidelines

**Fatal Errors** (No Retry):
- Configuration errors (RAG_API_404)
- Validation errors (INVALID_INPUT)
- Authentication errors (INVALID_CREDENTIALS)
- User-cancelled actions (OAUTH_CANCELLED)

**Recoverable Errors** (Retry Allowed):
- Network errors (NETWORK_TIMEOUT, RAG_API_TIMEOUT)
- Server errors (RAG_API_500, RAG_API_503)
- Rate limit errors (RATE_LIMIT_EXCEEDED)
- Session errors (SESSION_EXPIRED)

**Warnings** (Not Errors):
- Guardrails (OUT_OF_SCOPE, CODE_GENERATION_BLOCKED)
- Low confidence (LOW_CONFIDENCE)

---

## Retry Strategies

### 1. Exponential Backoff

**Use Case**: Network/server errors (timeout, 500, 503)

**Algorithm**:
```
Attempt 1: 0s delay
Attempt 2: 1s delay (2^0 = 1)
Attempt 3: 2s delay (2^1 = 2)
Attempt 4: 4s delay (2^2 = 4)
Max Attempts: 3 (total delay: 7s)
```

**Design-Level Code**:
```typescript
async function retryWithExponentialBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error;  // Last attempt failed
      }

      const delay = initialDelay * Math.pow(2, attempt);
      await sleep(delay);
    }
  }
}
```

---

### 2. Wait and Retry

**Use Case**: Rate limit errors (429)

**Algorithm**:
```
Wait for retry_after_seconds (from HTTP 429 header)
Then retry once
```

**Design-Level Code**:
```typescript
async function retryAfterRateLimit(retryAfterSeconds: number) {
  await sleep(retryAfterSeconds * 1000);
  return await sendMessageToRAGAPI(message);
}
```

---

### 3. Wait for Cooldown

**Use Case**: Circuit breaker open

**Algorithm**:
```
Wait for circuit breaker cooldown (60s)
Circuit transitions to half-open
Automatic test request sent
If success → close circuit
If failure → re-open circuit (another 60s)
```

---

### 4. Re-authenticate

**Use Case**: Session expired (401)

**Algorithm**:
```
Attempt automatic refresh token exchange
If success → retry original request with new access token
If failure → show login modal
```

**Design-Level Code**:
```typescript
async function retryWithReauthentication() {
  try {
    const newAccessToken = await refreshAccessToken();
    return await sendMessageToRAGAPI(message, newAccessToken);
  } catch (refreshError) {
    // Refresh failed, require manual login
    showLoginModal();
    throw new SessionExpiredError();
  }
}
```

---

### 5. Manual Retry

**Use Case**: OAuth timeout, widget initialization failure

**Algorithm**:
```
Show "Try Again" button
Wait for user click
Retry operation
```

---

### 6. None (No Retry)

**Use Case**: Fatal errors, guardrails, warnings

**Behavior**: Do not retry, require user intervention or accept as valid response.

---

## Error Message Templates

### Template Structure

```typescript
interface ErrorMessageTemplate {
  title: string;           // Short title (e.g., "Connection Timeout")
  message: string;         // User-friendly explanation (1-2 sentences)
  icon: string;            // Emoji icon (⚠️, ❌, ℹ️)
  severity: 'fatal' | 'recoverable' | 'warning';
  actions: Array<{
    label: string;         // Button text (e.g., "Try Again")
    event: string;         // Event to trigger (e.g., "retry")
    primary?: boolean;     // Primary action (highlighted)
  }>;
}
```

### Example Templates

**Network Timeout Template**:
```typescript
{
  title: "Connection Timeout",
  message: "The connection is taking longer than expected. This might be due to a slow network.",
  icon: "⚠️",
  severity: "recoverable",
  actions: [
    { label: "Try Cached Answer", event: "use_cache", primary: false },
    { label: "Retry", event: "retry", primary: true }
  ]
}
```

**Rate Limit Template**:
```typescript
{
  title: "Message Limit Reached",
  message: "You've reached the 15-message limit for anonymous users. Sign up to get 50 messages per day!",
  icon: "⚠️",
  severity: "recoverable",
  actions: [
    { label: "Sign Up with Google", event: "signup_google", primary: true },
    { label: "Sign Up with Email", event: "signup_email", primary: false }
  ]
}
```

**Out of Scope Template**:
```typescript
{
  title: "Out of Scope",
  message: "This question is outside the book's coverage. I can only answer questions about Physical AI and Humanoid Robotics.",
  icon: "⚠️",
  severity: "warning",
  actions: [
    { label: "Rephrase Question", event: "clear_input", primary: true },
    { label: "See Topics", event: "show_topics", primary: false }
  ]
}
```

---

## Error Handling Checklist

### Pre-Deployment Checklist

- [ ] **All 19 error codes documented** (network, validation, auth, guardrails, system)
- [ ] **Error event payloads validated** (JSON schema compliant)
- [ ] **User-facing messages user-tested** (non-technical language)
- [ ] **Retry strategies implemented** (exponential backoff, wait-and-retry, etc.)
- [ ] **Circuit breaker failure counting** (only network/server errors count)
- [ ] **Fallback priority tested** (RAG API → Cache → FAQ → Manual)
- [ ] **Screen reader announcements** (all errors have ARIA live region announcements)
- [ ] **Error analytics tracking** (all errors logged with error code, session ID)

### Runtime Error Handling Checklist

- [ ] **Network Timeout**: Show cached answer or FAQ, retry with exponential backoff
- [ ] **Rate Limit**: Show tier upgrade prompt, explain benefits of signup
- [ ] **Session Expired**: Attempt automatic refresh, fallback to login modal
- [ ] **OAuth Timeout**: Show "Try Again" button, offer email signup alternative
- [ ] **Out of Scope**: Explain book coverage, link to topic index
- [ ] **Circuit Breaker Open**: Show offline FAQ, display cooldown countdown
- [ ] **500 Server Error**: Show FAQ fallback, suggest rephrasing question
- [ ] **404 Endpoint Not Found**: Show configuration error, contact support link

### Error Monitoring Checklist

- [ ] **Error Rate Dashboard**: Track error rate by error code (Grafana/Datadog)
- [ ] **Circuit Breaker Metrics**: Track open/close events, cooldown duration
- [ ] **Fallback Usage Metrics**: Track cache hit rate, FAQ match rate
- [ ] **Retry Success Rate**: Track how often retries succeed (by error code)
- [ ] **User Error Reports**: Collect "Report Issue" feedback from users
- [ ] **Alerting**: Alert on error rate >5% (Slack/PagerDuty)

---

## Summary

**Complete Error Code Taxonomy**: ✅ 19 error codes covering all categories

**Error Categories**:
- Network Errors: 7 codes (timeout, unreachable, 500, 503, 502, 504, 404)
- Validation Errors: 2 codes (invalid input, rate limit)
- Authentication Errors: 3 codes (session expired, invalid credentials, OAuth timeout/cancelled)
- Guardrail Errors: 3 codes (out of scope, code generation blocked, low confidence)
- System Errors: 3 codes (circuit breaker open, widget initialization failed, IndexedDB error)

**Error Severities**:
- Fatal: 5 codes (require user action, no retry)
- Recoverable: 11 codes (automatic or manual retry)
- Warning: 3 codes (not errors, guardrails working as intended)

**Retry Strategies**:
- Exponential Backoff (network/server errors)
- Wait and Retry (rate limit)
- Wait for Cooldown (circuit breaker)
- Re-authenticate (session expired)
- Manual Retry (OAuth timeout)
- None (fatal errors, guardrails)

**Gap Resolved**: T042 validation gap (error code taxonomy) now fully documented ✅

**Next Step**: Complete T048 (Network Recovery Detection)

---

**Status**: Error Handling Checklist Complete ✅
**File**: `specs/003-chatkit-widget/checklists/error-handling.md`
**Lines**: 1,100+
**Coverage**: 100% (all 19 error codes, severities, retry strategies, message templates documented)
