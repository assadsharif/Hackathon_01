# ChatKit Widget - Functional Requirements Checklist

**Feature**: ChatKit Widget - Cross-Platform Chat Interface
**Specification**: `specs/003-chatkit-widget/spec.md`
**Status**: Design Specification (Phase 6)
**Last Updated**: 2025-12-26

---

## Core Chat Interaction (FR-001 to FR-005)

- [ ] **FR-001**: Widget renders as floating action button (FAB) in bottom-right corner
- [ ] **FR-002**: Widget opens chat panel on click (30% width desktop, 100% width mobile <768px)
- [ ] **FR-003**: Widget supports text input with max 500 characters per message
- [ ] **FR-004**: Widget displays conversation history in chronological order (newest at bottom)
- [ ] **FR-005**: Widget persists anonymous user sessions in browser localStorage for 30 days

**Acceptance Test**: Load documentation site, click FAB, type 500-character message, refresh page, verify history persists.

---

## RAG Integration (FR-006 to FR-011)

- [ ] **FR-006**: Widget integrates with RAG Orchestration Subagent (event-driven API)
- [ ] **FR-007**: Widget supports "full-corpus" mode (query entire documentation)
- [ ] **FR-008**: Widget supports "selected-text" mode (query constrained to selected content)
- [ ] **FR-009**: Widget displays citations as inline superscript numbers (e.g., [1], [2])
- [ ] **FR-010**: Widget renders citation links that navigate to exact documentation section
- [ ] **FR-011**: Widget enforces content boundary guardrails (no off-topic responses)

**Acceptance Test**: Ask "What is embodied intelligence?" in full-corpus mode, verify citations appear, click citation [1], verify navigation to correct section.

---

## Progressive Signup & Authentication (FR-012 to FR-017)

- [ ] **FR-012**: Widget allows anonymous usage (Tier 0) without prompting for signup
- [ ] **FR-013**: Widget provides "Save Progress" button after 10 messages (Tier 0 → Tier 1 upgrade)
- [ ] **FR-014**: Widget supports email/password signup (Tier 1: lightweight signup)
- [ ] **FR-015**: Widget supports OAuth authentication (Google, GitHub, Microsoft) for Tier 2
- [ ] **FR-016**: Widget merges browser-local sessions with server-side sessions on Tier upgrade
- [ ] **FR-017**: Widget displays user tier badge (Anonymous, Member, Premium) in chat header

**Acceptance Test**: Use widget anonymously for 10 messages, click "Save Progress", complete email signup, verify conversation history synced to server.

---

## Privacy & Compliance (FR-018 to FR-023)

- [ ] **FR-018**: Widget does NOT collect personal data for anonymous users (Tier 0)
- [ ] **FR-019**: Widget displays cookie consent banner on first visit (GDPR compliance)
- [ ] **FR-020**: Widget provides "Export Data" button for authenticated users (GDPR Article 20)
- [ ] **FR-021**: Widget provides "Delete Account" button with 30-day retention policy (GDPR Article 17)
- [ ] **FR-022**: Widget enforces age gate (13+ years) per COPPA regulations
- [ ] **FR-023**: Widget encrypts session tokens with HttpOnly, Secure, SameSite=Strict cookies

**Acceptance Test**: Use widget anonymously, verify no data sent to server. Create account, click "Export Data", verify JSON download. Click "Delete Account", verify 30-day deletion notice.

---

## Accessibility (FR-024 to FR-028)

- [ ] **FR-024**: Widget is fully navigable via keyboard (Tab, Shift+Tab, Enter, Escape)
- [ ] **FR-025**: Widget provides ARIA labels for all interactive elements
- [ ] **FR-026**: Widget announces state changes to screen readers via ARIA live regions
- [ ] **FR-027**: Widget supports high-contrast mode and respects `prefers-reduced-motion`
- [ ] **FR-028**: Widget has minimum touch target size of 44x44px (WCAG 2.1 AA)

**Acceptance Test**: Disable mouse, use Tab to navigate to FAB, press Enter to open panel, type question, verify screen reader announces "New message from assistant".

---

## Performance & Resilience (FR-029 to FR-034)

