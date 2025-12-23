# Research: Physical AI & Humanoid Robotics Book

**Feature Branch**: `001-physical-ai-book`
**Date**: 2025-12-22
**Phase**: 0 - Research

---

## Research Questions

### RQ-1: Docusaurus Version and Configuration

**Decision**: Use Docusaurus 3.x with TypeScript configuration

**Rationale**:
- Docusaurus 3.x is the current stable version with active support
- TypeScript configuration provides type safety for complex sidebar structures
- Better IDE support for configuration editing

**Alternatives Considered**:
- Docusaurus 2.x: Rejected - approaching end of life
- JavaScript configuration: Rejected - TypeScript provides better maintainability

---

### RQ-2: Project Structure Pattern

**Decision**: Use Classic template with docs-only mode

**Rationale**:
- Classic template includes all needed features (search, versioning, i18n hooks)
- Docs-only mode centers navigation on book content
- Blog feature can be disabled but easily re-enabled for future announcements

**Alternatives Considered**:
- Standalone docs template: Rejected - lacks theming flexibility
- Custom from scratch: Rejected - unnecessary complexity

---

### RQ-3: Module Organization Strategy

**Decision**: Each module is a top-level folder under `docs/` with `_category_.json` metadata

**Rationale**:
- Docusaurus auto-generates sidebar from folder structure
- `_category_.json` provides explicit control over ordering and labels
- Each module folder contains `index.md` (overview) + chapter files

**Alternatives Considered**:
- Flat file structure with prefixes: Rejected - harder to navigate in IDE
- Nested multi-level folders: Rejected - over-complicated for 7 modules

---

### RQ-4: Search Implementation

**Decision**: Use built-in Algolia DocSearch (free for open-source)

**Rationale**:
- Zero configuration for basic search
- Algolia provides free tier for documentation sites
- Scales well with content growth

**Alternatives Considered**:
- Local search plugin: Fallback option if Algolia unavailable
- No search: Rejected - violates FR-004

---

### RQ-5: GitHub Pages Deployment Strategy

**Decision**: Use GitHub Actions with `actions/deploy-pages`

**Rationale**:
- Official GitHub-supported deployment method
- Automatic deployment on push to main
- No need for separate gh-pages branch management

**Alternatives Considered**:
- Manual deployment: Rejected - violates FR-006 (automatic deployment)
- Netlify/Vercel: Rejected - adds external dependency when GitHub Pages sufficient

---

### RQ-6: Versioning Strategy for Future Phases

**Decision**: Use Docusaurus versioning feature, creating version snapshots at phase boundaries

**Rationale**:
- Phase 1 becomes `v1.0` when Phase 2 begins
- Readers can access historical versions
- Clean separation between documentation phases

**Alternatives Considered**:
- Git tags only: Rejected - doesn't provide version switcher UI
- No versioning: Rejected - would lose Phase 1 content organization

---

### RQ-7: Content Authoring Format

**Decision**: Standard Markdown with MDX for interactive components (future)

**Rationale**:
- Markdown is sufficient for Phase 1 (text-only content)
- MDX capability preserved for Phase 2+ interactive elements
- Authors familiar with Markdown can contribute immediately

**Alternatives Considered**:
- Pure MDX: Rejected - unnecessary complexity for Phase 1
- reStructuredText: Rejected - not supported by Docusaurus

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Docusaurus | 3.x |
| Language | TypeScript | 5.x |
| Runtime | Node.js | 20.x LTS |
| Package Manager | npm | 10.x |
| Deployment | GitHub Pages | - |
| CI/CD | GitHub Actions | - |
| Search | Algolia DocSearch | - |

---

## Constraints Resolved

1. **No robotics code**: Confirmed - Phase 1 is documentation structure only
2. **Static content**: Confirmed - no interactive simulations in Phase 1
3. **Docusaurus adequacy**: Confirmed - meets all FR requirements
4. **GitHub Pages limits**: Confirmed - 1GB storage, 100GB/month bandwidth sufficient
