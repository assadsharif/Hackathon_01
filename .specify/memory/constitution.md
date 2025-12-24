# Physical AI Book Constitution

<!--
## Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Amendment: Added MCP development scope clarification
- Added sections:
  - VI. MCP Server Development (Phase 2+)
- Structural changes:
  - Added mcp-servers/ directory for MCP server projects
  - Added .claude/skills/mcp-developer/ skill for MCP development guidance
- Templates requiring updates: None
- Follow-up TODOs: None
-->

## Core Principles

### I. Documentation-First

All deliverables in Phase 1 MUST be documentation artifacts only. No executable code, simulations, or interactive implementations are permitted until Phase 2+.

**Rules:**
- Content MUST be in Markdown/MDX format
- Configuration files (TypeScript, JSON) are permitted only for Docusaurus setup
- NO robotics code (ROS, Gazebo, Isaac SDK, Unity)
- NO backend services or APIs
- Build output MUST be static HTML/CSS/JS only

### II. Content Structure

Educational content MUST follow a consistent hierarchical structure that enables both sequential learning and random-access reference.

**Rules:**
- Every module MUST have an index.md with learning outcomes
- Every chapter MUST have: Key Concepts, Main Content, Summary sections
- Sidebar navigation MUST reflect content hierarchy (Module → Chapter)
- Any topic MUST be reachable within 3 clicks from homepage
- Cross-references between related topics MUST use relative links

### III. Build Verification

All changes MUST be validated through successful local builds before commit. Build verification is the primary "test" for documentation projects.

**Rules:**
- `npm run build` MUST complete without errors
- All internal links MUST resolve (no broken links)
- Search index MUST be generated successfully
- Build artifacts MUST not exceed reasonable size limits
- GitHub Actions deployment MUST succeed on main branch

### IV. Accessibility

Content MUST be accessible to users on various devices and with different abilities.

**Rules:**
- Site MUST be responsive at 375px viewport width minimum
- Navigation MUST work with keyboard-only interaction
- Images MUST have alt text descriptions
- Page load time MUST be under 3 seconds on standard connections
- Content MUST be readable without JavaScript (static HTML fallback)

### V. Simplicity

Use Docusaurus defaults and avoid premature customization. Complexity MUST be justified by concrete requirements.

**Rules:**
- Use classic template with minimal CSS customization
- NO custom React components in Phase 1
- NO plugins beyond what ships with Docusaurus
- NO external services (analytics, comments) in Phase 1
- Configuration changes MUST be documented with rationale

### VI. MCP Server Development (Phase 2+)

MCP (Model Context Protocol) servers MAY be developed to enhance the project with specialized tooling. MCP development is IN SCOPE for Phase 2+ but subject to documentation-first principles.

**Rules:**
- MCP servers MUST be developed using spec-driven methodology (spec → plan → implement)
- All MCP server projects MUST reside in `mcp-servers/` directory
- MCP servers MUST follow the mcp-developer skill guidance (`.claude/skills/mcp-developer/`)
- MCP servers SHOULD provide capabilities related to Physical AI research, documentation, or robotics workflows
- Phase 1: MCP development is OUT OF SCOPE (focus on book content only)
- Phase 2+: MCP development is IN SCOPE for project-relevant tooling

## Phase 1 Constraints

The following are explicitly OUT OF SCOPE for Phase 1 and MUST NOT be implemented:

| Excluded Item | Reason | Future Phase |
|---------------|--------|--------------|
| ROS tutorials | Requires executable code | Phase 2+ |
| Gazebo simulations | Requires external tools | Phase 3+ |
| Isaac SDK examples | Requires NVIDIA infrastructure | Phase 3+ |
| Interactive code execution | Requires backend | Phase 2+ |
| Video hosting | Requires external service | Phase 2+ |
| User accounts | Requires backend | Not planned |
| Comments/forums | Requires backend | Not planned |
| i18n/localization | Scope creep | Phase 2+ |

## Quality Standards

### Content Quality

- Technical accuracy: Content MUST be factually correct and cite sources where applicable
- Audience appropriateness: Content MUST target advanced AI students and robotics engineers
- Completeness: Each module MUST cover its stated learning outcomes
- Consistency: Terminology MUST be consistent across all modules (see terminology reference)

### File Organization

```
Hackathon_01/
├── .claude/                 # Claude Code configuration
│   ├── skills/              # Skills for development guidance
│   │   ├── docusaurus-book/
│   │   ├── github-manager/
│   │   ├── mcp-developer/   # MCP server development guide
│   │   └── physical-ai-content/
│   └── agents/              # Autonomous agents
│       └── github-workflow/
├── physical-ai-book/        # Docusaurus site
│   ├── docs/                # All content here
│   │   ├── curriculum-overview.md  # Homepage (slug: /)
│   │   └── module-N-name/   # One folder per module
│   │       ├── _category_.json  # Sidebar configuration
│   │       ├── index.md     # Module overview + outcomes
│   │       └── *.md         # Chapter files
│   ├── static/              # Assets
│   │   ├── img/module-N/    # Module-specific images
│   │   └── diagrams/        # Shared diagrams
│   └── src/css/custom.css   # Minimal styling only
├── mcp-servers/             # MCP server projects (Phase 2+)
│   └── README.md            # MCP development workspace
└── specs/                   # Feature specifications
    └── Phase I/
        └── 001-physical-ai-book/
```

## Governance

This constitution governs all development decisions for the Physical AI Book project.

**Amendment Process:**
1. Propose amendment with rationale
2. Document impact on existing artifacts
3. Update version number following semver
4. Update dependent templates if affected

**Compliance:**
- All PRs/commits MUST verify compliance with these principles
- Constitution violations MUST be justified in writing or resolved
- Phase 1 constraints are NON-NEGOTIABLE until Phase 2 begins

**Version**: 1.1.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-24

---

## Amendment History

### v1.1.0 (2025-12-24)
- **Added**: Principle VI - MCP Server Development (Phase 2+)
- **Added**: mcp-servers/ directory for MCP server projects
- **Added**: .claude/skills/mcp-developer/ skill for development guidance
- **Rationale**: MCP servers will enhance project with specialized tooling for Physical AI research and documentation workflows
- **Scope**: MCP development in scope for Phase 2+, out of scope for Phase 1

### v1.0.0 (2025-12-23)
- Initial constitution with 5 core principles
- Phase 1 constraints defined
- Quality standards established
