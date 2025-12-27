# Content Boundaries Guardrails Checklist

**Document Type**: Implementation Checklist
**User Story**: US2 (Dual-Mode Retrieval)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This checklist ensures correct implementation of content boundary guardrails for selected-text mode, preventing the RAG agent from answering questions that require information beyond the user's text selection.

**Requirements**:
- US2 AC2: Selected-text mode MUST constrain answers to selected content only
- FR-037: Widget MUST detect out-of-scope questions and prompt user to switch to full-corpus mode
- NFR-011: Guardrails MUST prevent hallucination by constraining answers to available context

**Pattern Reference**: Pattern 1 (Event-Driven Architecture) - guardrails_passed field in agent_response

---

## Pre-Implementation Review

### Design Artifacts

- [ ] Read Pattern 1 (Event-Driven) in `.claude/skills/chatkit-widget/patterns.md` lines 24-126
- [ ] Review agent_response event schema (SKILL.md lines 112-138) - includes guardrails_passed field
- [ ] Review mode-switching guide (integration/mode-switching.md) - selected-text mode behavior
- [ ] Review text selection pattern (integration/text-selection.md) - selection validation rules
- [ ] Review US2 acceptance criteria (spec.md lines 88-114) - constrained answers

---

## Guardrails Enforcement Strategy

### Strategy 1: Scope Detection (Required)

**Purpose**: Detect when user's question requires information beyond selected text

**Implementation Approach**:
1. RAG agent analyzes user question semantics
2. RAG agent compares question scope to selected_text content
3. If question mentions entities/concepts NOT in selected_text → Out-of-scope
4. If question requires synthesis across multiple sections → Out-of-scope

**Design-Level Logic**:
```typescript
function detectOutOfScope(question: string, selected_text: string): boolean {
  // Extract entities/concepts from question
  const questionEntities = extractEntities(question);

  // Extract entities/concepts from selected text
  const selectedTextEntities = extractEntities(selected_text);

  // Check if question mentions entities not in selection
  const missingEntities = questionEntities.filter(
    entity => !selectedTextEntities.includes(entity)
  );

  if (missingEntities.length > 0) {
    return true; // Out-of-scope: question mentions content not in selection
  }

  // Check if question requires cross-section synthesis
  if (requiresMultipleSections(question) && isShortSelection(selected_text)) {
    return true; // Out-of-scope: selection too narrow for question
  }

  return false; // In-scope: question can be answered from selection
}
```

---

### Strategy 2: Passthrough-Only Retrieval (Required)

**Purpose**: Ensure RAG agent does NOT perform vector search in selected-text mode

**Validation Rules**:
- [ ] If mode="selected-text", RAG agent MUST skip Qdrant vector search
- [ ] RAG agent MUST use selected_text as sole context (passthrough)
- [ ] RAG agent MUST NOT synthesize information from other documentation chunks
- [ ] RAG agent MUST NOT access embeddings or similarity search

**Design-Level Flow**:
```
user_message (mode="selected-text", selected_text="Vision sensors use cameras...")
  ↓
RAG Orchestration: Skip Step 1 (Context Selection)
  ↓
RAG Orchestration: Skip Step 2 (Retrieval - no vector search)
  ↓
RAG Orchestration: Step 3 (Synthesis from selected_text ONLY)
  ↓
RAG Orchestration: Step 4 (Guardrails validation)
  ↓
agent_response (citations to current page section only)
```

---

### Strategy 3: Guardrails Validation (Required)

**Purpose**: Validate answer references ONLY selected text content

**Validation Checks**:
1. **Citation Constraint**: All citations MUST point to current page section
2. **Content Constraint**: Answer MUST NOT include facts/entities from other modules
3. **Explicitness Constraint**: Answer MUST reference "selected text" or "the passage" explicitly

