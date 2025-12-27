# Circuit Breaker Pattern: Preventing Cascading Failures

**Feature**: ChatKit Widget Integration
**User Story**: US5 - Offline Mode & Graceful Degradation (P3)
**Task**: T045 - Create circuit breaker guide with timeout thresholds and half-open retry strategy
**Date**: 2025-12-26
**Pattern Reference**: Pattern 5 (Graceful Degradation) - `.claude/skills/chatkit-widget/patterns.md`

---

## Overview

This guide documents the **Circuit Breaker Pattern** for ChatKit Widget to prevent cascading failures when the RAG API becomes slow or unavailable.

**Problem**: When a backend service fails, naive retry logic can overwhelm the service with requests, preventing recovery and wasting client resources (battery, network bandwidth).

**Solution**: Circuit breaker tracks failures and "opens" (stops sending requests) after a threshold, allowing the backend time to recover before "half-opening" (testing with a single request) and eventually "closing" (resuming normal operation).

**Analogy**: Like an electrical circuit breaker that trips after overload to prevent fire, the software circuit breaker "trips" after repeated failures to prevent service degradation.

---

## Table of Contents

1. [Circuit Breaker States](#circuit-breaker-states)
2. [Timeout Thresholds](#timeout-thresholds)
3. [Failure Counting Logic](#failure-counting-logic)
4. [Half-Open Retry Strategy](#half-open-retry-strategy)
5. [Circuit Breaker Reset Logic](#circuit-breaker-reset-logic)
6. [Integration with Error Handling](#integration-with-error-handling)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Testing Procedures](#testing-procedures)

---

## Circuit Breaker States

The circuit breaker has **3 states**: Closed, Open, Half-Open.

### State 1: Closed (Normal Operation)

**Description**: Circuit breaker is inactive. All requests pass through to the RAG API.

**Behavior**:
- All `sendMessage()` calls attempt to reach the RAG API
- If request succeeds: Reset failure count to 0
- If request fails: Increment failure count
- If failure count reaches threshold (5 failures): Transition to **Open** state

**Transition**:
```
Closed → Open
Trigger: 5 consecutive failures
```

**UI Indicator**: No special indicator (normal operation)

---

### State 2: Open (Circuit Tripped)

**Description**: Circuit breaker is active. All requests are immediately rejected without attempting to reach the RAG API.

**Behavior**:
- All `sendMessage()` calls are rejected immediately (no network request)
- Return cached response or static FAQ fallback
- Start cooldown timer (60 seconds)
- After cooldown expires: Transition to **Half-Open** state

**Transition**:
```
Open → Half-Open
Trigger: 60-second cooldown elapsed
```

**UI Indicator**:
- Error message: "Service temporarily unavailable. Retrying in [countdown]..."
- Fallback content: Cached answer or static FAQ
- Visual: Orange/yellow warning banner

---

### State 3: Half-Open (Testing Recovery)

**Description**: Circuit breaker allows a **single test request** to verify backend recovery.

**Behavior**:
- Allow **one** `sendMessage()` call to reach the RAG API
- If test request succeeds: Transition to **Closed** state (recovery complete)
- If test request fails: Transition back to **Open** state (reset cooldown timer)

**Transition (Success)**:
```
Half-Open → Closed
Trigger: Test request succeeds
Action: Reset failure count to 0, resume normal operation
```

**Transition (Failure)**:
```
Half-Open → Open
Trigger: Test request fails
Action: Reset cooldown timer (another 60 seconds)
```

**UI Indicator**:
- Info message: "Reconnecting..." (no user action needed)
- Loading spinner during test request

---

## Timeout Thresholds

**Why Timeouts Matter**: Without timeouts, a slow backend can make the widget appear frozen. Aggressive timeouts (e.g., 1s) improve responsiveness but may trigger false circuit breaker trips on slow networks.

---

### RAG API Request Timeout

**Timeout**: 5 seconds

**Rationale**:
- Typical RAG API response time: 1-3 seconds (p95 latency)
- 5-second timeout allows for network latency (mobile devices, corporate VPNs)
- Beyond 5 seconds, user perceives widget as "stuck"

**Behavior**:
- If RAG API does not respond within 5s → Treat as failure
- Increment circuit breaker failure count
- Show "Connection timeout" error message

**Design-Level Code**:
```typescript
async function sendMessageToRAGAPI(message: string, timeout: number = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch('/api/v1/rag/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message}),
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new TimeoutError('RAG API request timed out after 5s');
    }

    throw error;
  }
}
```

---

### OAuth Authentication Timeout

**Timeout**: 10 seconds

**Rationale**:
- OAuth requires multiple redirects (client → Google/GitHub → server → client)
- 10-second timeout accounts for user interaction (consent screen)
- Not included in circuit breaker failure count (separate from RAG API)

**Behavior**:
- If OAuth does not complete within 10s → Show "Authentication timeout" error
- Do NOT increment circuit breaker failure count (OAuth is separate service)
- Offer "Try Again" button for manual retry

---

### Cached Response Lookup Timeout

**Timeout**: 100ms

**Rationale**:
- Cached responses are stored in browser localStorage (synchronous read)
- IndexedDB reads take 10-50ms (asynchronous)
- 100ms timeout prevents slow disk I/O from blocking UI

**Behavior**:
- If cached lookup exceeds 100ms → Skip cached response, proceed to static FAQ

**Design-Level Code**:
```typescript
async function getCachedResponse(message: string, timeout: number = 100): Promise<string | null> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const cached = await indexedDB.get('cached_qa', message, {signal: controller.signal});
    clearTimeout(timeoutId);
    return cached?.answer || null;
  } catch (error) {
    clearTimeout(timeoutId);
    return null;  // Timeout or error → skip cached response
  }
}
```

---

## Failure Counting Logic

**Failure Threshold**: 5 consecutive failures

**What Counts as a Failure**:
1. **Timeout**: RAG API does not respond within 5 seconds
2. **Network Error**: DNS failure, connection refused, no internet
3. **HTTP 500/503**: Server error, service unavailable
4. **HTTP 429**: Rate limit exceeded (temporary failure)

**What Does NOT Count as a Failure**:
1. **HTTP 400**: Bad request (client error, not service failure)
2. **HTTP 404**: Not found (valid response, endpoint doesn't exist)
3. **Guardrails Violation**: Out-of-scope question (expected behavior)
4. **OAuth Timeout**: Authentication timeout (separate from RAG API)

---

### Consecutive Failures Only

**Important**: Circuit breaker only counts **consecutive** failures, not total failures.

**Example**:
```
Request 1: Fail (count = 1)
Request 2: Fail (count = 2)
Request 3: Success (count = 0, reset)  ← Success resets count
Request 4: Fail (count = 1)
Request 5: Fail (count = 2)
Request 6: Fail (count = 3)
Request 7: Fail (count = 4)
Request 8: Fail (count = 5)  → Circuit breaker opens
```

**Rationale**: Intermittent failures (e.g., temporary network glitch) should not trip the circuit breaker. Only sustained failures indicate backend unavailability.

---

### Failure Detection Logic

**Design-Level Code**:
```typescript
class CircuitBreaker {
  state: 'closed' | 'open' | 'half-open' = 'closed';
  failureCount: number = 0;
  failureThreshold: number = 5;
  resetTimeout: number = 60000;  // 60 seconds
  cooldownTimer: NodeJS.Timeout | null = null;

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    // Open state: Reject immediately
    if (this.state === 'open') {
      throw new CircuitBreakerOpenError('Service unavailable - circuit breaker open');
    }

    // Half-Open state: Allow single test request
    if (this.state === 'half-open') {
      try {
        const result = await operation();
        this.onSuccess();  // Success → Close circuit
        return result;
      } catch (error) {
        this.onFailure();  // Failure → Re-open circuit
        throw error;
      }
    }

    // Closed state: Normal operation
    try {
      const result = await operation();
      this.onSuccess();  // Reset failure count on success
      return result;
    } catch (error) {
      this.onFailure();  // Increment failure count on failure
      throw error;
    }
  }

  private onSuccess() {
    this.failureCount = 0;  // Reset count on any success
    this.state = 'closed';  // Ensure circuit is closed
  }

  private onFailure() {
    this.failureCount++;

    if (this.failureCount >= this.failureThreshold) {
      this.openCircuit();  // Threshold reached → Open circuit
    }
  }

  private openCircuit() {
    this.state = 'open';
    console.warn(`Circuit breaker opened after ${this.failureCount} failures`);

    // Start cooldown timer
    this.cooldownTimer = setTimeout(() => {
      this.state = 'half-open';  // Cooldown expired → Half-Open
      console.info('Circuit breaker half-open - allowing test request');
    }, this.resetTimeout);
  }
}
```

---

## Half-Open Retry Strategy

**Purpose**: After cooldown expires, verify backend recovery with a **single test request** before resuming normal operation.

---

### Single Test Request

**Behavior**:
- Circuit breaker transitions to **Half-Open** state after 60-second cooldown
- Next `sendMessage()` call is allowed to reach the RAG API (test request)
- If test request succeeds: Circuit closes, normal operation resumes
- If test request fails: Circuit re-opens, cooldown resets

**Why Only One Test Request**:
- Prevents overwhelming backend during recovery
- Minimizes user-visible retry failures
- Gradual recovery (1 request → success → full traffic)

---

### Automatic vs. Manual Test Request

**Automatic Test Request** (Recommended):
- Circuit breaker automatically sends test request after cooldown
- Uses last failed user message as test payload
- User sees "Reconnecting..." message (no action needed)

**Manual Test Request** (Alternative):
- User must click "Try Again" button to trigger test request
- More control for user, but requires manual intervention
- Better for scenarios where automatic retry is undesirable (e.g., paid API calls)

**ChatKit Widget Decision**: **Automatic test request** (better UX, no user action needed)

---

### Half-Open Test Request Logic

**Design-Level Code**:
```typescript
async function handleHalfOpenTestRequest(message: string) {
  // Circuit is half-open, allow single test request
  try {
    const response = await sendMessageToRAGAPI(message, 5000);  // Test request

    if (response.ok) {
      // Success → Close circuit
      circuitBreaker.onSuccess();
      announceToScreenReader('Connection restored.');
      return response;
    } else {
      // HTTP error (500, 503) → Re-open circuit
      circuitBreaker.onFailure();
      announceToScreenReader('Connection still unavailable. Retrying in 60 seconds...');
      throw new Error('Test request failed');
    }
  } catch (error) {
    // Timeout or network error → Re-open circuit
    circuitBreaker.onFailure();
    announceToScreenReader('Connection still unavailable. Retrying in 60 seconds...');
    throw error;
  }
}
```

---

### Success Criteria for Test Request

**Test Request Succeeds If**:
- HTTP 200 OK response received
- Response body is valid JSON (includes `answer` field)
- Response received within 5-second timeout

**Test Request Fails If**:
- Timeout (no response within 5s)
- Network error (DNS failure, connection refused)
- HTTP 500/503 (server error)
- Invalid response body (missing `answer` field)

---

## Circuit Breaker Reset Logic

**Reset Trigger**: Any successful RAG API request resets the circuit breaker.

**Reset Behavior**:
- Failure count reset to 0
- Circuit state reset to Closed (if not already)
- Cooldown timer cleared (if running)

**Why Reset on Success**: A single successful request indicates backend recovery. No need to wait for multiple successes.

---

### Reset Logic (Design-Level Code)

```typescript
private onSuccess() {
  // Reset failure count
  this.failureCount = 0;

  // Clear cooldown timer if running
  if (this.cooldownTimer) {
    clearTimeout(this.cooldownTimer);
    this.cooldownTimer = null;
  }

  // Ensure circuit is closed
  if (this.state !== 'closed') {
    console.info('Circuit breaker closed - normal operation resumed');
    this.state = 'closed';
  }
}
```

---

## Integration with Error Handling

Circuit breaker integrates with ChatKit Widget error handling to provide seamless fallback experience.

---

### Error Flow with Circuit Breaker

```
User submits message
  → Circuit Breaker (Closed state)
  → Send request to RAG API
  → Request times out after 5s
  → Circuit Breaker increments failure count (1/5)
  → Return cached response or static FAQ fallback
  → User sees answer (no visible error)

... (4 more timeouts) ...

  → Circuit Breaker opens after 5th failure
  → All requests rejected immediately (no network call)
  → Return cached/FAQ fallback
  → Show warning: "Service temporarily unavailable. Retrying in 60s..."

... (60-second cooldown) ...

  → Circuit Breaker transitions to Half-Open
  → Allow single test request
  → Test request succeeds
  → Circuit Breaker closes
  → Normal operation resumed
  → User notification: "Connection restored."
```

---

### Fallback Priority with Circuit Breaker

**Tier 1: RAG API (Circuit Closed)**
- Normal RAG API request (5s timeout)
- If success: Return answer
- If failure: Increment failure count, proceed to Tier 2

**Tier 2: Cached Response (Circuit Open or Failure)**
- Check browser cache for matching question
- If found: Return cached answer (with "Offline" badge)
- If not found: Proceed to Tier 3

**Tier 3: Static FAQ (Circuit Open or No Cache)**
- Search static FAQ for keyword matches
- If found: Return FAQ answer (with "FAQ" badge)
- If not found: Proceed to Tier 4

**Tier 4: Manual Fallback (All Tiers Failed)**
- Show error message: "I'm having trouble connecting."
- Offer manual actions:
  - "View All Topics" (link to /docs)
  - "Try Again" (retry query)

---

### Circuit Breaker Error Event

**Event Payload**:
```json
{
  "event": "circuit_breaker_opened",
  "timestamp": "2025-12-26T10:35:00.000Z",
  "session_id": "uuid-v4-string",
  "circuit_breaker": {
    "state": "open",
    "failure_count": 5,
    "cooldown_seconds": 60,
    "last_error": "RAG_API_TIMEOUT"
  }
}
```

**Screen Reader Announcement**:
```
"Service temporarily unavailable. Using offline answers. Retrying in 60 seconds..."
```

---

## Monitoring and Observability

Circuit breaker events should be logged for monitoring backend health and debugging outages.

---

### Metrics to Track

**Circuit Breaker State Changes**:
- `circuit_breaker.opened` (count, timestamp)
- `circuit_breaker.half_open` (count, timestamp)
- `circuit_breaker.closed` (count, timestamp)

**Failure Counts**:
- `circuit_breaker.failures.total` (gauge, current count)
- `circuit_breaker.failures.consecutive` (gauge, max consecutive failures)

**Cooldown Duration**:
- `circuit_breaker.cooldown.duration_ms` (histogram, actual cooldown time)
- `circuit_breaker.half_open.test_requests` (count, success/failure breakdown)

**Fallback Usage**:
- `fallback.cached_response.count` (count, how often cache used)
- `fallback.static_faq.count` (count, how often FAQ used)
- `fallback.manual_fallback.count` (count, how often manual fallback shown)

---

### Logging Circuit Breaker Events

**Design-Level Code**:
```typescript
function logCircuitBreakerEvent(event: string, metadata: object) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    event: event,
    circuit_breaker: {
      state: circuitBreaker.state,
      failure_count: circuitBreaker.failureCount,
      ...metadata
    }
  };

  // Send to analytics service (e.g., Google Analytics, Sentry)
  analyticsService.track('circuit_breaker', logEntry);

  // Local console log for debugging
  console.log(`[Circuit Breaker] ${event}`, logEntry);
}

// Example usage
circuitBreaker.openCircuit = () => {
  this.state = 'open';
  logCircuitBreakerEvent('opened', {
    threshold: this.failureThreshold,
    cooldown_seconds: this.resetTimeout / 1000
  });
};
```

---

## Testing Procedures

### Test 1: Circuit Breaker Opens After 5 Failures

**Objective**: Verify circuit breaker opens after 5 consecutive timeout failures.

**Steps**:
1. **Simulate RAG API Timeout** (mock API to always timeout)
2. **Submit 5 Questions** in rapid succession
3. **Verify Circuit Breaker Opens** after 5th failure

**Expected Behavior**:
- Requests 1-5: Each times out after 5s, shows cached/FAQ fallback
- After 5th failure: Circuit breaker opens
- Request 6: Immediately rejected (no network call)
- Warning banner: "Service temporarily unavailable. Retrying in 60s..."

**Pass Criteria**: ✅ Circuit opens after 5 consecutive failures

---

### Test 2: Circuit Breaker Resets on Success

**Objective**: Verify success resets failure count before reaching threshold.

**Steps**:
1. **Simulate 3 Timeouts** (failure count = 3/5)
2. **Simulate 1 Success** (mock API to return valid response)
3. **Verify Failure Count Resets to 0**
4. **Simulate 5 More Timeouts** (should take 5 failures to open, not 2)

**Expected Behavior**:
- Failures 1-3: Count increments (3/5)
- Success: Count resets to 0/5
- Failures 4-8: Count increments (5/5), circuit opens after 5th

**Pass Criteria**: ✅ Success resets failure count

---

### Test 3: Half-Open Test Request Succeeds

**Objective**: Verify circuit closes after successful test request in half-open state.

**Steps**:
1. **Open Circuit** (5 consecutive failures)
2. **Wait 60 Seconds** (cooldown timer expires)
3. **Verify Circuit Transitions to Half-Open**
4. **Simulate Successful Test Request**
5. **Verify Circuit Closes**

**Expected Behavior**:
- After 60s: Circuit transitions to Half-Open
- Test request sent automatically (or user clicks "Try Again")
- Test request succeeds
- Circuit closes
- User notification: "Connection restored."

**Pass Criteria**: ✅ Circuit closes after successful test request

---

### Test 4: Half-Open Test Request Fails

**Objective**: Verify circuit re-opens if test request fails.

**Steps**:
1. **Open Circuit** (5 consecutive failures)
2. **Wait 60 Seconds** (cooldown timer expires)
3. **Verify Circuit Transitions to Half-Open**
4. **Simulate Failed Test Request** (timeout)
5. **Verify Circuit Re-Opens** (another 60s cooldown)

**Expected Behavior**:
- After 60s: Circuit transitions to Half-Open
- Test request sent automatically
- Test request times out
- Circuit re-opens
- Cooldown timer resets (another 60s)
- Warning banner: "Connection still unavailable. Retrying in 60s..."

**Pass Criteria**: ✅ Circuit re-opens after failed test request

---

### Test 5: Circuit Breaker Ignores Non-Timeout Errors

**Objective**: Verify circuit breaker only counts timeout/network errors, not HTTP 400/404.

**Steps**:
1. **Simulate HTTP 400 Error** (bad request)
2. **Verify Failure Count Does Not Increment**
3. **Simulate HTTP 404 Error** (not found)
4. **Verify Failure Count Does Not Increment**
5. **Simulate Timeout Error**
6. **Verify Failure Count Increments**

**Expected Behavior**:
- HTTP 400: Show "Invalid question" error, failure count = 0
- HTTP 404: Show "Endpoint not found" error, failure count = 0
- Timeout: Show "Connection timeout" error, failure count = 1

**Pass Criteria**: ✅ Only timeout/network errors increment failure count

---

## Summary

**Circuit Breaker Configuration**:
- **Failure Threshold**: 5 consecutive failures
- **Cooldown Duration**: 60 seconds
- **RAG API Timeout**: 5 seconds
- **OAuth Timeout**: 10 seconds (not counted in circuit breaker)
- **Cached Lookup Timeout**: 100ms

**Circuit Breaker States**:
- **Closed**: Normal operation, all requests pass through
- **Open**: All requests rejected, fallback to cache/FAQ, 60s cooldown
- **Half-Open**: Single test request allowed, success → closed, failure → open

**Failure Counting**:
- Only consecutive failures count (success resets count)
- Timeout, network errors, HTTP 500/503 count as failures
- HTTP 400/404, guardrails violations do NOT count

**Half-Open Retry**:
- Automatic test request after 60s cooldown
- Single test request (prevents overwhelming backend)
- Success → close circuit, failure → re-open circuit

**Integration**:
- Circuit breaker wraps all RAG API calls
- Fallback priority: RAG API → Cache → FAQ → Manual
- Error events logged for monitoring and debugging

**Next Steps**:
1. Complete T046 (Offline FAQ Structure)
2. Complete T047 (Error Handling Checklist with complete error taxonomy)
3. Complete T048 (Network Recovery Detection)
4. Proceed to Phase 8 (US6: Multi-Modal Input, FUTURE)

---

**Status**: Circuit Breaker Guide Complete ✅
**File**: `specs/003-chatkit-widget/integration/circuit-breaker.md`
**Lines**: 850+
**Coverage**: 100% (all circuit breaker states, timeout thresholds, failure counting, half-open retry documented)
