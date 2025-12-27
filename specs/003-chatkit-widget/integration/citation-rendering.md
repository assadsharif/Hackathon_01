# Citation-Aware Message Rendering Guide

**Document Type**: Integration Guide
**User Story**: US1 (Frictionless Q&A)
**Pattern**: Pattern 4 (Citation-Aware Message Rendering)
**Phase**: 6 (Design Specification)
**Created**: 2025-12-26

---

## Overview

This guide documents how to render chat messages with **inline citations** that link back to source documentation using the Stable-ID pattern.

**Requirements**:
- FR-009: Widget MUST display citations as inline superscript numbers (e.g., [1], [2])
- FR-010: Widget MUST render citation links that navigate to the exact documentation section

**Pattern Reference**: Pattern 4 (Citation-Aware Message Rendering) in `.claude/skills/chatkit-widget/patterns.md` lines 419-556

---

## Citation Data Structure

### agent_response Event with Citations

**Event**: `agent_response`
**Source**: RAG Orchestration Subagent (`.claude/agents/rag-orchestration/`)

```json
{
  "event": "agent_response",
  "timestamp": "2025-12-26T10:30:02.500Z",
  "session_id": "uuid-v4-string",
  "message": {
    "id": "response-uuid",
    "type": "text",
    "content": "Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences. This differs from traditional AI approaches that treat intelligence as purely computational.",
    "citations": [
      {
        "id": "citation-1",
        "module_id": "module-2-embodied",
        "chapter_id": "embodied-intelligence",
        "section_id": "definition",
        "url": "/docs/module-2-embodied/embodied-intelligence#definition",
        "excerpt": "Embodied intelligence is the idea that intelligence is not just a product of computational processes, but emerges from the body's interaction with the environment."
      },
      {
        "id": "citation-2",
        "module_id": "module-2-embodied",
        "chapter_id": "sensorimotor-integration",
        "section_id": "perception-action-loop",
        "url": "/docs/module-2-embodied/sensorimotor-integration#perception-action-loop",
        "excerpt": "The perception-action loop is fundamental to embodied intelligence, where sensory input directly influences motor output."
      }
    ],
    "metadata": {
      "mode": "full-corpus",
      "retrieval_count": 5,
      "synthesis_time_ms": 1200,
      "guardrails_passed": true
    }
  }
}
```

---

## Citation Rendering Strategies

### Strategy 1: Inline Superscript Numbers (Recommended)

**Format**: Answer text with superscript citation numbers

**Example Rendering**:
```
Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences.[1] This differs from traditional AI approaches that treat intelligence as purely computational.[2]
```

**HTML Structure** (design-level):
```html
<div class="message agent">
  <p class="message-content">
    Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences.
    <a href="/docs/module-2-embodied/embodied-intelligence#definition" class="citation-link" data-citation-id="citation-1">
      <sup>[1]</sup>
    </a>
    This differs from traditional AI approaches that treat intelligence as purely computational.
    <a href="/docs/module-2-embodied/sensorimotor-integration#perception-action-loop" class="citation-link" data-citation-id="citation-2">
      <sup>[2]</sup>
    </a>
  </p>
</div>
```

**CSS Styling** (design-level):
```css
.citation-link {
  text-decoration: none;
  color: var(--primary-color);
  font-weight: 500;
}

.citation-link:hover {
  text-decoration: underline;
}

.citation-link sup {
  font-size: 0.8em;
  vertical-align: super;
}
```

---

### Strategy 2: Footnote List (Alternative)

**Format**: Answer text followed by footnote list

**Example Rendering**:
```
Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences. This differs from traditional AI approaches that treat intelligence as purely computational.

Sources:
[1] Module 2: Embodied Intelligence > Definition
    "Embodied intelligence is the idea that intelligence is not just a product of computational processes..."

[2] Module 2: Sensorimotor Integration > Perception-Action Loop
    "The perception-action loop is fundamental to embodied intelligence..."
```

