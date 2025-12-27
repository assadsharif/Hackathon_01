# Implementation Repository Setup Guide

**Purpose**: Create a new repository/branch for Phase 7+ implementation work
**Design Reference**: Tag `v1.0-design-freeze` (commit 6067316)
**Status**: Ready to Execute

---

## Why a Separate Repository?

**Academic Integrity**: Clear separation between design artifacts (Phase 6) and implementation code (Phase 7+)

**Reviewer Clarity**: This repository (`Hackathon_01`) remains a **Design Reference Library**. Implementation work happens elsewhere.

**Credibility**: Single line in README: *"Implementation derived from frozen design at commit 5b2a756"* demonstrates design-first methodology.

---

## Option A: New Repository (Recommended)

### Step 1: Create New GitHub Repository

```bash
gh repo create chatkit-widget-implementation \
  --public \
  --description "Phase 7+ implementation derived from Hackathon_01 design freeze v1.0 (commit 5b2a756)" \
  --clone
```

Or manually via GitHub UI:
- Repository name: `chatkit-widget-implementation`
- Description: "Phase 7+ implementation derived from Hackathon_01 design freeze v1.0 (commit 5b2a756)"
- Visibility: Public (or Private)
- Initialize: ✅ README, ✅ .gitignore (Node), ❌ License (copy from design repo)

### Step 2: Create README with Design Reference

```bash
cd chatkit-widget-implementation
cat > README.md <<'EOF'
# ChatKit Widget - Phase 7 Implementation

**Status**: 🚧 In Development (Phase 7)
**Design Reference**: [Hackathon_01 v1.0-design-freeze](https://github.com/assadsharif/Hackathon_01/tree/v1.0-design-freeze)

---

## Design Provenance

**Implementation derived from frozen design at commit [5b2a756](https://github.com/assadsharif/Hackathon_01/commit/5b2a756).**

This repository implements the ChatKit Widget Integration design validated in Phase 6 (Design Validation). All design artifacts, patterns, specifications, and validation reports are frozen in the source repository.

---

## Design Artifacts Reference

**Source Repository**: [Hackathon_01](https://github.com/assadsharif/Hackathon_01)
**Design Tag**: `v1.0-design-freeze`
**Design Freeze Date**: 2025-12-27

**Key Design Artifacts**:
- [ChatKit Widget Specification](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/spec.md)
- [Validation Tasks](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/tasks.md)
- [Traceability Matrix](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/traceability.md)
- [Phase 7 Planning Guide](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/phase7-planning.md)
- [ChatKit Widget Patterns](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/.claude/skills/chatkit-widget/patterns.md)
- [Integration Guides](https://github.com/assadsharif/Hackathon_01/tree/v1.0-design-freeze/specs/003-chatkit-widget/integration)

---

## What is This?

This repository contains the **Phase 7+ runtime implementation** of the ChatKit Widget Integration feature. The implementation follows the design patterns, specifications, and validation tasks defined in the frozen design artifacts.

**Implementation Scope**:
- ✅ React + TypeScript + Tailwind CSS widget
- ✅ RAG API integration (dual-mode retrieval)
- ✅ Better-Auth OAuth integration (progressive signup)
- ✅ Accessibility (WCAG 2.1 AA compliance)
- ✅ Compliance (GDPR, CCPA, FERPA, COPPA)
- ✅ E2E testing (Playwright, Lighthouse CI)

**NOT in Scope**:
- ❌ Design modifications (frozen in source repository)
- ❌ Pattern changes (refer to design artifacts)
- ❌ Specification updates (use design freeze tag as reference)

---

## Project Structure

```
chatkit-widget-implementation/
├── README.md                    # This file
├── packages/
│   ├── widget/                  # ChatKit Widget (React + TypeScript)
│   │   ├── src/
│   │   │   ├── components/      # UI components (ChatPanel, CitationTooltip, etc.)
│   │   │   ├── hooks/           # React hooks (useChatSession, useRAG, useAuth)
│   │   │   ├── services/        # Event bus, RAG API, Better-Auth integration
│   │   │   └── types/           # TypeScript types from MCP event schemas
│   │   ├── tests/               # Unit tests (Jest + React Testing Library)
│   │   └── package.json
│   ├── rag-api/                 # RAG orchestration backend (optional)
│   └── docs-site/               # Docusaurus site (Physical AI Book)
├── .github/
│   └── workflows/
│       ├── ci.yml               # Lint, test, build
│       └── lighthouse.yml       # Lighthouse CI (performance, accessibility)
└── docs/
    └── DESIGN_REFERENCE.md      # Links to frozen design artifacts
