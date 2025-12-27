# Text Selection Detection Pattern

**Document Type**: Integration Guide
**User Story**: US2 (Dual-Mode Retrieval)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This guide documents how to detect and capture user text selection on documentation pages for selected-text mode Q&A.

**Browser API**: `window.getSelection()` (Selection API)
**Use Case**: User highlights paragraph → Widget detects selection → Widget switches to selected-text mode

---

## Browser Selection API

### Get Selected Text

**Design-Level Code** (not runtime implementation):
```typescript
function getSelectedText(): { text: string; range: Range | null } {
  const selection = window.getSelection();

  if (!selection || selection.rangeCount === 0) {
    return { text: "", range: null };
  }

  const range = selection.getRangeAt(0);
  const text = selection.toString().trim();

  return { text, range };
}
```

**Returns**:
- `text`: Selected text as string
- `range`: DOM Range object (for highlighting, positioning)

---

### Listen for Selection Changes

**Event**: `selectionchange`

**Design-Level Code**:
```typescript
document.addEventListener('selectionchange', () => {
  const { text, range } = getSelectedText();

  if (text.length >= 50) {
    // Valid selection detected
    onTextSelected(text, range);
  } else if (text.length === 0 && widget.mode === "selected-text") {
    // Selection cleared
    onSelectionCleared();
  }
});
```

**Debouncing** (prevent excessive events):
```typescript
let selectionTimeout: number | null = null;

document.addEventListener('selectionchange', () => {
  if (selectionTimeout) clearTimeout(selectionTimeout);

  selectionTimeout = window.setTimeout(() => {
    const { text, range } = getSelectedText();
    handleSelection(text, range);
  }, 100); // Wait 100ms after user stops selecting
});
```

---

## Selection Workflow

### Step 1: User Selects Text

**User Action**: User highlights 3 paragraphs about vision sensors

**Widget Detection**:
1. `selectionchange` event fires
2. Widget reads `window.getSelection().toString()`
3. Widget validates selection length (≥50 chars, ≤5000 chars)
4. Widget stores selected text: `selected_text = "Vision sensors use cameras..."`

---

### Step 2: Widget Updates UI

**UI Changes**:
1. Mode indicator changes: "📚 Full" → "🔍 Selected"
2. Selection preview appears: "Asking about 250 chars from 'Multimodal Sensing'"
3. Input placeholder updates: "Ask about this selection..."
4. (Optional) Highlight selected text with subtle yellow background

**Design-Level UI Update**:
```typescript
function onTextSelected(text: string, range: Range) {
  // Update widget state
  widget.mode = "selected-text";
  widget.selected_text = text;

  // Update UI
  modeIndicator.textContent = "🔍 Selected-Text Mode";
  selectionPreview.textContent = `Asking about ${text.length} chars from "${getCurrentPageTitle()}"`;
  inputPlaceholder.textContent = "Ask about this selection...";

  // Optional: Highlight selected text
  highlightRange(range, { backgroundColor: "rgba(255, 255, 0, 0.2)" });
}
```

---

### Step 3: User Asks Question

**User Input**: "What sensors are mentioned here?"

**Widget Behavior**:
1. Widget emits `user_message` event with:
   - `mode: "selected-text"`
   - `selected_text: "Vision sensors use cameras..."`
   - `content: "What sensors are mentioned here?"`

2. RAG agent receives event, uses `selected_text` as sole context (no vector search)

---

### Step 4: Widget Renders Answer

**Answer**: "The selected text mentions two types of sensors: vision sensors (cameras) and lidar sensors (3D point clouds)."

**Citation**: [1] Module 4: Perception > Multimodal Sensing (current selection)

---

## Selection Validation

### Validation 1: Minimum Length (50 chars)

**Purpose**: Prevent trivial selections (e.g., single word)

**Implementation**:
```typescript
const MIN_SELECTION_LENGTH = 50;

function validateSelection(text: string): { valid: boolean; error?: string } {
  if (text.length < MIN_SELECTION_LENGTH) {
    return {
      valid: false,
      error: `Selection too short (${text.length} chars). Please select at least ${MIN_SELECTION_LENGTH} characters.`
    };
  }
  return { valid: true };
}
```

**User Feedback**:
- If selection <50 chars: Show warning, stay in full-corpus mode
- If selection ≥50 chars: Auto-switch to selected-text mode

---

### Validation 2: Maximum Length (5000 chars)

**Purpose**: Prevent excessive context that degrades synthesis quality

**Implementation**:
```typescript
const MAX_SELECTION_LENGTH = 5000;

function validateSelection(text: string): { valid: boolean; error?: string } {
  if (text.length > MAX_SELECTION_LENGTH) {
    return {
      valid: false,
      error: `Selection too long (${text.length} chars). Please select up to ${MAX_SELECTION_LENGTH} characters (approximately 2-3 pages).`
    };
  }
  return { valid: true };
}
```

**User Feedback**:
- If selection >5000 chars: Show warning, truncate to first 5000 chars, or revert to full-corpus mode

---

### Validation 3: Whitespace Trimming

**Purpose**: Remove leading/trailing whitespace

