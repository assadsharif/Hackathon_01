# Keyboard Navigation Flows Guide

**Document Type**: Integration Guide
**User Story**: US4 (Accessibility & Keyboard Navigation)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This guide documents complete keyboard navigation workflows for the ChatKit widget, ensuring 100% keyboard operability per WCAG 2.1 AA standards.

**Requirements**:
- FR-024: Widget MUST be fully navigable via keyboard (Tab, Shift+Tab, Enter, Escape)
- NFR-005: Widget MUST achieve 100% keyboard navigation coverage

**Design Principle**: Every mouse interaction has a keyboard equivalent

---

## Keyboard Shortcuts Reference

| Key | Action | Context | Behavior |
|-----|--------|---------|----------|
| **Tab** | Move focus forward | Any | Focus moves to next interactive element |
| **Shift+Tab** | Move focus backward | Any | Focus moves to previous interactive element |
| **Enter** | Activate element | Focusable element | Activates button, link, or input submission |
| **Space** | Activate button | Button focused | Same as Enter for buttons |
| **Escape** | Close/Cancel | Widget open | Closes widget/modal, returns focus to trigger |
| **Arrow Up/Down** | Navigate list | Conversation history | Scrolls through messages |
| **Arrow Left/Right** | Switch mode | Mode toggle focused | Switches between Full-Corpus and Selected-Text |
| **Home** | Jump to start | Input field | Moves cursor to beginning of text |
| **End** | Jump to end | Input field | Moves cursor to end of text |
| **Ctrl+A** | Select all | Input field | Selects all text in input |
| **Shift+Arrow** | Extend selection | Documentation page | Extends text selection for selected-text mode |

---

## Navigation Flow 1: Opening the Widget

### Starting State: Widget Closed

**Visual State**: Floating widget button visible on page (bottom-right corner)

**Keyboard Flow**:

```
1. User presses Tab repeatedly to navigate page
   ↓
2. Focus reaches widget button (visual indicator: outline around button)
   Browser announces: "Open chat to ask questions, button"
   ↓
3. User presses Enter or Space
   ↓
4. Widget panel slides open (CSS animation)
   ↓
5. Focus automatically moves to chat input field
   Browser announces: "Type your question about Physical AI, edit text"
```

**Design-Level Focus Management**:
```typescript
// When widget opens
function openWidget() {
  widgetPanel.style.display = 'block';
  widgetPanel.setAttribute('aria-hidden', 'false');

  // Auto-focus input field (WCAG 2.4.3 Focus Order)
  setTimeout(() => {
    chatInput.focus();
  }, 300);  // Wait for CSS animation to complete

  // Update widget button state
  widgetButton.setAttribute('aria-expanded', 'true');
}
```

**Accessibility**:
- [ ] Widget button has `aria-expanded="false"` when closed
- [ ] Widget button has `aria-expanded="true"` when open
- [ ] Widget panel has `aria-hidden="true"` when closed
- [ ] Focus moves to input field automatically (2.4.3 Focus Order)

---

## Navigation Flow 2: Asking a Question

### Starting State: Widget Open, Input Field Focused

**Keyboard Flow**:

```
1. Input field is focused (cursor blinking)
   Browser announces: "Type your question about Physical AI, edit text"
   ↓
2. User types question: "What is embodied intelligence?"
   (No announcement while typing)
   ↓
3. User presses Enter
   ↓
4. Widget emits user_message event, transitions to Processing state
   Browser announces: "Processing your question..." (aria-live="polite")
   ↓
5. Focus remains on input field (disabled during processing)
   Input field shows placeholder: "Processing..."
   ↓
6. RAG agent responds, widget transitions to Responding state
   Browser announces: "Answer ready. Embodied intelligence refers to..." (aria-live="polite")
   ↓
7. Input field re-enabled, placeholder restored: "Ask a follow-up question..."
   Focus returns to input field
```

