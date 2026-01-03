# Phase 7 Implementation Planning Guide

**Task**: T056 - Create Phase 7 implementation planning guide
**Date**: 2025-12-27
**Status**: Draft
**Purpose**: Bridge Phase 6 design validation to Phase 7+ runtime implementation

---

## Overview

This guide provides a comprehensive roadmap for implementing the ChatKit Widget based on Phase 6 design validation artifacts. It covers framework selection, runtime architecture decisions, implementation strategy, and deployment planning.

**Context**: Phase 6 completed design-only validation (no code). Phase 7+ will implement the actual runtime widget.

---

## Prerequisites (Critical Blockers)

Before starting Phase 7 implementation, the following artifacts **MUST** be created:

### 1. Better-Auth MCP Server
**Path**: `.claude/mcp/better-auth/`
**Purpose**: OAuth integration (Google, GitHub, Microsoft), email verification, JWT session management
**Referenced By**: Pattern 1 (Event-Driven Widget), Pattern 3 (Session Continuity)
**Estimated Effort**: ~500 lines (mcp.json + README.md)
**Priority**: 🔴 **CRITICAL** (blocks US3: Progressive Signup)

**Capabilities Required**:
- OAuth provider configuration (Google, GitHub, Microsoft)
- Email verification flows
- JWT session management
- Session merge for anonymous → authenticated upgrade
- GDPR/CCPA/FERPA compliance guidance

**Deliverables**:
- `.claude/mcp/better-auth/mcp.json` (MCP server manifest)
- `.claude/mcp/better-auth/README.md` (integration guide)

**Validation Checklist**:
- [ ] OAuth flow diagrams for all 3 providers
- [ ] Session merge algorithm documented
- [ ] Tier upgrade flow (Tier 0 → Tier 1 → Tier 2)
- [ ] GDPR consent management
- [ ] Email verification template

---

### 2. Signup-Personalization Skill
**Path**: `.claude/skills/signup-personalization/`
**Purpose**: 4-tier progressive enhancement, tier upgrade flows, session merge logic
**Referenced By**: Pattern 3 (Session Continuity), Pattern 6 (Contextual Discovery)
**Estimated Effort**: ~1,000 lines (SKILL.md + patterns.md with 4+ patterns)
**Priority**: 🔴 **CRITICAL** (blocks US3: Progressive Signup)

**Patterns Required**:
1. **Progressive Enhancement Signup** (referenced by Pattern 3, Pattern 6)
2. **Layered Personalization** (referenced by Pattern 6)
3. **Privacy-First Data Management** (recommended, not yet referenced)
4. **Educational Gamification** (recommended, not yet referenced)

**Deliverables**:
- `.claude/skills/signup-personalization/SKILL.md` (533 lines estimated)
- `.claude/skills/signup-personalization/patterns.md` (783 lines estimated)

**Validation Checklist**:
- [ ] 4-tier progressive enhancement documented (Tier 0-3)
- [ ] Tier upgrade flows with session merge
- [ ] Privacy compliance (GDPR, CCPA, FERPA, COPPA)
- [ ] Data classification (4-tier: Public, Pseudonymous, Personal, Sensitive)
- [ ] Gamification without dark patterns

---

## Framework Selection Matrix

### Frontend Framework Options

| Framework | Bundle Size | Learning Curve | Docusaurus Integration | Recommendation |
|-----------|-------------|----------------|------------------------|----------------|
| **React** | 42KB (gzip) | Medium | ✅ Native (Docusaurus is React) | ⭐ **Recommended** |
| **Preact** | 3KB (gzip) | Low | ⚠️ Compatible (preact-compat) | ⭐ Alternative (smaller) |
| **Vue 3** | 34KB (gzip) | Medium | ⚠️ Possible (custom wrapper) | ❌ Not recommended |
| **Svelte** | 2KB (gzip) | Low | ⚠️ Possible (custom wrapper) | ❌ Not recommended |
| **Vanilla JS** | 0KB | Low | ✅ Works everywhere | ⭐ Tier 0 only |

**Decision**: **React** for Tiers 1-3, **Vanilla JS** for Tier 0 (widget button)

**Rationale**:
- Docusaurus is React-based → seamless integration
- React component can be swizzled into Docusaurus theme
- Tier 0 (widget button) uses Vanilla JS for minimal bundle size (<15KB)
- Tier 1+ lazy-loads React bundle on demand

**Alternative**: **Preact** if bundle size becomes critical (saves ~39KB but adds compatibility risk)

---

### State Management Options

| Library | Bundle Size | Complexity | Recommendation |
|---------|-------------|------------|----------------|
| **React Context** | 0KB (built-in) | Low | ⭐ **Recommended** (Tier 1-2) |
| **Zustand** | 1KB (gzip) | Low | ⭐ Alternative (simpler than Redux) |
| **Redux Toolkit** | 12KB (gzip) | High | ❌ Overkill for widget |
| **Jotai** | 2KB (gzip) | Low | ⭐ Alternative (atomic state) |

**Decision**: **React Context** for MVP, **Zustand** if complexity grows

**Rationale**:
- Widget has simple state (open/closed, messages, session)
- React Context is sufficient for Tier 1-2
- Upgrade to Zustand if cross-component state becomes unwieldy

---

### HTTP Client Options

| Library | Bundle Size | Features | Recommendation |
|---------|-------------|----------|----------------|
| **Fetch API** | 0KB (native) | Basic | ⭐ **Recommended** |
| **Axios** | 5KB (gzip) | Interceptors, timeout | ❌ Not needed |
| **ky** | 2KB (gzip) | Retry, timeout | ⭐ Alternative (if retry needed) |

**Decision**: **Fetch API** with manual timeout and retry logic

**Rationale**:
- Native browser API (no bundle cost)
- Circuit breaker handles retry logic (see Pattern 5)
- Timeout via `AbortController` (native)

**Alternative**: **ky** if retry logic becomes complex

---

### Session Storage Options