- [ ] **FR-029**: Widget loads core UI (Tier 0 essential features) in ≤100ms
- [ ] **FR-030**: Widget lazy-loads advanced features (Tier 1-3) on demand
- [ ] **FR-031**: Widget displays "Typing..." indicator within 200ms of user input
- [ ] **FR-032**: Widget timeouts RAG API requests after 10 seconds
- [ ] **FR-033**: Widget implements circuit breaker pattern (3 failures → 60s cooldown)
- [ ] **FR-034**: Widget caches static FAQ answers for offline fallback

**Acceptance Test**: Load page, measure Time to Interactive (TTI) for widget ≤100ms. Disconnect network, submit question, verify offline fallback message appears.

---

## State Management (FR-035 to FR-037)

- [ ] **FR-035**: Widget implements 6-state state machine (Idle, Typing, Processing, Responding, Error, SignupFlow)
- [ ] **FR-036**: Widget prevents invalid state transitions (e.g., Typing → Responding without Processing)
- [ ] **FR-037**: Widget emits standardized events (user_message, agent_response, system_message, error, signup_initiated)

**Acceptance Test**: Open browser DevTools, monitor widget events, submit question, verify state transitions: Idle → Typing → Processing → Responding → Idle.

---

## Analytics & Telemetry (FR-038 to FR-040)

- [ ] **FR-038**: Widget logs query analytics (anonymized session_id, response_latency_ms, retrieval_count)
- [ ] **FR-039**: Widget does NOT log message content for anonymous users
- [ ] **FR-040**: Widget aggregates error rates (timeout, network, validation) for monitoring

**Acceptance Test**: Use widget anonymously, inspect network requests, verify no message content sent to analytics endpoint.

---

## Non-Functional Requirements Checklist

### Performance (NFR-001 to NFR-004)

- [ ] **NFR-001**: Widget bundle size ≤15 KB (Tier 0), ≤175 KB (Tier 3) with gzip
- [ ] **NFR-002**: Time to Interactive (TTI) ≤100ms for initial widget load
- [ ] **NFR-003**: RAG API response time ≤3 seconds (p95 latency)
- [ ] **NFR-004**: Widget renders 1000-message conversation history without UI lag

**Acceptance Test**: Run Lighthouse audit, verify bundle size and TTI metrics. Load 1000-message history, scroll to bottom, verify no lag.

---

### Accessibility (NFR-005 to NFR-008)

- [ ] **NFR-005**: Widget achieves 100% keyboard navigation coverage
- [ ] **NFR-006**: Widget has color contrast ratio ≥4.5:1 (normal text), ≥3:1 (large text)
- [ ] **NFR-007**: Widget supports screen readers (NVDA, JAWS, VoiceOver, TalkBack)
- [ ] **NFR-008**: Widget is fully usable at 200% zoom (up to 400% zoom)

**Acceptance Test**: Run axe DevTools accessibility audit, verify WCAG 2.1 AA compliance. Test with NVDA screen reader on Windows.

---

### Security (NFR-009 to NFR-012)

- [ ] **NFR-009**: Widget sanitizes all user input to prevent XSS attacks
- [ ] **NFR-010**: Widget implements CSRF protection via SameSite cookies
- [ ] **NFR-011**: Widget uses HTTPS for all API requests
- [ ] **NFR-012**: Widget enforces rate limiting (10 messages/min anonymous, 30/min authenticated)

**Acceptance Test**: Attempt XSS injection in chat input (`<script>alert('XSS')</script>`), verify sanitization. Submit 11 messages in 1 minute as anonymous user, verify rate limit message.

---

### Privacy (NFR-013 to NFR-015)

- [ ] **NFR-013**: Widget does NOT use third-party analytics or tracking pixels
- [ ] **NFR-014**: Widget stores anonymous sessions in browser localStorage only (no server upload)
- [ ] **NFR-015**: Widget deletes user data within 30 days of account deletion request

**Acceptance Test**: Inspect network requests, verify no third-party domains. Use widget anonymously, verify no data sent to server.

---

### Cross-Browser Compatibility (NFR-016 to NFR-017)

- [ ] **NFR-016**: Widget supports Chrome, Firefox, Safari, Edge (last 2 major versions)
- [ ] **NFR-017**: Widget supports iOS Safari, Chrome Mobile, Samsung Internet

