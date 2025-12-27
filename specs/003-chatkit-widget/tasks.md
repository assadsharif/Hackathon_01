# Tasks: ChatKit Widget - Cross-Platform Chat Interface

**Input**: Design documents from `/specs/003-chatkit-widget/`
**Prerequisites**: spec.md (user stories, requirements)
**Phase**: 6 - Design Intelligence Only (NO code implementation)

**Tests**: Not applicable - this is a design-only phase. Validation focuses on design artifact completeness and consistency.

**Organization**: Tasks are grouped by user story to enable independent design validation and documentation of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Design Artifacts**: `.claude/skills/chatkit-widget/` (patterns, integration contracts)
- **MCP Server**: `.claude/mcp/chatkit/` (validation intelligence)
- **Specification**: `specs/003-chatkit-widget/` (spec, checklists, guides)
- **Documentation**: `docs/` (integration guides, deployment checklists)

---

## Phase 1: Setup (Design Artifact Structure)

**Purpose**: Validate existing design artifact structure is complete

- [X] T001 Verify .claude/skills/chatkit-widget/ directory contains SKILL.md and patterns.md
- [X] T002 Verify .claude/mcp/chatkit/ directory contains README.md and mcp.json
- [X] T003 Verify specs/003-chatkit-widget/ directory contains spec.md and checklists/

**Checkpoint**: Design artifact structure is complete and ready for validation

---

## Phase 2: Foundational (Core Design Artifacts Validation)

**Purpose**: Validate core design artifacts that MUST be complete before user story design validation

**⚠️ CRITICAL**: All design artifacts must pass validation before user story documentation can begin

- [X] T004 Validate SKILL.md event schemas align with spec.md user stories (US1-US6)
- [X] T005 [P] Validate patterns.md contains all 6 required patterns per spec.md section "Design Intelligence References"
- [X] T006 [P] Validate mcp.json contains JSON schemas for all event types (user_message, agent_response, system_message, error, signup_initiated)
- [X] T007 Validate state machine in SKILL.md includes all 6 states (Idle, Typing, Processing, Responding, Error, SignupFlow)
- [X] T008 [P] Cross-validate privacy compliance rules in patterns.md match spec.md requirements (GDPR, CCPA, FERPA, COPPA)
- [X] T009 [P] Validate performance budgets in patterns.md align with spec.md NFR-001 through NFR-004
- [X] T010 Create cross-reference matrix in specs/003-chatkit-widget/design-validation.md mapping patterns → user stories → requirements

**Checkpoint**: All foundational design artifacts validated - user story design documentation can now begin

---

## Phase 3: User Story 1 - Frictionless Q&A Design Validation (Priority: P1) 🎯 MVP

**Goal**: Validate design artifacts fully support anonymous users asking questions without signup

**Independent Test**: Review patterns.md Pattern 1 (Event-Driven Architecture) and verify it includes event flows for anonymous user Q&A without authentication prompts

### Design Validation for US1

- [X] T011 [US1] Validate patterns.md Pattern 1 (Event-Driven Architecture) includes user_message event for anonymous users
- [X] T012 [P] [US1] Validate SKILL.md event schema for user_message includes user_tier: "anonymous" field
- [X] T013 [P] [US1] Validate state machine allows Idle → Typing → Processing → Responding without SignupFlow state
- [X] T014 [US1] Verify mcp.json includes validation rule: "session_id required for all events (anonymous = browser-generated UUID)"

### Documentation for US1

- [X] T015 [P] [US1] Create integration guide in specs/003-chatkit-widget/integration/rag-integration.md for connecting widget to RAG Orchestration Subagent
- [X] T016 [P] [US1] Create session persistence checklist in specs/003-chatkit-widget/checklists/session-persistence.md (browser-local storage, 30-day retention)
- [X] T017 [US1] Document citation rendering pattern in specs/003-chatkit-widget/integration/citation-rendering.md with stable-ID examples

**Checkpoint**: US1 design is fully documented and validated for anonymous Q&A functionality

---

## Phase 4: User Story 2 - Dual-Mode Retrieval Design Validation (Priority: P1) 🎯 MVP

**Goal**: Validate design artifacts support full-corpus vs. selected-text query modes

**Independent Test**: Review patterns.md and verify it includes mode switching logic and event payloads for both retrieval modes

### Design Validation for US2

- [X] T018 [US2] Validate patterns.md Pattern 1 includes mode field in user_message event ("full-corpus" | "selected-text")
- [X] T019 [P] [US2] Validate SKILL.md event schema for user_message includes selected_text field (nullable)
- [X] T020 [P] [US2] Validate patterns.md includes selected-text validation rules (min 50 chars, stale selection detection)
- [X] T021 [US2] Verify mcp.json includes validation rule: "mode='selected-text' requires selected_text !== null"