| Technology | Capacity | Persistence | Use Case | Recommendation |
|------------|----------|-------------|----------|----------------|
| **localStorage** | 5-10MB | Permanent | Tier 0 (anonymous) | ⭐ **Recommended** |
| **IndexedDB** | 50MB+ | Permanent | Tier 1+ (authenticated) | ⭐ **Recommended** |
| **sessionStorage** | 5-10MB | Tab session | N/A | ❌ Not suitable |
| **In-memory** | Unlimited | Page session | N/A | ❌ Loses on refresh |

**Decision**: **localStorage** for Tier 0, **IndexedDB** for Tier 1+

**Rationale**:
- Tier 0 (anonymous): localStorage (simple key-value, <5MB conversation history)
- Tier 1+ (authenticated): IndexedDB (larger capacity, structured queries)
- See Pattern 5 (Session Continuity) for migration logic

---

### OAuth Provider Options

| Provider | Integration | User Base | Recommendation |
|----------|-------------|-----------|----------------|
| **Google** | ✅ Better-Auth | 3B+ users | ⭐ **Required** |
| **GitHub** | ✅ Better-Auth | 100M+ developers | ⭐ **Required** (tech audience) |
| **Microsoft** | ✅ Better-Auth | 1B+ users | ⭐ **Required** (enterprise) |
| **Email** | ✅ Better-Auth | Universal | ⭐ **Required** (fallback) |

**Decision**: All 4 providers (Google, GitHub, Microsoft, Email)

**Rationale**:
- Maximize signup conversion (users prefer existing accounts)
- Tech/academic audience → GitHub, Microsoft (work/school)
- Email as fallback for users without OAuth accounts

---

## Runtime Architecture Decisions

### 1. Widget Loading Strategy (Pattern 2: Progressive Loading)

**Decision**: 4-tier lazy loading

```
Tier 0: Widget Button (Vanilla JS, <15KB)
  ↓ (on click)
Tier 1: Chat Panel (React, <50KB total)
  ↓ (on first message)
Tier 2: Full Features (OAuth, <100KB total)
  ↓ (on tier upgrade)
Tier 3: Analytics (Optional, <150KB total)
```

**Implementation**:
```typescript
// Tier 0: Widget button (loaded immediately with Docusaurus)
<button class="chatkit-widget-button" onclick="loadChatPanel()">
  💬 Ask
</button>

// Tier 1: Lazy load chat panel on click
async function loadChatPanel() {
  const { ChatPanel } = await import('./components/ChatPanel');
  ReactDOM.render(<ChatPanel />, document.getElementById('chatkit-root'));
}

// Tier 2: Lazy load OAuth on signup
async function loadOAuthLogin() {
  const { OAuthProvider } = await import('./components/OAuthProvider');
  // ... OAuth flow
}
```

**Bundle Size Validation**:
| Tier | Target | Maximum | Validation Command |
|------|--------|---------|-------------------|
| Tier 0 | <12KB | 15KB | `bundlesize` (CI) |
| Tier 1 | <40KB | 50KB | `bundlesize` (CI) |
| Tier 2 | <80KB | 100KB | `bundlesize` (CI) |
| Tier 3 | <120KB | 150KB | `bundlesize` (CI) |

---

### 2. Event Bus Architecture (Pattern 1: Event-Driven Widget)

**Decision**: Custom event bus (no external library)

**Rationale**:
- Widget needs decoupled communication between:
  - Widget UI ↔ RAG API
  - Widget UI ↔ OAuth Provider
  - Widget UI ↔ Session Manager
- Custom event bus is <1KB (vs. 5KB+ for EventEmitter library)

**Implementation**:
```typescript
// Event bus (design-level code from patterns.md)
class WidgetEventBus {
  private listeners: Map<string, Function[]> = new Map();

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event: string, payload: object) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => callback(payload));
  }

  off(event: string, callback: Function) {
    const callbacks = this.listeners.get(event) || [];
    this.listeners.set(event, callbacks.filter(cb => cb !== callback));
  }
}
```

**Event Types** (from SKILL.md):
- `user_typing` → Show typing indicator
- `user_message` → Send query to RAG API
- `agent_started` → Show "thinking" indicator
- `agent_streaming` → Update message with streaming tokens
- `agent_completed` → Show final answer + citations
- `agent_error` → Show error message (use error taxonomy from T047)
- `session_tier_upgraded` → Merge anonymous → authenticated session
- `oauth_success` / `oauth_error` → Handle OAuth flow

---

### 3. Session Continuity (Pattern 3: Session Continuity)

**Decision**: localStorage (Tier 0) → IndexedDB (Tier 1+) with server merge

**Flow**:
```
1. User asks question (Tier 0: Anonymous)
   → Store in localStorage: { session_id: "uuid-v4", messages: [...] }

2. User clicks "Sign in" (Tier 0 → Tier 1 upgrade)
   → Read localStorage session
   → Upload to server via /api/v1/session/merge
   → Receive user_id and session_token

3. User refresh page (Tier 1: Authenticated)
   → Load session from server via /api/v1/session/{user_id}
   → Store in IndexedDB for offline access
   → Clear localStorage (no longer needed)
```

**API Endpoints Required** (Phase 7+ backend work):
- `POST /api/v1/session/merge` - Merge anonymous → authenticated
- `GET /api/v1/session/{user_id}` - Load authenticated session
- `POST /api/v1/session/update` - Save session updates

**Validation**:
- [ ] Session merge without data loss (test: ask 5 questions, sign in, verify all 5 appear)
- [ ] Session survives page refresh (test: refresh page, verify conversation history)
- [ ] Session isolation (test: logout, verify session cleared)

---

### 4. Citation Rendering (Pattern 4: Citation-Aware Message Rendering)

**Decision**: Inline citations with stable IDs

**Stable ID Format** (from RAG Chatbot Pattern 3):
```
module:<module-number>:<section>:<heading-slug>
Example: module:1:overview:what-is-physical-ai
```

