# Implementation Plan: Physical AI & Humanoid Robotics Book

**Branch**: `001-physical-ai-book` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-physical-ai-book/spec.md`
**Phase**: 1 - Foundations Only

---

## Summary

Build a Docusaurus-based educational book on Physical AI and Humanoid Robotics. Phase 1 establishes the complete documentation structure, module organization, and GitHub Pages deployment pipeline—without any robotics implementation code. The book will contain 7 modules with 3-4 chapters each, all focused on conceptual content and learning outcomes.

---

## Technical Context

**Framework/Version**: Docusaurus 3.x with TypeScript
**Language**: TypeScript 5.x for configuration, Markdown/MDX for content
**Runtime**: Node.js 20.x LTS
**Package Manager**: npm 10.x
**Storage**: N/A (static site)
**Testing**: Build verification, link checking
**Target Platform**: GitHub Pages (static hosting)
**Project Type**: Documentation/Book site
**Performance Goals**: Page load < 3 seconds, search indexing all content
**Constraints**: No executable code, no interactive simulations, English-only
**Scale/Scope**: 7 modules, ~28 chapters, supporting 50+ pages

---

## Constitution Check

*Note: Project constitution is template-only. Applying documentation-focused principles.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Simplicity | PASS | Docusaurus classic template, minimal customization |
| Documentation-First | PASS | Entire project is documentation |
| Testability | PASS | Build verification, link checking |
| No Premature Optimization | PASS | Using defaults, will customize only when needed |

---

## Project Structure

### Documentation (this feature)

```
specs/001-physical-ai-book/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research decisions
├── data-model.md        # Content entity structure
├── quickstart.md        # Developer setup guide
├── checklists/
│   └── requirements.md  # Quality validation
└── tasks.md             # (Future: /sp.tasks output)
```

### Source Code (Docusaurus Book)

```
physical-ai-book/                    # Docusaurus project root
├── docusaurus.config.ts             # Site configuration
├── sidebars.ts                      # Navigation structure
├── package.json                     # Dependencies
├── tsconfig.json                    # TypeScript config
│
├── docs/                            # Book content
│   ├── curriculum-overview.md       # Homepage/landing
│   │
│   ├── module-1-intro/              # Module 1
│   │   ├── _category_.json
│   │   ├── index.md                 # Module overview + learning outcomes
│   │   ├── what-is-physical-ai.md
│   │   ├── embodiment-significance.md
│   │   └── application-domains.md
│   │
│   ├── module-2-embodied/           # Module 2
│   │   ├── _category_.json
│   │   ├── index.md
│   │   ├── embodied-cognition.md
│   │   ├── sensorimotor-integration.md
│   │   └── physical-interaction-learning.md
│   │
│   ├── module-3-humanoid/           # Module 3
│   │   ├── _category_.json
│   │   ├── index.md
│   │   ├── major-platforms.md
│   │   ├── bipedal-locomotion.md
│   │   └── human-robot-morphology.md
│   │
│   ├── module-4-perception/         # Module 4
│   │   ├── _category_.json
│   │   ├── index.md
│   │   ├── multimodal-sensing.md
│   │   ├── spatial-awareness.md
│   │   └── object-recognition.md
│   │
│   ├── module-5-control/            # Module 5
│   │   ├── _category_.json
│   │   ├── index.md
│   │   ├── motion-planning.md
│   │   ├── control-hierarchies.md
│   │   └── action-perception-loop.md
│   │
│   ├── module-6-learning/           # Module 6
│   │   ├── _category_.json
│   │   ├── index.md
│   │   ├── simulation-vs-reality.md
│   │   ├── transfer-learning.md
│   │   └── reinforcement-learning.md
│   │
│   └── module-7-future/             # Module 7
│       ├── _category_.json
│       ├── index.md
│       ├── emerging-trends.md
│       ├── ethical-considerations.md
│       └── industry-applications.md
│
├── src/
│   ├── css/
│   │   └── custom.css               # Theme customization
│   └── pages/                       # (Empty - docs-only mode)
│
├── static/
│   ├── img/
│   │   ├── module-1/
│   │   ├── module-2/
│   │   ├── module-3/
│   │   ├── module-4/
│   │   ├── module-5/
│   │   ├── module-6/
│   │   └── module-7/
│   └── diagrams/
│       └── curriculum-path.svg
│
└── .github/
    └── workflows/
        └── deploy.yml               # GitHub Pages deployment