**HTML Structure** (design-level):
```html
<div class="message agent">
  <p class="message-content">
    Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences. This differs from traditional AI approaches that treat intelligence as purely computational.
  </p>

  <div class="citations-list">
    <h4 class="citations-header">Sources:</h4>
    <ol class="citations">
      <li class="citation-item">
        <a href="/docs/module-2-embodied/embodied-intelligence#definition" class="citation-link">
          Module 2: Embodied Intelligence > Definition
        </a>
        <p class="citation-excerpt">"Embodied intelligence is the idea that intelligence is not just a product of computational processes..."</p>
      </li>
      <li class="citation-item">
        <a href="/docs/module-2-embodied/sensorimotor-integration#perception-action-loop" class="citation-link">
          Module 2: Sensorimotor Integration > Perception-Action Loop
        </a>
        <p class="citation-excerpt">"The perception-action loop is fundamental to embodied intelligence..."</p>
      </li>
    </ol>
  </div>
</div>
```

---

## Citation URL Generation

### Stable-ID Pattern

**Input**: Citation object from `agent_response`

```json
{
  "id": "citation-1",
  "module_id": "module-2-embodied",
  "chapter_id": "embodied-intelligence",
  "section_id": "definition",
  "url": "/docs/module-2-embodied/embodied-intelligence#definition",
  "excerpt": "..."
}
```

**Output**: Full URL with hash anchor

**Design-Level Logic**:
```typescript
function generateCitationURL(citation: Citation): string {
  // Option 1: Use pre-generated URL from RAG agent (recommended)
  if (citation.url) {
    return citation.url;
  }

  // Option 2: Construct URL from Stable-ID components
  const basePath = "/docs";
  const modulePath = citation.module_id;
  const chapterPath = citation.chapter_id;
  const sectionAnchor = citation.section_id;

  return `${basePath}/${modulePath}/${chapterPath}#${sectionAnchor}`;
}
```

**Example URLs**:
```
/docs/module-2-embodied/embodied-intelligence#definition
/docs/module-4-perception/multimodal-sensing#vision-sensors
/docs/module-6-learning/reinforcement-learning#policy-gradients
```

---

### Citation Click Behavior

**Trigger**: User clicks citation link (e.g., [1])

**Behavior**:
1. Navigate to citation URL (e.g., `/docs/module-2-embodied/embodied-intelligence#definition`)
2. Scroll page to section anchor (`#definition`)
3. Highlight cited section briefly (optional: 2-second yellow highlight fade)
4. Maintain chat panel state (keep open or close based on user preference)

**Accessibility**:
- Ensure citation links are keyboard-navigable (Tab key)
- Provide ARIA labels: `aria-label="Citation 1: Module 2, Embodied Intelligence"`
- Announce navigation to screen readers: "Navigating to source: Module 2, Embodied Intelligence"

---

## Citation Hover Previews (Optional Enhancement)

**Feature**: Show citation excerpt on hover

**Behavior**:
1. User hovers over citation link (e.g., [1])
2. Tooltip appears with excerpt text
3. Tooltip includes "Click to view source" hint

**HTML Structure** (design-level):
```html
<a href="/docs/module-2-embodied/embodied-intelligence#definition"
   class="citation-link"
   data-citation-id="citation-1"
   title="Embodied intelligence is the idea that intelligence is not just a product of computational processes..."
   aria-describedby="citation-tooltip-1">
  <sup>[1]</sup>
</a>

<div id="citation-tooltip-1" class="citation-tooltip" role="tooltip" hidden>
  <p class="citation-excerpt">
    "Embodied intelligence is the idea that intelligence is not just a product of computational processes, but emerges from the body's interaction with the environment."
  </p>
  <span class="citation-hint">Click to view source →</span>
</div>
```

**CSS Styling** (design-level):
```css
.citation-tooltip {
  position: absolute;
  background: var(--tooltip-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px 12px;
  max-width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.citation-excerpt {
  font-size: 0.9em;
  font-style: italic;
  margin-bottom: 4px;
}

.citation-hint {
  font-size: 0.8em;
  color: var(--primary-color);
}
```

---

## Citation Count Display

**Feature**: Show total citation count in message footer

**Example Rendering**:
```
Embodied intelligence refers to the theory that intelligence emerges from the interaction between an agent's body, environment, and sensorimotor experiences.[1] This differs from traditional AI approaches that treat intelligence as purely computational.[2]

📚 2 sources
```