**Rendering Logic**:
```typescript
// Replace [1], [2], [3] with clickable links
function renderMessageWithCitations(message: string, citations: Citation[]) {
  let renderedMessage = message;

  citations.forEach((citation, index) => {
    const citationMarker = `[${index + 1}]`;
    const citationLink = `
      <a href="${citation.url}"
         target="_blank"
         rel="noopener"
         aria-label="Citation ${index + 1}: ${citation.title}">
        ${citationMarker}
      </a>
    `;

    renderedMessage = renderedMessage.replace(
      new RegExp(`\\[${index + 1}\\]`, 'g'),
      citationLink
    );
  });

  return renderedMessage;
}
```

**Citation Schema** (from SKILL.md):
```json
{
  "citations": [
    {
      "id": "module:1:overview:what-is-physical-ai",
      "title": "What is Physical AI?",
      "url": "/docs/module-1-intro/what-is-physical-ai#overview",
      "excerpt": "Physical AI refers to..."
    }
  ]
}
```

**Validation**:
- [ ] Citations are clickable links
- [ ] Citations open in new tab (target="_blank")
- [ ] Citations have accessible labels (aria-label)
- [ ] Citation numbering is consistent (1, 2, 3, not 1, 3, 2)

---

### 5. Error Handling (Pattern 5: Graceful Degradation)

**Decision**: 4-tier fallback with circuit breaker

**Error Taxonomy** (from T047: error-handling.md):
- **19 error codes** across 5 categories:
  1. Network Errors (7)
  2. Validation Errors (2)
  3. Authentication Errors (3)
  4. Guardrail Errors (3)
  5. System Errors (4)

**Circuit Breaker Thresholds**:
- **5 consecutive failures** → Open (block requests)
- **60-second cooldown** → Half-Open (allow 1 test request)
- **1 success** → Closed (resume normal operation)

**Fallback Tiers**:
```
Tier 1: RAG API (full retrieval, <3s p95 latency)
  ↓ (on timeout/error)
Tier 2: Cached responses (IndexedDB, instant)
  ↓ (on cache miss)
Tier 3: Static FAQ (40 questions, offline-ready)
  ↓ (on no match)
Tier 4: Manual fallback ("I'm having trouble connecting...")
```

**Implementation**:
```typescript
async function sendMessageWithFallback(message: string) {
  try {
    // Tier 1: Try full RAG API
    const response = await circuitBreaker.execute(() =>
      fetch('/api/v1/rag/query', {
        method: 'POST',
        body: JSON.stringify({ message, mode: 'full-corpus' }),
        signal: AbortSignal.timeout(5000)  // 5s timeout
      })
    );
    return response.json();
  } catch (error) {
    if (error.code === 'RAG_API_TIMEOUT' || error.code === 'NETWORK_UNREACHABLE') {
      // Tier 2: Try cached responses
      const cached = await getCachedResponse(message);
      if (cached) return { ...cached, source: 'cache' };

      // Tier 3: Try static FAQ
      const faq = getStaticFAQ(message);
      if (faq) return { ...faq, source: 'faq' };

      // Tier 4: Manual fallback
      return {
        type: 'fallback',
        content: "I'm having trouble connecting. Check your internet and try again.",
        error_code: error.code
      };
    }
    throw error;  // Re-throw if not recoverable
  }
}
```

**Validation**:
- [ ] All 19 error codes have user-facing messages
- [ ] Circuit breaker opens after 5 failures
- [ ] Circuit breaker half-opens after 60s
- [ ] Fallback tiers are tried in order (RAG → Cache → FAQ → Manual)
- [ ] Network recovery auto-retries pending query (see T048)

---

### 6. Offline Mode (Pattern 5 + T045-T048)

**Decision**: Service Worker with static FAQ fallback

**Service Worker Scope**:
- **Cache**: Static FAQ (40 questions, ~30KB JSON)
- **Strategy**: Network-first, fallback to cache
- **No caching**: RAG API responses (privacy concern)

**Offline FAQ Structure** (from T046):
```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-27",
  "categories": [
    {
      "id": "getting-started",
      "name": "Getting Started",
      "questions": [
        {
          "id": "how-to-ask-questions",
          "question": "How do I ask questions?",
          "answer": "Type your question in the chat input...",
          "keywords": ["ask", "question", "how to use", "start"]
        }
      ]
    }
  ]
}
```

**Keyword Matching** (0.4 threshold = 40% token overlap):
```typescript
function findBestFAQMatch(userQuery: string, faq: FAQ[]): FAQ | null {
  const userTokens = tokenize(userQuery.toLowerCase());

  let bestMatch = null;
  let bestScore = 0;

  for (const question of faq) {
    const keywordTokens = question.keywords.flatMap(kw => tokenize(kw));
    const overlap = userTokens.filter(token => keywordTokens.includes(token));
    const score = overlap.length / userTokens.length;

    if (score >= 0.4 && score > bestScore) {
      bestMatch = question;
      bestScore = score;
    }
  }

  return bestMatch;
}
```

**Validation**:
- [ ] Service worker caches offline FAQ
- [ ] Offline FAQ loads when network unreachable
- [ ] FAQ search finds relevant questions (40% threshold)
- [ ] FAQ version is displayed ("Last updated: 2025-12-27")

---

### 7. Network Recovery (T048: network-recovery.md)

**Decision**: Browser online/offline events + fetch ping validation

**Implementation**:
```typescript
// Listen for browser online event
window.addEventListener('online', async () => {
  // Validate connectivity (avoid captive portal false positives)
  const isReachable = await isInternetReachable();
  if (!isReachable) return;

  // Announce to user
  announceToUser('✅ Connection restored.');

  // Reset circuit breaker to half-open (allow test request)
  if (circuitBreaker.state === 'open') {
    circuitBreaker.state = 'half-open';
    clearTimeout(circuitBreaker.cooldownTimer);
  }

  // Auto-retry pending query (if <5 minutes old)
  if (pendingQuery && (Date.now() - pendingQuery.timestamp) < 300000) {
    try {
      const response = await sendMessageToRAGAPI(pendingQuery.message);
      showAnswer(response.answer, response.citations);
      announceToUser('✅ Answer updated.');
      pendingQuery = null;
    } catch (error) {
      announceToUser('⚠️ Retry failed. Try again.');
    }
  }
});

// Connectivity validation (fetch ping)
async function isInternetReachable(): Promise<boolean> {
  try {
    await fetch('https://www.cloudflare.com/cdn-cgi/trace', {
      method: 'HEAD',
      cache: 'no-cache',
      signal: AbortSignal.timeout(3000)
    });
    return true;
  } catch {
    return false;
  }
}
```

