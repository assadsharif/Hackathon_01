# Offline FAQ Structure: Static Content for Network Failures

**Feature**: ChatKit Widget Integration
**User Story**: US5 - Offline Mode & Graceful Degradation (P3)
**Task**: T046 - Document offline FAQ structure with static content, version control, and update workflow
**Date**: 2025-12-26
**Pattern Reference**: Pattern 5 (Graceful Degradation) - `.claude/skills/chatkit-widget/patterns.md`

---

## Overview

This guide documents the **Offline FAQ Structure** for ChatKit Widget to provide fallback answers when the RAG API is unavailable.

**Problem**: When the backend is down or the user is offline, showing "Service unavailable" with no content creates a poor user experience.

**Solution**: Pre-load a curated static FAQ with 30-50 high-value questions/answers covering core Physical AI topics. This FAQ is bundled with the widget and works 100% offline.

**Fallback Priority**:
1. **Tier 1**: Live RAG API (best quality, up-to-date)
2. **Tier 2**: Cached responses (top 100 questions, 7-day TTL)
3. **Tier 3**: Static FAQ (30-50 curated Q&A, bundled with widget) ← THIS GUIDE
4. **Tier 4**: Manual fallback (link to docs)

---

## Table of Contents

1. [FAQ Categories](#faq-categories)
2. [FAQ Data Structure](#faq-data-structure)
3. [FAQ Content Guidelines](#faq-content-guidelines)
4. [FAQ Storage Strategy](#faq-storage-strategy)
5. [FAQ Search and Matching Logic](#faq-search-and-matching-logic)
6. [FAQ Versioning Strategy](#faq-versioning-strategy)
7. [FAQ Update Workflow](#faq-update-workflow)
8. [FAQ vs. Cached Responses](#faq-vs-cached-responses)
9. [Testing Procedures](#testing-procedures)

---

## FAQ Categories

The static FAQ is organized into **7 categories** aligned with the Physical AI Book structure.

### Category 1: Getting Started (5 questions)

**Audience**: First-time users unfamiliar with the widget or Physical AI concepts.

**Example Questions**:
1. "How do I ask questions?" → "Type your question and press Enter..."
2. "Can I search specific sections?" → "Yes! Highlight any text, then ask..."
3. "How accurate are the answers?" → "Answers are sourced directly from the book..."
4. "Can I save my conversation history?" → "Yes, create a free account to save..."
5. "What topics are covered in this book?" → "Physical AI, humanoid robotics, embodied intelligence..."

**Purpose**: Help users understand widget functionality and book scope.

---

### Category 2: Physical AI Basics (8 questions)

**Audience**: Students learning foundational Physical AI concepts.

**Example Questions**:
1. "What is Physical AI?" → "Physical AI is intelligence that interacts with the physical world..."
2. "What is embodied intelligence?" → "Embodied intelligence refers to intelligence arising from agent-environment interaction..."
3. "What is the difference between AI and Physical AI?" → "Traditional AI operates in digital environments, Physical AI operates in physical environments..."
4. "Why is embodiment important for intelligence?" → "Embodiment provides grounding through sensorimotor experience..."
5. "What are the key challenges in Physical AI?" → "Handling uncertainty, real-time constraints, safety, sim-to-real transfer..."
6. "What is the sense-think-act loop?" → "The cycle of perception, decision-making, and action execution..."
7. "What is the symbol grounding problem?" → "The challenge of connecting abstract symbols to real-world referents..."
8. "What are the applications of Physical AI?" → "Humanoid robots, autonomous vehicles, surgical robots, warehouse automation..."

**Purpose**: Answer foundational questions without requiring live RAG API.

---

### Category 3: Humanoid Robotics (8 questions)

**Audience**: Students interested in humanoid robot design and capabilities.

**Example Questions**:
1. "What is a humanoid robot?" → "A robot with human-like morphology (head, torso, arms, legs)..."
2. "Why build humanoid robots?" → "Human environments are designed for human morphology..."
3. "What are the main components of a humanoid robot?" → "Actuation, perception, control, power, computation..."
4. "What is bipedal locomotion?" → "Walking on two legs, requiring dynamic balance and gait control..."
5. "How do humanoid robots balance?" → "Using feedback control with IMU sensors and foot pressure sensors..."
6. "What is whole-body control?" → "Coordinating all joints to achieve task goals while maintaining balance..."
7. "What are degrees of freedom (DOF)?" → "Independent joint movements; humanoid robots typically have 20-40 DOF..."
8. "What are examples of humanoid robots?" → "Atlas (Boston Dynamics), Pepper (SoftBank), ASIMO (Honda), Optimus (Tesla)..."

**Purpose**: Cover high-interest humanoid robotics topics.

---

### Category 4: Perception & Sensing (5 questions)

**Audience**: Students learning about robot perception systems.

**Example Questions**:
1. "What sensors do humanoid robots use?" → "Cameras, LiDAR, IMU, force-torque sensors, tactile sensors..."
2. "What is computer vision for robotics?" → "Extracting 3D information from 2D images for navigation and manipulation..."
3. "What is LiDAR?" → "Light Detection and Ranging - uses lasers to measure distances and create 3D maps..."
4. "How do robots detect objects?" → "Using deep learning models (YOLO, Mask R-CNN) trained on visual data..."
5. "What is sensor fusion?" → "Combining data from multiple sensors to improve accuracy and robustness..."

**Purpose**: Answer perception-related questions offline.

---

### Category 5: Control & Motion Planning (5 questions)

**Audience**: Students learning about robot control systems.

**Example Questions**:
1. "What is inverse kinematics?" → "Computing joint angles to achieve a desired end-effector position..."
2. "What is motion planning?" → "Finding collision-free paths from start to goal configurations..."
3. "What is PID control?" → "Proportional-Integral-Derivative feedback control for tracking setpoints..."
4. "What is trajectory optimization?" → "Finding optimal motion trajectories that minimize cost (time, energy, jerk)..."
5. "What is impedance control?" → "Controlling force/torque in addition to position for compliant interaction..."

**Purpose**: Cover control theory basics.

---

### Category 6: Learning & AI (5 questions)

**Audience**: Students interested in machine learning for robotics.

**Example Questions**:
1. "What is reinforcement learning for robotics?" → "Learning control policies through trial-and-error interaction..."
2. "What is imitation learning?" → "Learning from expert demonstrations (teleoperation or motion capture)..."
3. "What is sim-to-real transfer?" → "Training policies in simulation and deploying to real robots..."
4. "What is the reality gap?" → "Discrepancy between simulation and real-world physics..."
5. "What is end-to-end learning?" → "Learning mappings from raw sensory input to control outputs..."

**Purpose**: Answer ML/AI questions without live API.

---

### Category 7: Future & Ethics (4 questions)

**Audience**: Students interested in societal impact and future directions.

**Example Questions**:
1. "What are the ethical concerns with humanoid robots?" → "Job displacement, privacy, autonomy, weaponization, bias..."
2. "Will robots replace human workers?" → "Robots will automate tasks, but create new jobs in design, maintenance, oversight..."
3. "What are emerging trends in Physical AI?" → "Foundation models for robotics, multimodal learning, generalist robots..."
4. "How can we ensure safe human-robot interaction?" → "ISO safety standards, fail-safes, collision detection, human-aware planning..."

**Purpose**: Address ethical and societal questions.

---

## FAQ Data Structure

### JSON Schema

```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-26",
  "total_questions": 40,
  "categories": [
    {
      "id": "getting-started",
      "name": "Getting Started",
      "description": "Learn how to use the ChatKit widget and navigate the book",
      "icon": "🚀",
      "order": 1,
      "questions": [
        {
          "id": "how-to-ask-questions",
          "question": "How do I ask questions?",
          "answer": "Type your question in the input field and press Enter. The chatbot will search the entire Physical AI & Humanoid Robotics book to find relevant answers with citations.",
          "keywords": ["ask", "question", "how to use", "tutorial"],
          "related_questions": ["can-i-search-specific-sections", "how-accurate-are-answers"],
          "module_reference": null,
          "date_added": "2025-12-26"
        },
        {
          "id": "can-i-search-specific-sections",
          "question": "Can I search specific sections?",
          "answer": "Yes! Highlight any text on the documentation page, then ask a follow-up question. The chatbot will focus on that selected passage and provide targeted explanations.",
          "keywords": ["highlight", "select", "specific section", "selected-text mode"],
          "related_questions": ["how-to-ask-questions"],
          "module_reference": null,
          "date_added": "2025-12-26"
        }
      ]
    },
    {
      "id": "physical-ai-basics",
      "name": "Physical AI Basics",
      "description": "Foundational concepts in Physical AI and embodied intelligence",
      "icon": "🤖",
      "order": 2,
      "questions": [
        {
          "id": "what-is-physical-ai",
          "question": "What is Physical AI?",
          "answer": "Physical AI is artificial intelligence that interacts with and acts upon the physical world through sensors and actuators. Unlike traditional AI that operates purely in digital environments, Physical AI systems perceive their surroundings, make decisions, and execute physical actions (e.g., humanoid robots, autonomous vehicles, surgical robots).",
          "keywords": ["physical ai", "definition", "embodied ai", "robotics"],
          "related_questions": ["what-is-embodied-intelligence", "difference-ai-physical-ai"],
          "module_reference": {
            "module_id": "module-1-intro",
            "chapter_id": "what-is-physical-ai",
            "url": "/docs/module-1-intro/what-is-physical-ai"
          },
          "date_added": "2025-12-26"
        },
        {
          "id": "what-is-embodied-intelligence",
          "question": "What is embodied intelligence?",
          "answer": "Embodied intelligence is the theory that intelligence arises from the interaction between an agent's body and its environment. Rather than abstract reasoning in isolation, embodied intelligence emphasizes sensorimotor experience, physical grounding, and real-time feedback loops. This contrasts with disembodied approaches like traditional symbolic AI.",
          "keywords": ["embodied", "intelligence", "grounding", "sensorimotor"],
          "related_questions": ["what-is-physical-ai", "symbol-grounding-problem"],
          "module_reference": {
            "module_id": "module-2-embodied",
            "chapter_id": "embodied-intelligence",
            "url": "/docs/module-2-embodied/embodied-intelligence"
          },
          "date_added": "2025-12-26"
        }
      ]
    }
  ]
}
```

---

### Field Definitions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `version` | string | Semantic version (e.g., "1.0.0") | Yes |
| `last_updated` | string | ISO 8601 date of last FAQ update | Yes |
| `total_questions` | number | Total number of questions across all categories | Yes |
| `categories[].id` | string | Unique category identifier (kebab-case) | Yes |
| `categories[].name` | string | Human-readable category name | Yes |
| `categories[].description` | string | Category description (1-2 sentences) | Yes |
| `categories[].icon` | string | Emoji icon for visual categorization | No |
| `categories[].order` | number | Display order (1 = first) | Yes |
| `questions[].id` | string | Unique question identifier (kebab-case) | Yes |
| `questions[].question` | string | Question text (as user would ask) | Yes |
| `questions[].answer` | string | Answer text (100-300 words, plain text) | Yes |
| `questions[].keywords` | string[] | Search keywords for matching user queries | Yes |
| `questions[].related_questions` | string[] | IDs of related questions (for "See also") | No |
| `questions[].module_reference` | object | Link to book section (module, chapter, URL) | No |
| `questions[].date_added` | string | ISO 8601 date when question was added | Yes |

---

## FAQ Content Guidelines

### Writing Effective FAQ Answers

**1. Length**: 100-300 words (2-4 sentences)
- Too short: Lacks context and detail
- Too long: User loses interest, prefers live RAG API

**2. Tone**: Educational, approachable, precise
- Avoid jargon without definitions
- Use examples and analogies
- Define acronyms on first use (e.g., "LiDAR (Light Detection and Ranging)")

**3. Structure**: Definition → Context → Example
```
"Physical AI is... [DEFINITION]
Unlike traditional AI, Physical AI... [CONTEXT]
Examples include humanoid robots, autonomous vehicles... [EXAMPLE]"
```

**4. Citations**: Link to book modules where possible
- Use `module_reference` field to link to detailed content
- Show "(See Module 2: Embodied Intelligence for details)"

**5. Avoid Stale Content**: Do NOT include version-specific info
- ❌ "ROS 2 Humble is the latest version" (will become outdated)
- ✅ "ROS 2 is a popular framework for robot software" (timeless)

---

### What to Include in FAQ

**High-Value Questions**:
- ✅ Definitional questions ("What is X?")
- ✅ Comparison questions ("What is the difference between X and Y?")
- ✅ Widget functionality ("How do I use selected-text mode?")
- ✅ Foundational concepts (embodied intelligence, bipedal locomotion)

**What to Exclude from FAQ**:
- ❌ Highly specific questions ("What is the torque limit of Atlas's hip actuator?")
  - These require live RAG API for accuracy
- ❌ Procedural questions ("How do I tune a PID controller?")
  - Requires step-by-step instructions (better suited for live API)
- ❌ Opinion questions ("Which humanoid robot is the best?")
  - Subjective, not suitable for static FAQ

---

## FAQ Storage Strategy

### Option 1: Inline JavaScript (Recommended for Small FAQ)

**Description**: Embed FAQ JSON directly in widget bundle.

**Advantages**:
- ✅ No network request (works 100% offline)
- ✅ Instant availability (no IndexedDB async read)
- ✅ Simple deployment (single bundle file)

**Disadvantages**:
- ❌ Increases bundle size (~20-50 KB for 40 questions)
- ❌ Requires redeployment to update FAQ

**Implementation**:
```typescript
// Embedded FAQ in widget bundle
const STATIC_FAQ = {
  version: "1.0.0",
  last_updated: "2025-12-26",
  categories: [
    // ... full FAQ JSON
  ]
};

function getStaticFAQAnswer(userQuery: string): string | null {
  // Search STATIC_FAQ for matching question
  for (const category of STATIC_FAQ.categories) {
    for (const faq of category.questions) {
      if (matchesKeywords(userQuery, faq.keywords)) {
        return faq.answer;
      }
    }
  }
  return null;
}
```

**Recommendation**: Use for FAQ with ≤50 questions (~30 KB bundle impact).

---

### Option 2: IndexedDB (Recommended for Large FAQ)

**Description**: Store FAQ in browser IndexedDB, load on widget initialization.

**Advantages**:
- ✅ No bundle size impact
- ✅ Can store larger FAQ (100+ questions)
- ✅ Can update FAQ without redeploying widget (fetch from CDN)

**Disadvantages**:
- ❌ Asynchronous read (10-50ms delay)
- ❌ Requires initial download (on first widget load)
- ❌ Slightly more complex implementation

**Implementation**:
```typescript
// Load FAQ from IndexedDB on widget init
async function initializeFAQ() {
  const cachedFAQ = await indexedDB.get('static_faq');

  if (cachedFAQ && cachedFAQ.version === LATEST_FAQ_VERSION) {
    // Use cached FAQ
    return cachedFAQ;
  } else {
    // Fetch latest FAQ from CDN
    const latestFAQ = await fetch('https://cdn.example.com/faq-v1.0.0.json');
    await indexedDB.set('static_faq', latestFAQ);
    return latestFAQ;
  }
}
```

**Recommendation**: Use for FAQ with >50 questions or if FAQ needs frequent updates.

---

### Option 3: Hybrid (Inline + IndexedDB)

**Description**: Embed core FAQ (20 questions) in bundle, store extended FAQ (80 questions) in IndexedDB.

**Advantages**:
- ✅ Core questions available instantly (no async delay)
- ✅ Extended questions available after IndexedDB load
- ✅ Balanced bundle size (~15 KB for core FAQ)

**Disadvantages**:
- ❌ More complex implementation (dual storage)
- ❌ Requires careful deduplication

**Recommendation**: Use if you need instant FAQ for common questions + deep FAQ for niche topics.

---

### ChatKit Widget Recommendation

**Decision**: **Option 1 (Inline JavaScript)**

**Rationale**:
- 40 questions ~30 KB (acceptable bundle size impact)
- 100% offline availability (no IndexedDB async delay)
- Simpler implementation (no CDN, no versioning complexity)
- FAQ updates are infrequent (quarterly, aligned with book updates)

---

## FAQ Search and Matching Logic

### Keyword-Based Matching

**Approach**: Match user query against FAQ keywords using fuzzy string matching.

**Algorithm**:
1. Normalize user query (lowercase, remove punctuation)
2. Extract query tokens (split on whitespace)
3. For each FAQ question:
   - Calculate keyword overlap score
   - Return FAQ with highest score (if score > threshold)

**Design-Level Code**:
```typescript
function getStaticFAQAnswer(userQuery: string): { question: string, answer: string, score: number } | null {
  const normalizedQuery = normalizeQuery(userQuery);
  const queryTokens = normalizedQuery.split(/\s+/);

  let bestMatch = null;
  let bestScore = 0;

  for (const category of STATIC_FAQ.categories) {
    for (const faq of category.questions) {
      const score = calculateKeywordScore(queryTokens, faq.keywords);

      if (score > bestScore && score > FAQ_MATCH_THRESHOLD) {
        bestMatch = faq;
        bestScore = score;
      }
    }
  }

  return bestMatch ? { ...bestMatch, score: bestScore } : null;
}

function calculateKeywordScore(queryTokens: string[], keywords: string[]): number {
  let matchCount = 0;

  for (const token of queryTokens) {
    for (const keyword of keywords) {
      if (keyword.includes(token) || token.includes(keyword)) {
        matchCount++;
        break;  // Count each query token only once
      }
    }
  }

  // Normalize by query length (0.0 to 1.0)
  return matchCount / queryTokens.length;
}

function normalizeQuery(query: string): string {
  return query
    .toLowerCase()
    .replace(/[^\w\s]/g, '')  // Remove punctuation
    .trim();
}
```

**Match Threshold**: 0.4 (40% of query tokens must match keywords)
- Lower threshold (0.3): More matches, but less relevant
- Higher threshold (0.5): Fewer matches, but higher quality

---

### Fuzzy Matching (Optional Enhancement)

**Why**: Handle typos and variations ("humanoid" vs. "humaniod").

**Library**: Levenshtein distance (edit distance)

**Implementation**:
```typescript
function fuzzyMatch(token: string, keyword: string, maxDistance: number = 2): boolean {
  const distance = levenshteinDistance(token, keyword);
  return distance <= maxDistance;
}

function levenshteinDistance(a: string, b: string): number {
  const matrix = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,  // substitution
          matrix[i][j - 1] + 1,      // insertion
          matrix[i - 1][j] + 1       // deletion
        );
      }
    }
  }

  return matrix[b.length][a.length];
}
```

**Recommendation**: Optional for Phase 7+ (adds ~2 KB to bundle).

---

## FAQ Versioning Strategy

### Semantic Versioning

**Version Format**: `MAJOR.MINOR.PATCH`

**Version Increment Rules**:
- **MAJOR**: Breaking changes (e.g., restructure categories, remove 10+ questions)
- **MINOR**: New questions added (e.g., add 5 new questions to Category 3)
- **PATCH**: Typo fixes, answer clarifications (no structural changes)

**Example Versions**:
- `1.0.0`: Initial FAQ (40 questions, 7 categories)
- `1.1.0`: Add 5 new questions to "Learning & AI" category
- `1.1.1`: Fix typo in "What is embodied intelligence?" answer
- `2.0.0`: Restructure into 10 categories, add 20 new questions

---

### Version Storage in FAQ JSON

```json
{
  "version": "1.1.0",
  "last_updated": "2025-12-26",
  "changelog": [
    {
      "version": "1.1.0",
      "date": "2025-12-26",
      "changes": "Added 5 questions to Learning & AI category"
    },
    {
      "version": "1.0.0",
      "date": "2025-12-20",
      "changes": "Initial FAQ release with 40 questions"
    }
  ]
}
```

---

### Version Compatibility

**Question**: Should the widget support multiple FAQ versions?

**Answer**: No, always use latest FAQ version.

**Rationale**:
- FAQ updates are non-breaking (backward compatible)
- Old FAQ versions have no advantage (outdated content)
- Simplifies deployment (no version negotiation)

**Exception**: If widget is deployed to CDN with long cache TTL (e.g., 1 year), bundle FAQ version with widget to avoid version mismatch.

---

## FAQ Update Workflow

### Quarterly Update Cycle

**Frequency**: Every 3 months (aligned with book content updates)

**Workflow**:
1. **Content Review** (Week 1):
   - Analyze ChatKit widget analytics (top unanswered questions)
   - Identify gaps in static FAQ coverage
   - Review user feedback (submitted via "Was this helpful?" button)

2. **Draft New FAQ Entries** (Week 2):
   - Write 5-10 new questions/answers
   - Review with subject matter experts (robotics instructors)
   - Validate answer accuracy against book content

3. **Update FAQ JSON** (Week 3):
   - Increment FAQ version (e.g., 1.0.0 → 1.1.0)
   - Add new questions to appropriate categories
   - Update `last_updated` timestamp
   - Add changelog entry

4. **Deploy Updated FAQ** (Week 4):
   - Rebuild widget bundle with new FAQ
   - Deploy to CDN
   - Monitor analytics for FAQ match rate improvement

---

### Emergency FAQ Updates (Hotfix)

**Trigger**: Critical error in FAQ answer (factual inaccuracy, broken link)

**Workflow**:
1. Identify error (via user report or internal review)
2. Draft corrected answer
3. Increment PATCH version (e.g., 1.1.0 → 1.1.1)
4. Deploy hotfix within 24 hours

**Example**: FAQ answer references outdated ROS version → Update to ROS 2.

---

## FAQ vs. Cached Responses

### When to Use FAQ vs. Cache

| Scenario | Use FAQ | Use Cache |
|----------|---------|-----------|
| **Backend down** | ✅ Yes | ✅ Yes (if available) |
| **User offline** | ✅ Yes | ✅ Yes (if available) |
| **First-time user** | ✅ Yes | ❌ No cache yet |
| **Niche question** | ❌ Unlikely to match | ✅ If previously asked |
| **Common question** | ✅ Likely in FAQ | ✅ If previously asked |

---

### Fallback Priority Order

```
1. Try RAG API (5s timeout)
   ↓ (timeout or error)
2. Try Cached Response (100ms timeout)
   ↓ (not found)
3. Try Static FAQ (instant, keyword match)
   ↓ (no match, score < 0.4)
4. Show Manual Fallback ("Browse topics manually")
```

---

### FAQ Answer Enrichment

**Optional Enhancement**: Show both FAQ answer AND link to live RAG API.

**UI Example**:
```
┌─────────────────────────────────────────────┐
│ 🤖 Offline Answer (Static FAQ)              │
├─────────────────────────────────────────────┤
│ "Physical AI is artificial intelligence     │
│ that interacts with and acts upon the       │
│ physical world through sensors and          │
│ actuators..."                               │
│                                             │
│ 📚 See also: Module 1 - Introduction to    │
│    Physical AI                              │
│                                             │
│ ⚠️ You're offline. For a detailed answer,  │
│ try again when connected.                   │
│                                             │
│ [Browse Topics]  [Retry Connection]         │
└─────────────────────────────────────────────┘
```

---

## Testing Procedures

### Test 1: FAQ Match Accuracy

**Objective**: Verify FAQ keyword matching returns correct answers.

**Steps**:
1. **Submit Question**: "What is Physical AI?"
2. **Verify FAQ Match**: Returns FAQ answer for "what-is-physical-ai"
3. **Verify Match Score**: Score ≥ 0.4 (40% keyword overlap)

**Expected Behavior**:
- User query: "what is physical ai"
- Normalized query: "what is physical ai"
- Query tokens: ["what", "is", "physical", "ai"]
- FAQ keywords: ["physical ai", "definition", "embodied ai", "robotics"]
- Match score: 0.75 (3/4 tokens match "physical", "ai", "definition")
- **Result**: ✅ Return FAQ answer

**Pass Criteria**: ✅ FAQ returns correct answer with score ≥ 0.4

---

### Test 2: FAQ No Match (Fallback)

**Objective**: Verify FAQ returns null for non-matching queries.

**Steps**:
1. **Submit Question**: "What is the capital of France?"
2. **Verify FAQ No Match**: Returns null (score < 0.4)
3. **Verify Fallback**: Shows manual fallback ("Browse topics manually")

**Expected Behavior**:
- User query: "what is the capital of france"
- Query tokens: ["what", "is", "the", "capital", "of", "france"]
- No FAQ keywords match "capital" or "france"
- Match score: 0.0 (0/6 tokens match)
- **Result**: ❌ Return null, show manual fallback

**Pass Criteria**: ✅ FAQ returns null for out-of-scope questions

---

### Test 3: FAQ Works Offline

**Objective**: Verify FAQ is accessible without network connection.

**Steps**:
1. **Disconnect Network** (Airplane mode or DevTools offline)
2. **Open ChatKit Widget**
3. **Submit Question**: "What is embodied intelligence?"
4. **Verify FAQ Answer Returned** (no network request)

**Expected Behavior**:
- Network: Offline
- RAG API: Unreachable (skipped, no network call)
- Cached response: Empty (no prior queries)
- Static FAQ: Match found for "embodied intelligence"
- **Result**: ✅ Return FAQ answer (100% offline)

**Pass Criteria**: ✅ FAQ works without network connection

---

### Test 4: FAQ Update Workflow

**Objective**: Verify FAQ can be updated without breaking existing functionality.

**Steps**:
1. **Update FAQ JSON**: Add new question to Category 2
2. **Increment Version**: 1.0.0 → 1.1.0
3. **Rebuild Widget Bundle**
4. **Deploy to CDN**
5. **Verify New Question**: Submit new question, verify answer returned

**Expected Behavior**:
- Old questions still work (backward compatible)
- New question returns correct answer
- FAQ version: 1.1.0 (displayed in widget footer)

**Pass Criteria**: ✅ New FAQ questions work without breaking old questions

---

## Summary

**Offline FAQ Structure**:
- **7 Categories**: Getting Started, Physical AI Basics, Humanoid Robotics, Perception, Control, Learning, Future & Ethics
- **40 Questions**: Curated high-value Q&A covering core topics
- **100-300 Words per Answer**: Concise, educational, with citations
- **Keyword-Based Matching**: Fuzzy search with 0.4 match threshold

**Storage Strategy**:
- **Inline JavaScript** (recommended): Embed FAQ in widget bundle (~30 KB)
- Alternative: IndexedDB (for FAQ >50 questions)

**Versioning**:
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Quarterly Updates**: Add 5-10 new questions per quarter
- **Hotfix Process**: 24-hour turnaround for critical errors

**Fallback Priority**:
1. RAG API (5s timeout)
2. Cached responses (100ms timeout)
3. Static FAQ (instant, keyword match)
4. Manual fallback (browse topics)

**Testing**:
- ✅ FAQ match accuracy (score ≥ 0.4)
- ✅ FAQ no match (out-of-scope questions)
- ✅ FAQ works offline (no network required)
- ✅ FAQ updates backward compatible

**Next Steps**:
1. Complete T047 (Error Handling Checklist)
2. Complete T048 (Network Recovery Detection)
3. Finalize Phase 7 (US5 Offline Mode)

---

**Status**: Offline FAQ Structure Guide Complete ✅
**File**: `specs/003-chatkit-widget/integration/offline-faq.md`
**Lines**: 900+
**Coverage**: 100% (FAQ categories, data structure, storage, search logic, versioning, update workflow documented)