**Implementation**:
```typescript
const text = window.getSelection().toString().trim();
```

**Reason**: Selections often include unintended whitespace at boundaries

---

### Validation 4: Empty Selection Detection

**Purpose**: Clear selected-text mode when user deselects

**Implementation**:
```typescript
document.addEventListener('selectionchange', () => {
  const text = window.getSelection().toString().trim();

  if (text.length === 0 && widget.mode === "selected-text") {
    // User cleared selection
    onSelectionCleared();
  }
});

function onSelectionCleared() {
  widget.mode = "full-corpus";
  widget.selected_text = null;
  modeIndicator.textContent = "📚 Full-Corpus Mode";
  selectionPreview.style.display = "none";
}
```

---

## Context Menu Integration (Optional)

### Right-Click → "Ask about selection"

**User Workflow**:
1. User selects text
2. User right-clicks → Context menu appears
3. User clicks "Ask about this selection" → Widget opens in selected-text mode

**Implementation** (design-level):
```typescript
document.addEventListener('contextmenu', (event) => {
  const text = window.getSelection().toString().trim();

  if (text.length >= 50) {
    // Show custom context menu item
    addContextMenuItem({
      label: "Ask about this selection",
      onclick: () => {
        openWidget({ mode: "selected-text", selected_text: text });
      }
    });
  }
});
```

**Note**: Custom context menus require browser extension or native integration. For web widgets, use alternative triggers (floating button near selection).

---

## Floating "Ask" Button (Recommended Alternative)

**Design**: Show floating button near selected text

**User Workflow**:
1. User selects text
2. Floating "Ask about selection" button appears above/below selection
3. User clicks button → Widget opens in selected-text mode

**Implementation** (design-level):
```typescript
document.addEventListener('selectionchange', () => {
  const { text, range } = getSelectedText();

  if (text.length >= 50) {
    showFloatingAskButton(range);
  } else {
    hideFloatingAskButton();
  }
});

function showFloatingAskButton(range: Range) {
  const rect = range.getBoundingClientRect();

  // Position button above selection
  floatingButton.style.top = `${rect.top - 40}px`;
  floatingButton.style.left = `${rect.left + rect.width / 2 - 50}px`;
  floatingButton.style.display = "block";

  floatingButton.onclick = () => {
    const text = window.getSelection().toString().trim();
    openWidget({ mode: "selected-text", selected_text: text });
  };
}
```

**UI Design**:
```
┌─────────────────────────────────┐
│  Vision sensors use cameras to  │
│  capture RGB images and depth   │ ← Selected text
│  maps. Lidar sensors provide... │
└─────────────────────────────────┘
          ▲
    ┌───────────┐
    │ 🔍 Ask    │ ← Floating button
    └───────────┘
```

---

## Keyboard Text Selection Support

**Accessibility**: Users with keyboard-only navigation must be able to select text

**Keyboard Selection**:
- **Shift + Arrow keys**: Extend selection character-by-character
- **Shift + Ctrl + Arrow keys**: Extend selection word-by-word
- **Shift + Home/End**: Select to beginning/end of line

**Widget Integration**:
- Widget MUST detect keyboard-based selections (same `selectionchange` event)
- Floating "Ask" button MUST be keyboard-accessible (Tab to focus, Enter to activate)

**Design-Level Code**:
```typescript
// Keyboard-accessible floating button
floatingButton.setAttribute('tabindex', '0');

floatingButton.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    floatingButton.click();
  }
});
```

---

## Selection Persistence (Across Page Navigation)

### Problem: Stale Selections

**Scenario**: User selects text on page A, navigates to page B, widget still shows selected-text mode with page A text

**Solution**: Clear selection on page navigation

**Implementation**:
```typescript
let lastPageURL = window.location.href;

// Detect page navigation
window.addEventListener('popstate', () => {
  if (window.location.href !== lastPageURL) {
    clearSelection();
    lastPageURL = window.location.href;
  }
});

// Also detect programmatic navigation (SPA)
const observer = new MutationObserver(() => {
  if (window.location.href !== lastPageURL) {
    clearSelection();
    lastPageURL = window.location.href;
  }
});

observer.observe(document.body, { childList: true, subtree: true });

function clearSelection() {
  widget.selected_text = null;
  widget.mode = "full-corpus";
  window.getSelection()?.removeAllRanges();
}
```

---

## Selection Highlighting (Optional Visual Feedback)

**Purpose**: Visually highlight selected text when in selected-text mode

**Design**:
- Add semi-transparent yellow background to selected text
- Remove highlight when user clears selection or asks question

**Implementation** (design-level):
```typescript
function highlightRange(range: Range, style: { backgroundColor: string }) {
  const mark = document.createElement('mark');
  mark.style.backgroundColor = style.backgroundColor;
  mark.style.color = 'inherit'; // Preserve text color

  try {
    range.surroundContents(mark);
  } catch (error) {
    // If range spans multiple elements, use CSS highlight API instead
    CSS.highlights.set('selected-text-highlight', new Highlight(range));
  }
}

function removeHighlight() {
  // Remove <mark> elements
  document.querySelectorAll('mark[data-chatkit-highlight]').forEach(el => el.replaceWith(...el.childNodes));

  // Remove CSS highlights
  CSS.highlights.clear();
}
```