**Validation**:
- [ ] online event triggers connectivity check
- [ ] Fetch ping validates real internet access
- [ ] Circuit breaker transitions open → half-open on recovery
- [ ] Pending query auto-retries (if <5 min old)
- [ ] 3-second debounce prevents rapid retries

---

### 8. Accessibility (T037-T040: WCAG 2.1 AA)

**Decision**: Built-in accessibility (no external libraries)

**WCAG 2.1 AA Compliance** (from T037: wcag-compliance.md):

**Keyboard Navigation** (T038):
| Key | Action | WCAG Criterion |
|-----|--------|----------------|
| Tab | Focus next element | 2.1.1 Keyboard |
| Shift+Tab | Focus previous element | 2.1.1 Keyboard |
| Enter | Activate button/link | 2.1.1 Keyboard |
| Escape | Close modal/widget | 2.1.2 No Keyboard Trap |
| Arrow Up/Down | Navigate messages | 2.1.1 Keyboard |

**Focus Management** (WCAG 2.4.3 Focus Order, 2.4.7 Focus Visible):
```typescript
// Focus trap for modal (from T038)
function openModal(modalElement: HTMLElement, triggerElement: HTMLElement) {
  modalElement.style.display = 'block';
  modalElement.setAttribute('aria-hidden', 'false');

  const focusableElements = modalElement.querySelectorAll(
    'input, button, textarea, select, a[href]'
  );
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  firstFocusable.focus();  // Focus first element

  // Trap focus inside modal
  modalElement.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') {
      if (event.shiftKey && document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      } else if (!event.shiftKey && document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    } else if (event.key === 'Escape') {
      closeModal(modalElement, triggerElement);
    }
  });
}
```

**Screen Reader Announcements** (T039):
```html
<!-- ARIA live region for announcements -->
<div id="chatkit-announcer"
     class="sr-only"
     aria-live="polite"
     aria-atomic="true"
     role="status">
  <!-- Announcements dynamically inserted here -->
</div>
```

**High-Contrast Mode** (T040):
```css
/* High-contrast mode (Windows) */
@media (prefers-contrast: high) {
  .chatkit-widget {
    border: 2px solid;
    outline: 2px solid;
  }

  *:focus {
    outline: 3px solid;
    outline-offset: 3px;
  }
}
```