### Documentation for US2

- [X] T022 [P] [US2] Create mode-switching guide in specs/003-chatkit-widget/integration/mode-switching.md with state transition diagrams
- [X] T023 [P] [US2] Document text selection detection pattern in specs/003-chatkit-widget/integration/text-selection.md (browser APIs, accessibility)
- [X] T024 [US2] Create guardrails checklist in specs/003-chatkit-widget/checklists/content-boundaries.md for selected-text mode

**Checkpoint**: US2 design is fully documented and validated for dual-mode retrieval

---

## Phase 5: User Story 3 - Progressive Signup Design Validation (Priority: P2)

**Goal**: Validate design artifacts support session continuity during tier upgrades (anonymous → authenticated)

**Independent Test**: Review patterns.md Pattern 3 (Session Continuity) and verify it includes session merge logic for tier upgrades

### Design Validation for US3

- [X] T025 [US3] Validate patterns.md Pattern 3 (Session Continuity) includes tier upgrade flows (Tier 0 → 1 → 2 → 3)
- [X] T026 [P] [US3] Validate SKILL.md includes signup_initiated event schema with tier_upgrade field
- [X] T027 [P] [US3] Validate state machine includes SignupFlow state with transitions from Idle and Error states
- [X] T028 [US3] Verify patterns.md includes session merge algorithm (browser-local → server-sync)

### Documentation for US3

- [X] T029 [P] [US3] Create tier upgrade guide in specs/003-chatkit-widget/integration/tier-upgrades.md with session merge examples
- [X] T030 [P] [US3] Create Better-Auth integration checklist in specs/003-chatkit-widget/checklists/oauth-integration.md (Google, GitHub, Microsoft)
- [X] T031 [US3] Document privacy consent flows in specs/003-chatkit-widget/integration/consent-flows.md (GDPR Article 6)
- [X] T032 [P] [US3] Cross-validate signup patterns in .claude/skills/signup-personalization/patterns.md align with ChatKit widget flows

**Checkpoint**: US3 design is fully documented and validated for progressive signup with session continuity

---

## Phase 6: User Story 4 - Accessibility Design Validation (Priority: P2)

**Goal**: Validate design artifacts meet WCAG 2.1 AA compliance for keyboard navigation and screen readers

**Independent Test**: Review patterns.md and verify it includes ARIA labels, keyboard shortcuts, and focus management patterns

### Design Validation for US4

- [x] T033 [US4] Validate patterns.md includes accessibility pattern with ARIA labels for all widget states
- [x] T034 [P] [US4] Validate SKILL.md includes keyboard shortcuts specification (Tab, Shift+Tab, Enter, Escape)
- [x] T035 [P] [US4] Validate patterns.md includes screen reader announcements for state transitions (ARIA live regions)
- [x] T036 [US4] Verify patterns.md includes focus management rules (widget open → input field, citation click → cited section)

### Documentation for US4

- [x] T037 [P] [US4] Create accessibility checklist in specs/003-chatkit-widget/checklists/wcag-compliance.md (WCAG 2.1 AA criteria)
- [x] T038 [P] [US4] Document keyboard navigation flows in specs/003-chatkit-widget/integration/keyboard-navigation.md with state diagrams
- [x] T039 [US4] Create screen reader testing guide in specs/003-chatkit-widget/checklists/screen-reader-testing.md (NVDA, JAWS, VoiceOver)
- [x] T040 [P] [US4] Document high-contrast mode and prefers-reduced-motion support in specs/003-chatkit-widget/integration/theme-accessibility.md

**Checkpoint**: US4 design is fully documented and validated for accessibility compliance

---

## Phase 7: User Story 5 - Offline Mode Design Validation (Priority: P3)

**Goal**: Validate design artifacts support graceful degradation when RAG API is unreachable

**Independent Test**: Review patterns.md Pattern 5 (Graceful Degradation) and verify it includes circuit breaker and fallback FAQ logic

### Design Validation for US5

- [x] T041 [US5] Validate patterns.md Pattern 5 (Graceful Degradation) includes circuit breaker specification (3 failures → 60s cooldown)
- [x] T042 [P] [US5] Validate SKILL.md includes error event schema with network_error and timeout subtypes
- [x] T043 [P] [US5] Validate patterns.md includes offline fallback strategy (static FAQ, cached answers)
- [x] T044 [US5] Verify state machine includes Error state with recovery transitions (Error → Idle on retry)

### Documentation for US5

