# Data Model: Physical AI Book Content Structure

**Feature Branch**: `001-physical-ai-book`
**Date**: 2025-12-22
**Phase**: 1 - Design

---

## Content Entities

### Module

A major section of the book containing related chapters.

**File Structure**:
```
docs/module-N-name/
├── _category_.json    # Module metadata
├── index.md           # Module overview page
├── chapter-1.md
├── chapter-2.md
└── chapter-3.md
```

**_category_.json Schema**:
```json
{
  "label": "Module N: Display Title",
  "position": 1,
  "link": {
    "type": "doc",
    "id": "module-N-name/index"
  },
  "collapsible": true,
  "collapsed": false
}
```

**index.md Frontmatter**:
```yaml
---
sidebar_position: 0
title: Module Title
description: SEO description for the module
keywords: [keyword1, keyword2]
---
```

**index.md Required Sections**:
1. Overview (2-3 paragraphs)
2. Learning Outcomes (bulleted list)
3. Prerequisites (if any)
4. Chapter Overview (brief description of each chapter)

---

### Chapter

A discrete topic within a module.

**Frontmatter Schema**:
```yaml
---
sidebar_position: 1
title: Chapter Title
description: Brief description for SEO
keywords: [physical-ai, embodiment, topic-specific]
---
```

**Required Sections**:
1. Key Concepts (bullet points)
2. Main Content (topic-specific)
3. Summary (key takeaways)
4. Further Reading (optional for Phase 1)

---

### Curriculum Overview Page

A top-level page showing the complete learning path.

**Location**: `docs/curriculum-overview.md`

**Frontmatter**:
```yaml
---
sidebar_position: 0
title: Curriculum Overview
description: Complete learning path for Physical AI and Humanoid Robotics
slug: /
---
```

**Required Sections**:
1. Introduction to the Book
2. Target Audience
3. Prerequisites
4. Module Progression Diagram (text-based for Phase 1)
5. How to Use This Book

---

## Module-to-Folder Mapping

| Module | Folder Name | Position |
|--------|-------------|----------|
| Curriculum Overview | (root) | 0 |
| Module 1: Introduction to Physical AI | `module-1-intro` | 1 |
| Module 2: Foundations of Embodied Intelligence | `module-2-embodied` | 2 |
| Module 3: Humanoid Robotics Overview | `module-3-humanoid` | 3 |
| Module 4: Perception for Physical AI | `module-4-perception` | 4 |
| Module 5: Action and Control Fundamentals | `module-5-control` | 5 |
| Module 6: Learning in Physical Environments | `module-6-learning` | 6 |
| Module 7: Future Directions and Applications | `module-7-future` | 7 |

---

## Chapter Mapping per Module

### Module 1: Introduction to Physical AI
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | what-is-physical-ai.md | What is Physical AI? |
| 2 | embodiment-significance.md | Why Embodiment Matters |
| 3 | application-domains.md | Application Domains |

### Module 2: Foundations of Embodied Intelligence
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | embodied-cognition.md | Embodied Cognition Principles |
| 2 | sensorimotor-integration.md | Sensorimotor Integration |
| 3 | physical-interaction-learning.md | Physical Interaction and Learning |

### Module 3: Humanoid Robotics Overview
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | major-platforms.md | Major Platforms |
| 2 | bipedal-locomotion.md | Bipedal Locomotion Challenges |
| 3 | human-robot-morphology.md | Human-Robot Morphology |

### Module 4: Perception for Physical AI
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | multimodal-sensing.md | Multimodal Sensing |
| 2 | spatial-awareness.md | Spatial Awareness |
| 3 | object-recognition.md | Object Recognition |

### Module 5: Action and Control Fundamentals
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | motion-planning.md | Motion Planning Concepts |
| 2 | control-hierarchies.md | Control Hierarchies |
| 3 | action-perception-loop.md | Action-Perception Loop |

### Module 6: Learning in Physical Environments
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | simulation-vs-reality.md | Simulation vs. Reality |
| 2 | transfer-learning.md | Transfer Learning |
| 3 | reinforcement-learning.md | Reinforcement Learning for Robots |

### Module 7: Future Directions and Applications
| Position | File | Title |
|----------|------|-------|
| 0 | index.md | Module Overview |
| 1 | emerging-trends.md | Emerging Trends |
| 2 | ethical-considerations.md | Ethical Considerations |
| 3 | industry-applications.md | Industry Applications |

---

## Static Assets Structure

```
static/
├── img/
│   ├── module-1/
│   ├── module-2/
│   ├── module-3/
│   ├── module-4/
│   ├── module-5/
│   ├── module-6/
│   └── module-7/
└── diagrams/
    └── curriculum-path.svg
```

---

## Validation Rules

1. **Every module MUST have an index.md** with learning outcomes
2. **Every chapter MUST have frontmatter** with title and description
3. **sidebar_position MUST be sequential** within each module
4. **_category_.json position MUST match** module number
5. **All images MUST be in** `static/img/<module-name>/`