**Design-Level Validation**:
```typescript
function validateSelectedTextAnswer(
  answer: string,
  citations: Citation[],
  selected_text: string,
  current_page: string
): { guardrails_passed: boolean; error?: string } {

  // Check 1: All citations from current page only
  const externalCitations = citations.filter(c => !c.url.startsWith(current_page));
  if (externalCitations.length > 0) {
    return {
      guardrails_passed: false,
      error: "Answer references external sources (not in selection)"
    };
  }

  // Check 2: Answer mentions entities in selected_text
  const answerEntities = extractEntities(answer);
  const selectedEntities = extractEntities(selected_text);

  const externalEntities = answerEntities.filter(
    entity => !selectedEntities.includes(entity) && !isGenericTerm(entity)
  );

  if (externalEntities.length > 0) {
    return {
      guardrails_passed: false,
      error: `Answer mentions entities not in selection: ${externalEntities.join(", ")}`
    };
  }

  // Check 3: Answer explicitly references selection
  const referencesSelection = /selected text|the passage|highlighted text|this section/i.test(answer);
  if (!referencesSelection) {
    console.warn("Answer does not explicitly reference selected text (non-blocking)");
  }

  return { guardrails_passed: true };
}
```

---

## Out-of-Scope Question Handling

### Scenario 1: User Asks Cross-Module Question in Selected-Text Mode

**Example**:
- Selected text: "Vision sensors use cameras to capture RGB images and depth maps."
- User question: "How do vision sensors compare to proprioceptive sensors?"

**Detection**:
- "proprioceptive sensors" NOT mentioned in selected text → Out-of-scope

**RAG Agent Response**:
```json
{
  "event": "agent_response",
  "message": {
    "content": "This question requires information beyond the selected text (proprioceptive sensors are not mentioned in the highlighted passage). Would you like to switch to full-corpus mode to search across all modules?",
    "citations": [],
    "metadata": {
      "guardrails_passed": false,
      "out_of_scope_reason": "Question mentions entities not in selection",
      "suggested_action": "switch_to_full_corpus"
    }
  }
}
```

**Widget Behavior**:
1. Display out-of-scope message
2. Show mode-switch suggestion: "Switch to 📚 Full-Corpus Mode to answer this question?"
3. User clicks "Switch" → Widget changes mode to full-corpus, re-submits question

---

### Scenario 2: User Asks Multi-Section Question with Short Selection

**Example**:
- Selected text: "Bipedal locomotion requires dynamic balance." (1 sentence, 50 chars)
- User question: "What are the key challenges in bipedal locomotion?"

**Detection**:
- Selection too short (50 chars) to answer multi-faceted question → Out-of-scope

**RAG Agent Response**:
```json
{
  "event": "agent_response",
  "message": {
    "content": "The selected text is too brief to fully answer this question. Please select a larger passage (at least 2-3 paragraphs) or switch to full-corpus mode.",
    "citations": [],
    "metadata": {
      "guardrails_passed": false,
      "out_of_scope_reason": "Selection too short for question complexity",
      "suggested_action": "select_more_text_or_switch_mode"
    }
  }
}
```

---

### Scenario 3: User Asks In-Scope Question (Success Case)

**Example**:
- Selected text: "Vision sensors use cameras to capture RGB images and depth maps. Lidar sensors provide 3D point clouds for obstacle detection."
- User question: "What sensors are mentioned here?"

**Detection**:
- "sensors" mentioned in selected text ✅
- Question scope matches selection ✅

**RAG Agent Response**:
```json
{
  "event": "agent_response",
  "message": {
    "content": "The selected text mentions two types of sensors: vision sensors (cameras for RGB images and depth maps) and lidar sensors (3D point clouds for obstacle detection).",
    "citations": [
      {
        "id": "citation-1",
        "url": "/docs/module-4-perception/multimodal-sensing#vision-sensors",
        "excerpt": "Vision sensors use cameras to capture RGB images and depth maps."
      }
    ],
    "metadata": {
      "guardrails_passed": true,
      "mode": "selected-text",
      "retrieval_count": 0
    }
  }
}
```

**Widget Rendering**:
```
The selected text mentions two types of sensors: vision sensors (cameras for RGB images and depth maps) and lidar sensors (3D point clouds for obstacle detection).[1]

Sources:
[1] Module 4: Perception > Multimodal Sensing (current selection)
```

---

## guardrails_passed Field Usage

### Field Definition

**Location**: agent_response.message.metadata.guardrails_passed (mcp.json line 106)

**Type**: Boolean
**Required**: Yes (for all RAG responses)

**Values**:
- `true`: Answer is valid and constrained to selected text (selected-text mode) or documentation (full-corpus mode)
- `false`: Answer violates content boundaries (out-of-scope question, hallucination detected, unsafe content)

