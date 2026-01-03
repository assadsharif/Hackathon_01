# Developer Quickstart: RAG Chatbot

**Feature**: Integrated RAG Chatbot for Physical AI Book
**Audience**: Developers setting up local development environment
**Last Updated**: 2025-12-25

## Overview

This guide walks through setting up the RAG chatbot development environment, running the backend API, integrating the frontend component, and indexing book content for retrieval.

**Architecture Summary**:
- **Backend**: Python 3.11+ FastAPI service with agent orchestration
- **Frontend**: React/TypeScript components embedded in Docusaurus
- **Storage**: Neon Serverless Postgres (metadata), Qdrant Cloud (vectors), Browser LocalStorage (sessions)

---

## Prerequisites

### Required Software

- **Python 3.11+** ([download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([download](https://nodejs.org/))
- **Docker Desktop** (optional, for containerized deployment) ([download](https://www.docker.com/products/docker-desktop/))
- **Git** ([download](https://git-scm.com/downloads))

### Required Accounts & API Keys

1. **OpenAI API Key** ([get key](https://platform.openai.com/api-keys))
   - Used for embeddings (text-embedding-3-small) and answer synthesis (GPT-3.5-turbo)
   - Billing enabled required

2. **Qdrant Cloud Account** ([sign up](https://cloud.qdrant.io/))
   - Create free cluster (1GB limit)
   - Get API URL and API Key from dashboard

3. **Neon Serverless Postgres** ([sign up](https://neon.tech/))
   - Create free project
   - Copy connection string (postgres://...)

---

## Project Structure

```text
Hackathon_01/
├── rag-chatbot/                  # Backend API service
│   ├── src/
│   ├── tests/
│   ├── scripts/
│   ├── pyproject.toml
│   └── .env.example
├── physical-ai-book/             # Docusaurus site
│   ├── src/
│   │   └── components/ChatbotPanel/
│   └── docs/                     # Book content (MDX files)
└── specs/001-rag-chatbot/        # This directory
    ├── spec.md
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── contracts/
    └── quickstart.md (this file)
```

---

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/Hackathon_01.git
cd Hackathon_01
git checkout 001-rag-chatbot
```

---

## Step 2: Backend Setup (FastAPI Service)

### 2.1 Create Python Virtual Environment

```bash
cd rag-chatbot
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
# Install production dependencies
pip install --upgrade pip
pip install -e .

# Install development dependencies (testing, linting)
pip install -e ".[dev]"
```

**Dependencies** (defined in `pyproject.toml`):
- `fastapi[all]` - Web framework
- `openai>=1.0.0` - OpenAI SDK (embeddings, LLM)
- `qdrant-client` - Vector database client
- `psycopg[binary]>=3.0` - Postgres driver
- `pydantic>=2.0` - Data validation
- `tiktoken` - Token counting
- `pytest`, `pytest-asyncio` - Testing
- `black`, `ruff` - Code formatting/linting

### 2.3 Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...

# Qdrant Configuration
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=physical-ai-book-v1

# Neon Postgres Configuration
POSTGRES_URL=postgres://user:password@host.neon.tech/dbname

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_QUERIES_PER_MINUTE=10

# Performance Tuning
CHUNK_RETRIEVAL_COUNT=5
RETRIEVAL_TIMEOUT_SECONDS=2
SYNTHESIS_TIMEOUT_SECONDS=2
```

### 2.4 Initialize Database Schema

```bash
# Run Postgres migrations
python scripts/migrate_db.py

# Verify tables created
python -c "from src.services.storage import check_postgres_health; check_postgres_health()"
```

### 2.5 Create Qdrant Collection

```bash
# Setup vector database collection
python scripts/setup_vector_db.py

# Verify collection exists
python -c "from src.services.storage import check_qdrant_health; check_qdrant_health()"
```

---

## Step 3: Index Book Content

### 3.1 Verify Book Content Exists

```bash
cd ../physical-ai-book
ls -la docs/
# Should see: module-1-intro/, module-2-embodied/, ..., Part-1/, Part-2/, etc.
```

### 3.2 Run Indexing Script

```bash
cd ../rag-chatbot
python scripts/index_book_content.py \
  --book-path ../physical-ai-book/docs \
  --collection physical-ai-book-v1 \
  --chunk-size 250 \
  --overlap 50

# Expected output:
# Parsed 7 modules, 50 chapters
# Generated 3,482 chunks
# Created embeddings (batch 1/70)...
# Upserted to Qdrant: 3,482 vectors
# Inserted to Postgres: 3,482 metadata records
# Indexing complete in 4m 32s
```

**What this does**:
1. Parses all Markdown files in `docs/`
2. Chunks paragraphs (~250 tokens with 50-token overlap)
3. Generates embeddings via OpenAI API (`text-embedding-3-small`)
4. Uploads vectors to Qdrant
5. Stores metadata (module, chapter, section IDs) in Postgres

---

## Step 4: Run Backend API

### 4.1 Start FastAPI Server

```bash
cd rag-chatbot
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4.2 Test Health Endpoint

```bash
curl http://localhost:8000/v1/health | jq
```

**Expected response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "qdrant": {"status": "healthy", "latency_ms": 45},
    "postgres": {"status": "healthy", "latency_ms": 12},
    "openai": {"status": "healthy", "latency_ms": 230}
  },
  "timestamp": "2025-12-25T10:30:00Z"
}
```

### 4.3 Test Query Endpoint

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "What is sensor fusion?",
    "mode": "full-book",
    "current_page_url": "/docs/module-4/perception"
  }' | jq
```

**Expected response**:
```json
{
  "answer": "Sensor fusion is the process of combining data from multiple sensors...",
  "citations": [
    {"text": "Module 4: Perception Systems", "url": "/docs/module-4/sensor-fusion#overview"}
  ],
  "mode": "full-book",
  "latency_ms": 2350
}
```

---

## Step 5: Frontend Setup (Docusaurus Integration)

### 5.1 Install Frontend Dependencies

```bash
cd ../physical-ai-book
npm install
```

### 5.2 Configure API Endpoint

Edit `docusaurus.config.ts` to add chatbot API URL:

```typescript
const config: Config = {
  // ... existing config
  customFields: {
    chatbotApiUrl: process.env.CHATBOT_API_URL || 'http://localhost:8000/v1',
  },
};
```

Create `.env.local`:

```bash
CHATBOT_API_URL=http://localhost:8000/v1
```

### 5.3 Integrate Chatbot Component

Create `src/theme/Root.tsx` (Docusaurus theme wrapper):

```typescript
import React from 'react';
import ChatbotIntegration from '@site/src/components/ChatbotPanel/ChatbotIntegration';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <ChatbotIntegration />
    </>
  );
}
```

### 5.4 Start Docusaurus Dev Server

```bash
npm start
```

**Expected output**:
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### 5.5 Test Chatbot Integration

1. Open browser: http://localhost:3000
2. Click chatbot icon (bottom-right corner)
3. Type question: "What is Physical AI?"
4. Verify:
   - Loading indicator appears
   - Answer renders with citations
   - Citations are clickable and navigate to correct sections
   - Conversation persists in LocalStorage (check DevTools → Application → LocalStorage)

---

## Step 6: Run Tests

### 6.1 Backend Tests

```bash
cd ../rag-chatbot

# Run unit tests (agent roles)
pytest tests/unit/ -v

# Run integration tests (API endpoints)
pytest tests/integration/ -v

# Run all tests with coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### 6.2 Frontend Tests

```bash
cd ../physical-ai-book

# Run component tests
npm test

# Run E2E tests (requires backend running)
npx playwright install  # First time only
npm run test:e2e
```

---

## Step 7: Development Workflow

### Common Tasks

**Add new book content**:
```bash
cd physical-ai-book/docs
# Edit/add MDX files
cd ../../rag-chatbot
python scripts/index_book_content.py --incremental  # Re-index only changed files
```

**Update agent logic**:
```bash
cd rag-chatbot
# Edit src/agents/*.py
pytest tests/unit/test_agents.py  # Test changes
uvicorn src.api.main:app --reload  # Auto-reloads on file save
```

**Update frontend UI**:
```bash
cd physical-ai-book
# Edit src/components/ChatbotPanel/*.tsx
npm start  # Auto-reloads on file save
```

### Debugging Tips

**Backend debugging**:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn src.api.main:app --reload

# Use Python debugger
python -m pdb scripts/index_book_content.py
```

**Frontend debugging**:
- Open browser DevTools → Console
- Check Network tab for API calls
- Inspect LocalStorage for session data
- Use React DevTools extension

---

## Step 8: Deployment (Production)

### 8.1 Backend Deployment (Render/Railway)

**Option A: Deploy to Render**

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: rag-chatbot-api
    env: python
    buildCommand: pip install -e .
    startCommand: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: POSTGRES_URL
        sync: false
```

2. Push to GitHub and connect Render service
3. Set environment variables in Render dashboard
4. Deploy

**Option B: Deploy to Railway**

```bash
cd rag-chatbot
railway login
railway init
railway up
```

### 8.2 Frontend Deployment (GitHub Pages)

```bash
cd physical-ai-book

# Update docusaurus.config.ts with production API URL
# customFields.chatbotApiUrl = 'https://your-api.onrender.com/v1'

npm run build
npm run deploy
```

### 8.3 Update Frontend to Use Production API

Edit `docusaurus.config.ts`:

```typescript
customFields: {
  chatbotApiUrl: 'https://rag-chatbot-api.onrender.com/v1',
},
```

---

## Troubleshooting

### Backend won't start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
source venv/bin/activate  # Activate virtual environment
pip install -e ".[dev]"
```

### Qdrant connection fails

**Problem**: `QdrantException: Connection timeout`

**Solution**:
- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant Cloud dashboard for cluster status
- Test connection: `curl -H "api-key: YOUR_KEY" https://your-cluster.cloud.qdrant.io/collections`

### OpenAI API errors

**Problem**: `AuthenticationError: Incorrect API key`

**Solution**:
- Verify `OPENAI_API_KEY` in `.env`
- Ensure billing enabled on OpenAI account
- Check API key has not expired

### Book indexing fails

**Problem**: `FileNotFoundError: No such file or directory: '../physical-ai-book/docs'`

**Solution**:
```bash
# Ensure you're in rag-chatbot directory
cd rag-chatbot
# Verify book path exists
ls -la ../physical-ai-book/docs
# Run with absolute path
python scripts/index_book_content.py --book-path /absolute/path/to/physical-ai-book/docs
```

### Frontend chatbot not loading

**Problem**: Chatbot icon doesn't appear

**Solution**:
1. Check `src/theme/Root.tsx` exists
2. Verify `ChatbotIntegration` component imported correctly
3. Check browser console for errors
4. Ensure Docusaurus dev server restarted after adding Root.tsx

### CORS errors in browser

**Problem**: `Access to XMLHttpRequest at 'http://localhost:8000' ... has been blocked by CORS policy`

**Solution**:
Add CORS middleware to FastAPI (in `src/api/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Docusaurus dev server
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

---

## Next Steps

1. **Read Architecture Docs**: Review `plan.md` for system design details
2. **Explore API Contract**: See `contracts/openapi.yaml` for full API specification
3. **Understand Data Model**: Review `data-model.md` for entity schemas
4. **Run E2E Tests**: Validate full user journeys with Playwright
5. **Customize UI**: Edit ChatbotPanel components to match branding

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Cloud Docs](https://qdrant.tech/documentation/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Docusaurus Docs](https://docusaurus.io/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/yourusername/Hackathon_01/issues
- **Spec Reference**: `specs/001-rag-chatbot/spec.md`
- **Architecture Plan**: `specs/001-rag-chatbot/plan.md`
