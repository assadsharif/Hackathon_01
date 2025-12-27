# Feature Specification: ChatKit Widget - Cross-Platform Chat Interface

**Feature Branch**: `003-chatkit-widget-integration`
**Created**: 2025-12-26
**Status**: Design Specification (Phase 6)
**Input**: User description: "Design a reusable, privacy-first chat widget for documentation platforms that integrates RAG chatbot, signup/personalization, and multi-modal interactions following Spec-Driven Development principles"

---

## Executive Summary

The **ChatKit Widget** is a cross-platform, embeddable chat interface designed for educational documentation sites. It provides a unified interaction layer for:
- Document-grounded Q&A (RAG chatbot integration)
- User authentication and personalization flows
- Future multi-modal interactions (voice, image, collaborative features)

**Design Principle**: Event-driven, privacy-first, framework-agnostic architecture ensuring compliance with GDPR, CCPA, FERPA, and COPPA regulations.

**Key Design Intelligence References**:
- Design Patterns: `.claude/skills/chatkit-widget/patterns.md` (6 reusable patterns)
- Integration Contracts: `.claude/skills/chatkit-widget/SKILL.md` (event schemas, state machine)
- Validation Intelligence: `.claude/mcp/chatkit/` (compliance & schema validation)

---

## User Personas

### Persona 1: Anonymous Learner (Tier 0)
- **Profile**: Student exploring Physical AI concepts without creating an account
- **Goals**: Quick answers to documentation questions, frictionless learning
- **Constraints**: Privacy-conscious, unwilling to share personal data
- **Needs**: Zero-friction access, browser-local session persistence, no mandatory signup

### Persona 2: Registered Learner (Tier 1-2)
- **Profile**: Engaged student who creates an account for personalized learning
- **Goals**: Track progress, bookmark content, export conversation history
- **Constraints**: Mobile-first usage, intermittent connectivity
- **Needs**: Cross-device session sync, offline mode, accessible UI

### Persona 3: Instructor/Course Creator (Tier 3)
- **Profile**: Educator using the platform to teach robotics concepts
- **Goals**: Understand student engagement, identify knowledge gaps
- **Constraints**: Limited technical expertise, requires analytics dashboards
- **Needs**: Query analytics, content effectiveness metrics, privacy-compliant data export

### Persona 4: Accessibility-Focused User
- **Profile**: User relying on assistive technologies (screen readers, keyboard-only navigation)
- **Goals**: Full access to chat functionality without mouse/touch input
- **Constraints**: Visual impairment or motor disabilities
- **Needs**: ARIA labels, keyboard shortcuts, high-contrast themes

---

## User Scenarios & Testing

### User Story 1 - Frictionless Q&A for Anonymous Users (Priority: P1)

**Description**: An anonymous student visiting the Physical AI documentation wants to ask "What is embodied intelligence?" without creating an account or providing personal information.

**Why this priority**: Core value proposition - immediate access to knowledge without barriers. 90% of users start as anonymous learners.

**Independent Test**: Can be fully tested by loading the documentation site, clicking the chat widget, asking a question, and receiving a grounded answer with citations - all without any signup prompt.

**Acceptance Scenarios**:

1. **Given** a user visits `/docs/module-2-embodied/embodied-intelligence` for the first time
   **When** they click the floating chat button in the bottom-right corner
   **Then** the chat panel opens without requiring login or email

2. **Given** the chat panel is open
   **When** the user types "What is embodied intelligence?" and presses Enter
   **Then** they receive an answer grounded in the book content within 3 seconds

3. **Given** a chat response with citations
   **When** the user clicks on a citation number (e.g., [1])
   **Then** they navigate to the exact section in the documentation

4. **Given** an anonymous user has a 10-message conversation
   **When** they refresh the page or close and reopen the browser
   **Then** their conversation history persists in the chat panel (browser-local storage)

5. **Given** an anonymous user on a mobile device (375px width)
   **When** they open the chat panel
   **Then** the panel occupies 100% of the viewport width and is fully usable

---

### User Story 2 - Dual-Mode Retrieval (Full-Corpus vs. Selected-Text) (Priority: P1)

**Description**: A learner studying a specific section wants to ask questions constrained to that section's content (selected-text mode) rather than the entire book (full-corpus mode).

**Why this priority**: Differentiated feature from generic chatbots. Reduces hallucination risk and improves answer precision for focused study.