```

---

## Getting Started

### Prerequisites

- Node.js 20+
- npm 10+
- Git

### Installation

```bash
git clone https://github.com/assadsharif/chatkit-widget-implementation.git
cd chatkit-widget-implementation
npm install
```

### Development

```bash
npm run dev
```

Runs the widget in development mode with hot reload.

### Testing

```bash
npm run test          # Unit tests (Jest)
npm run test:e2e      # E2E tests (Playwright)
npm run test:a11y     # Accessibility tests (axe-core)
npm run lighthouse    # Lighthouse CI
```

### Build

```bash
npm run build
```

Builds the widget for production (outputs to `packages/widget/dist/`).

---

## Design Compliance

This implementation follows all design patterns and validation tasks from the frozen design:

| Design Artifact | Implementation Status |
|-----------------|----------------------|
| [US1: Anonymous Support](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/validation/T011-T014-US1-anonymous-support.md) | 🚧 In Progress |
| [US2: Dual-Mode Support](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/validation/T018-T021-US2-dual-mode-support.md) | ⏸️ Not Started |
| [US3: Progressive Signup](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/validation/T025-T028-US3-progressive-signup.md) | ⏸️ Not Started |
| [US4: Accessibility](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/validation/T033-T036-US4-accessibility-support.md) | ⏸️ Not Started |
| [US5: Offline Mode](https://github.com/assadsharif/Hackathon_01/blob/v1.0-design-freeze/specs/003-chatkit-widget/validation/T041-T044-US5-offline-mode.md) | ⏸️ Not Started |

---

## Contributing

This is an academic project. Contributions must:
1. Reference the frozen design artifacts
2. Follow design patterns from `.claude/skills/chatkit-widget/patterns.md`
3. Pass all validation tasks from `specs/003-chatkit-widget/tasks.md`
4. Maintain 100% compliance and accessibility coverage

---

## License

[Your License]

---

## Citation

If you reference this implementation in academic work, please cite the original design repository:

```
[Your Name]. (2025). Physical AI & Humanoid Robotics Educational Platform:
Design Validation for Privacy-First, Accessible Learning Systems.
[Your Institution]. Retrieved from https://github.com/assadsharif/Hackathon_01/tree/v1.0-design-freeze
```

---

**Design Reference**: Implementation derived from frozen design at commit [5b2a756](https://github.com/assadsharif/Hackathon_01/commit/5b2a756)

**Last Updated**: 2025-12-27
EOF

git add README.md
git commit -m "docs: add README with design reference (commit 5b2a756)"
git push origin main
```

---

## Option B: New Branch in Same Repository (Alternative)

If you prefer to keep implementation in the same repository (less recommended for academic clarity):

```bash
cd /mnt/c/Users/assad/Desktop/CODE/Hackathon_01

# Create new orphan branch (no shared history with design branch)
git checkout --orphan implementation/chatkit-widget

# Remove all files from staging
git rm -rf .

# Create new README
cat > README.md <<'EOF'
# ChatKit Widget - Phase 7 Implementation

**Implementation derived from frozen design at commit 5b2a756.**

See design artifacts at tag `v1.0-design-freeze`.
EOF

git add README.md
git commit -m "chore: initialize implementation branch"
git push -u origin implementation/chatkit-widget
```

**Note**: Option B is less recommended because it mixes design and implementation in the same repository, reducing reviewer clarity.

---

## Next Steps After Repository Creation

1. **Copy Design Artifacts** (reference only, not for modification):
   ```bash
   # In the new implementation repository
   mkdir -p docs/design-reference

   # Copy key design files (read-only reference)
   curl -o docs/design-reference/spec.md \
     https://raw.githubusercontent.com/assadsharif/Hackathon_01/v1.0-design-freeze/specs/003-chatkit-widget/spec.md

   curl -o docs/design-reference/phase7-planning.md \
     https://raw.githubusercontent.com/assadsharif/Hackathon_01/v1.0-design-freeze/specs/003-chatkit-widget/phase7-planning.md
   ```

2. **Set Up Project Structure** (follow phase7-planning.md):
   ```bash
   npx create-react-app packages/widget --template typescript
   npm install tailwindcss @headlessui/react lucide-react
   ```

3. **Configure CI/CD** (GitHub Actions):
   - Lint (ESLint, Prettier)
   - Test (Jest, Playwright)
   - Build (TypeScript compilation)
   - Lighthouse CI (performance, accessibility)

4. **Start Implementation** (Tier 0 → Tier 1 → Tier 2 → Tier 3):
   - Tier 0: Anonymous support, browser-local storage
   - Tier 1: Email verification, session sync
   - Tier 2: OAuth integration, personalization
   - Tier 3: Advanced analytics, API access

---

## Verification Checklist

After creating the implementation repository:

- [ ] README includes: "Implementation derived from frozen design at commit 5b2a756"
- [ ] Design reference links point to `v1.0-design-freeze` tag
- [ ] Repository description mentions design freeze commit
- [ ] No design artifacts copied for modification (only reference)
- [ ] Clear boundary between design (Hackathon_01) and implementation (new repo)

---

## Design Freeze Commit Reference

**Commit SHA**: `5b2a756`
**Commit Message**: "docs: declare Design Freeze v1.0.0 (Phase 6 Complete)"
**Tag**: `v1.0-design-freeze`
**Date**: 2025-12-27
**Repository**: https://github.com/assadsharif/Hackathon_01

**Direct Link**: https://github.com/assadsharif/Hackathon_01/commit/5b2a756

---

**That single line earns massive credibility.**

---

**Last Updated**: 2025-12-27