**Alternative: Tab to Submit Button**:
```
1. Input field focused, user types question
   ↓
2. User presses Tab
   Focus moves to Submit button
   Browser announces: "Submit question, button"
   ↓
3. User presses Enter or Space
   Widget submits question (same as pressing Enter in input field)
```

**Design-Level Input Handling**:
```typescript
// Input field Enter key
chatInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    submitQuestion(chatInput.value);
  }
});

// Submit button click (keyboard: Enter or Space)
submitButton.addEventListener('click', () => {
  submitQuestion(chatInput.value);
});

function submitQuestion(text: string) {
  // Disable input during processing
  chatInput.disabled = true;
  chatInput.placeholder = 'Processing...';

  // Announce to screen readers
  announceToScreenReader('Processing your question...', 'polite');

  // Emit user_message event
  emitEvent({ event: 'user_message', message: { content: text } });
}
```

**Accessibility**:
- [ ] Input field has `aria-label` or `<label>` element
- [ ] Submit button has `aria-label="Submit question"`
- [ ] Processing state announced via `aria-live="polite"`
- [ ] Input disabled during processing (visual + programmatic)

---

## Navigation Flow 3: Navigating Mode Toggle

### Starting State: Widget Open, Full-Corpus Mode Active

**Keyboard Flow**:

```
1. User presses Tab (from input field or submit button)
   Focus moves to mode toggle (Full-Corpus button)
   Browser announces: "Full-Corpus Mode, radio button, checked, 1 of 2"
   ↓
2. User presses Arrow Right (or Arrow Down)
   Focus moves to Selected-Text mode button
   Browser announces: "Selected-Text Mode, radio button, not checked, 2 of 2"
   ↓
3. User presses Enter or Space
   Mode switches to Selected-Text
   Browser announces: "Selected-Text mode activated. Please select text on the page."
   ↓
4. Visual indicator updates: Selected-Text button highlighted
   Full-Corpus button unhighlighted
```

**Design-Level Mode Toggle**:
```html
<div role="radiogroup" aria-label="Retrieval mode" class="mode-toggle">
  <button role="radio"
          aria-checked="true"
          aria-label="Full-Corpus Mode"
          data-mode="full-corpus">
    📚 Full
  </button>
  <button role="radio"
          aria-checked="false"
          aria-label="Selected-Text Mode"
          data-mode="selected-text">
    🔍 Selected
  </button>
</div>
```

```typescript
// Arrow key navigation within radiogroup
modeToggle.addEventListener('keydown', (event) => {
  const buttons = modeToggle.querySelectorAll('[role="radio"]');
  const currentIndex = Array.from(buttons).findIndex(b => b === document.activeElement);

  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    const nextIndex = (currentIndex + 1) % buttons.length;
    buttons[nextIndex].focus();
  } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    const prevIndex = (currentIndex - 1 + buttons.length) % buttons.length;
    buttons[prevIndex].focus();
  } else if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    switchMode(buttons[currentIndex].dataset.mode);
  }
});
```

**Accessibility**:
- [ ] Mode toggle uses `role="radiogroup"` (mutually exclusive options)
- [ ] Each button has `role="radio"` and `aria-checked="true|false"`
- [ ] Arrow keys move focus between modes (ARIA authoring practices)
- [ ] Enter/Space activates mode switch

---

## Navigation Flow 4: Navigating Citations

### Starting State: Answer Rendered with 3 Citations

**Keyboard Flow**:

```
1. User presses Tab (from mode toggle)
   Focus moves to first citation link [1]
   Browser announces: "Citation 1: Module 2, Embodied Intelligence, Definition section, link"
   ↓
2. User presses Tab again
   Focus moves to second citation link [2]
   Browser announces: "Citation 2: Module 2, Sensorimotor Integration, Perception-Action Loop, link"
   ↓
3. User presses Enter (on citation [2])
   Browser navigates to /docs/module-2-embodied/sensorimotor-integration#perception-action-loop
   Page scrolls to section anchor
   Browser announces: "Navigating to source: Module 2, Sensorimotor Integration"
```