**Independent Test**: Select text on any documentation page, right-click to trigger "Ask about this selection" context menu, submit a question, and verify the answer references only the selected content.

**Acceptance Scenarios**:

1. **Given** a user is reading the "Perception Systems" chapter
   **When** they select 3 paragraphs about vision sensors and click "Ask about selection"
   **Then** the chat widget opens in "selected-text mode" with the selection highlighted

2. **Given** the chat is in "selected-text mode"
   **When** the user asks "What sensors are mentioned here?"
   **Then** the answer references only the selected text, not the entire book

3. **Given** the chat is in "selected-text mode"
   **When** the user clicks "Switch to full-corpus mode"
   **Then** subsequent questions use the entire documentation as context

4. **Given** a user submits a question in "full-corpus mode"
   **When** the answer includes citations from multiple modules
   **Then** each citation displays the module name and chapter title

---

### User Story 3 - Progressive Signup with Session Continuity (Priority: P2)

**Description**: An anonymous user who has been chatting for 10 minutes decides to create an account to save their conversation history and access advanced features.

**Why this priority**: Conversion path from anonymous to registered users. Tier upgrades unlock personalization without disrupting the user experience.

**Independent Test**: Use the widget anonymously for 5 messages, click "Save Progress" in the chat UI, complete email signup, and verify the conversation history is preserved server-side.

**Acceptance Scenarios**:

1. **Given** an anonymous user has a 10-message conversation (stored browser-local)
   **When** they click "Sign up to save progress" in the chat panel
   **Then** a signup modal appears without closing the chat or losing context

2. **Given** the user completes email verification
   **When** they return to the chat panel
   **Then** their previous conversation is synced to the server and accessible on other devices

3. **Given** a Tier 1 (lightweight signup) user
   **When** they request "Export my conversation history"
   **Then** they receive a downloadable JSON or Markdown file of all messages

4. **Given** a user signs in with OAuth (Google, GitHub, Microsoft)
   **When** OAuth completes successfully
   **Then** they are upgraded to Tier 2 (full profile) without re-entering information

5. **Given** a Tier 0 (anonymous) user asks more than 10 questions in 10 minutes
   **When** rate limiting triggers
   **Then** they see a non-intrusive prompt: "Create a free account for unlimited questions"

---

### User Story 4 - Accessibility & Keyboard Navigation (Priority: P2)

**Description**: A user relying on screen readers and keyboard-only navigation wants to use the chat widget to ask questions about robotics concepts.

**Why this priority**: Legal requirement (WCAG 2.1 AA, Section 508) and ethical imperative. 15-20% of users may rely on assistive technologies.

**Independent Test**: Disable mouse input, use Tab/Shift+Tab to navigate to chat widget, use Enter to open panel, type a question using keyboard only, and verify screen reader announces all state changes.

**Acceptance Scenarios**:

1. **Given** a user with keyboard-only navigation
   **When** they press Tab repeatedly from page load
   **Then** the floating chat button receives focus with a visible outline

2. **Given** the chat button is focused
   **When** the user presses Enter or Space
   **Then** the chat panel opens and focus moves to the text input field

3. **Given** a screen reader is active
   **When** a new message arrives from the chatbot
   **Then** the screen reader announces "New message from assistant: [content preview]"

4. **Given** the user submits a question
   **When** the chatbot is processing the query
   **Then** the screen reader announces "Loading response" with an ARIA live region

5. **Given** the user navigates citations with keyboard
   **When** they press Tab to focus a citation link and press Enter
   **Then** the page scrolls to the cited section with focus management

---

### User Story 5 - Offline & Degraded Mode Handling (Priority: P3)

**Description**: A user with intermittent internet connectivity (e.g., on a train) wants to continue interacting with the chat widget even when the RAG API is unreachable.

**Why this priority**: Resilience requirement. Mobile users frequently experience network issues. Graceful degradation improves perceived reliability.

**Independent Test**: Load the documentation site, open the chat widget, disconnect network, submit a question, and verify the widget displays a helpful fallback message (e.g., "Offline mode: Showing FAQ answers").

**Acceptance Scenarios**:

1. **Given** a user has an active internet connection
   **When** they submit a question and the RAG API responds within 5 seconds
   **Then** the full RAG-generated answer appears with citations

2. **Given** the RAG API is unreachable (timeout after 5 seconds)
   **When** the user submits a question
   **Then** the widget falls back to a static FAQ index and displays: "Network unavailable. Showing cached answers."

