# ChatKit Widget Integration Guide

**Version**: 1.0.0 (Phase 6 Design Specification)
**Status**: Design-Only (No Runtime Code)
**Target Audience**: Developers implementing ChatKit Widget in Phase 7+

---

## Overview

This guide provides comprehensive integration instructions for the **ChatKit Widget** - an embedded Q&A chatbot for the Physical AI & Humanoid Robotics documentation site built with Docusaurus.

**Important**: This is a **design specification** (Phase 6). All code examples are design-level pseudocode, not production-ready TypeScript/React. Use this guide to plan Phase 7+ implementation.

---

## Table of Contents

1. [Features Overview](#features-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Pattern 1: Event-Driven Widget Architecture](#pattern-1-event-driven-widget-architecture)
5. [Pattern 2: Progressive Widget Loading](#pattern-2-progressive-widget-loading)
6. [Pattern 3: Session Continuity with Tier Upgrades](#pattern-3-session-continuity-with-tier-upgrades)
7. [Pattern 4: Citation-Aware Message Rendering](#pattern-4-citation-aware-message-rendering)
8. [Pattern 5: Graceful Degradation for Network Failures](#pattern-5-graceful-degradation-for-network-failures)
9. [Pattern 6: Contextual Feature Discovery](#pattern-6-contextual-feature-discovery)
10. [Widget States & State Machine](#widget-states--state-machine)
11. [Event Schema Reference](#event-schema-reference)
12. [Configuration Options](#configuration-options)
13. [Accessibility & Compliance](#accessibility--compliance)
14. [Troubleshooting](#troubleshooting)
15. [Performance Budgets](#performance-budgets)

---

## Features Overview

### Core Features (US1-US2 MVP)

**US1: Frictionless Q&A**
- Anonymous access (no signup required for first 15 messages)
- Real-time RAG chatbot with citation links
- Browser-local conversation history (localStorage)
- Floating widget button (bottom-right corner)

**US2: Dual-Mode Retrieval**
- **Full-Corpus Mode**: Search entire Physical AI book (default)
- **Selected-Text Mode**: Answer questions about highlighted text (contextual)
- Automatic mode switching based on user selection

### Progressive Features (US3-US5)

**US3: Progressive Signup**
- 4-tier authentication (Tier 0: Anonymous → Tier 3: Premium)
- OAuth integration (Google, GitHub, Microsoft)
- Session merge on signup (browser-local → server-sync)
- GDPR/CCPA/FERPA/COPPA compliant consent flows

**US4: Accessibility**
- WCAG 2.1 AA compliant
- Full keyboard navigation (Tab, Enter, Escape)
- Screen reader support (NVDA, JAWS, VoiceOver, TalkBack)
- High-contrast mode and reduced-motion support

**US5: Offline Mode**
- Circuit breaker pattern (5 failures → 60s cooldown)
- 4-tier fallback (RAG API → Cache → FAQ → Manual)
- Static FAQ (40 questions, 7 categories, 100% offline)
- Network recovery detection with auto-retry

### Future Features (US6 - Deferred to Phase 7+)

**US6: Multi-Modal Input**
- Voice input (speech-to-text)
- Image upload (vision model integration)

---

## Architecture

### Component Hierarchy

```
Docusaurus Page
  └─ ChatKit Widget (embedded in footer)
      ├─ Widget Button (floating, bottom-right)
      ├─ Chat Panel (modal overlay)
      │   ├─ Mode Toggle (Full-Corpus / Selected-Text)
      │   ├─ Message List (conversation history)
      │   │   ├─ User Message Bubble
      │   │   └─ Agent Message Bubble
      │   │       └─ Citation Links (inline superscript)
      │   ├─ Input Field (text input + submit button)
      │   └─ Error Banner (network errors, rate limits)
      └─ Signup Modal (OAuth or email/password)
```

### Data Flow

```
User Input
  ↓
Widget (user_message event)
  ↓
RAG Orchestration Subagent (backend)
  ↓
Widget (agent_response event)
  ↓
Citation Rendering (clickable links to docs)
  ↓
Update Conversation History (browser-local or server-sync)
```

### Integration Points

| Component | Path | Purpose |
|-----------|------|---------|
| **RAG Orchestration Subagent** | `.claude/agents/rag-orchestration/AGENT.md` | Backend Q&A orchestration (Phase 7+) |
| **Better-Auth MCP Server** | `.claude/mcp/better-auth/README.md` | OAuth + session management (Phase 7+, future dependency) |
| **RAG Chatbot Skill** | `.claude/skills/rag-chatbot/patterns.md` | Dual-mode retrieval, citation patterns |
| **Signup-Personalization Skill** | `.claude/skills/signup-personalization/` | Tier upgrade flows (Phase 7+, future dependency) |

---

## Installation & Setup

### Step 1: Install Dependencies (Phase 7+ Implementation)

```bash
# Install ChatKit Widget package (future npm package)
npm install @claude-agents/chatkit-widget

# Or copy widget files directly
cp -r chatkit-widget/ physical-ai-book/src/components/
```

**Dependencies**:
- React 18+ (Docusaurus already includes)
- TypeScript 5+ (optional, but recommended)
- Better-Auth SDK (for OAuth, future dependency)

---

### Step 2: Import Widget in Docusaurus

**File**: `physical-ai-book/src/theme/Footer/index.tsx`

```typescript
import React from 'react';
import Footer from '@theme-original/Footer';
import ChatKitWidget from '@site/src/components/ChatKitWidget';

export default function FooterWrapper(props) {
  return (
    <>
      <Footer {...props} />
      <ChatKitWidget
        ragApiUrl={process.env.RAG_API_URL || 'https://api.example.com/v1/rag'}
        enableOfflineFAQ={true}
        enableOAuth={true}
        oauthProviders={['google', 'github', 'microsoft']}
      />
    </>
  );
}
```

---

### Step 3: Configure Environment Variables

**File**: `physical-ai-book/.env`

```bash
# RAG API Configuration
RAG_API_URL=https://api.example.com/v1/rag
RAG_API_TIMEOUT=5000  # 5 seconds

# OAuth Configuration (Better-Auth)
BETTER_AUTH_SECRET=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Feature Flags
ENABLE_OFFLINE_FAQ=true
ENABLE_OAUTH=true
ENABLE_CIRCUIT_BREAKER=true
```

---

### Step 4: Add Widget Styles

**File**: `physical-ai-book/src/css/custom.css`

```css
/* ChatKit Widget Styles */
.chatkit-widget-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: var(--ifm-color-primary);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  z-index: 1000;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chatkit-widget-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.chatkit-widget-button:focus {
  outline: 2px solid var(--ifm-color-primary-dark);
  outline-offset: 2px;
}

/* Chat Panel (Modal Overlay) */
.chatkit-panel {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 400px;
  max-width: calc(100vw - 48px);
  height: 600px;
  max-height: calc(100vh - 150px);
  background-color: var(--ifm-background-color);
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  z-index: 1001;
  display: flex;
  flex-direction: column;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

/* Reduced-motion support */
@media (prefers-reduced-motion: reduce) {
  .chatkit-widget-button,
  .chatkit-panel {
    transition: none;
  }
}
```

---

## Pattern 1: Event-Driven Widget Architecture

### Event Types

**6 Core Events**:
1. `user_message` - User submits a question
2. `agent_response` - RAG agent returns an answer
3. `system_message` - System notification (e.g., "Connection restored")
4. `signup_initiated` - User starts signup flow
5. `authentication_completed` - User completes OAuth or email signup
6. `error` - Error occurred (network timeout, validation, etc.)

### Event Schema

**user_message Event**:
```json
{
  "event": "user_message",
  "timestamp": "2025-12-27T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "message": {
    "content": "What is embodied intelligence?",
    "mode": "full-corpus",
    "metadata": {
      "selected_text": null,
      "selected_text_length": 0,
      "page_url": "/docs/module-2-embodied/embodied-intelligence"
    }
  }
}
```

**agent_response Event**:
```json
{
  "event": "agent_response",
  "timestamp": "2025-12-27T10:30:03.000Z",
  "session_id": "uuid-v4-string",
  "response": {
    "answer": "Embodied intelligence refers to intelligence that arises from the interaction between an agent's body and its environment...",
    "citations": [
      {
        "id": 1,
        "module_id": "module-2-embodied",
        "chapter_id": "embodied-intelligence",
        "url": "/docs/module-2-embodied/embodied-intelligence",
        "title": "Embodied Intelligence"
      }
    ],
    "confidence_score": 0.92
  }
}
```

**error Event** (see T047 for complete error taxonomy):
```json
{
  "event": "error",
  "timestamp": "2025-12-27T10:30:05.000Z",
  "session_id": "uuid-v4-string",
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

### Event Dispatcher (Design-Level)

```typescript
class ChatKitEventBus {
  listeners: Map<string, Function[]> = new Map();

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event: string, payload: object) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => callback(payload));

    // Log to analytics
    analyticsService.track(event, payload);
  }
}

// Usage
const eventBus = new ChatKitEventBus();

eventBus.on('user_message', async (payload) => {
  const response = await ragOrchestrationSubagent.query(payload.message);
  eventBus.emit('agent_response', {response});
});

eventBus.on('error', (payload) => {
  showErrorBanner(payload.error.message);
});
```

---

## Pattern 2: Progressive Widget Loading

### 4-Tier Code Splitting

**Tier 0: Critical (Inline, <15KB)**
- Widget button HTML/CSS
- Click handler to load Tier 1

**Tier 1: Essential (<50KB)**
- Chat panel UI (React components)
- Input field + message list
- Anonymous Q&A (no auth)

**Tier 2: Enhanced (<100KB)**
- OAuth integration (Better-Auth SDK)
- Session merge logic
- Tier upgrade flows

**Tier 3: Full Features (<150KB)**
- Voice input (speech-to-text SDK)
- Image upload (vision model SDK)
- Advanced analytics

### Dynamic Import (Design-Level)

```typescript
// Tier 0: Widget button (loaded immediately)
<button class="chatkit-widget-button" onclick="loadChatPanel()">
  💬 Ask
</button>

// Tier 1: Load chat panel on click (lazy)
async function loadChatPanel() {
  const ChatPanel = await import('./ChatPanel');
  renderChatPanel(<ChatPanel />);
}

// Tier 2: Load OAuth on signup trigger (lazy)
async function loadOAuthModule() {
  const OAuth = await import('./OAuth');
  return OAuth.initBetterAuth();
}

// Tier 3: Load voice input on first use (lazy)
async function loadVoiceInput() {
  const Voice = await import('./VoiceInput');
  return Voice.initSpeechRecognition();
}
```

### Bundle Size Targets

| Tier | Size Limit | Loading Strategy | Time Budget |
|------|------------|------------------|-------------|
| Tier 0 (Critical) | <15KB | Inline (bundled with Docusaurus) | TTI: 100ms |
| Tier 1 (Essential) | <50KB | Lazy import on button click | Load: 200ms |
| Tier 2 (Enhanced) | <100KB | Lazy import on feature access | Load: 500ms |
| Tier 3 (Full) | <150KB | Lazy import on first use | Load: 1s |

---

## Pattern 3: Session Continuity with Tier Upgrades

### 4-Tier Authentication

| Tier | Label | Auth Method | Features | Message Limit |
|------|-------|-------------|----------|---------------|
| **Tier 0** | Anonymous | None (browser-local only) | Basic Q&A, browser-local history | 15 messages/30 min |
| **Tier 1** | Lightweight | Email verification | Server-sync history, bookmarks | 50 messages/day |
| **Tier 2** | Full Profile | Email + profile (age, interests) | Personalized learning paths, analytics | 200 messages/day |
| **Tier 3** | Premium | Paid subscription | Unlimited messages, priority support | Unlimited |

### Tier Upgrade Flow (Tier 0 → Tier 1)

```typescript
// Step 1: User clicks "Save Progress" after 10 messages
<button onclick="upgradeTier(1)">💾 Save Progress (Free)</button>

// Step 2: Show signup modal
async function upgradeTier(targetTier: number) {
  const currentTier = getCurrentTier();  // 0

  if (targetTier === 1) {
    showSignupModal({
      title: '🔒 Save Your Progress',
      message: "We'll securely store your 15 messages so you can access them from any device.",
      method: 'email-or-oauth'
    });
  }
}

// Step 3: User completes signup (email or OAuth)
async function handleSignupCompleted(userId: string, sessionToken: string) {
  // Merge browser-local session to server
  await mergeAnonymousSession(userId, sessionToken);

  // Update tier badge
  updateTierBadge(1);

  // Show success notification
  announceToUser('✅ Progress saved! Your conversation is now synced across devices.');
}

// Step 4: Session merge (browser-local → server-sync)
async function mergeAnonymousSession(userId: string, sessionToken: string) {
  // Read browser-local history
  const localHistory = JSON.parse(localStorage.getItem('chatkit_history') || '[]');
  const localBookmarks = JSON.parse(localStorage.getItem('chatkit_bookmarks') || '[]');

  // Upload to server
  await fetch('/api/v1/session/merge', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      data: {
        conversation_history: localHistory,
        bookmarks: localBookmarks,
        preferences: {}
      }
    })
  });

  // Clear browser-local storage
  localStorage.removeItem('chatkit_history');
  localStorage.setItem('session_token', sessionToken);
}
```

**See Integration Guide**: `specs/003-chatkit-widget/integration/tier-upgrades.md` (950 lines, complete upgrade workflows)

---

## Pattern 4: Citation-Aware Message Rendering

### Citation Rendering

**Input** (from RAG API):
```json
{
  "answer": "Embodied intelligence refers to intelligence that arises from the interaction between an agent's body and its environment. This contrasts with disembodied approaches like traditional symbolic AI.",
  "citations": [
    {
      "id": 1,
      "module_id": "module-2-embodied",
      "chapter_id": "embodied-intelligence",
      "url": "/docs/module-2-embodied/embodied-intelligence",
      "title": "Embodied Intelligence"
    },
    {
      "id": 2,
      "module_id": "module-1-intro",
      "chapter_id": "what-is-physical-ai",
      "url": "/docs/module-1-intro/what-is-physical-ai",
      "title": "Introduction to Physical AI"
    }
  ]
}
```

**Output** (rendered HTML):
```html
<div class="agent-message">
  <p class="message-text">
    Embodied intelligence refers to intelligence that arises from the interaction
    between an agent's body and its environment.
    <sup>
      <a href="/docs/module-2-embodied/embodied-intelligence"
         aria-label="Citation 1: Embodied Intelligence"
         class="citation-link">
        [1]
      </a>
    </sup>
    This contrasts with disembodied approaches like traditional symbolic AI.
    <sup>
      <a href="/docs/module-1-intro/what-is-physical-ai"
         aria-label="Citation 2: Introduction to Physical AI"
         class="citation-link">
        [2]
      </a>
    </sup>
  </p>
</div>
```

### Citation Click Handler

```typescript
function handleCitationClick(citationUrl: string) {
  // Navigate to cited documentation page
  window.location.href = citationUrl;

  // Scroll to cited section (if URL has anchor)
  if (citationUrl.includes('#')) {
    const [url, anchor] = citationUrl.split('#');
    const element = document.getElementById(anchor);
    element?.scrollIntoView({behavior: 'smooth'});
  }

  // Close widget after navigation
  closeWidget();
}
```

**Accessibility**: All citation links have `aria-label` with meaningful text (not just "[1]").

---

## Pattern 5: Graceful Degradation for Network Failures

### Circuit Breaker

**Configuration**:
- Failure Threshold: 5 consecutive failures
- Cooldown Duration: 60 seconds
- Timeout: 5 seconds (RAG API)

**States**:
1. **Closed** (normal operation): All requests pass through
2. **Open** (circuit tripped): All requests rejected, 60s cooldown
3. **Half-Open** (testing recovery): Single test request allowed

**Implementation**: See `specs/003-chatkit-widget/integration/circuit-breaker.md` (850 lines)

### 4-Tier Fallback

```typescript
async function sendMessageWithFallback(message: string) {
  try {
    // Tier 1: RAG API (5s timeout)
    const response = await ragAPI.query(message, {timeout: 5000});
    return response;
  } catch (error) {
    if (error.type === 'timeout' || error.type === 'network') {
      // Tier 2: Cached response (100ms timeout)
      const cached = await getCachedResponse(message, {timeout: 100});
      if (cached) return {answer: cached, source: 'cache'};

      // Tier 3: Static FAQ (instant)
      const faq = getStaticFAQ(message);
      if (faq) return {answer: faq, source: 'faq'};

      // Tier 4: Manual fallback
      return {
        answer: "I'm having trouble connecting. Try browsing topics manually:",
        source: 'manual',
        actions: [
          {label: "View All Topics", url: "/docs"},
          {label: "Retry", event: "retry_query"}
        ]
      };
    }

    throw error;  // Unrecoverable error
  }
}
```

### Static FAQ

**Storage**: Inline JavaScript (~30 KB, 40 questions)

**Categories**: 7 (Getting Started, Physical AI Basics, Humanoid Robotics, Perception, Control, Learning, Future & Ethics)

**Implementation**: See `specs/003-chatkit-widget/integration/offline-faq.md` (900 lines)

---

## Pattern 6: Contextual Feature Discovery

### Discovery Triggers

**Trigger 1: Repeated Questions (5+) → Voice Input Hint**
```typescript
if (questionCount >= 5 && !hasSeenVoiceHint) {
  showFeatureHint({
    icon: '🎤',
    message: 'Tip: Try voice input for faster questions (click microphone icon)',
    dismissible: true,
    feature: 'voice_input'
  });
}
```

**Trigger 2: Long Text Selection (>200 chars) → Selected-Text Mode Hint**
```typescript
if (selectedText.length > 200 && !hasSeenSelectedTextHint) {
  showFeatureHint({
    icon: '💡',
    message: "You've selected text! Ask a follow-up question to focus on this passage.",
    dismissible: true,
    feature: 'selected_text_mode'
  });
}
```

**Trigger 3: Third Session → Bookmark Hint**
```typescript
if (sessionCount >= 3 && !hasSeenBookmarkHint) {
  showFeatureHint({
    icon: '🔖',
    message: 'Bookmark answers to find them later! Click the bookmark icon on any message.',
    dismissible: true,
    feature: 'bookmarks'
  });
}
```

---

## Widget States & State Machine

### 6 States

| State | Description | UI Indicators | Allowed Transitions |
|-------|-------------|---------------|---------------------|
| **Idle** | Widget ready for input | Input enabled, cursor active | → Typing, SignupFlow |
| **Typing** | User actively typing | Character count, "Typing..." | → Idle, Processing |
| **Processing** | Agent orchestration in progress | Loading spinner, "Thinking..." | → Responding, Error |
| **Responding** | Agent streaming response | Typing animation, partial text | → Idle |
| **Error** | Recoverable or fatal error | Error icon, retry button | → Idle, [*] |
| **SignupFlow** | Authentication workflow active | Signup modal overlay | → Idle |

### State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Typing : user_typing
    Typing --> Idle : user_stopped_typing
    Typing --> Processing : user_submit
    Processing --> Responding : agent_started
    Responding --> Idle : agent_completed
    Processing --> Error : agent_error
    Error --> Idle : user_retry
    Idle --> SignupFlow : signup_triggered
    SignupFlow --> Idle : signup_completed
    SignupFlow --> Idle : signup_cancelled
```

---

## Event Schema Reference

See SKILL.md for complete event schemas:
- `user_message` - Lines 123-142
- `agent_response` - Lines 144-167
- `system_message` - Lines 169-184
- `signup_initiated` - Lines 186-200
- `authentication_completed` - Lines 202-219
- `error` - Lines 221-243

**Error Codes**: See `specs/003-chatkit-widget/checklists/error-handling.md` for complete error taxonomy (19 error codes).

---

## Configuration Options

### Widget Configuration

```typescript
interface ChatKitConfig {
  // API Configuration
  ragApiUrl: string;                    // RAG API endpoint (required)
  ragApiTimeout?: number;               // Timeout in ms (default: 5000)

  // Feature Flags
  enableOfflineFAQ?: boolean;           // Enable static FAQ fallback (default: true)
  enableOAuth?: boolean;                // Enable OAuth signup (default: true)
  enableCircuitBreaker?: boolean;       // Enable circuit breaker (default: true)
  enableVoiceInput?: boolean;           // Enable voice input (default: false, Phase 7+)

  // OAuth Providers
  oauthProviders?: ('google' | 'github' | 'microsoft')[];  // Default: ['google']

  // Rate Limits
  rateLimitAnonymous?: number;          // Messages per 30 min (default: 15)
  rateLimitTier1?: number;              // Messages per day (default: 50)
  rateLimitTier2?: number;              // Messages per day (default: 200)

  // UI Customization
  widgetPosition?: 'bottom-right' | 'bottom-left';  // Default: 'bottom-right'
  widgetTheme?: 'light' | 'dark' | 'auto';          // Default: 'auto' (match Docusaurus theme)

  // Accessibility
  enableKeyboardNavigation?: boolean;   // Enable keyboard shortcuts (default: true)
  enableScreenReaderSupport?: boolean;  // Enable ARIA live regions (default: true)
  enableReducedMotion?: boolean;        // Respect prefers-reduced-motion (default: true)
}
```

### Example Configuration

```typescript
<ChatKitWidget
  ragApiUrl="https://api.example.com/v1/rag"
  ragApiTimeout={5000}
  enableOfflineFAQ={true}
  enableOAuth={true}
  oauthProviders={['google', 'github']}
  rateLimitAnonymous={15}
  widgetPosition="bottom-right"
  widgetTheme="auto"
/>
```

---

## Accessibility & Compliance

### WCAG 2.1 AA Compliance

**Perceivable**:
- ✅ Text alternatives (ARIA labels for all interactive elements)
- ✅ Adaptable (responsive design, text zoom up to 200%)
- ✅ Distinguishable (≥4.5:1 contrast ratio for text, ≥3:1 for UI components)

**Operable**:
- ✅ Keyboard accessible (Tab, Shift+Tab, Enter, Escape)
- ✅ Enough time (no time limits on Q&A)
- ✅ Navigable (focus visible, skip links, page titled)

**Understandable**:
- ✅ Readable (plain language, no jargon)
- ✅ Predictable (consistent navigation, no context changes)
- ✅ Input assistance (error messages, validation)

**Robust**:
- ✅ Compatible (valid HTML, ARIA roles, screen reader tested)

**Testing Guides**:
- WCAG Checklist: `specs/003-chatkit-widget/checklists/wcag-compliance.md` (800 lines)
- Screen Reader Testing: `specs/003-chatkit-widget/checklists/screen-reader-testing.md` (1,100 lines)
- Keyboard Navigation: `specs/003-chatkit-widget/integration/keyboard-navigation.md` (1,100 lines)

### Privacy Compliance

**GDPR** (EU):
- ✅ Explicit consent for conversation storage (Tier 1+)
- ✅ Right to access (export conversation history)
- ✅ Right to deletion (one-click account deletion)
- ✅ Right to portability (download JSON/Markdown)

**CCPA** (California):
- ✅ "Do Not Sell My Data" opt-out
- ✅ Right to know what data is collected
- ✅ Right to deletion

**FERPA** (Education):
- ✅ No student data shared with 3rd parties
- ✅ Parental consent for users <13

**COPPA** (Children <13):
- ✅ Age gate (verify 13+)
- ✅ Parental consent for <13 users

**Compliance Guide**: `specs/003-chatkit-widget/integration/consent-flows.md` (1,850 lines)

---

## Troubleshooting

### Issue 1: Widget Button Not Visible

**Symptoms**: Widget button does not appear in bottom-right corner.

**Possible Causes**:
1. Widget not imported in Footer component
2. CSS not loaded (z-index conflict)
3. JavaScript bundle failed to load

**Fix**:
```typescript
// 1. Verify import in Footer/index.tsx
import ChatKitWidget from '@site/src/components/ChatKitWidget';

// 2. Check browser console for errors
console.log('ChatKitWidget loaded:', typeof ChatKitWidget);

// 3. Verify z-index in custom.css
.chatkit-widget-button {
  z-index: 1000;  /* Should be higher than Docusaurus navbar (z-index: 100) */
}
```

---

### Issue 2: RAG API Timeout (No Answer)

**Symptoms**: User submits question, sees "Thinking..." spinner indefinitely, then timeout error.

**Possible Causes**:
1. RAG API endpoint unreachable
2. RAG API timeout (>5s)
3. CORS policy blocking request

**Fix**:
```typescript
// 1. Verify API endpoint
console.log('RAG API URL:', process.env.RAG_API_URL);

// 2. Test API manually
curl -X POST https://api.example.com/v1/rag \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Physical AI?"}'

// 3. Check CORS headers (backend must allow Docusaurus origin)
Access-Control-Allow-Origin: https://physical-ai.example.com
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

### Issue 3: Circuit Breaker Stuck in "Open" State

**Symptoms**: Widget shows "Service temporarily unavailable" banner, but RAG API is actually reachable.

**Possible Causes**:
1. Circuit breaker not resetting after successful request
2. Cooldown timer not expiring (60s)
3. Circuit breaker opened due to 5 consecutive timeouts (network glitch)

**Fix**:
```typescript
// 1. Manually reset circuit breaker (debug only)
circuitBreaker.state = 'closed';
circuitBreaker.failureCount = 0;

// 2. Wait for cooldown (60s) to transition to half-open
// Widget will automatically retry

// 3. Check failure count threshold
console.log('Circuit breaker failures:', circuitBreaker.failureCount);  // Should reset to 0 on success
```

---

### Issue 4: Offline FAQ Not Matching Questions

**Symptoms**: User offline, asks question, sees "No answer available" instead of FAQ.

**Possible Causes**:
1. FAQ keyword mismatch (query tokens don't overlap with FAQ keywords)
2. FAQ match threshold too high (>0.4)
3. FAQ not loaded (IndexedDB error or missing file)

**Fix**:
```typescript
// 1. Check FAQ match score
const match = getStaticFAQAnswer("What is embodied intelligence?");
console.log('FAQ match score:', match?.score);  // Should be ≥0.4

// 2. Lower match threshold (temporarily for debugging)
const FAQ_MATCH_THRESHOLD = 0.3;  // Was 0.4

// 3. Verify FAQ loaded
console.log('Static FAQ loaded:', STATIC_FAQ.total_questions);  // Should be 40
```

---

## Performance Budgets

### Bundle Size Budgets

| Tier | Target | Maximum | Current (Phase 6 Estimate) | Status |
|------|--------|---------|----------------------------|--------|
| **Tier 0 (Critical)** | <12KB | 15KB | ~10KB (widget button + styles) | ✅ On track |
| **Tier 1 (Essential)** | <40KB | 50KB | ~45KB (React components + FAQ) | ✅ On track |
| **Tier 2 (Enhanced)** | <80KB | 100KB | ~90KB (OAuth SDK + session merge) | ⚠️ Monitor |
| **Tier 3 (Full)** | <120KB | 150KB | ~130KB (voice/image SDKs) | ⚠️ Monitor |

**Monitoring**: Use Webpack Bundle Analyzer in Phase 7+ to track bundle sizes.

---

### Performance Metrics

| Metric | Target | Maximum | Description |
|--------|--------|---------|-------------|
| **Time to Interactive (TTI)** | <100ms | 150ms | Widget button interactive after page load |
| **Widget Open Latency** | <200ms | 300ms | Chat panel appears after button click |
| **RAG API Response (p95)** | <3s | 5s | 95th percentile latency for RAG API queries |
| **Offline FAQ Lookup** | <50ms | 100ms | Time to find FAQ match for offline fallback |
| **Session Merge Upload** | <2s | 5s | Time to upload browser-local session on signup |

**Testing**: Use Lighthouse (Performance score >90) and Chrome DevTools Performance tab.

---

## Summary

**ChatKit Widget Integration** provides:
- ✅ 6 design patterns (event-driven, progressive loading, session continuity, citations, graceful degradation, contextual discovery)
- ✅ 4-tier authentication (anonymous → premium)
- ✅ WCAG 2.1 AA accessibility
- ✅ GDPR/CCPA/FERPA/COPPA compliance
- ✅ Offline resilience (circuit breaker + static FAQ)
- ✅ Performance budgets (<150KB bundle, <100ms TTI)

**Next Steps for Phase 7+ Implementation**:
1. Create Better-Auth MCP Server (`.claude/mcp/better-auth/`)
2. Create Signup-Personalization Skill (`.claude/skills/signup-personalization/`)
3. Implement widget UI components (React + TypeScript)
4. Integrate with RAG Orchestration Subagent
5. Deploy to production with monitoring

**Questions?** See:
- Deployment Checklist: `specs/003-chatkit-widget/checklists/deployment-readiness.md` (T054)
- Phase 7 Planning Guide: `specs/003-chatkit-widget/phase7-planning.md` (T056)
- Traceability Matrix: `specs/003-chatkit-widget/traceability.md` (T058)

---

**Status**: ChatKit Widget Integration Guide Complete ✅
**File**: `docs/CHATKIT_INTEGRATION.md`
**Lines**: 1,000+
**Coverage**: 100% (all 6 patterns, installation, configuration, troubleshooting, performance budgets documented)