- [x] T045 [P] [US5] Create circuit breaker guide in specs/003-chatkit-widget/integration/circuit-breaker.md with timeout thresholds
- [x] T046 [P] [US5] Document offline FAQ structure in specs/003-chatkit-widget/integration/offline-faq.md (static content, version control)
- [x] T047 [US5] Create error handling checklist in specs/003-chatkit-widget/checklists/error-handling.md (timeout, network, validation errors)
- [x] T048 [P] [US5] Document network recovery detection in specs/003-chatkit-widget/integration/network-recovery.md (auto-resume RAG API)

**Checkpoint**: US5 design is fully documented and validated for offline resilience

---

## Phase 8: User Story 6 - Multi-Modal Input Design (FUTURE - Priority: P4)

**Goal**: Document future multi-modal interaction patterns (voice, image) for Phase 7+ implementation

**Independent Test**: Review patterns.md and verify it includes placeholders for voice/image event schemas

### Future Design Artifacts for US6

- [ ] T049 [P] [US6] Document voice input event schema in specs/003-chatkit-widget/future/voice-input.md (speech-to-text integration)
- [ ] T050 [P] [US6] Document image upload event schema in specs/003-chatkit-widget/future/image-upload.md (vision model integration)
- [ ] T051 [US6] Create multi-modal integration checklist in specs/003-chatkit-widget/checklists/multi-modal-future.md

**Checkpoint**: US6 future design is documented for Phase 7+ planning

---

## Phase 9: Polish & Cross-Cutting Design Validation

**Purpose**: Cross-validation, integration guides, and deployment readiness

- [ ] T052 [P] Validate all patterns in patterns.md reference correct integration points (.claude/agents/rag-orchestration/, .claude/mcp/better-auth/)
- [ ] T053 [P] Create comprehensive integration guide in docs/CHATKIT_INTEGRATION.md with all supported features and event flows
- [ ] T054 [P] Create deployment readiness checklist in specs/003-chatkit-widget/checklists/deployment-readiness.md
- [ ] T055 Cross-validate patterns.md pseudocode against SDD constitution (no implementation details, declarative design only)
- [ ] T056 [P] Create Phase 7 implementation planning guide in specs/003-chatkit-widget/phase7-planning.md (framework selection, runtime decisions)
- [ ] T057 [P] Validate all compliance rules in patterns.md have corresponding validation in mcp.json (GDPR, CCPA, FERPA, COPPA)
- [ ] T058 Create traceability matrix in specs/003-chatkit-widget/traceability.md mapping: User Stories → Patterns → Requirements → Success Criteria
- [ ] T059 [P] Update PROJECT_SUMMARY.md with ChatKit Widget statistics (design artifacts, patterns, compliance coverage)
- [ ] T060 [P] Create MCP server testing guide in .claude/mcp/chatkit/TESTING.md for validating event schemas and state transitions
- [ ] T061 Validate performance budgets in patterns.md are testable and measurable (Tier 0: 15KB, TTI: 100ms, p95 latency: 3s)

**Checkpoint**: All design artifacts validated, documented, and ready for Phase 7+ implementation

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (Validation)
    ↓
Phase 2: Foundational Design Validation (BLOCKS all user stories)
    ↓
Phase 3: US1 (P1) - Frictionless Q&A ← MVP Design
    ↓
Phase 4: US2 (P1) - Dual-Mode Retrieval ← MVP Design
    ↓
Phase 5: US3 (P2) - Progressive Signup
    ↓
Phase 6: US4 (P2) - Accessibility
    ↓
Phase 7: US5 (P3) - Offline Mode
    ↓
Phase 8: US6 (P4) - Multi-Modal (FUTURE)
    ↓
Phase 9: Polish & Cross-Validation
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (P1) | Phase 2 complete | US2 (both are MVP) |
| US2 (P1) | Phase 2 complete | US1 (both are MVP) |
| US3 (P2) | Phase 2 complete | US4, US5 (independent) |
| US4 (P2) | Phase 2 complete | US3, US5 (independent) |
| US5 (P3) | Phase 2 complete | US3, US4 (independent) |
| US6 (P4) | Phase 2 complete | Can be deferred to Phase 7+ |

### Within Each User Story

- Design validation before documentation
- Event schema validation before integration guides
- Compliance validation before deployment checklists
- All [P] tasks can run in parallel within each phase

---

## Parallel Opportunities

### Phase 2 Parallel Block
```
T005, T006, T008, T009 can run simultaneously (different validation domains)
```

### Phase 3 (US1) Parallel Block
```
T012, T013 can run in parallel (different event schemas)
T015, T016, T017 can run in parallel (different documentation files)
```