3. **Given** the widget is in offline mode
   **When** the user asks "What is embodied intelligence?"
   **Then** a pre-cached answer from the FAQ appears with a disclaimer: "⚠ Offline mode: Limited to cached content"

4. **Given** the network connection is restored
   **When** the user submits a new question
   **Then** the widget automatically resumes using the RAG API without manual refresh

5. **Given** the widget encounters 3 consecutive API failures
   **When** the circuit breaker opens
   **Then** all queries use the fallback FAQ for 60 seconds before retrying the API

---

### User Story 6 - Multi-Modal Input (Voice & Image) - FUTURE (Priority: P4)

**Description**: A learner wants to ask a question using voice input or upload an image of a robot diagram for analysis.

**Why this priority**: Phase 7+ feature. Deferred until core text-based interactions are stable.

**Independent Test**: Click the microphone icon in the chat input, speak "What is a humanoid robot?", and verify the transcribed text appears in the input field.

**Acceptance Scenarios**:

1. **Given** a user clicks the voice input button
   **When** they speak into the microphone
   **Then** the speech is transcribed to text in the chat input field

2. **Given** a user uploads an image of a robot diagram
   **When** they submit the query "What is this component?"
   **Then** the vision model analyzes the image and provides a grounded answer

---

### Edge Cases

1. **What happens when a user has 1000+ messages in their conversation history?**
   - Widget paginates history (load latest 50 messages by default)
   - Infinite scroll loads older messages on demand
   - Search functionality allows filtering by keywords

2. **How does the system handle concurrent sessions across devices?**
   - Server-side session merges messages by timestamp
   - Conflict resolution: Last-write-wins with tombstone markers
   - User receives notification: "Conversation updated on another device"

3. **What happens when citations point to deleted or moved documentation pages?**
   - Widget displays: "⚠ Citation unavailable (content moved)"
   - Stable-ID system maintains fallback links to archived versions
   - Analytics log broken citation events for content team review

4. **How does the widget handle languages other than English?**
   - Out of scope for Phase 6 (English-only)
   - Phase 8+ internationalization: Widget UI translatable, RAG model supports multilingual corpus

5. **What happens when a user blocks cookies or disables localStorage?**
   - Widget displays warning: "Session persistence disabled. Enable cookies to save conversations."
   - Ephemeral mode: Conversations lost on page refresh
   - Server-side sessions still work for authenticated users

6. **How does the widget handle malicious input (XSS, injection attacks)?**
   - Input sanitization layer escapes HTML entities
   - Content Security Policy (CSP) headers prevent script injection
   - Rate limiting prevents automated abuse (10 messages/min for anonymous, 30 for authenticated)

---

## Requirements

### Functional Requirements

#### Core Chat Interaction

- **FR-001**: Widget MUST render as a floating action button (FAB) in the bottom-right corner of documentation pages
- **FR-002**: Widget MUST open a chat panel on click, occupying 30% viewport width (desktop) or 100% width (mobile <768px)
- **FR-003**: Widget MUST support text input with a maximum of 500 characters per message
- **FR-004**: Widget MUST display conversation history in chronological order (newest at bottom)
- **FR-005**: Widget MUST persist anonymous user sessions in browser localStorage for 30 days

#### RAG Integration

- **FR-006**: Widget MUST integrate with RAG Orchestration Subagent (event-driven API)
- **FR-007**: Widget MUST support "full-corpus" mode (query entire documentation)
- **FR-008**: Widget MUST support "selected-text" mode (query constrained to user-selected content)
- **FR-009**: Widget MUST display citations as inline superscript numbers (e.g., [1], [2])
- **FR-010**: Widget MUST render citation links that navigate to the exact documentation section
- **FR-011**: Widget MUST enforce content boundary guardrails (no off-topic responses)

#### Progressive Signup & Authentication

- **FR-012**: Widget MUST allow anonymous usage (Tier 0) without prompting for signup
- **FR-013**: Widget MUST provide "Save Progress" button after 10 messages (Tier 0 → Tier 1 upgrade)
- **FR-014**: Widget MUST support email/password signup (Tier 1: lightweight signup)
- **FR-015**: Widget MUST support OAuth authentication (Google, GitHub, Microsoft) for Tier 2 (full profile)
- **FR-016**: Widget MUST merge browser-local sessions with server-side sessions on Tier upgrade
- **FR-017**: Widget MUST display user tier badge (Anonymous, Member, Premium) in chat header

