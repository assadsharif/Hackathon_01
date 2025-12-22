# Quickstart: Physical AI Book Development

**Feature Branch**: `001-physical-ai-book`
**Date**: 2025-12-22
**Phase**: 1

---

## Prerequisites

- Node.js 20.x LTS
- npm 10.x
- Git
- GitHub account with repository access

---

## Initial Setup

### 1. Initialize Docusaurus Project

```bash
# From repository root, create the book project
npx create-docusaurus@latest physical-ai-book classic --typescript

# Navigate to project
cd physical-ai-book

# Install dependencies
npm install
```

### 2. Configure for GitHub Pages

Edit `docusaurus.config.ts`:

```typescript
const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive guide to embodied intelligence',
  favicon: 'img/favicon.ico',

  url: 'https://<org-or-user>.github.io',
  baseUrl: '/physical-ai-book/',

  organizationName: '<org-or-user>',
  projectName: 'physical-ai-book',
  trailingSlash: false,

  // Docs-only mode
  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',  // Docs at root
          sidebarPath: './sidebars.ts',
        },
        blog: false,  // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],
};
```

### 3. Create Module Folders

```bash
# Remove default docs
rm -rf docs/*

# Create module structure
mkdir -p docs/module-1-intro
mkdir -p docs/module-2-embodied
mkdir -p docs/module-3-humanoid
mkdir -p docs/module-4-perception
mkdir -p docs/module-5-control
mkdir -p docs/module-6-learning
mkdir -p docs/module-7-future

# Create static asset folders
mkdir -p static/img/module-{1,2,3,4,5,6,7}
mkdir -p static/diagrams
```

### 4. Create Curriculum Overview

Create `docs/curriculum-overview.md` as the homepage.

### 5. Create Module Category Files

For each module, create `_category_.json` with appropriate position and label.

---

## Local Development

```bash
# Start development server
npm run start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

---

## Adding Content

### New Module Overview
1. Create `docs/module-N-name/index.md`
2. Add frontmatter with `sidebar_position: 0`
3. Include learning outcomes section

### New Chapter
1. Create `docs/module-N-name/chapter-name.md`
2. Add frontmatter with sequential `sidebar_position`
3. Follow chapter template structure

---

## Deployment

### GitHub Actions (Automatic)

Push to `main` branch triggers automatic deployment.

### Manual Build

```bash
npm run build
# Output in `build/` directory
```

---

## Verification Checklist

- [ ] `npm run build` completes without errors
- [ ] All modules appear in sidebar
- [ ] Search indexes content correctly
- [ ] Mobile layout works (test at 375px width)
- [ ] All internal links resolve