---

### Widget Response to guardrails_passed

**If guardrails_passed = true**:
- [ ] Widget renders answer normally
- [ ] Widget displays citations (inline superscripts)
- [ ] Widget marks message as successful (no error state)

**If guardrails_passed = false**:
- [ ] Widget displays out-of-scope message instead of answer
- [ ] Widget suggests mode switch: "Switch to 📚 Full-Corpus Mode?"
- [ ] Widget displays metadata.out_of_scope_reason (if provided)
- [ ] Widget marks message as warning (not error - user can retry with different mode)

**Design-Level Rendering**:
```typescript
function renderAgentResponse(response: AgentResponse) {
  const { content, citations, metadata } = response.message;

  if (metadata.guardrails_passed === false) {
    // Out-of-scope or guardrails violation
    renderOutOfScopeMessage(content, metadata.suggested_action);
  } else {
    // Valid answer
    renderAnswer(content, citations);
  }
}

function renderOutOfScopeMessage(message: string, suggested_action: string) {
  // Display warning icon + message
  displayWarning(message);

  // Show action button
  if (suggested_action === "switch_to_full_corpus") {
    showModeSwitchButton("📚 Switch to Full-Corpus Mode");
  } else if (suggested_action === "select_more_text_or_switch_mode") {
    showModeSwitchButton("📚 Switch to Full-Corpus Mode");
    showSelectionHint("Or select a larger passage (2-3 paragraphs)");
  }
}
```

---

## Guardrails Testing Checklist

### Selected-Text Mode Guardrails

- [ ] **Test 1**: Ask question about entity NOT in selection → Verify guardrails_passed=false
- [ ] **Test 2**: Ask question about entity IN selection → Verify guardrails_passed=true
- [ ] **Test 3**: Ask multi-section question with 1-sentence selection → Verify out-of-scope detection
- [ ] **Test 4**: Ask focused question with 3-paragraph selection → Verify in-scope answer
- [ ] **Test 5**: Verify RAG agent does NOT perform vector search in selected-text mode

### Citation Constraints

- [ ] **Test 6**: Verify all citations in selected-text mode point to current page only
- [ ] **Test 7**: Verify no citations to external modules in selected-text mode
- [ ] **Test 8**: Verify citation labels include "(current selection)" suffix

### Out-of-Scope Handling

- [ ] **Test 9**: Out-of-scope question → Verify widget displays mode-switch suggestion
- [ ] **Test 10**: Click "Switch to Full-Corpus" → Verify question re-submitted in full-corpus mode
- [ ] **Test 11**: Out-of-scope question → Verify widget shows metadata.out_of_scope_reason

### Edge Cases

- [ ] **Test 12**: Selection with ambiguous entities (e.g., "it", "this") → Verify RAG handles pronouns
- [ ] **Test 13**: Question mentions synonyms of entities in selection → Verify guardrails accept synonyms
- [ ] **Test 14**: Factual error in selected text → Verify RAG answers based on selection (not external knowledge)
- [ ] **Test 15**: Empty citations array + guardrails_passed=false → Verify widget renders out-of-scope message

---

## Full-Corpus Mode Guardrails (Comparison)

**Difference from Selected-Text Mode**:

| Aspect | Selected-Text Mode | Full-Corpus Mode |
|--------|-------------------|------------------|
| **Context Source** | selected_text field ONLY | Qdrant vector search (all modules) |
| **Vector Search** | ❌ Disabled (passthrough) | ✅ Enabled (top-k=5 chunks) |
| **Citation Constraint** | Current page section only | Multiple modules/chapters allowed |
| **Out-of-Scope Detection** | Strict (question must match selection) | Relaxed (any documentation topic) |
| **guardrails_passed=false** | Out-of-scope question | No relevant documentation found OR unsafe content |

**Full-Corpus Guardrails** (for comparison):
1. **Relevance Check**: Vector search returns no chunks with similarity >0.7 → guardrails_passed=false
2. **Documentation Constraint**: Answer must reference documentation only (no external web knowledge)
3. **Safety Check**: Answer does not contain harmful/inappropriate content

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| Guardrails validation latency | ≤100ms | NFR-011 |
| Out-of-scope detection accuracy | ≥95% | US2 acceptance criteria |
| False positive rate (valid questions flagged) | ≤5% | US2 acceptance criteria |
| Citation constraint validation | ≤50ms | NFR-011 |