#### Privacy & Compliance

- **FR-018**: Widget MUST NOT collect personal data for anonymous users (Tier 0)
- **FR-019**: Widget MUST display cookie consent banner on first visit (GDPR compliance)
- **FR-020**: Widget MUST provide "Export Data" button for authenticated users (GDPR Article 20)
- **FR-021**: Widget MUST provide "Delete Account" button with 30-day retention policy (GDPR Article 17)
- **FR-022**: Widget MUST enforce age gate (13+ years) per COPPA regulations
- **FR-023**: Widget MUST encrypt session tokens with HttpOnly, Secure, SameSite=Strict cookies

#### Accessibility

- **FR-024**: Widget MUST be fully navigable via keyboard (Tab, Shift+Tab, Enter, Escape)
- **FR-025**: Widget MUST provide ARIA labels for all interactive elements
- **FR-026**: Widget MUST announce state changes to screen readers via ARIA live regions
- **FR-027**: Widget MUST support high-contrast mode and respect `prefers-reduced-motion`
- **FR-028**: Widget MUST have a minimum touch target size of 44x44px (WCAG 2.1 AA)

#### Performance & Resilience

- **FR-029**: Widget MUST load core UI (Tier 0 essential features) in ≤100ms
- **FR-030**: Widget MUST lazy-load advanced features (Tier 1-3) on demand
- **FR-031**: Widget MUST display "Typing..." indicator within 200ms of user input
- **FR-032**: Widget MUST timeout RAG API requests after 10 seconds
- **FR-033**: Widget MUST implement circuit breaker pattern (3 failures → 60s cooldown)
- **FR-034**: Widget MUST cache static FAQ answers for offline fallback

#### State Management

- **FR-035**: Widget MUST implement 6-state state machine (Idle, Typing, Processing, Responding, Error, SignupFlow)
- **FR-036**: Widget MUST prevent invalid state transitions (e.g., Typing → Responding without Processing)
- **FR-037**: Widget MUST emit standardized events (user_message, agent_response, system_message, error, signup_initiated)

#### Analytics & Telemetry (Privacy-Compliant)

- **FR-038**: Widget MUST log query analytics (anonymized session_id, response_latency_ms, retrieval_count)
- **FR-039**: Widget MUST NOT log message content for anonymous users
- **FR-040**: Widget MUST aggregate error rates (timeout, network, validation) for monitoring

---

### Non-Functional Requirements

#### Performance

- **NFR-001**: Widget bundle size MUST NOT exceed 15 KB (Tier 0 essential), 175 KB (Tier 3 premium) with gzip compression
- **NFR-002**: Time to Interactive (TTI) MUST be ≤100ms for initial widget load
- **NFR-003**: RAG API response time MUST be ≤3 seconds (p95 latency)
- **NFR-004**: Widget MUST render 1000-message conversation history without UI lag

#### Accessibility (WCAG 2.1 AA)

- **NFR-005**: Widget MUST achieve 100% keyboard navigation coverage
- **NFR-006**: Widget MUST have color contrast ratio ≥4.5:1 for normal text, ≥3:1 for large text
- **NFR-007**: Widget MUST support screen readers (NVDA, JAWS, VoiceOver, TalkBack)
- **NFR-008**: Widget MUST be fully usable at 200% zoom (up to 400% zoom)

#### Security

- **NFR-009**: Widget MUST sanitize all user input to prevent XSS attacks
- **NFR-010**: Widget MUST implement CSRF protection via SameSite cookies
- **NFR-011**: Widget MUST use HTTPS for all API requests
- **NFR-012**: Widget MUST enforce rate limiting (10 messages/min anonymous, 30 messages/min authenticated)

#### Privacy

- **NFR-013**: Widget MUST NOT use third-party analytics or tracking pixels
- **NFR-014**: Widget MUST store anonymous sessions in browser localStorage only (no server upload)
- **NFR-015**: Widget MUST delete user data within 30 days of account deletion request

#### Cross-Browser Compatibility

- **NFR-016**: Widget MUST support Chrome, Firefox, Safari, Edge (last 2 major versions)
- **NFR-017**: Widget MUST support iOS Safari, Chrome Mobile, Samsung Internet

#### Responsive Design