**Acceptance Test**: Test widget on Chrome 120, Firefox 121, Safari 17, Edge 120. Test on iPhone 14 (iOS Safari 17), Samsung Galaxy S23 (Samsung Internet).

---

### Responsive Design (NFR-018 to NFR-019)

- [ ] **NFR-018**: Widget is fully functional on screens ≥375px width
- [ ] **NFR-019**: Widget adapts layout for portrait and landscape orientations

**Acceptance Test**: Load widget on 375px viewport (iPhone SE), verify full functionality. Rotate device to landscape, verify layout adapts.

---

## Success Criteria Checklist

- [ ] **SC-001**: 90% of anonymous users submit first question within 30 seconds
- [ ] **SC-002**: Widget achieves ≤3 seconds p95 response latency for RAG queries
- [ ] **SC-003**: Widget maintains 99.5% uptime (excluding planned maintenance)
- [ ] **SC-004**: Zero XSS, CSRF, or injection vulnerabilities in security audit
- [ ] **SC-005**: Widget achieves WCAG 2.1 AA compliance (automated + manual testing)
- [ ] **SC-006**: 80% of users with 10+ questions upgrade to Tier 1 within 7 days
- [ ] **SC-007**: Widget bundle size remains ≤15 KB for Tier 0 essential features
- [ ] **SC-008**: Circuit breaker prevents cascading failures (99.9% of timeout events trigger degraded mode within 5s)
- [ ] **SC-009**: Widget renders correctly on all supported browsers without visual regressions
- [ ] **SC-010**: 95% of users report "Easy" or "Very Easy" usability rating

---

## Design Artifact Validation

### Patterns (`.claude/skills/chatkit-widget/patterns.md`)

- [ ] Pattern 1: Event-Driven Widget Architecture (event bus abstraction)
- [ ] Pattern 2: Progressive Widget Loading (4-tier code-splitting) - **FIXED: Abstract pseudocode**
- [ ] Pattern 3: Session Continuity with Tier Upgrades (browser-local → server merge)
- [ ] Pattern 4: Citation-Aware Message Rendering (superscript links)
- [ ] Pattern 5: Graceful Degradation for Network Failures (circuit breaker + FAQ fallback)
- [ ] Pattern 6: Contextual Feature Discovery (just-in-time hints)

### Integration Contracts (`.claude/skills/chatkit-widget/SKILL.md`)

- [ ] Event schema definitions (6 event types: user_message, agent_response, system_message, signup_initiated, authentication_completed, error)
- [ ] State machine transitions (6 states: Idle, Typing, Processing, Responding, Error, SignupFlow)
- [ ] Widget configuration schema (JSON)
- [ ] Security & compliance guidelines (GDPR, CCPA, FERPA, COPPA)

### MCP Server (`.claude/mcp/chatkit/mcp.json`)

- [ ] JSON Schema validation rules (all 6 event types)
- [ ] State transition validation (6 allowed states, 8 valid transitions)
- [ ] Compliance validation (GDPR consent, CCPA opt-out, FERPA age gate, COPPA parental consent)
- [ ] Performance budget tracking (bundle size targets: 15 KB → 175 KB)

---

## Phase 6 Completion Checklist

- [x] **spec.md created** - Formal specification with user scenarios, functional requirements, success criteria
- [x] **patterns.md refined** - Pattern 2 updated with abstract pseudocode (SDD compliance)
- [x] **SKILL.md verified** - Event schemas, state machine, integration contracts are design-level only
- [x] **mcp.json verified** - Design intelligence server (not runtime service)
- [ ] **plan.md created** - Architecture decisions, integration points, performance optimization strategy
- [ ] **tasks.md created** - Atomic, testable tasks with dependency graph
- [ ] **PHR created** - Prompt History Record for spec phase
- [ ] **ADR created** (if significant decisions made) - Document architectural decisions

---

## Notes

**Phase 6 Status**: Design specification complete. No runtime implementation in Phase 6.

**Phase 7 Implementation**: Runtime widget implementation, backend API integration, end-to-end testing will follow formal approval of this specification.

**SDD Compliance**: All artifacts follow Spec-Driven Development principles - technology-agnostic, traceable to requirements, decoupled from implementation details.

**Last Review**: 2025-12-26 (SDD Compliance Assessment - Score: 9.5/10)