**HTML Structure** (design-level):
```html
<div class="message agent">
  <p class="message-content">...</p>
  <div class="message-footer">
    <span class="citation-count">📚 2 sources</span>
  </div>
</div>
```

---

## No Citations Scenario

**Condition**: `citations` array is empty (e.g., guardrails failure, out-of-scope question)

**Rendering**:
```
This question is outside the book's scope. I can only answer questions about Physical AI and Humanoid Robotics topics covered in the documentation.

No sources available.
```

**HTML Structure** (design-level):
```html
<div class="message agent">
  <p class="message-content">
    This question is outside the book's scope. I can only answer questions about Physical AI and Humanoid Robotics topics covered in the documentation.
  </p>
  <div class="message-footer">
    <span class="no-citations">No sources available.</span>
  </div>
</div>
```

---

## Multi-Module Citations

**Scenario**: Answer synthesizes information from multiple modules

**Example**: Query about "How do humanoid robots use vision for navigation?"

**Citations**:
- [1] Module 3: Humanoid Robotics > Bipedal Locomotion
- [2] Module 4: Perception > Multimodal Sensing > Vision Sensors
- [3] Module 4: Perception > Spatial Awareness

**Rendering with Module Labels**:
```
Humanoid robots use vision sensors to perceive their environment[1][2] and build spatial maps for navigation.[3]

Sources:
[1] Module 3: Humanoid Robotics > Bipedal Locomotion
[2] Module 4: Perception > Multimodal Sensing
[3] Module 4: Perception > Spatial Awareness
```

**Design Consideration**: Group citations by module for easier scanning

---

## Citation Rendering Performance

### Performance Targets

| Metric | Target | Test Scenario |
|--------|--------|---------------|
| Render 10 citations | ≤50ms | Typical RAG response |
| Render 100 citations | ≤100ms | Extensive multi-module answer |
| Citation click latency | ≤10ms | Navigate to source |
| Hover tooltip display | ≤100ms | Show excerpt on hover |

**Optimization**: Pre-generate citation HTML during `agent_response` event consumption

---

## Accessibility (WCAG 2.1 AA)

### Keyboard Navigation

- [ ] Citation links are focusable with Tab key
- [ ] Enter key activates citation link (navigates to source)
- [ ] Escape key dismisses hover tooltip
- [ ] Focus visible with outline (`:focus` CSS state)

### Screen Reader Support

- [ ] Citation links have descriptive ARIA labels:
  ```html
  <a href="..." aria-label="Citation 1: Module 2, Embodied Intelligence, Definition section">
    <sup>[1]</sup>
  </a>
  ```

- [ ] Citation count announced:
  ```html
  <span class="citation-count" aria-label="2 sources cited">📚 2 sources</span>
  ```

- [ ] Tooltip content announced on focus:
  ```html
  <div role="tooltip" aria-live="polite">...</div>
  ```

### High-Contrast Mode

- [ ] Citation links maintain ≥4.5:1 contrast ratio (WCAG AA)
- [ ] Hover/focus states have ≥3:1 contrast ratio
- [ ] Superscript numbers remain readable at 200% zoom

---

## Mobile Responsiveness

### Touch Target Size

- [ ] Citation links have ≥44x44px touch target (FR-028, WCAG 2.1 AA)
- [ ] Increase padding around superscript numbers for touch:
  ```css
  @media (max-width: 768px) {
    .citation-link {
      padding: 8px;
      margin: -8px;
    }
  }
  ```

### Citation Tooltip on Mobile

- [ ] Replace hover tooltip with tap-to-show tooltip on mobile
- [ ] Tooltip closes on outside tap or scroll
- [ ] Tooltip positioned above citation link (not off-screen)

---

## Error Handling

### Broken Citation Links

**Scenario**: Citation URL points to deleted or moved documentation page

**Fallback Behavior**:
1. Detect 404 error on citation click
2. Display inline warning: "⚠ Citation unavailable (content moved)"
3. Log broken citation event for analytics
4. Provide fallback: "Search for '{chapter_id}' in documentation"