- **NFR-018**: Widget MUST be fully functional on screens ≥375px width
- **NFR-019**: Widget MUST adapt layout for portrait and landscape orientations

---

### Key Entities

**Note**: These entities define conceptual data structures, not implementation schemas.

#### ChatMessage
- **Represents**: A single message in a conversation
- **Key Attributes**: Unique ID, type (user/agent/system), content, timestamp, citations[]
- **Relationships**: Belongs to ConversationSession

#### ConversationSession
- **Represents**: A persistent chat session (browser-local or server-synced)
- **Key Attributes**: Session ID (UUID), user tier (anonymous/lightweight/full/premium), messages[], created_at, last_active_at
- **Relationships**: Has many ChatMessages

#### Citation
- **Represents**: A reference to documentation content
- **Key Attributes**: Stable ID, module_id, chapter_id, section_id, URL, excerpt (50 chars)
- **Relationships**: Linked to ChatMessage (one message can have multiple citations)

#### UserProfile (Tier 1+)
- **Represents**: Authenticated user account
- **Key Attributes**: User ID, email, tier level, OAuth providers[], bookmarks[], preferences
- **Relationships**: Has one ConversationSession (server-synced)

#### WidgetState
- **Represents**: Current operational state of the widget
- **Key Attributes**: Current state (Idle/Typing/Processing/Responding/Error/SignupFlow), last event, timestamp
- **Relationships**: State machine transitions defined in `.claude/mcp/chatkit/mcp.json`

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: 90% of anonymous users successfully submit their first question within 30 seconds of opening the widget
- **SC-002**: Widget achieves ≤3 seconds p95 response latency for RAG queries (measured server-side)
- **SC-003**: Widget maintains 99.5% uptime (excluding planned maintenance)
- **SC-004**: Zero XSS, CSRF, or injection vulnerabilities in security audit
- **SC-005**: Widget achieves WCAG 2.1 AA compliance (validated by automated + manual accessibility testing)
- **SC-006**: 80% of users who ask 10+ questions upgrade to Tier 1 (lightweight signup) within 7 days
- **SC-007**: Widget bundle size remains ≤15 KB for Tier 0 essential features (measured with gzip compression)
- **SC-008**: Circuit breaker prevents cascading failures (99.9% of timeout events trigger degraded mode within 5 seconds)
- **SC-009**: Widget renders correctly on all supported browsers (Chrome, Firefox, Safari, Edge) without visual regressions
- **SC-010**: 95% of users report "Easy" or "Very Easy" usability rating in post-interaction survey

---

## Out of Scope (Phase 6)

**Explicitly NOT included in this design specification**:

1. **Multi-Language Support**: Widget UI and RAG model are English-only. Internationalization deferred to Phase 8.

2. **Voice & Image Input**: Multi-modal interactions (speech-to-text, vision model analysis) deferred to Phase 7+.

3. **Collaborative Chat**: Multi-user conversations, shared sessions, or instructor-student interactions deferred to Phase 8.

4. **Spaced Repetition**: Learning reinforcement prompts based on forgetting curves deferred to Phase 9.

5. **Code Execution**: Sandboxed Python/JavaScript REPL for interactive coding exercises deferred to Phase 8.

6. **Advanced Analytics Dashboards**: Instructor-facing analytics with student engagement metrics deferred to Phase 7.

7. **Custom Theming API**: Programmatic theme customization beyond dark/light mode deferred to Phase 7.

8. **Push Notifications**: Browser push notifications for conversation updates deferred to Phase 8.

9. **Third-Party Integrations**: Slack, Discord, or Microsoft Teams integrations deferred to Phase 9.

10. **Runtime Implementation**: This specification defines WHAT the widget should accomplish, not HOW it is implemented. Implementation details are intentionally excluded to maintain technology-agnostic design.

---

## Design Intelligence References

This specification is supported by the following design artifacts:

1. **Design Patterns**: `.claude/skills/chatkit-widget/patterns.md`
   - Event-Driven Widget Architecture
   - Progressive Widget Loading (4-tier code-splitting)
   - Session Continuity with Tier Upgrades
   - Citation-Aware Message Rendering
   - Graceful Degradation for Network Failures
   - Contextual Feature Discovery

2. **Integration Contracts**: `.claude/skills/chatkit-widget/SKILL.md`
   - Event schema definitions (JSON examples)
   - State machine transitions
   - Widget configuration contracts
   - Security & compliance guidelines