---

## Error Handling

### Error 1: Guardrails Validation Timeout

**Scenario**: RAG agent takes >100ms to validate guardrails

**Fallback Behavior**:
1. Skip guardrails validation (set guardrails_passed=true by default)
2. Log timeout event for monitoring
3. Display answer with warning: "⚠ Answer not validated for scope compliance"

---

### Error 2: Ambiguous Entity Extraction

**Scenario**: RAG agent cannot extract entities from question (e.g., "What about that?")

**Fallback Behavior**:
1. Assume question is in-scope (optimistic default)
2. Proceed with answer generation
3. Post-hoc validation: Check if answer mentions entities in selected_text

---

### Error 3: Citation Constraint Violation (Post-Generation)

**Scenario**: RAG agent generates answer with external citations despite selected-text mode

**Fallback Behavior**:
1. Filter out external citations (keep current-page citations only)
2. If no current-page citations remain: Set guardrails_passed=false
3. Display out-of-scope message

**Design-Level Logic**:
```typescript
function postProcessCitations(citations: Citation[], current_page: string, mode: string): Citation[] {
  if (mode !== "selected-text") {
    return citations; // No filtering in full-corpus mode
  }

  const currentPageCitations = citations.filter(c => c.url.startsWith(current_page));

  if (currentPageCitations.length === 0 && citations.length > 0) {
    console.error("Guardrails violation: All citations external in selected-text mode");
    // Trigger out-of-scope response
  }

  return currentPageCitations;
}
```

---

## Privacy & Compliance

### GDPR (General Data Protection Regulation)

- [ ] **No Personal Data in Guardrails**: Guardrails logic MUST NOT log message content for anonymous users
- [ ] **Data Minimization**: Only log guardrails_passed boolean + timestamp (no question text)

### FERPA (Family Educational Rights and Privacy Act)

- [ ] **Student Privacy**: Guardrails MUST NOT expose student-identifiable information in error messages
- [ ] **Content Boundaries**: Selected-text mode prevents accidental disclosure of adjacent content

---

## Implementation Notes

### Entity Extraction (Design-Level)

**Options for Implementation Phase (Phase 7+)**:

1. **Simple Keyword Matching** (fastest):
   - Extract nouns/noun phrases from question and selected_text
   - Compare sets: if question mentions nouns not in selection → out-of-scope

2. **Semantic Similarity** (better accuracy):
   - Embed question and selected_text
   - If semantic similarity <0.7 → out-of-scope

3. **LLM-Based Classification** (most accurate):
   - Prompt RAG agent: "Can this question be answered using only the selected text? Yes/No"
   - Parse response for in-scope/out-of-scope classification

**Recommendation**: Start with Option 1 (keyword matching) for Phase 7 MVP, upgrade to Option 3 (LLM classification) in Phase 8+ for better accuracy.

---

### Guardrails Configuration

**Design-Level Configuration** (for future implementation):
```json
{
  "guardrails": {
    "selected_text_mode": {
      "strict_citation_constraint": true,
      "min_selection_length": 50,
      "max_selection_length": 5000,
      "out_of_scope_detection": "keyword_matching",
      "fallback_on_ambiguity": "in_scope"
    },
    "full_corpus_mode": {
      "min_similarity_threshold": 0.7,
      "max_retrieval_count": 5,
      "safety_check_enabled": true
    }
  }
}
```

---

## References

- **Pattern 1 (Event-Driven)**: `.claude/skills/chatkit-widget/patterns.md` lines 24-126
- **agent_response Event Schema**: `.claude/skills/chatkit-widget/SKILL.md` lines 112-138
- **Mode-Switching Guide**: `specs/003-chatkit-widget/integration/mode-switching.md`
- **Text Selection Pattern**: `specs/003-chatkit-widget/integration/text-selection.md`
- **US2 Acceptance Criteria**: `specs/003-chatkit-widget/spec.md` lines 88-114
- **FR-037**: Widget detects out-of-scope questions
- **NFR-011**: Guardrails prevent hallucination

---

**Status**: Design Checklist Complete ✅
**Next Step**: Implement guardrails validation logic (Phase 7+)