**HTML Structure** (design-level):
```html
<a href="/docs/module-2-embodied/removed-page#section"
   class="citation-link citation-broken"
   aria-label="Citation 1: Source unavailable">
  <sup>[1]</sup>
  <span class="citation-warning">⚠</span>
</a>
```

---

### Missing Citation Fields

**Scenario**: RAG agent returns incomplete citation object (missing `url` or `excerpt`)

**Fallback Logic**:
```typescript
function renderCitation(citation: Citation): string {
  // Required field: url
  if (!citation.url) {
    console.error("Citation missing URL", citation);
    return `[${citation.id}]`; // Non-clickable placeholder
  }

  // Optional field: excerpt (use placeholder if missing)
  const excerpt = citation.excerpt || "Source excerpt not available";

  // Render citation link
  return `<a href="${citation.url}" title="${excerpt}">[${citation.id}]</a>`;
}
```

---

## Testing Checklist

### Citation Rendering

- [ ] **Test 1**: Message with 2 citations → Verify inline superscripts [1], [2] rendered
- [ ] **Test 2**: Click citation [1] → Verify navigates to correct documentation section
- [ ] **Test 3**: Hover citation [1] → Verify tooltip shows excerpt
- [ ] **Test 4**: Message with 0 citations → Verify "No sources available" displayed
- [ ] **Test 5**: Message with 10 citations → Verify all citations numbered correctly

### Accessibility

- [ ] **Test 6**: Tab navigation → Verify all citations focusable with visible outline
- [ ] **Test 7**: Screen reader → Verify ARIA labels announced correctly
- [ ] **Test 8**: 200% zoom → Verify citations remain readable
- [ ] **Test 9**: High-contrast mode → Verify citation links have ≥4.5:1 contrast

### Mobile

- [ ] **Test 10**: Mobile (375px) → Verify citation links have ≥44x44px touch targets
- [ ] **Test 11**: Tap citation on mobile → Verify navigates (no hover required)
- [ ] **Test 12**: Long-press citation → Verify context menu appears (browser default)

### Error Handling

- [ ] **Test 13**: Citation with missing `url` → Verify non-clickable placeholder rendered
- [ ] **Test 14**: Citation pointing to 404 page → Verify warning displayed
- [ ] **Test 15**: Malformed citation object → Verify widget doesn't crash, logs error

---

## Implementation Notes

### Citation Insertion Logic

**Design-Level Algorithm**:
```typescript
function insertCitations(content: string, citations: Citation[]): string {
  // Option 1: Append citations at end (simplest)
  const citationLinks = citations.map((c, i) =>
    `<a href="${c.url}" class="citation-link"><sup>[${i + 1}]</sup></a>`
  ).join(" ");

  return `${content} ${citationLinks}`;

  // Option 2: Smart inline insertion (advanced)
  // Parse content for sentence boundaries, insert citations contextually
  // Requires NLP or manual citation placement from RAG agent
}
```

**Recommendation**: Use Option 1 (append at end) for Phase 6-7, consider Option 2 for Phase 8+ if RAG agent provides citation positions.

---

### Citation Storage

**LocalStorage** (Anonymous Users):
```json
{
  "chatkit_history": [
    {
      "id": "msg-uuid",
      "role": "agent",
      "content": "Embodied intelligence refers to...",
      "citations": [
        {
          "id": "citation-1",
          "url": "/docs/module-2-embodied/embodied-intelligence#definition",
          "excerpt": "..."
        }
      ]
    }
  ]
}
```

**Server Storage** (Authenticated Users):
- Same schema as LocalStorage
- Citations stored with message in database
- Citations retrieved when loading conversation history

---

## References

- **Pattern 4 (Citation-Aware Rendering)**: `.claude/skills/chatkit-widget/patterns.md` lines 419-556
- **agent_response Event Schema**: `.claude/skills/chatkit-widget/SKILL.md` lines 112-138
- **Citation Object Schema**: `.claude/mcp/chatkit/mcp.json` lines 84-95
- **FR-009**: Citations as inline superscript numbers
- **FR-010**: Clickable citation links to documentation
- **Stable-ID Pattern**: `.claude/skills/rag-chatbot/patterns.md` (citation stable IDs)

---

**Status**: Design Guide Complete ✅
**Next Step**: Implement citation rendering UI (Phase 7+)