**Reduced Motion** (T040):
```css
/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Validation**:
- [ ] WCAG 2.1 AA compliance checklist (50+ criteria from T037)
- [ ] Keyboard navigation flows tested (7 flows from T038)
- [ ] Screen reader testing (NVDA, JAWS, VoiceOver, TalkBack from T039)
- [ ] High-contrast mode tested (Windows, macOS from T040)
- [ ] Reduced motion tested (prefers-reduced-motion from T040)

---

## Implementation Phases

### Phase 7A: Core Widget (MVP)
**Duration**: 2-3 weeks (estimated)
**Dependencies**: None (can start immediately)
**Deliverables**:
- Tier 0 widget button (Vanilla JS)
- Tier 1 chat panel (React)
- RAG API integration (fetch)
- localStorage session (anonymous only)
- Error handling (4-tier fallback)
- Circuit breaker (5 failures → 60s cooldown)

**Acceptance Criteria**:
- [ ] Widget button loads with Docusaurus (<15KB)
- [ ] Chat panel lazy-loads on click (<50KB total)
- [ ] RAG API queries work (full-corpus mode)
- [ ] Conversation history persists in localStorage
- [ ] Error messages match taxonomy (19 error codes)
- [ ] Circuit breaker opens after 5 failures

**Testing**:
- Unit tests: Event bus, circuit breaker, fallback logic
- Integration tests: RAG API integration, error scenarios
- E2E tests: Widget open → ask question → receive answer

---

### Phase 7B: Progressive Signup (US3)
**Duration**: 2-3 weeks (estimated)
**Dependencies**: Better-Auth MCP Server, Signup-Personalization Skill
**Deliverables**:
- OAuth login (Google, GitHub, Microsoft)
- Email verification
- Session merge (anonymous → authenticated)
- IndexedDB session storage (Tier 1+)
- Tier upgrade flows (Tier 0 → Tier 1 → Tier 2)

**Acceptance Criteria**:
- [ ] OAuth login works for all 3 providers
- [ ] Email verification sends verification link
- [ ] Session merge preserves conversation history
- [ ] IndexedDB stores authenticated sessions
- [ ] Tier upgrades trigger session migration

**Testing**:
- Unit tests: Session merge, tier upgrade logic
- Integration tests: OAuth flow, email verification
- E2E tests: Ask question (Tier 0) → sign in → verify history preserved

---

### Phase 7C: Citations & Accessibility (US2, US4)
**Duration**: 1-2 weeks (estimated)
**Dependencies**: Phase 7A complete
**Deliverables**:
- Citation-aware message rendering (stable IDs)
- Keyboard navigation (7 flows)
- Screen reader support (ARIA labels, live regions)
- High-contrast mode
- Reduced motion support

**Acceptance Criteria**:
- [ ] Citations are clickable links with stable IDs
- [ ] Keyboard navigation works (Tab, Enter, Escape, Arrows)
- [ ] Screen reader announces messages (polite live region)
- [ ] High-contrast mode passes Windows/macOS tests
- [ ] Reduced motion disables animations

**Testing**:
- Unit tests: Citation rendering, keyboard handlers
- Accessibility tests: WCAG 2.1 AA checklist (50+ criteria)
- Manual tests: Screen reader testing (4 platforms from T039)

---

### Phase 7D: Offline Mode (US5)
**Duration**: 1 week (estimated)
**Dependencies**: Phase 7A complete
**Deliverables**:
- Service worker (cache static FAQ)
- Offline FAQ (40 questions, keyword matching)
- Network recovery (online event, fetch ping)
- Auto-retry pending query

**Acceptance Criteria**:
- [ ] Service worker caches offline FAQ
- [ ] Offline FAQ loads when network unreachable
- [ ] FAQ search finds relevant questions (40% threshold)
- [ ] Network recovery triggers auto-retry
- [ ] Circuit breaker transitions to half-open on recovery

**Testing**:
- Unit tests: FAQ matching, network detection
- Integration tests: Service worker caching
- E2E tests: Disconnect network → verify FAQ → reconnect → verify auto-retry

---

### Phase 7E: Polish & Optimization
**Duration**: 1 week (estimated)
**Dependencies**: All Phase 7A-D complete
**Deliverables**:
- Bundle size optimization (meet targets)
- Performance monitoring (TTI, widget open, RAG API latency)
- Error tracking (Sentry/similar)
- Analytics (optional Tier 3)

**Acceptance Criteria**:
- [ ] Bundle sizes meet targets (Tier 0: <15KB, Tier 1: <50KB, etc.)
- [ ] TTI <100ms for widget button
- [ ] Widget open <200ms
- [ ] RAG API p95 latency <3s
- [ ] Error tracking captures all 19 error codes

**Testing**:
- Performance tests: Lighthouse CI, bundle size validation
- Load tests: 100 concurrent users
- Error tracking: Verify all error codes appear in Sentry

---

## Testing Strategy

### Unit Tests (Jest + React Testing Library)
**Coverage Target**: 80%+ for core logic

**Test Files**:
- `WidgetEventBus.test.ts` - Event bus (on, emit, off)
- `CircuitBreaker.test.ts` - Circuit breaker (closed, open, half-open)
- `SessionManager.test.ts` - Session merge, tier upgrades
- `CitationRenderer.test.ts` - Citation link generation
- `FAQMatcher.test.ts` - Keyword matching (40% threshold)
- `ErrorHandler.test.ts` - Error taxonomy, fallback tiers

**Example Test**:
```typescript
describe('CircuitBreaker', () => {
  test('opens after 5 consecutive failures', async () => {
    const breaker = new CircuitBreaker();
    const failingOperation = jest.fn().mockRejectedValue(new Error('Timeout'));

    // Trigger 5 failures
    for (let i = 0; i < 5; i++) {
      await expect(breaker.execute(failingOperation)).rejects.toThrow();
    }

    // 6th call should throw CircuitBreakerOpenError
    await expect(breaker.execute(failingOperation)).rejects.toThrow(
      'Circuit breaker open'
    );
    expect(breaker.state).toBe('open');
  });
});
```

---

### Integration Tests (Playwright)
**Coverage**: API integration, OAuth flows, session persistence

**Test Scenarios**:
- RAG API integration (send query → receive answer + citations)
- OAuth login (Google, GitHub, Microsoft)
- Session merge (ask question anonymous → sign in → verify history)
- Error handling (timeout, network unreachable, 503)
- Circuit breaker (5 failures → 60s cooldown → half-open)

**Example Test**:
```typescript
test('session merge preserves conversation history', async ({ page }) => {
  // 1. Ask 3 questions as anonymous user (Tier 0)
  await page.goto('/docs/intro');
  await page.click('.chatkit-widget-button');
  await page.fill('#chatkit-input', 'What is physical AI?');
  await page.press('#chatkit-input', 'Enter');
  await page.waitForSelector('.chatkit-message');  // Wait for answer

  // Repeat for 2 more questions
  // ...

  // 2. Sign in with Google OAuth
  await page.click('#chatkit-signin-button');
  await page.click('#oauth-google');
  // ... OAuth flow

  // 3. Verify all 3 questions appear in conversation history
  const messages = await page.$$('.chatkit-message');
  expect(messages.length).toBe(6);  // 3 questions + 3 answers
});
```

---

### E2E Tests (Playwright)
**Coverage**: Full user flows across multiple sessions

**Test Scenarios**:
- End-to-end chat flow (open widget → ask question → receive answer)
- Multi-session persistence (ask question → refresh page → verify history)
- Offline mode (disconnect network → verify FAQ → reconnect → verify recovery)
- Accessibility (keyboard navigation, screen reader announcements)

**Example Test**:
```typescript
test('offline mode shows FAQ when network unreachable', async ({ page, context }) => {
  await page.goto('/docs/intro');
  await page.click('.chatkit-widget-button');

  // Simulate offline (block all network requests)
  await context.route('**/*', route => route.abort());

  // Ask question that matches FAQ
  await page.fill('#chatkit-input', 'How do I ask questions?');
  await page.press('#chatkit-input', 'Enter');

  // Verify FAQ answer appears
  await page.waitForSelector('.chatkit-message[data-source="faq"]');
  const answer = await page.textContent('.chatkit-message[data-source="faq"]');
  expect(answer).toContain('Type your question in the chat input');
});
```

---

### Accessibility Tests (axe-core + Manual)
**Coverage**: WCAG 2.1 AA compliance (50+ criteria from T037)

**Automated Tests** (axe-core):
```typescript
test('widget has no accessibility violations', async ({ page }) => {
  await page.goto('/docs/intro');
  await page.click('.chatkit-widget-button');

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

**Manual Tests** (from T039: screen-reader-testing.md):
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS, iOS)
- TalkBack (Android)

**Test Scripts** (7 flows from T038: keyboard-navigation.md):
1. Open widget with keyboard (Tab → Enter)
2. Navigate messages with Arrow keys
3. Close widget with Escape
4. Focus trap in modal (Tab, Shift+Tab)
5. Submit message with Enter
6. Navigate citations with Tab
7. Sign in with keyboard (Tab → Enter)

---

### Performance Tests (Lighthouse CI)
**Coverage**: Bundle size, TTI, widget performance

**Lighthouse Thresholds**:
```json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000/docs/intro"]
    },
    "assert": {
      "assertions": {
        "first-contentful-paint": ["error", {"maxNumericValue": 2000}],
        "interactive": ["error", {"maxNumericValue": 5000}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}]
      }
    }
  }
}
```

**Bundle Size Validation** (bundlesize):
```json
{
  "files": [
    {
      "path": "dist/tier0-widget-button.js",
      "maxSize": "15 kB"
    },
    {
      "path": "dist/tier1-chat-panel.js",
      "maxSize": "50 kB"
    }
  ]
}
```

---

## Deployment Strategy

### 1. Integration with Docusaurus
**Approach**: Swizzle Docusaurus theme component

**File**: `src/theme/Root.js` (Docusaurus theme wrapper)

```jsx
import React from 'react';
import ChatKitWidget from '@site/src/components/ChatKitWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatKitWidget
        ragApiUrl={process.env.RAG_API_URL}
        ragApiTimeout={5000}
        enableOfflineFAQ={true}
        enableOAuth={true}
        oauthProviders={['google', 'github', 'microsoft']}
        widgetPosition="bottom-right"
        widgetTheme="auto"
      />
    </>
  );
}
```

**Rationale**:
- Docusaurus Root wrapper renders on every page
- Widget button always available (Tier 0)
- React component integrates natively (no custom loader)

---

### 2. Environment Configuration
**File**: `.env` (not committed)

```bash
# RAG API
RAG_API_URL=https://api.example.com/v1/rag
RAG_API_TIMEOUT=5000

# OAuth (Better-Auth)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# Session (IndexedDB)
INDEXEDDB_NAME=chatkit_sessions
INDEXEDDB_VERSION=1

# Error Tracking (Sentry)
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production

# Analytics (Optional Tier 3)
GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X
```

**Validation**:
- [ ] All OAuth client IDs/secrets configured
- [ ] RAG API URL points to production endpoint
- [ ] Sentry DSN configured for error tracking
- [ ] No secrets committed to git (.env in .gitignore)

---

### 3. CI/CD Pipeline (GitHub Actions)
**File**: `.github/workflows/chatkit-widget.yml`

```yaml
name: ChatKit Widget CI

on:
  push:
    branches: [main, feature/*]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test -- --coverage
      - run: npm run build
      - run: npx bundlesize  # Validate bundle sizes
      - run: npx playwright test  # E2E tests

  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - run: npm run serve &  # Start dev server
      - run: npx lhci autorun  # Lighthouse CI

  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - run: npx playwright test --grep @a11y  # Accessibility tests
```

**Validation**:
- [ ] All tests pass (unit, integration, E2E)
- [ ] Bundle sizes meet targets (bundlesize)
- [ ] Lighthouse scores pass (FCP <2s, TTI <5s)
- [ ] Accessibility tests pass (axe-core)

---

### 4. Rollout Strategy
**Approach**: Feature flag-based gradual rollout

**Phase 1: Internal Testing (Week 1)**
- Enable widget for internal team only (via feature flag)
- Monitor error rates, bundle sizes, performance

**Phase 2: Beta Testing (Week 2-3)**
- Enable widget for 10% of users (via A/B test)
- Monitor engagement metrics (widget opens, messages sent)
- Validate error rates <1%

**Phase 3: Full Rollout (Week 4)**
- Enable widget for 100% of users
- Monitor performance (RAG API latency, circuit breaker triggers)
- Validate WCAG 2.1 AA compliance

**Feature Flag Configuration** (e.g., LaunchDarkly):
```json
{
  "chatkit-widget-enabled": {
    "variations": [true, false],
    "targets": [
      {"values": ["team@example.com"], "variation": 0}  // Internal team
    ],
    "rules": [
      {"variation": 0, "rollout": {"percentage": 10}}  // 10% rollout
    ],
    "fallthrough": {"variation": 1}  // Default: disabled
  }
}
```

---

### 5. Rollback Plan
**Trigger**: If any of these occur:
- Error rate >1% (from Sentry)
- Circuit breaker open rate >5% (from monitoring)
- WCAG violations reported (from user feedback)
- Bundle size exceeds limits (from CI)

**Rollback Steps**:
1. Disable feature flag (`chatkit-widget-enabled: false`)
2. Widget disappears from all pages (Tier 0 not loaded)
3. Investigate issue (check Sentry, Lighthouse, WCAG logs)
4. Fix and redeploy (re-enable feature flag after validation)

**Rollback Time**: <5 minutes (feature flag toggle)

---

## Monitoring & Observability

### 1. Error Tracking (Sentry)
**Capture**:
- All 19 error codes (from T047)
- Circuit breaker state transitions (closed → open → half-open)
- OAuth failures (timeout, cancelled, invalid_credentials)
- Session merge errors (data loss, indexeddb errors)

**Sentry Configuration**:
```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT,
  beforeSend(event) {
    // Enrich with widget context
    event.contexts = {
      ...event.contexts,
      widget: {
        tier: getCurrentTier(),
        session_id: getSessionId(),
        circuit_breaker_state: circuitBreaker.state
      }
    };
    return event;
  }
});
```

**Alerts**:
- Error rate >1% → Slack alert
- Circuit breaker open rate >5% → PagerDuty alert

---

### 2. Performance Monitoring (Lighthouse CI)
**Metrics**:
- TTI (Time to Interactive): <100ms for widget button
- Widget Open Latency: <200ms (Tier 0 → Tier 1)
- RAG API p95 Latency: <3s
- Bundle Sizes: Tier 0 <15KB, Tier 1 <50KB, Tier 2 <100KB, Tier 3 <150KB

**Lighthouse CI Configuration**:
```json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000/docs/intro"]
    },
    "assert": {
      "assertions": {
        "first-contentful-paint": ["error", {"maxNumericValue": 2000}],
        "interactive": ["error", {"maxNumericValue": 5000}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}]
      }
    }
  }
}
```

---

### 3. Analytics (Optional Tier 3)
**Metrics**:
- Widget Opens (daily, weekly)
- Messages Sent (total, per user)
- Error Rate (by error code)
- Circuit Breaker Triggers (by hour)
- Session Tier Distribution (Tier 0, 1, 2, 3)
- OAuth Provider Usage (Google, GitHub, Microsoft)

**Google Analytics Configuration**:
```typescript
// Track widget open
window.gtag('event', 'widget_open', {
  event_category: 'chatkit',
  event_label: 'tier_0_to_tier_1'
});

// Track message sent
window.gtag('event', 'message_sent', {
  event_category: 'chatkit',
  event_label: getCurrentTier(),
  value: 1
});
```

---

## Privacy & Compliance

### GDPR Compliance (EU)
**Requirements**:
- [ ] Cookie consent banner (before setting cookies)
- [ ] Data access request (user can download conversation history)
- [ ] Data deletion request (user can delete all data)
- [ ] Data portability (export conversation history as JSON)

**Implementation** (from Better-Auth MCP Server, Signup-Personalization Skill):
- Tier 0 (Anonymous): No cookies, localStorage only (no GDPR consent required)
- Tier 1+ (Authenticated): Cookie consent banner before OAuth login

---

### CCPA Compliance (California)
**Requirements**:
- [ ] "Do Not Sell My Data" opt-out (no data selling)
- [ ] Privacy Policy disclosure (data collection practices)

---

### FERPA Compliance (Education)
**Requirements**:
- [ ] Student privacy protection (no PII in chat logs without consent)
- [ ] Parental consent (<13 years old)

---

### COPPA Compliance (<13 years)
**Requirements**:
- [ ] Age gate (ask user age before signup)
- [ ] Parental consent (if <13, require parent email)
- [ ] No behavioral advertising

---

## Risk Analysis

### Risk 1: Better-Auth MCP Server Delays Phase 7B
**Impact**: High (blocks US3: Progressive Signup)
**Probability**: Medium
**Mitigation**:
- Start Better-Auth MCP development in parallel with Phase 7A
- Use mock OAuth provider for Phase 7A testing
- Defer Phase 7B until Better-Auth MCP is ready

---

### Risk 2: Bundle Size Exceeds Limits
**Impact**: Medium (degrades performance, fails CI)
**Probability**: Low
**Mitigation**:
- Use bundlesize CI check (fails PR if exceeded)
- Consider Preact instead of React (saves ~39KB)
- Lazy-load Tier 2-3 features aggressively

---

### Risk 3: RAG API Latency >3s p95
**Impact**: High (poor UX, circuit breaker triggers)
**Probability**: Medium
**Mitigation**:
- Use circuit breaker (fallback to cache/FAQ)
- Add RAG API caching (Redis, 1-hour TTL)
- Optimize RAG API query performance (server-side)

---

### Risk 4: WCAG 2.1 AA Violations
**Impact**: High (accessibility non-compliance, legal risk)
**Probability**: Low
**Mitigation**:
- Use axe-core CI check (fails PR if violations)
- Manual screen reader testing (T039)
- Accessibility audit by external consultant

---

### Risk 5: Session Merge Data Loss
**Impact**: Critical (lose user conversation history)
**Probability**: Low
**Mitigation**:
- Add session merge transaction (atomic write)
- Add session merge validation (verify all messages)
- Add session merge rollback (restore localStorage on error)

---

## Success Metrics

### Phase 7A Success Criteria
- [ ] Widget button loads <15KB (Tier 0)
- [ ] Chat panel loads <50KB total (Tier 1)
- [ ] RAG API integration works (full-corpus mode)
- [ ] Error handling covers all 19 error codes
- [ ] Circuit breaker opens after 5 failures

---

### Phase 7B Success Criteria
- [ ] OAuth login works (Google, GitHub, Microsoft)
- [ ] Session merge preserves conversation history (100% accuracy)
- [ ] Tier upgrades trigger session migration (Tier 0 → Tier 1 → Tier 2)

---

### Phase 7C Success Criteria
- [ ] Citations are clickable links with stable IDs
- [ ] WCAG 2.1 AA compliance (50+ criteria pass)
- [ ] Keyboard navigation works (7 flows)
- [ ] Screen reader support (4 platforms)

---

### Phase 7D Success Criteria
- [ ] Offline FAQ loads when network unreachable
- [ ] FAQ search finds relevant questions (40% threshold)
- [ ] Network recovery triggers auto-retry
- [ ] Circuit breaker transitions to half-open on recovery

---

### Phase 7E Success Criteria
- [ ] Bundle sizes meet targets (Tier 0-3)
- [ ] TTI <100ms (widget button)
- [ ] Widget open <200ms (Tier 0 → Tier 1)
- [ ] RAG API p95 latency <3s
- [ ] Error rate <1% (Sentry)

---

## Next Steps (Immediate)

### Before Starting Phase 7 Implementation

1. **Create Better-Auth MCP Server** (`.claude/mcp/better-auth/`)
   - Estimated: ~500 lines (mcp.json + README.md)
   - Priority: 🔴 CRITICAL (blocks Phase 7B)

2. **Create Signup-Personalization Skill** (`.claude/skills/signup-personalization/`)
   - Estimated: ~1,000 lines (SKILL.md + patterns.md)
   - Priority: 🔴 CRITICAL (blocks Phase 7B)

3. **Review T057-T061 Validation Reports** (remaining Phase 9 tasks)
   - Ensure all design artifacts are validated before implementation
   - Estimated: 2-3 days

---

## Appendix

### A. File Structure (Phase 7+ Implementation)

```
physical-ai-book/
├── src/
│   ├── components/
│   │   ├── ChatKitWidget/
│   │   │   ├── index.tsx              # Main widget component
│   │   │   ├── WidgetButton.tsx       # Tier 0 button (Vanilla JS wrapper)
│   │   │   ├── ChatPanel.tsx          # Tier 1 chat panel
│   │   │   ├── OAuthProvider.tsx      # Tier 2 OAuth login
│   │   │   ├── AnalyticsPanel.tsx     # Tier 3 analytics (optional)
│   │   │   ├── MessageList.tsx        # Message list with citations
│   │   │   ├── MessageInput.tsx       # Input with keyboard shortcuts
│   │   │   ├── ErrorMessage.tsx       # Error display (19 error codes)
│   │   │   └── OfflineFAQ.tsx         # Offline FAQ fallback
│   │   └── ...
│   ├── hooks/
│   │   ├── useEventBus.ts             # Event bus hook
│   │   ├── useCircuitBreaker.ts       # Circuit breaker hook
│   │   ├── useSessionManager.ts       # Session merge, tier upgrades
│   │   ├── useOfflineFAQ.ts           # FAQ matching
│   │   └── useNetworkRecovery.ts      # Network online/offline detection
│   ├── lib/
│   │   ├── WidgetEventBus.ts          # Event bus implementation
│   │   ├── CircuitBreaker.ts          # Circuit breaker implementation
│   │   ├── SessionManager.ts          # Session storage (localStorage, IndexedDB)
│   │   ├── ErrorHandler.ts            # Error taxonomy, fallback logic
│   │   ├── CitationRenderer.ts        # Citation link generation
│   │   └── FAQMatcher.ts              # Keyword matching (0.4 threshold)
│   └── theme/
│       └── Root.js                    # Docusaurus theme wrapper
├── static/
│   ├── offline-faq.json               # Static FAQ (40 questions)
│   └── service-worker.js              # Service worker (cache FAQ)
└── package.json
```

---

### B. API Endpoints (Phase 7+ Backend Work)

**RAG API** (Physical AI Chatbot Backend):
- `POST /api/v1/rag/query` - Send query, receive answer + citations
  - Request: `{ "message": "What is embodied intelligence?", "mode": "full-corpus" }`
  - Response: `{ "answer": "...", "citations": [...], "session_id": "uuid-v4" }`

**Session API** (Authentication Backend):
- `POST /api/v1/session/merge` - Merge anonymous → authenticated session
  - Request: `{ "anonymous_session_id": "uuid-v4", "user_id": "user-123", "data": {...} }`
  - Response: `{ "session_id": "uuid-v4", "user_id": "user-123" }`
- `GET /api/v1/session/{user_id}` - Load authenticated session
  - Response: `{ "session_id": "uuid-v4", "messages": [...] }`
- `POST /api/v1/session/update` - Save session updates
  - Request: `{ "session_id": "uuid-v4", "messages": [...] }`
  - Response: `{ "success": true }`

**OAuth API** (Better-Auth):
- `GET /api/v1/auth/oauth/{provider}` - Initiate OAuth flow
  - Provider: `google` | `github` | `microsoft`
  - Response: Redirect to OAuth provider
- `GET /api/v1/auth/oauth/callback` - OAuth callback
  - Response: `{ "user_id": "user-123", "session_token": "jwt-token" }`

---

### C. Error Taxonomy Reference (from T047)

**Network Errors (7)**:
1. `NETWORK_UNREACHABLE` - No internet connection
2. `NETWORK_TIMEOUT` - Request took >5s
3. `RAG_API_TIMEOUT` - RAG API took >5s
4. `RAG_API_503` - RAG API service unavailable
5. `RAG_API_500` - RAG API internal server error
6. `RAG_API_502` - RAG API bad gateway
7. `RAG_API_404` - RAG API endpoint not found

**Validation Errors (2)**:
8. `INVALID_INPUT` - Empty message, >500 chars
9. `RATE_LIMIT_EXCEEDED` - >10 messages/minute

**Authentication Errors (3)**:
10. `SESSION_EXPIRED` - JWT token expired
11. `INVALID_CREDENTIALS` - OAuth token invalid
12. `OAUTH_TIMEOUT` - OAuth flow took >60s

**Guardrail Errors (3)**:
13. `OUT_OF_SCOPE` - Question not about Physical AI
14. `CODE_GENERATION_BLOCKED` - User asked for code (Phase 1 constraint)
15. `LOW_CONFIDENCE` - RAG confidence <0.5

**System Errors (4)**:
16. `OAUTH_CANCELLED` - User cancelled OAuth flow
17. `CIRCUIT_BREAKER_OPEN` - Circuit breaker blocking requests
18. `WIDGET_INITIALIZATION_FAILED` - Widget failed to load
19. `INDEXEDDB_ERROR` - IndexedDB write failed

---

### D. Performance Budget Reference (from T061)

| Metric | Target | Maximum | Validation |
|--------|--------|---------|------------|
| **Bundle Sizes** ||||
| Tier 0 (Widget Button) | <12KB | 15KB | bundlesize CI |
| Tier 1 (Chat Panel) | <40KB | 50KB | bundlesize CI |
| Tier 2 (OAuth) | <80KB | 100KB | bundlesize CI |
| Tier 3 (Analytics) | <120KB | 150KB | bundlesize CI |
| **Performance** ||||
| TTI (Widget Button) | <80ms | 100ms | Lighthouse CI |
| Widget Open Latency | <150ms | 200ms | Custom metric |
| RAG API p50 Latency | <1.5s | 2s | Backend monitoring |
| RAG API p95 Latency | <2.5s | 3s | Backend monitoring |
| **Accessibility** ||||
| WCAG 2.1 AA Compliance | 100% | 100% | axe-core CI |

---

**Status**: T056 Phase 7 Planning Guide Complete ✅
**File**: `specs/003-chatkit-widget/phase7-planning.md`
**Lines**: 1,200+
**Coverage**: Framework selection, runtime decisions, implementation phases, testing strategy, deployment, monitoring, compliance, risk analysis