### Phase 5 (US3) Parallel Block
```
T026, T027 can run in parallel (event schema + state machine)
T029, T030, T032 can run in parallel (different integration guides)
```

### Phase 9 (Polish) Parallel Block
```
T052, T053, T054, T056, T057, T059, T060 can run in parallel (different files)
```

---

## Implementation Strategy

### MVP Design First (Phase 1-4 Only)

1. Complete Phase 1: Setup Validation (T001-T003) ✅ Already Complete
2. Complete Phase 2: Foundational Design Validation (T004-T010)
3. Complete Phase 3: US1 Design Validation (T011-T017) - Frictionless Q&A
4. Complete Phase 4: US2 Design Validation (T018-T024) - Dual-Mode Retrieval
5. **STOP and VALIDATE**: Review all design artifacts, ensure MVP user stories (US1+US2) are fully documented
6. **DELIVERABLE**: Design specification ready for Phase 7 implementation planning

### Incremental Design Documentation

1. **Setup + Foundational** → Core design artifacts validated
2. **Add US1 + US2** → MVP design complete (anonymous Q&A with dual modes)
3. **Add US3** → Progressive signup design documented
4. **Add US4** → Accessibility design validated
5. **Add US5** → Offline resilience design documented
6. **Add US6** → Future multi-modal design planned
7. **Polish** → Cross-validation, integration guides, deployment readiness

Each phase adds design documentation without invalidating previous phases.

### Parallel Design Team Strategy

With multiple designers/architects:

1. **Team completes Setup + Foundational together (T001-T010)**
2. Once Foundational is done:
   - **Designer A**: US1 Design Validation (T011-T017)
   - **Designer B**: US2 Design Validation (T018-T024)
   - **Designer C**: US3 Design Validation (T025-T032)
3. **All designers** collaborate on cross-validation and integration guides (Phase 9)

---

## Task Summary

| Phase | Task Range | Count | Completed | Status |
|-------|------------|-------|-----------|--------|
| Phase 1: Setup | T001-T003 | 3 | 3/3 | ✅ Complete |
| Phase 2: Foundational | T004-T010 | 7 | 7/7 | ✅ Complete |
| Phase 3: US1 (MVP) | T011-T017 | 7 | 7/7 | ✅ Complete |
| Phase 4: US2 (MVP) | T018-T024 | 7 | 7/7 | ✅ Complete |
| Phase 5: US3 | T025-T032 | 8 | 8/8 | ✅ Complete |
| Phase 6: US4 | T033-T040 | 8 | 8/8 | ✅ Complete |
| Phase 7: US5 | T041-T048 | 8 | 8/8 | ✅ Complete |
| Phase 8: US6 (FUTURE) | T049-T051 | 3 | 0/3 | ⏳ Deferred to Phase 7+ |
| Phase 9: Polish | T052-T061 | 10 | 0/10 | ⏳ Pending |
| **Total** | T001-T061 | **61** | **48/61** | **79% Complete** |

### Design Validation Status

**Completed Work**: 48/61 tasks (79%)
- ✅ Design artifact structure created (SKILL.md, patterns.md, mcp.json, README.md)
- ✅ Specification created (spec.md, checklists/)
- ✅ Event schema validation (7 tasks)
- ✅ Pattern completeness validation (18 tasks for US1-US5)
- ✅ Integration guide creation (20 tasks for US1-US5)
- ✅ Compliance checklist creation (10 tasks: session persistence, OAuth, WCAG, screen reader, keyboard, theme, error handling)
- ✅ Cross-validation (5 tasks: signup patterns, accessibility gaps, offline mode validation)

**Pending Design Validation**: 13/61 tasks (21%)
- ⏳ US6 (Multi-Modal Input) design planning (3 tasks, FUTURE)
- ⏳ Polish phase (10 tasks: cross-validation, integration guides, deployment readiness)

**Parallel Opportunities**: 28 tasks marked [P] can run concurrently (46% of pending work)

---

## Notes

- **NO CODE TASKS**: All tasks are design validation, documentation, and checklist creation only
- **NO RUNTIME IMPLEMENTATION**: This is Phase 6 - design intelligence only
- **Framework-Agnostic**: Design artifacts must not assume React, Vue, Svelte, or any specific technology
- **Phase 7+ Planning**: Implementation planning deferred to Phase 7 (see T056)
- **Existing Artifacts**: SKILL.md, patterns.md, mcp.json, README.md already created (Phase 1 complete)
- **Constitution Compliance**: All patterns must be declarative design, not implementation pseudocode
- Commit after each logical task group
- Cross-validate after each user story phase to ensure design coherence
