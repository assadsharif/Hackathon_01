# WCAG 2.1 AA Compliance Checklist

**Document Type**: Implementation Checklist
**User Story**: US4 (Accessibility & Keyboard Navigation)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This checklist ensures the ChatKit widget meets **WCAG 2.1 Level AA** accessibility standards for users with disabilities.

**Requirements**:
- FR-024: Widget MUST be fully navigable via keyboard (Tab, Shift+Tab, Enter, Escape)
- FR-025: Widget MUST provide ARIA labels for all interactive elements
- FR-026: Widget MUST announce state changes to screen readers via ARIA live regions
- FR-027: Widget MUST support high-contrast mode and respect `prefers-reduced-motion`
- FR-028: Widget MUST have minimum touch target size of 44x44px (WCAG 2.1 AA)
- NFR-005: Widget MUST achieve 100% keyboard navigation coverage
- NFR-006: Color contrast ratio ≥4.5:1 for normal text, ≥3:1 for large text
- NFR-007: Widget MUST support screen readers (NVDA, JAWS, VoiceOver, TalkBack)
- NFR-008: Widget MUST be fully usable at 200% zoom (up to 400% zoom)

**Success Criterion**: SC-005 - Widget achieves WCAG 2.1 AA compliance (validated by automated + manual accessibility testing)

---

## WCAG 2.1 AA Principles

**POUR Principles**:
1. **Perceivable**: Information presented in ways all users can perceive
2. **Operable**: UI components are operable by all users
3. **Understandable**: Information and operation are understandable
4. **Robust**: Content works with current and future assistive technologies

---

## Principle 1: Perceivable

### 1.1 Text Alternatives (Level A)

#### 1.1.1 Non-Text Content (A)

**Requirement**: All non-text content has a text alternative

**Widget Elements**:
- [ ] **Widget Button Icon**: `<button aria-label="Open chat to ask questions"><svg>...</svg></button>`
- [ ] **Loading Spinner**: `<div role="status" aria-label="Loading answer"><svg>...</svg></div>`
- [ ] **Error Icon**: `<div role="alert" aria-label="Error occurred"><svg>...</svg></div>`
- [ ] **Citation Superscripts**: `<sup><a aria-label="Citation 1: Module 2, Embodied Intelligence">[1]</a></sup>`
- [ ] **Mode Icons** (📚 Full, 🔍 Selected): `<button aria-label="Full-Corpus Mode">📚 Full</button>`
- [ ] **Close Button (X)**: `<button aria-label="Close chat panel">✕</button>`

---

### 1.2 Time-Based Media (Level A/AA)

**Not Applicable**: ChatKit widget does not use time-based media (video, audio)

---

### 1.3 Adaptable (Level A)

#### 1.3.1 Info and Relationships (A)

**Requirement**: Information, structure, and relationships conveyed through presentation can be programmatically determined

**Widget Elements**:
- [ ] **Form Labels**: Input field has `<label>` or `aria-label`
  ```html
  <label for="chat-input">Type your question</label>
  <input id="chat-input" type="text" aria-required="true">
  ```
- [ ] **Heading Structure**: Chat messages use semantic headings
  ```html
  <h2 class="sr-only">Conversation History</h2>
  <div role="list">
    <div role="listitem">Message 1</div>
    <div role="listitem">Message 2</div>
  </div>
  ```
- [ ] **List Semantics**: Citations rendered as ordered list `<ol>`

#### 1.3.2 Meaningful Sequence (A)

**Requirement**: Reading order is logical

**Widget Flow**:
- [ ] Tab order matches visual order: widget button → input field → submit button → mode toggle → citations → close button
- [ ] Conversation history in chronological order (oldest first or newest first, but consistent)

#### 1.3.3 Sensory Characteristics (A)

**Requirement**: Instructions don't rely solely on sensory characteristics (shape, color, location)

**Widget Instructions**:
- [ ] **Bad**: "Click the blue button to submit"
- [ ] **Good**: "Click the Submit button (labeled 'Ask') to send your question"
- [ ] Mode toggle uses both icon AND text label: "📚 Full-Corpus Mode" (not just icon)

#### 1.3.4 Orientation (AA)

**Requirement**: Content not restricted to single display orientation

**Widget Behavior**:
- [ ] Widget works in both portrait and landscape orientations (mobile)
- [ ] No orientation lock (user can rotate device)

#### 1.3.5 Identify Input Purpose (AA)

**Requirement**: Input fields have autocomplete attributes

