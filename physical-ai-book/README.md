# Physical AI & Humanoid Robotics Documentation Book

An interactive educational resource on Physical AI and Humanoid Robotics, built with [Docusaurus](https://docusaurus.io/) and enhanced with an intelligent RAG chatbot for Q&A.

## Overview

This documentation site provides comprehensive coverage of:
- **Module 1**: Introduction to Physical AI
- **Module 2**: Embodied Intelligence
- **Module 3**: Humanoid Robotics
- **Module 4**: Perception Systems
- **Module 5**: Control and Motion
- **Module 6**: Learning Approaches
- **Module 7**: Future Directions

### Features

- 📚 Structured curriculum with 7 learning modules
- 🤖 **Integrated RAG Chatbot** - Ask questions about book content in two modes:
  - **Full-book mode**: Search entire book for answers
  - **Selected-text mode**: Ask about highlighted passages
- 🔍 Algolia DocSearch integration for fast content search
- 📱 Responsive design for desktop and mobile
- 🌙 Dark mode support
- 🎯 Precise citations linking back to source material

## Quick Start

### Installation

```bash
# Using npm
npm install

# Using yarn
yarn install
```

### Local Development

```bash
# Using npm
npm start

# Using yarn
yarn start
```

This starts a local development server at `http://localhost:3000` with hot-reload.

### Build

```bash
# Using npm
npm run build

# Using yarn
yarn build
```

Generates static content into the `build/` directory for production deployment.

### Local Testing of Production Build

```bash
# Using npm
npm run serve

# Using yarn
yarn serve
```

Serves the production build locally to test before deployment.

## Chatbot Integration (T058 - Phase 7)

The site includes an embedded RAG (Retrieval-Augmented Generation) chatbot that helps users explore book content.

### How the Chatbot Works

1. **Frontend Components** (this repo):
   - `src/components/ChatbotPanel/` - React UI components
   - `src/hooks/` - Custom hooks for session, API, text selection
   - `src/theme/Root.tsx` - Global chatbot mount point

2. **Backend API** (see `../rag-chatbot/README.md`):
   - FastAPI server with multi-agent RAG pipeline
   - Vector search via Qdrant
   - OpenAI GPT-4 for answer synthesis

### Local Development with Chatbot

**Option 1: Frontend Only** (chatbot disabled)
```bash
npm start
# Chatbot will show "Service unavailable" - frontend works normally
```

**Option 2: Full Stack** (frontend + backend)

1. **Start Backend Services**
   ```bash
   # In rag-chatbot directory
   cd ../rag-chatbot
   docker-compose up -d

   # Verify backend is running
   curl http://localhost:8000/v1/health
   ```

2. **Configure Frontend**
   ```bash
   # In physical-ai-book directory
   # Create .env file (or use existing)
   echo "CHATBOT_API_URL=http://localhost:8000/v1" > .env
   ```

3. **Start Frontend**
   ```bash
   npm start
   # Open http://localhost:3000
   # Click chatbot FAB (floating button) to test
   ```

### Production Configuration

For GitHub Pages deployment with hosted backend:

1. **Set environment variable** in `.env`:
   ```
   CHATBOT_API_URL=https://your-backend-api.onrender.com/v1
   ```

2. **Build and deploy**:
   ```bash
   npm run build
   GIT_USER=<username> yarn deploy
   ```

3. **Verify CORS** in backend:
   - Ensure `ALLOWED_ORIGINS` includes `https://assadsharif.github.io`
   - See `../rag-chatbot/README.md` for backend deployment

## Project Structure

```
physical-ai-book/
├── docs/                    # Markdown documentation content
│   ├── Part-1/             # Theoretical foundations (Modules 1-3)
│   ├── Part-2/             # Technical implementations (Modules 4-7)
│   └── curriculum-overview.md
├── src/
│   ├── components/
│   │   └── ChatbotPanel/   # RAG chatbot UI components
│   ├── hooks/              # Custom React hooks
│   │   ├── useChatbotAPI.ts
│   │   ├── useChatSession.ts
│   │   └── useTextSelection.ts
│   ├── theme/
│   │   ├── Root.tsx        # Global chatbot integration
│   │   └── ChatbotIntegration.tsx
│   ├── css/
│   │   └── custom.css      # Global styles + chatbot theming
│   └── pages/              # Custom React pages
├── static/                 # Static assets (images, files)
├── docusaurus.config.ts    # Docusaurus configuration
├── sidebars.ts             # Sidebar structure
└── package.json

```

## Deployment

### GitHub Pages (Automated)

This site is deployed to GitHub Pages via GitHub Actions:

1. **Push to main branch**
   ```bash
   git push origin main
   ```

2. **GitHub Actions runs**:
   - Builds Docusaurus site
   - Deploys to `gh-pages` branch
   - Available at: `https://assadsharif.github.io/Hackathon_01/`

3. **Workflow file**: `.github/workflows/deploy-gh-pages.yml`

### Manual Deployment

Using SSH:
```bash
USE_SSH=true yarn deploy
```

Not using SSH:
```bash
GIT_USER=<Your GitHub username> yarn deploy
```

### Other Platforms

- **Vercel**: Connect GitHub repo, set root directory to `physical-ai-book/`
- **Netlify**: Same as Vercel
- **Cloudflare Pages**: Build command: `npm run build`, output: `build/`

## Development Guidelines

### Adding New Content

1. **Create markdown file** in appropriate module:
   ```bash
   # Example: New chapter in Module 4
   touch docs/Part-2/module-4-perception/new-chapter.md
   ```

2. **Update sidebar** in `sidebars.ts`:
   ```typescript
   {
     type: 'category',
     label: 'Module 4: Perception',
     items: [
       'Part-2/module-4-perception/new-chapter',
     ],
   }
   ```

3. **Re-index for chatbot** (if backend is deployed):
   ```bash
   cd ../rag-chatbot
   python scripts/index_book_content.py --force
   ```

### Customizing Chatbot Appearance

Edit `src/css/custom.css`:
```css
:root {
  --chatbot-fab-bg: var(--ifm-color-primary);
  --chatbot-z-index: 100;
  /* ... other chatbot variables */
}
```

### Modifying Chatbot Behavior

- **API client**: `src/hooks/useChatbotAPI.ts`
- **Session management**: `src/hooks/useChatSession.ts`
- **Text selection**: `src/hooks/useTextSelection.ts`
- **UI components**: `src/components/ChatbotPanel/`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHATBOT_API_URL` | Backend API URL | `http://localhost:8000/v1` |
| `NODE_ENV` | Build environment | `development` |

Create `.env` file in project root:
```bash
CHATBOT_API_URL=https://your-backend.onrender.com/v1
```

## Troubleshooting

### Chatbot Not Responding

1. Check backend health:
   ```bash
   curl https://your-backend.onrender.com/v1/health
   ```

2. Check browser console for CORS errors

3. Verify `ALLOWED_ORIGINS` in backend includes your domain

### Build Fails

1. Clear cache and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. Check for broken markdown links:
   ```bash
   npm run build 2>&1 | grep "Broken link"
   ```

### Algolia Search Not Working

1. Apply for DocSearch at [docsearch.algolia.com/apply/](https://docsearch.algolia.com/apply/)
2. Update `docusaurus.config.ts` with provided credentials
3. Rebuild and redeploy

## Documentation

- [RAG Chatbot Backend](../rag-chatbot/README.md)
- [Chatbot Feature Specification](../specs/001-rag-chatbot/spec.md)
- [Implementation Tasks](../specs/001-rag-chatbot/tasks.md)
- [Docusaurus Documentation](https://docusaurus.io/)

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-chapter`
3. Add content and test locally
4. Commit changes: `git commit -m "Add new chapter on X"`
5. Push branch: `git push origin feature/new-chapter`
6. Open Pull Request

## Support

For issues or questions:
- Open an issue on GitHub
- See [specification documentation](../specs/001-rag-chatbot/)
- Check [Docusaurus community](https://discord.gg/docusaurus)