**Design-Level Citation Links**:
```html
<p class="message-content">
  Embodied intelligence refers to...
  <a href="/docs/module-2-embodied/embodied-intelligence#definition"
     class="citation-link"
     aria-label="Citation 1: Module 2, Embodied Intelligence, Definition section">
    <sup>[1]</sup>
  </a>
  This contrasts with traditional AI...
  <a href="/docs/module-2-embodied/sensorimotor-integration#perception-action-loop"
     class="citation-link"
     aria-label="Citation 2: Module 2, Sensorimotor Integration, Perception-Action Loop">
    <sup>[2]</sup>
  </a>
</p>
```

**Accessibility**:
- [ ] Citation links have descriptive `aria-label` (not just "[1]")
- [ ] Citation links are in DOM order (chronological)
- [ ] Focus visible on citation links (`:focus` outline)
- [ ] Navigation to source announced to screen readers

---

## Navigation Flow 5: Closing the Widget

### Starting State: Widget Open, Focus on Any Element

**Method 1: Escape Key**

**Keyboard Flow**:
```
1. Widget open, focus on input field (or any element inside widget)
   ↓
2. User presses Escape
   ↓
3. Widget panel closes (CSS animation)
   ↓
4. Focus returns to widget button (trigger element)
   Browser announces: "Open chat to ask questions, button, collapsed"
```

**Method 2: Close Button**

**Keyboard Flow**:
```
1. User presses Tab repeatedly until close button is focused
   Browser announces: "Close chat panel, button"
   ↓
2. User presses Enter or Space
   ↓
3. Widget panel closes (CSS animation)
   ↓
4. Focus returns to widget button
```

**Design-Level Close Behavior**:
```typescript
// Escape key handler (global)
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && widgetIsOpen) {
    closeWidget();
  }
});

// Close button click
closeButton.addEventListener('click', () => {
  closeWidget();
});

function closeWidget() {
  widgetPanel.style.display = 'none';
  widgetPanel.setAttribute('aria-hidden', 'true');
  widgetButton.setAttribute('aria-expanded', 'false');

  // Return focus to widget button (WCAG 2.4.3 Focus Order)
  widgetButton.focus();

  // Announce to screen readers
  announceToScreenReader('Chat panel closed', 'polite');
}
```

**Accessibility**:
- [ ] Escape key closes widget from anywhere inside widget
- [ ] Close button has `aria-label="Close chat panel"`
- [ ] Focus returns to widget button (trigger element)
- [ ] Widget panel has `aria-hidden="true"` when closed

---

## Navigation Flow 6: Modal Focus Trap (Signup Modal)

### Starting State: User Clicks "Save Progress", Signup Modal Opens

**Keyboard Flow**:

```
1. Signup modal opens (overlay blocks main content)
   Focus automatically moves to first input (email field)
   Browser announces: "Signup modal opened. Email, edit text, required"
   ↓
2. User types email, presses Tab
   Focus moves to password field
   Browser announces: "Password, edit text, required"
   ↓
3. User types password, presses Tab
   Focus moves to "Create Account" button
   Browser announces: "Create Account, button"
   ↓
4. User presses Tab again
   Focus moves to "Cancel" button
   Browser announces: "Cancel, button"
   ↓
5. User presses Tab again
   Focus LOOPS BACK to email field (focus trap)
   Browser announces: "Email, edit text, required"
```

**Alternative: Escape to Close**

**Keyboard Flow**:
```
1. Modal open, focus on any field
   ↓
2. User presses Escape
   ↓
3. Modal closes
   ↓
4. Focus returns to "Save Progress" button (trigger element)
   Browser announces: "Save Progress, button"
```