**Widget Elements**:
- [ ] Email input (signup): `<input type="email" autocomplete="email">`
- [ ] Password input (signup): `<input type="password" autocomplete="current-password">`
- [ ] Question input: `<input type="text" autocomplete="off">` (no autocomplete for questions)

---

### 1.4 Distinguishable (Level A/AA)

#### 1.4.1 Use of Color (A)

**Requirement**: Color is not the only visual means of conveying information

**Widget Elements**:
- [ ] **Error State**: Use icon + text + color (not color alone)
  ```html
  <div class="error" style="color: red;">
    ⚠️ Error: Unable to connect to server. <button>Retry</button>
  </div>
  ```
- [ ] **Mode Toggle**: Active mode uses color + `aria-pressed="true"` + visual indicator (not color alone)

#### 1.4.2 Audio Control (A)

**Not Applicable**: ChatKit widget does not auto-play audio

#### 1.4.3 Contrast (Minimum) (AA)

**Requirement**: Text has contrast ratio ≥4.5:1 for normal text, ≥3:1 for large text (18pt+)

**Widget Elements**:
- [ ] **Normal Text (14px)**: ≥4.5:1 contrast ratio
  - Example: Black text (#000) on white background (#FFF) = 21:1 ✅
  - Example: Gray text (#777) on white background (#FFF) = 4.6:1 ✅
- [ ] **Large Text (18px+)**: ≥3:1 contrast ratio
  - Example: Light gray (#AAA) on white (#FFF) = 3.1:1 ✅
- [ ] **Interactive Elements** (buttons, links): ≥4.5:1 contrast ratio
- [ ] **Focus Outline**: ≥3:1 contrast ratio against background

**Testing Tools**:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Chrome DevTools: Inspect element → Lighthouse → Accessibility audit

#### 1.4.4 Resize Text (AA)

**Requirement**: Text can be resized up to 200% without loss of content or functionality

**Widget Behavior**:
- [ ] At 200% zoom: All text remains readable (no horizontal scrolling inside widget)
- [ ] At 200% zoom: All buttons remain clickable (no overlapping elements)
- [ ] Use relative units: `font-size: 1rem` (not `16px`)

#### 1.4.5 Images of Text (AA)

**Requirement**: Prefer actual text over images of text

**Widget Elements**:
- [ ] Tier badges use text + emoji (not image): `<span>👤 Member</span>` ✅
- [ ] Mode icons use emoji + text (not image): `📚 Full-Corpus` ✅
- [ ] No logos rendered as text images

#### 1.4.10 Reflow (AA)

**Requirement**: Content reflows at 320px width (no horizontal scrolling)

**Widget Behavior**:
- [ ] Widget is responsive: works on 320px width (iPhone SE)
- [ ] Chat messages wrap to multiple lines (no horizontal scroll)
- [ ] Long URLs in citations wrap or truncate

#### 1.4.11 Non-Text Contrast (AA)

**Requirement**: UI components and graphical objects have ≥3:1 contrast ratio

**Widget Elements**:
- [ ] **Input Field Border**: ≥3:1 contrast against background
- [ ] **Button Border**: ≥3:1 contrast against background
- [ ] **Focus Outline**: ≥3:1 contrast against background (`:focus` state)

#### 1.4.12 Text Spacing (AA)

**Requirement**: No loss of content when user adjusts text spacing

**Widget Behavior**:
- [ ] User CSS overrides: `line-height: 1.5`, `letter-spacing: 0.12em`, `word-spacing: 0.16em`
- [ ] Widget content remains readable (no text clipping or overflow)

#### 1.4.13 Content on Hover or Focus (AA)

**Requirement**: Hover/focus content is dismissable, hoverable, and persistent

**Widget Elements**:
- [ ] **Citation Tooltip**:
  - Dismissable: Press Escape to close
  - Hoverable: User can move mouse over tooltip (tooltip doesn't disappear)
  - Persistent: Tooltip remains until dismissed (not auto-hide after 1 second)

---

## Principle 2: Operable

### 2.1 Keyboard Accessible (Level A)

#### 2.1.1 Keyboard (A)

**Requirement**: All functionality available via keyboard

**Widget Elements**:
- [ ] **Open Widget**: Tab to widget button → Press Enter
- [ ] **Type Question**: Tab to input field → Type question
- [ ] **Submit Question**: Tab to submit button → Press Enter (or press Enter in input field)
- [ ] **Navigate Mode Toggle**: Tab to mode toggle → Use Arrow keys to switch modes
- [ ] **Click Citation**: Tab to citation link → Press Enter
- [ ] **Close Widget**: Press Escape (or Tab to close button → Press Enter)

#### 2.1.2 No Keyboard Trap (A)

**Requirement**: Focus can always be moved away from any component using keyboard

**Widget Behavior**:
- [ ] **Modal Open**: Focus trapped inside modal (Tab cycles within modal)
- [ ] **Modal Close**: Press Escape → Focus returns to trigger element (no keyboard trap)
- [ ] **Widget Open**: Press Escape → Widget closes, focus returns to widget button

#### 2.1.4 Character Key Shortcuts (A)

**Requirement**: Single-character keyboard shortcuts can be turned off or remapped

**Widget Behavior**:
- [ ] No single-character shortcuts used (e.g., pressing "c" to close widget)
- [ ] All shortcuts require modifier keys (Ctrl, Alt) or are contextual (input field focused)

---

### 2.2 Enough Time (Level A)

#### 2.2.1 Timing Adjustable (A)

**Requirement**: Users can turn off, adjust, or extend time limits

**Widget Behavior**:
- [ ] **No Time Limits**: ChatKit widget has no session timeouts for Tier 0 (anonymous) users
- [ ] **Rate Limiting Warning**: Display 10-second countdown before enforcing rate limit (user can upgrade to avoid timeout)

#### 2.2.2 Pause, Stop, Hide (A)

**Requirement**: Users can pause, stop, or hide moving/auto-updating content

**Widget Behavior**:
- [ ] **No Auto-Play**: Widget does not auto-open or auto-scroll
- [ ] **Typing Indicator**: Animated "..." can be paused if user enables `prefers-reduced-motion`

---

### 2.3 Seizures and Physical Reactions (Level A/AA)

#### 2.3.1 Three Flashes or Below Threshold (A)

**Requirement**: No content flashes more than 3 times per second

**Widget Behavior**:
- [ ] **No Flashing Content**: Widget does not use flashing animations
- [ ] **Loading Spinner**: Smooth rotation (no flashing)

---

### 2.4 Navigable (Level A/AA)

#### 2.4.1 Bypass Blocks (A)

**Requirement**: Mechanism to skip repeated content

**Widget Behavior**:
- [ ] **Skip Link**: Provide "Skip to chat input" link for keyboard users (hidden until focused)
  ```html
  <a href="#chat-input" class="skip-link">Skip to chat input</a>
  ```

#### 2.4.2 Page Titled (A)

**Not Applicable**: ChatKit widget is embedded component (not a page)

#### 2.4.3 Focus Order (A)

**Requirement**: Focusable elements receive focus in an order that preserves meaning and operability

**Widget Focus Order**:
1. Widget button (to open chat)
2. Input field (to type question)
3. Submit button (to send question)
4. Mode toggle buttons (Full-Corpus / Selected-Text)
5. Citation links (in chronological order)
6. Close button (to close chat)

**Validation**:
- [ ] Tab order matches visual order (left to right, top to bottom)
- [ ] Focus does not jump unexpectedly (e.g., submit button → citation link is logical)

#### 2.4.4 Link Purpose (In Context) (A)

**Requirement**: Purpose of each link can be determined from link text alone

**Widget Elements**:
- [ ] **Good**: Citation link = "Citation 1: Module 2, Embodied Intelligence" (ARIA label)
- [ ] **Bad**: Citation link = "Click here" (ambiguous)
- [ ] **Good**: "Export Data" button (clear purpose)

#### 2.4.5 Multiple Ways (AA)

**Not Applicable**: ChatKit widget is single-purpose component (ask questions)

#### 2.4.6 Headings and Labels (AA)

**Requirement**: Headings and labels describe topic or purpose

**Widget Elements**:
- [ ] **Chat Header**: "Physical AI & Humanoid Robotics - ChatKit" (describes widget purpose)
- [ ] **Input Label**: "Type your question about Physical AI" (describes input field)
- [ ] **Error Message**: "Error: Unable to connect to server" (describes error state)

#### 2.4.7 Focus Visible (AA)

**Requirement**: Keyboard focus indicator is visible

**Widget Elements**:
- [ ] **Focus Outline**: All focusable elements have visible `:focus` outline
  ```css
  button:focus {
    outline: 2px solid #0078D4;  /* ≥3:1 contrast */
    outline-offset: 2px;
  }
  ```
- [ ] **High-Contrast Mode**: Focus outline remains visible in high-contrast mode

---

### 2.5 Input Modalities (Level A/AA)

#### 2.5.1 Pointer Gestures (A)

**Requirement**: All multi-point or path-based gestures have single-pointer alternative

**Widget Behavior**:
- [ ] **No Multi-Touch Gestures**: Widget does not require pinch-to-zoom or two-finger swipe
- [ ] **Single-Tap**: All interactions use single tap (button, link, input field)

#### 2.5.2 Pointer Cancellation (A)

**Requirement**: Down-event does not execute action (wait for up-event)

**Widget Behavior**:
- [ ] **Button Click**: Execute on `mouseup` (not `mousedown`) to allow cancellation
- [ ] **Link Click**: User can cancel click by moving pointer away before release

#### 2.5.3 Label in Name (A)

**Requirement**: Visible label matches accessible name

**Widget Elements**:
- [ ] **Submit Button**: Visual label = "Ask", accessible name (`aria-label`) = "Ask" or "Submit question" ✅
- [ ] **Mode Toggle**: Visual label = "📚 Full", accessible name = "Full-Corpus Mode" ✅

#### 2.5.4 Motion Actuation (A)

**Requirement**: Functions activated by device motion can also be activated by UI

**Widget Behavior**:
- [ ] **No Motion Activation**: Widget does not use shake-to-undo or tilt-to-scroll

#### 2.5.5 Target Size (AA)

**Requirement**: Touch targets are at least 44x44px

**Widget Elements**:
- [ ] **Widget Button**: ≥44x44px (FR-028)
- [ ] **Submit Button**: ≥44x44px
- [ ] **Close Button**: ≥44x44px
- [ ] **Citation Links**: ≥44x44px touch target (add padding to increase hit area)
  ```css
  .citation-link {
    padding: 12px;  /* Increases touch target from 16px to 40px */
  }
  ```
- [ ] **Mode Toggle Buttons**: ≥44x44px

---

## Principle 3: Understandable

### 3.1 Readable (Level A/AA)

#### 3.1.1 Language of Page (A)

**Requirement**: Default language is programmatically determined

**Widget Elements**:
- [ ] **Widget Container**: `<div lang="en">...</div>` (English)
- [ ] **Multi-Language Support**: If user selects Spanish, update `lang="es"`

#### 3.1.2 Language of Parts (AA)

**Requirement**: Language of each passage is programmatically determined

**Widget Behavior**:
- [ ] **Code Snippets**: Mark code as no language `<code lang="none">...</code>`
- [ ] **Foreign Terms**: Mark foreign terms `<span lang="fr">raison d'être</span>`

---

### 3.2 Predictable (Level A/AA)

#### 3.2.1 On Focus (A)

**Requirement**: Receiving focus does not initiate a change of context

**Widget Behavior**:
- [ ] **Input Field Focus**: Does NOT auto-submit question on focus
- [ ] **Mode Toggle Focus**: Does NOT auto-switch modes on focus (requires click/Enter)

#### 3.2.2 On Input (A)

**Requirement**: Changing setting does not automatically cause change of context

**Widget Behavior**:
- [ ] **Input Field Typing**: Does NOT auto-submit question while typing
- [ ] **Mode Toggle Click**: Switches mode but does NOT submit question automatically

#### 3.2.3 Consistent Navigation (AA)

**Requirement**: Repeated navigation is in consistent order

**Widget Behavior**:
- [ ] **Tab Order**: Always consistent (input → submit → mode toggle → citations → close)
- [ ] **Modal Tab Order**: Always consistent (email → password → submit → cancel)

#### 3.2.4 Consistent Identification (AA)

**Requirement**: Components with same functionality are identified consistently

**Widget Elements**:
- [ ] **Submit Button**: Always labeled "Ask" or "Submit question" (not "Send" in one place, "Ask" in another)
- [ ] **Close Button**: Always labeled "Close chat panel" (not "Exit" or "Dismiss")

---

### 3.3 Input Assistance (Level A/AA)

#### 3.3.1 Error Identification (A)

**Requirement**: Input errors are identified and described to user

**Widget Behavior**:
- [ ] **Empty Input**: Display error "Please enter a question before submitting"
- [ ] **Network Error**: Display error "Unable to connect to server. Check your internet connection and try again."
- [ ] **ARIA Alert**: `<div role="alert">Error message</div>`

#### 3.3.2 Labels or Instructions (A)

**Requirement**: Labels or instructions are provided when user input is required

**Widget Elements**:
- [ ] **Input Field**: Placeholder = "Ask about Physical AI..." OR label = "Type your question"
- [ ] **Signup Email**: Label = "Email" + example = "example@email.com"
- [ ] **Signup Password**: Label = "Password" + requirement = "Minimum 8 characters"

#### 3.3.3 Error Suggestion (AA)

**Requirement**: Suggestions for fixing input errors are provided

**Widget Behavior**:
- [ ] **Invalid Email**: "Email format invalid. Example: user@example.com"
- [ ] **Short Password**: "Password too short (5 characters). Minimum 8 characters required."

#### 3.3.4 Error Prevention (Legal, Financial, Data) (AA)

**Requirement**: Submissions can be reversed, checked, or confirmed

**Widget Behavior**:
- [ ] **Delete Account**: Confirmation modal before deletion ("Are you sure? This cannot be undone.")
- [ ] **Session Upload**: Consent modal before uploading conversation history (GDPR)

---

## Principle 4: Robust

### 4.1 Compatible (Level A/AA)

#### 4.1.1 Parsing (A)

**Requirement**: Markup is well-formed (no duplicate IDs, proper nesting)

**Widget Validation**:
- [ ] **No Duplicate IDs**: Each element has unique ID
- [ ] **Proper Nesting**: `<button>` not nested inside `<a>`, etc.
- [ ] **Valid HTML**: Pass W3C HTML validator

#### 4.1.2 Name, Role, Value (A)

**Requirement**: All UI components have accessible name, role, and value

**Widget Elements**:
- [ ] **Input Field**: Name = "Type your question" (aria-label), Role = textbox, Value = user's text
- [ ] **Submit Button**: Name = "Submit question", Role = button, Value = N/A
- [ ] **Mode Toggle**: Name = "Full-Corpus Mode", Role = radio, Value = checked (aria-pressed="true")

#### 4.1.3 Status Messages (AA)

**Requirement**: Status messages can be programmatically determined

**Widget Behavior**:
- [ ] **Loading State**: `<div role="status" aria-live="polite">Loading answer...</div>`
- [ ] **Error State**: `<div role="alert" aria-live="assertive">Error: Unable to connect</div>`
- [ ] **Success State**: `<div role="status" aria-live="polite">Account created successfully!</div>`

---

## Testing Checklist

### Automated Testing

- [ ] **axe DevTools**: Run in Chrome DevTools → Lighthouse → Accessibility (target: 100 score)
- [ ] **WAVE**: WebAIM WAVE browser extension (0 errors, 0 contrast errors)
- [ ] **pa11y**: Command-line accessibility tester `pa11y https://widget-url.com`
- [ ] **Lighthouse CI**: Automated accessibility testing in CI/CD pipeline

### Manual Testing

#### Keyboard Navigation

- [ ] **Test 1**: Tab through entire widget (no keyboard traps)
- [ ] **Test 2**: Open widget with Enter key
- [ ] **Test 3**: Submit question with Enter key (from input field)
- [ ] **Test 4**: Close widget with Escape key
- [ ] **Test 5**: Navigate citations with Tab + Enter

#### Screen Reader Testing

- [ ] **NVDA** (Windows): All state changes announced
- [ ] **JAWS** (Windows): All ARIA labels read correctly
- [ ] **VoiceOver** (macOS): Tab order logical, all elements identified
- [ ] **TalkBack** (Android): Touch exploration works, buttons labeled

#### Visual Testing

- [ ] **200% Zoom**: All content readable, no horizontal scrolling
- [ ] **High-Contrast Mode** (Windows): All elements visible (≥4.5:1 contrast)
- [ ] **Dark Mode**: All text readable (≥4.5:1 contrast on dark background)
- [ ] **Color Blindness Simulation**: Errors visible without color (use icon + text)

#### Touch Target Testing

- [ ] **Mobile (375px)**: All buttons ≥44x44px touch targets
- [ ] **Tablet (768px)**: All interactive elements easily tappable
- [ ] **Apple Pencil / Stylus**: All elements responsive to stylus input

---

## Performance Targets

| Metric | Target | Source |
|--------|--------|--------|
| Lighthouse Accessibility Score | 100/100 | SC-005 |
| Keyboard Navigation Coverage | 100% | NFR-005 |
| ARIA Label Coverage | 100% of interactive elements | FR-025 |
| Screen Reader Support | NVDA, JAWS, VoiceOver, TalkBack | NFR-007 |
| Touch Target Size | ≥44x44px for all buttons | FR-028 |

---

## References

- **WCAG 2.1 Official**: https://www.w3.org/WAI/WCAG21/quickref/
- **FR-024 to FR-028**: Accessibility requirements (spec.md lines 306-310)
- **NFR-005 to NFR-008**: Accessibility NFRs (spec.md lines 346-349)
- **SC-005**: WCAG 2.1 AA compliance success criterion (spec.md line 415)
- **WebAIM**: https://webaim.org (accessibility resources)

---

**Status**: Design Checklist Complete ✅
**Next Step**: Implement WCAG 2.1 AA compliance (Phase 7+)