**Note**: CSS Highlight API is experimental (Chrome 105+, Firefox not supported as of 2025). Use `<mark>` element for broader compatibility.

---

## Mobile Touch Selection

**Challenge**: Mobile selection UI differs from desktop (long-press, selection handles)

**Mobile Selection Detection**:
- Same `selectionchange` event works on mobile
- Mobile browsers show native selection handles
- Floating "Ask" button should appear above selection (not obscured by handles)

**Mobile-Specific Considerations**:
```typescript
function isMobile(): boolean {
  return /Android|iPhone|iPad/i.test(navigator.userAgent);
}

function showFloatingAskButton(range: Range) {
  const rect = range.getBoundingClientRect();

  if (isMobile()) {
    // Position button above selection (mobile selection handles below)
    floatingButton.style.top = `${rect.top - 60}px`; // Extra space for handles
  } else {
    // Desktop: position button above selection
    floatingButton.style.top = `${rect.top - 40}px`;
  }

  floatingButton.style.left = `${rect.left + rect.width / 2 - 50}px`;
  floatingButton.style.display = "block";
}
```

---

## Accessibility (WCAG 2.1 AA)

### Screen Reader Announcements

**Requirement**: Announce when selected-text mode is activated

**Implementation**:
```html
<div class="sr-only" aria-live="polite" role="status">
  <!-- Dynamically updated by JavaScript -->
</div>
```

```typescript
function announceToScreenReader(message: string) {
  const srElement = document.querySelector('[aria-live="polite"]');
  if (srElement) {
    srElement.textContent = message;
  }
}

// When user selects text
onTextSelected(text, range) {
  announceToScreenReader(`Selected text mode activated. Asking about ${text.length} characters from ${getCurrentPageTitle()}.`);
}
```

### Keyboard Navigation

**Requirements**:
- Floating "Ask" button MUST be keyboard-focusable (tabindex="0")
- Button MUST be activatable with Enter or Space key
- Clear selection button MUST be keyboard-accessible

---

## Testing Checklist

### Selection Detection

- [ ] **Test 1**: Select text (mouse) → Verify `selectionchange` event fires
- [ ] **Test 2**: Select text (keyboard Shift+Arrow) → Verify detection works
- [ ] **Test 3**: Select 49 chars → Verify mode stays full-corpus (too short)
- [ ] **Test 4**: Select 50 chars → Verify mode switches to selected-text
- [ ] **Test 5**: Select 5001 chars → Verify warning or truncation

### UI Updates

- [ ] **Test 6**: Select text → Verify mode indicator updates to "🔍 Selected"
- [ ] **Test 7**: Select text → Verify selection preview shows char count
- [ ] **Test 8**: Clear selection → Verify mode reverts to "📚 Full"
- [ ] **Test 9**: Floating button appears near selection

### Stale Selection Handling

- [ ] **Test 10**: Select text on page A → Navigate to page B → Verify selection cleared
- [ ] **Test 11**: Select text → Reload page → Verify selection cleared

### Accessibility

- [ ] **Test 12**: Select text with keyboard → Verify detection works
- [ ] **Test 13**: Tab to floating button → Verify focusable
- [ ] **Test 14**: Screen reader → Verify "Selected text mode activated" announced
- [ ] **Test 15**: High-contrast mode → Verify selection highlighting visible

### Mobile

- [ ] **Test 16**: Long-press text (mobile) → Verify selection detected
- [ ] **Test 17**: Floating button positioned above selection (not obscured by handles)
- [ ] **Test 18**: Tap floating button → Verify widget opens in selected-text mode

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Selection detection latency | ≤100ms (with debouncing) |
| Floating button display | ≤50ms after selection |
| Mode switch latency | ≤50ms |
| Highlight rendering | ≤100ms |

---

## Error Handling

### Error 1: Selection API Not Supported

**Scenario**: Old browser doesn't support `window.getSelection()`

**Fallback**:
```typescript
if (!window.getSelection) {
  console.warn("Selection API not supported. Selected-text mode disabled.");
  disableSelectedTextMode();
}
```

### Error 2: Selection Spans Multiple Frames (iframes)

**Scenario**: User selects text across iframe boundary

**Behavior**:
- Modern browsers: `getSelection()` returns empty string (cross-origin security)
- Fallback: Widget shows warning "Cannot select text across iframes"

---

## References

- **Selection API**: [MDN - Window.getSelection()](https://developer.mozilla.org/en-US/docs/Web/API/Window/getSelection)
- **selectionchange Event**: [MDN - selectionchange](https://developer.mozilla.org/en-US/docs/Web/API/Document/selectionchange_event)
- **Mode-Switching Guide**: `specs/003-chatkit-widget/integration/mode-switching.md`
- **spec.md US2**: Lines 88-114

---

**Status**: Design Guide Complete ✅
**Next Step**: Implement text selection detection (Phase 7+)