```

**Structure Decision**: Docusaurus classic template in docs-only mode. Each module is a folder under `docs/` with `_category_.json` for sidebar control. Content is Markdown with MDX capability reserved for future phases.

---

## Toolchain Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        AUTHORING PHASE                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Author writes Markdown content in docs/<module>/<chapter>.md│
│  2. Frontmatter defines sidebar position, title, description    │
│  3. _category_.json controls module ordering and labels         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LOCAL DEVELOPMENT                          │
├─────────────────────────────────────────────────────────────────┤
│  npm run start                                                  │
│  - Hot reload on content changes                                │
│  - Sidebar auto-updates from folder structure                   │
│  - Search available in dev mode                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BUILD PHASE                             │
├─────────────────────────────────────────────────────────────────┤
│  npm run build                                                  │
│  - Compiles Markdown to static HTML                             │
│  - Generates search index                                       │
│  - Optimizes assets                                             │
│  - Output to build/ directory                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT PHASE                           │
├─────────────────────────────────────────────────────────────────┤
│  Push to main → GitHub Actions                                  │
│  - actions/checkout                                             │
│  - actions/setup-node (20.x)                                    │
│  - npm ci && npm run build                                      │
│  - actions/upload-pages-artifact                                │
│  - actions/deploy-pages                                         │
│  → Live at https://<org>.github.io/physical-ai-book/            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Content Strategy

### Language & Tone
- **Audience**: Advanced AI students, robotics engineers, ML developers
- **Tone**: Technical but accessible, academic yet practical
- **Voice**: Second person ("you will learn") for outcomes, third person for concepts

### Content Hierarchy
1. **Curriculum Overview**: Book introduction, audience, prerequisites, module map
2. **Module Overview (index.md)**: Learning outcomes, chapter summaries, prerequisites
3. **Chapter**: Key concepts → main content → summary → further reading

### Naming Conventions
- Module folders: `module-N-shortname` (e.g., `module-1-intro`)
- Chapter files: `kebab-case.md` (e.g., `what-is-physical-ai.md`)
- Images: `static/img/module-N/<descriptive-name>.png`

---

## Versioning & Extensibility

### Phase Versioning Strategy

```
Phase 1 Complete → Create version 1.0
├── versioned_docs/version-1.0/  (Phase 1 snapshot)
└── docs/                        (Phase 2 development)

Phase 2 Complete → Create version 2.0
├── versioned_docs/version-1.0/  (Phase 1)
├── versioned_docs/version-2.0/  (Phase 2)
└── docs/                        (Phase 3 development)
```

### Future Phase Integration Points

| Phase | Content Addition | Integration Approach |
|-------|-----------------|---------------------|
| Phase 2 | ROS tutorials | New `tutorials/` section, MDX components |
| Phase 3 | Gazebo simulations | New `simulations/` section, embedded viewers |
| Phase 4 | Isaac examples | New `isaac/` section, code blocks |
| Phase N | Interactive demos | MDX components, external embeds |

### Extensibility Hooks (Built-in but unused in Phase 1)
- **MDX support**: Ready for React components when needed
- **Blog**: Disabled but can enable for announcements
- **i18n**: Structure supports future localization
- **Plugins**: Can add Mermaid diagrams, code playground later

---

## Deployment Configuration

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: physical-ai-book
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: physical-ai-book/package-lock.json
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: physical-ai-book/build

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

### Repository Settings Required
1. Settings → Pages → Source: GitHub Actions
2. Settings → Actions → General → Workflow permissions: Read and write

---

## Explicit Exclusions (Phase 1)

The following are **NOT** part of Phase 1 and **MUST NOT** be implemented:

| Excluded Item | Reason | Future Phase |
|---------------|--------|--------------|
| ROS code/tutorials | Out of scope | Phase 2+ |
| Gazebo simulations | Out of scope | Phase 3+ |
| Isaac SDK examples | Out of scope | Phase 3+ |
| Unity integration | Out of scope | Phase 4+ |
| VLA implementations | Out of scope | Phase 4+ |
| Interactive code execution | Requires infrastructure | Phase 2+ |
| Video hosting | Requires external service | Phase 2+ |
| User accounts | Requires backend | Not planned |
| Comments/forums | Requires backend | Not planned |

---

## Success Criteria Mapping

| Spec Criteria | Implementation Verification |
|---------------|----------------------------|
| SC-001: 3 clicks to any topic | Sidebar navigation depth ≤ 3 |
| SC-002: 100% modules with outcomes | Each index.md has Learning Outcomes section |
| SC-003: < 3s load time | Lighthouse performance audit |
| SC-004: 50+ chapters supported | Test sidebar with full content |
| SC-005: Keyboard navigation | Docusaurus default accessibility |
| SC-006: 90% search relevance | Algolia configuration tuning |
| SC-007: Mobile 375px+ | Responsive CSS, manual testing |
| SC-008: < 5min deployment | GitHub Actions timing |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Algolia free tier limits | Local search plugin as fallback |
| GitHub Pages bandwidth limits | Monitor usage, CDN if needed |
| Build time increases with content | Enable incremental builds |
| Search relevance issues | Custom search configuration |

---

## Artifacts Generated

| Artifact | Path | Purpose |
|----------|------|---------|
| Research | `specs/001-physical-ai-book/research.md` | Technology decisions |
| Data Model | `specs/001-physical-ai-book/data-model.md` | Content structure |
| Quickstart | `specs/001-physical-ai-book/quickstart.md` | Developer setup |
| Plan | `specs/001-physical-ai-book/plan.md` | This document |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks to scaffold Docusaurus project
3. Create module structure and placeholder content
4. Configure GitHub Actions deployment
5. Validate against success criteria
