# Mode-Switching Guide: Full-Corpus ↔ Selected-Text

**Document Type**: Integration Guide
**User Story**: US2 (Dual-Mode Retrieval)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This guide documents how users switch between **full-corpus mode** (query entire documentation) and **selected-text mode** (query constrained to user's text selection).

**Modes**:
1. **Full-Corpus Mode** (Default): RAG agent searches all modules/chapters
2. **Selected-Text Mode**: RAG agent uses only user-highlighted text as context

**Design Pattern**: Event-Driven Architecture (Pattern 1)

---

## Mode Definitions

### Full-Corpus Mode

**Purpose**: Answer questions using the entire documentation as context

**Use Case**: Broad questions like "What is embodied intelligence?" or "How do humanoid robots walk?"

**Event Payload**:
```json
{
  "event": "user_message",
  "metadata": {
    "mode": "full-corpus",
    "selected_text": null,
    "context": {
      "current_page": "/docs/module-2-embodied/embodied-intelligence",
      "user_tier": "anonymous"
    }
  }
}
```

**RAG Agent Behavior**:
1. Perform vector search across **all documentation chunks** (Qdrant)
2. Retrieve top-k most relevant chunks (default: k=5)
3. Synthesize answer from retrieved chunks
4. Generate citations from multiple modules/chapters

---

### Selected-Text Mode

**Purpose**: Answer questions using only user-selected text as context

**Use Case**: Focused questions like "What sensors are mentioned here?" when user highlights a paragraph about vision sensors

**Event Payload**:
```json
{
  "event": "user_message",
  "metadata": {
    "mode": "selected-text",
    "selected_text": "Vision sensors use cameras to capture RGB images and depth maps. Lidar sensors provide 3D point clouds for obstacle detection.",
    "context": {
      "current_page": "/docs/module-4-perception/multimodal-sensing",
      "user_tier": "anonymous"
    }
  }
}
```

**RAG Agent Behavior**:
1. **Skip vector search** (no Qdrant query)
2. Use `selected_text` as sole context (passthrough)
3. Synthesize answer from selected text only
4. Generate citation to current page section (Stable-ID)

---

## Mode Switching Triggers

### Trigger 1: User Selects Text

**Scenario**: User highlights text on documentation page → Widget switches to selected-text mode

**Flow**:
1. User highlights 3 paragraphs about vision sensors
2. User right-clicks → Context menu appears
3. User clicks "Ask about this selection" → Widget opens in selected-text mode
4. Widget pre-fills mode indicator: "🔍 Selected-Text Mode"
5. User types question: "What sensors are mentioned here?"
6. Widget emits `user_message` with `mode: "selected-text"` and `selected_text: "..."`

**Alternative Trigger** (no right-click):
- User highlights text
- User clicks chat widget button
- Widget detects active text selection
- Widget auto-switches to selected-text mode
- Widget shows selection preview: "Asking about 250 characters from 'Multimodal Sensing'"

---

### Trigger 2: User Clears Selection

**Scenario**: User was in selected-text mode → Clears selection → Widget reverts to full-corpus mode

**Flow**:
1. Widget is in selected-text mode
2. User clicks elsewhere (deselects text)
3. Widget detects selection cleared (`window.getSelection().toString() === ""`)
4. Widget reverts to full-corpus mode
5. Mode indicator updates: "📚 Full-Corpus Mode"

---

### Trigger 3: User Clicks Mode Toggle Button

**Scenario**: User manually switches modes via toggle button in widget UI

**Flow**:
1. Widget displays mode toggle button (e.g., 📚 Full / 🔍 Selected toggle)
2. User clicks toggle button
3. If switching to selected-text mode BUT no text selected:
   - Show prompt: "Please select text on the page to ask about"
   - Do not switch mode (stay in full-corpus)
4. If switching to full-corpus mode:
   - Clear `selected_text` field
   - Update mode indicator

**UI Design** (design-level):
```html
<div class="mode-toggle">
  <button class="mode-btn mode-full-corpus active" aria-label="Full-Corpus Mode" aria-pressed="true">
    📚 Full
  </button>
  <button class="mode-btn mode-selected-text" aria-label="Selected-Text Mode" aria-pressed="false">
    🔍 Selected
  </button>
</div>
```

---

### Trigger 4: User Navigates to Different Page

**Scenario**: User was in selected-text mode → Navigates to different page → Widget clears selection (stale selection detection)

**Flow**:
1. Widget is in selected-text mode with `selected_text` from page A
2. User navigates to page B (different URL)
3. Widget detects page navigation (`window.location.href` changed)
4. Widget clears `selected_text` (now stale/irrelevant)
5. Widget reverts to full-corpus mode
6. User must re-select text on new page to use selected-text mode

---

## Selected-Text Validation Rules

### Rule 1: Minimum Length

**Constraint**: Selected text MUST be ≥50 characters

**Reason**: Prevent trivial selections (e.g., single word) that lack sufficient context

**Validation** (design-level):
```typescript
if (selected_text.length < 50) {
  showError("Please select at least 50 characters for focused Q&A");
  revertToFullCorpusMode();
}
```

**User Feedback**:
```
⚠ Selection too short (25 chars)
Please select at least 50 characters for focused Q&A.
```

---

### Rule 2: Maximum Length

**Constraint**: Selected text MUST be ≤5000 characters

**Reason**: Prevent excessive context that degrades RAG synthesis quality

**Validation** (design-level):
```typescript
if (selected_text.length > 5000) {
  showError("Selection too long (5200 chars). Please select up to 5000 characters.");
  revertToFullCorpusMode();
}
```

**User Feedback**:
```
⚠ Selection too long (5200 chars)
Please select up to 5000 characters (approximately 2-3 pages).
```

---

### Rule 3: Mode Consistency

**Constraint**: If `mode="selected-text"`, then `selected_text` MUST NOT be null

**Validation** (design-level):
```typescript
if (mode === "selected-text" && !selected_text) {
  console.error("Mode consistency violation: selected-text mode requires selected_text field");
  revertToFullCorpusMode();
}
```

**Impact**: Prevents invalid event payloads from reaching RAG agent

---

### Rule 4: Stale Selection Detection

**Constraint**: Clear `selected_text` when user navigates to different page

**Validation** (design-level):
```typescript
// Listen for page navigation
window.addEventListener('popstate', () => {
  if (currentMode === "selected-text") {
    clearSelection();
    revertToFullCorpusMode();
  }
});

// Also check on page load
if (currentPage !== previousPage && selected_text) {
  clearSelection();
  revertToFullCorpusMode();
}
```

---

## UI/UX Design Guidance

### Mode Indicator

**Purpose**: Show user which mode is active

**Design** (visual indicator in chat header):
```
┌─────────────────────────────────┐
│ 📚 Full-Corpus Mode             │  ← Indicator
├─────────────────────────────────┤
│ User: What is embodied intel... │
│ Agent: Embodied intelligence... │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│ 🔍 Selected-Text Mode           │  ← Indicator
│ Asking about 250 chars from     │  ← Selection preview
│ "Multimodal Sensing"            │
├─────────────────────────────────┤
│ User: What sensors are mentio...│
│ Agent: The selected text menti..│
└─────────────────────────────────┘
```

---

### Selection Preview

**Purpose**: Show user what text they're asking about in selected-text mode

**Design**:
```html
<div class="mode-indicator selected-text-mode">
  <span class="mode-label">🔍 Selected-Text Mode</span>
  <span class="selection-preview">
    Asking about 250 chars from <em>"Multimodal Sensing"</em>
  </span>
  <button class="clear-selection-btn" aria-label="Clear selection and switch to full-corpus mode">
    ✕
  </button>
</div>
```

**User Actions**:
- Click "✕" button → Clear selection, revert to full-corpus mode
- Hover over selection preview → Show tooltip with full selected text (truncated to 200 chars)

---

### Mode Toggle Button

**Purpose**: Allow manual mode switching

**Design** (toggle button group):
```html
<div class="mode-toggle" role="radiogroup" aria-label="Retrieval mode">
  <button class="mode-btn" role="radio" aria-checked="true" data-mode="full-corpus">
    📚 Full
  </button>
  <button class="mode-btn" role="radio" aria-checked="false" data-mode="selected-text">
    🔍 Selected
  </button>
</div>
```

**Accessibility**:
- Use `role="radiogroup"` for mode toggle (only one mode active at a time)
- Use `aria-checked="true|false"` to indicate active mode
- Keyboard navigation: Arrow keys to switch modes, Enter to activate

---

## Mode-Specific Answer Rendering

### Full-Corpus Mode Answers

**Characteristics**:
- Citations from **multiple modules/chapters**
- Citation labels show module + chapter: "[1] Module 2: Embodied Intelligence"
- Answer synthesizes information from diverse sources

**Example Rendering**:
```
Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences.[1] Humanoid robots apply this principle through bipedal locomotion and adaptive control.[2]

Sources:
[1] Module 2: Embodied Intelligence > Definition
[2] Module 3: Humanoid Robotics > Bipedal Locomotion
```

---

### Selected-Text Mode Answers

**Characteristics**:
- Citation to **current page section only**
- Citation label shows page section: "[1] Multimodal Sensing (current selection)"
- Answer references "the selected text" or "the passage" explicitly

**Example Rendering**:
```
The selected text mentions two types of sensors: vision sensors (cameras for RGB images and depth maps) and lidar sensors (3D point clouds for obstacle detection).[1]

Sources:
[1] Module 4: Perception > Multimodal Sensing (current selection)
```

---

## Error Handling

### Error 1: No Text Selected (User Tries to Activate Selected-Text Mode)

**Scenario**: User clicks "🔍 Selected" button but hasn't highlighted any text

**Behavior**:
1. Widget displays error: "⚠ Please select text on the page to ask about"
2. Mode toggle button remains on "📚 Full" (no mode change)
3. Input field remains active (user can still ask full-corpus questions)

---

### Error 2: Selection Too Short (<50 chars)

**Scenario**: User selects 25 characters and tries to ask question

**Behavior**:
1. Widget displays warning: "⚠ Selection too short (25 chars). Please select at least 50 characters."
2. Widget auto-reverts to full-corpus mode
3. User's question is sent in full-corpus mode instead

**Alternative** (stricter):
- Disable "Ask" button in selected-text mode if selection <50 chars
- Show inline validation: "Selection: 25 / 50 chars minimum"

---

### Error 3: Selection Becomes Stale (User Navigates Away)

**Scenario**: User selects text on page A, navigates to page B, returns to chat

**Behavior**:
1. Widget detects `selected_text` is from different page
2. Widget clears selection automatically
3. Mode indicator updates: "📚 Full-Corpus Mode (selection cleared)"
4. User can select text on new page to re-enable selected-text mode

---

## Performance Considerations

### Mode Switching Latency

**Target**: ≤50ms to switch modes

**Optimization**:
- Cache selected text in memory (don't re-query `window.getSelection()` on every keystroke)
- Debounce text selection events (wait 100ms after user stops selecting)
- Pre-validate selection length before user asks question

---

### Selected-Text Mode Response Time

**Advantage**: Faster than full-corpus mode (no vector search)

**Expected Latency**:
- Full-corpus mode: ~2-3 seconds (p95) - includes Qdrant search + synthesis
- Selected-text mode: ~1-2 seconds (p95) - passthrough + synthesis only

**Reason**: Selected-text mode skips vector search step (RAG agent directly synthesizes from provided text)

---

## Testing Checklist

### Mode Switching

- [ ] **Test 1**: Full → Selected (with text selected) → Verify mode changes
- [ ] **Test 2**: Full → Selected (no text selected) → Verify error shown, mode stays Full
- [ ] **Test 3**: Selected → Full (manual toggle) → Verify mode changes, selection cleared
- [ ] **Test 4**: Selected → Full (clear selection on page) → Verify auto-revert

### Selection Validation

- [ ] **Test 5**: Select 25 chars → Verify warning "too short"
- [ ] **Test 6**: Select 50 chars → Verify accepted
- [ ] **Test 7**: Select 5001 chars → Verify warning "too long"
- [ ] **Test 8**: Select valid text → Navigate to new page → Verify selection cleared

### Answer Quality

- [ ] **Test 9**: Full-corpus question → Verify citations from multiple modules
- [ ] **Test 10**: Selected-text question → Verify citation to current page only
- [ ] **Test 11**: Selected-text question → Verify answer references "selected text"
- [ ] **Test 12**: Ask same question in both modes → Verify different answers

### Accessibility

- [ ] **Test 13**: Tab navigation → Verify mode toggle reachable
- [ ] **Test 14**: Arrow keys → Verify mode toggle switches
- [ ] **Test 15**: Screen reader → Verify mode changes announced
- [ ] **Test 16**: Keyboard text selection (Shift+Arrow) → Verify selected-text mode activated

---

## Implementation Notes

### Browser Text Selection API

**Design-Level Code** (not runtime implementation):
```typescript
// Get selected text
function getSelectedText(): string | null {
  const selection = window.getSelection();
  const text = selection?.toString().trim();
  return text || null;
}

// Detect selection change
window.addEventListener('selectionchange', () => {
  const selected_text = getSelectedText();

  if (selected_text && selected_text.length >= 50) {
    // Auto-switch to selected-text mode
    switchMode("selected-text", selected_text);
  } else if (!selected_text && currentMode === "selected-text") {
    // Auto-revert to full-corpus mode
    switchMode("full-corpus", null);
  }
});
```

---

### Mode State Management

**Design-Level State** (not runtime implementation):
```typescript
interface ModeState {
  mode: "full-corpus" | "selected-text";
  selected_text: string | null;
  current_page: string;
  previous_page: string | null;
}

// Initialize state
const state: ModeState = {
  mode: "full-corpus",
  selected_text: null,
  current_page: window.location.pathname,
  previous_page: null
};

// Mode switcher
function switchMode(newMode: "full-corpus" | "selected-text", selectedText: string | null) {
  state.mode = newMode;
  state.selected_text = selectedText;
  updateModeIndicator();
}
```

---

## References

- **Event Schema**: `.claude/skills/chatkit-widget/SKILL.md` lines 86-104 (user_message)
- **Pattern 1 (Event-Driven)**: `.claude/skills/chatkit-widget/patterns.md` lines 24-126
- **T018-T021 Validation Report**: `specs/003-chatkit-widget/validation/T018-T021-US2-dual-mode-support.md`
- **spec.md US2**: Lines 88-114 (Dual-Mode Retrieval acceptance scenarios)

---

**Status**: Design Guide Complete ✅
**Next Step**: Implement mode-switching UI and selection detection (Phase 7+)