3. **Validation Intelligence**: `.claude/mcp/chatkit/`
   - JSON Schema validation rules
   - State transition validation
   - Compliance checklist (GDPR, CCPA, FERPA, COPPA)
   - Performance budget tracking

---

## Assumptions & Constraints

### Assumptions

1. **RAG API Availability**: RAG Orchestration Subagent (Phase 2-4) is operational and reachable via HTTP/HTTPS
2. **Better-Auth MCP Integration**: OAuth providers (Google, GitHub, Microsoft) are configured and functional
3. **Browser Capabilities**: Target browsers support ES2020, LocalStorage, WebSockets (for future features)
4. **Documentation Stability**: Stable-ID citation system is implemented and maintained in documentation
5. **Analytics Infrastructure**: Server-side analytics aggregation is available for query metrics

### Constraints

1. **Phase 1 Constitution Compliance**: Widget must NOT interfere with static documentation site (Docusaurus defaults)
2. **No Backend in Phase 6**: This is a design-only specification. No runtime widget implementation or backend services are created in Phase 6.
3. **Mobile-First Design**: Widget MUST work on screens as small as 375px width (iPhone SE)
4. **Privacy-First Data Handling**: Anonymous user data (Tier 0) MUST remain browser-local (no server upload)
5. **Framework-Agnostic**: Design must not assume React, Vue, Svelte, or any specific frontend framework

---

## Risks & Mitigation

### High-Priority Risks

1. **Risk**: Widget performance degrades with 1000+ message conversations
   - **Mitigation**: Implement pagination (load latest 50 messages by default) and virtual scrolling for long histories

2. **Risk**: RAG API timeout or unavailability causes widget to become unusable
   - **Mitigation**: Circuit breaker pattern + static FAQ fallback ensures degraded mode functionality

3. **Risk**: Privacy compliance gaps (GDPR, COPPA) expose legal liability
   - **Mitigation**: MCP validation server (`.claude/mcp/chatkit/`) enforces compliance rules during design phase

4. **Risk**: Accessibility violations prevent users with disabilities from using the widget
   - **Mitigation**: WCAG 2.1 AA checklist (FR-024 through FR-028) + manual accessibility testing with screen readers

5. **Risk**: Widget bundle size exceeds 15 KB (Tier 0 essential), slowing page load
   - **Mitigation**: Progressive loading (4-tier code-splitting) + performance budgets tracked by MCP server

---

## Traceability Matrix

| User Story | Functional Requirements | Success Criteria |
|------------|-------------------------|------------------|
| US-1 (Frictionless Q&A) | FR-001, FR-002, FR-005, FR-006, FR-009 | SC-001, SC-002, SC-009 |
| US-2 (Dual-Mode Retrieval) | FR-007, FR-008, FR-010, FR-011 | SC-002, SC-010 |
| US-3 (Progressive Signup) | FR-012, FR-013, FR-014, FR-015, FR-016 | SC-006, SC-010 |
| US-4 (Accessibility) | FR-024, FR-025, FR-026, FR-027, FR-028 | SC-005, SC-009 |
| US-5 (Offline Mode) | FR-032, FR-033, FR-034 | SC-003, SC-008 |

---

## Next Steps

After this specification is approved:

1. **Create Implementation Plan** (`specs/003-chatkit-widget/plan.md`)
   - Architecture decisions (event bus, state management, API client)
   - Integration points with RAG Orchestration, Better-Auth, Signup-Personalization
   - Performance optimization strategy (code-splitting, lazy loading)

2. **Generate Testable Tasks** (`specs/003-chatkit-widget/tasks.md`)
   - Atomic, independently testable tasks with acceptance criteria
   - Dependency graph (prerequisite tasks)
   - Estimated complexity (S/M/L/XL)

3. **Review Design Artifacts** (`.claude/skills/chatkit-widget/`, `.claude/mcp/chatkit/`)
   - Validate patterns align with specification
   - Refine Pattern 2 (Progressive Loading) pseudocode per SDD review findings
   - Ensure MCP validation rules cover all functional requirements

4. **Phase 7 Implementation Planning** (FUTURE)
   - Runtime widget implementation (framework selection)
   - Backend API integration (RAG, Auth, Analytics)
   - End-to-end testing strategy

---

**Specification Version**: 1.0.0
**Last Updated**: 2025-12-26
**Authors**: SDD Compliance Team
**Reviewers**: [Pending]