**Design-Level Focus Trap**:
```typescript
function openModal(modalElement: HTMLElement, triggerElement: HTMLElement) {
  modalElement.style.display = 'block';
  modalElement.setAttribute('aria-hidden', 'false');

  // Store trigger element for focus restoration
  modalElement.dataset.triggerElement = triggerElement.id;

  // Get all focusable elements inside modal
  const focusableElements = modalElement.querySelectorAll(
    'input, button, textarea, select, a[href]'
  );
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  // Auto-focus first element
  firstFocusable.focus();

  // Focus trap: Tab from last element loops to first
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
      closeModal(modalElement);
    }
  });
}

function closeModal(modalElement: HTMLElement) {
  modalElement.style.display = 'none';
  modalElement.setAttribute('aria-hidden', 'true');

  // Restore focus to trigger element
  const triggerElementId = modalElement.dataset.triggerElement;
  const triggerElement = document.getElementById(triggerElementId);
  triggerElement.focus();
}
```

**Accessibility**:
- [ ] Focus trapped inside modal (Tab loops: first → last → first)
- [ ] Shift+Tab reverses focus order
- [ ] Escape closes modal and restores focus to trigger
- [ ] Modal has `aria-modal="true"` and `role="dialog"`
- [ ] Background content has `aria-hidden="true"` when modal open

---

## Navigation Flow 7: Text Selection (Keyboard)

### Starting State: User Wants to Use Selected-Text Mode with Keyboard

**Keyboard Flow**:

```
1. User navigates to documentation page (not widget)
   ↓
2. User presses Shift+Arrow Right (repeatedly)
   Text selection extends character-by-character
   Browser announces: (no announcement during selection)
   ↓
3. User selects 250 characters (paragraph about vision sensors)
   Widget detects selection via `selectionchange` event
   Browser announces: "Selected text mode activated. Asking about 250 characters from Multimodal Sensing."
   ↓
4. Floating "Ask" button appears near selection
   ↓
5. User presses Tab (repeatedly) until floating button is focused
   Browser announces: "Ask about this selection, button"
   ↓
6. User presses Enter
   Widget opens in selected-text mode with selected text pre-loaded
```

**Design-Level Keyboard Selection**:
```typescript
// Listen for selection changes (keyboard or mouse)
document.addEventListener('selectionchange', () => {
  const selection = window.getSelection();
  const text = selection.toString().trim();

  if (text.length >= 50) {
    // Show floating "Ask" button
    showFloatingAskButton(selection.getRangeAt(0));

    // Announce to screen readers
    announceToScreenReader(
      `Selected text mode activated. Asking about ${text.length} characters from ${getCurrentPageTitle()}.`,
      'polite'
    );
  }
});

// Floating button must be keyboard-accessible
function showFloatingAskButton(range: Range) {
  const rect = range.getBoundingClientRect();

  floatingButton.style.top = `${rect.top - 40}px`;
  floatingButton.style.left = `${rect.left}px`;
  floatingButton.style.display = 'block';

  // Make keyboard-focusable
  floatingButton.setAttribute('tabindex', '0');
  floatingButton.setAttribute('aria-label', 'Ask about this selection');

  // Enter/Space activates
  floatingButton.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openWidgetWithSelection(window.getSelection().toString());
    }
  });
}
```

**Accessibility**:
- [ ] Keyboard text selection works (Shift+Arrow, Shift+Ctrl+Arrow)
- [ ] Floating button is keyboard-focusable (`tabindex="0"`)
- [ ] Floating button activates with Enter or Space
- [ ] Selection announcement via `aria-live="polite"`

---

## Focus Visible Styles

### Requirement: All Focusable Elements Have Visible Outline

**Design-Level CSS**:

```css
/* Global focus styles (WCAG 2.4.7 Focus Visible) */
*:focus {
  outline: 2px solid #0078D4;  /* ≥3:1 contrast ratio */
  outline-offset: 2px;
}

/* Button focus */
button:focus {
  outline: 2px solid #0078D4;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 120, 212, 0.2);  /* Additional visual indicator */
}

/* Input field focus */
input:focus,
textarea:focus {
  outline: 2px solid #0078D4;
  outline-offset: 2px;
  border-color: #0078D4;
}

/* Citation link focus */
.citation-link:focus {
  outline: 2px solid #0078D4;
  outline-offset: 2px;
  text-decoration: underline;
}

/* Skip link (visible on focus only) */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #0078D4;
  color: #FFF;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;  /* Becomes visible when focused */
}

/* High-contrast mode (Windows) */
@media (prefers-contrast: high) {
  *:focus {
    outline: 3px solid;  /* Thicker outline for high-contrast */
    outline-offset: 3px;
  }
}
```

**Accessibility**:
- [ ] All focusable elements have `:focus` outline (≥3:1 contrast)
- [ ] Outline visible in both light and dark mode
- [ ] Outline visible in high-contrast mode
- [ ] Skip link visible on Tab focus

---

## Tab Order Summary

**Complete Tab Order** (Widget Open):

1. **Widget Button** (if widget closed) → Opens widget
2. **Skip Link** (hidden until focused) → Jumps to input
3. **Chat Input Field** → Type question
4. **Submit Button** → Send question
5. **Mode Toggle (Full-Corpus)** → Switch to full-corpus mode
6. **Mode Toggle (Selected-Text)** → Switch to selected-text mode
7. **Citation Link [1]** → Navigate to source
8. **Citation Link [2]** → Navigate to source
9. **Citation Link [3]** → Navigate to source
10. **Close Button** → Close widget

**Tab Order Validation**:
- [ ] Order matches visual layout (left-to-right, top-to-bottom)
- [ ] No unexpected focus jumps
- [ ] Tab order preserves meaning (WCAG 2.4.3)

---

## Testing Checklist

### Keyboard Navigation Tests

- [ ] **Test 1**: Tab to widget button → Press Enter → Verify widget opens, focus on input
- [ ] **Test 2**: Type question → Press Enter → Verify question submitted
- [ ] **Test 3**: Tab to mode toggle → Arrow Right → Verify mode switches
- [ ] **Test 4**: Tab to citation link → Press Enter → Verify navigates to source
- [ ] **Test 5**: Press Escape → Verify widget closes, focus returns to button
- [ ] **Test 6**: Shift+Tab (reverse order) → Verify focus moves backward

### Focus Trap Tests

- [ ] **Test 7**: Open signup modal → Tab to last element → Tab again → Verify focus loops to first element
- [ ] **Test 8**: Modal open → Press Escape → Verify modal closes, focus returns to trigger
- [ ] **Test 9**: Modal open → Shift+Tab from first element → Verify focus moves to last element

### Focus Visible Tests

- [ ] **Test 10**: Tab to any element → Verify visible outline (≥3:1 contrast)
- [ ] **Test 11**: Enable high-contrast mode → Verify outlines still visible
- [ ] **Test 12**: Tab to skip link → Verify link becomes visible

### Keyboard Selection Tests

- [ ] **Test 13**: Shift+Arrow to select text → Verify floating button appears
- [ ] **Test 14**: Tab to floating button → Press Enter → Verify widget opens in selected-text mode
- [ ] **Test 15**: Ctrl+A in input field → Verify all text selected

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| Tab navigation latency | ≤50ms per Tab press | NFR-002 |
| Focus outline render | ≤10ms | CSS performance |
| Modal focus trap setup | ≤100ms | Modal open latency |
| Keyboard shortcut response | ≤50ms | User perception threshold |

---

## References

- **WCAG 2.1 Keyboard**: https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html
- **ARIA Authoring Practices**: https://www.w3.org/WAI/ARIA/apg/ (keyboard patterns)
- **FR-024**: Keyboard navigation requirement (spec.md line 306)
- **NFR-005**: 100% keyboard coverage (spec.md line 346)
- **WCAG 2.4.3**: Focus Order
- **WCAG 2.4.7**: Focus Visible

---

**Status**: Design Guide Complete ✅
**Next Step**: Implement keyboard navigation (Phase 7+)
