# RAG Chatbot for Physical AI Book

A Retrieval-Augmented Generation (RAG) chatbot that provides intelligent question-answering capabilities for the Physical AI & Humanoid Robotics Docusaurus book. The chatbot supports two modes: full-book retrieval and selected-text-only retrieval, with precise source citations.

## Overview

This backend API service orchestrates multiple specialized agent roles to deliver accurate, cited responses:

- **Context Selection Agent**: Determines retrieval scope (full-book vs selected-text)
- **Retrieval Agent**: Fetches relevant book chunks via vector search (Qdrant)
- **Answer Synthesis Agent**: Generates natural language responses using LLM (OpenAI GPT-3.5-turbo)
- **Citation & Guardrails Agent**: Creates precise citations and enforces content boundaries

## Architecture

- **Backend**: Python 3.11+ with FastAPI
- **Vector Database**: Qdrant Cloud (free tier)
- **Metadata Storage**: Neon Serverless Postgres
- **LLM**: OpenAI API (text-embedding-3-small for embeddings, GPT-3.5-turbo for synthesis)
- **Frontend Integration**: React components embedded in Docusaurus site

## Prerequisites

- Python 3.11 or higher
- OpenAI API key ([get here](https://platform.openai.com/api-keys))
- Qdrant Cloud account ([sign up](https://cloud.qdrant.io/))
- Neon Serverless Postgres account ([sign up](https://neon.tech/))

## Quick Start

### 1. Clone and Setup

```bash
cd rag-chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Initialize Database

```bash
# Run Postgres migrations
python scripts/migrate_db.py

# Setup Qdrant collection
python scripts/setup_vector_db.py
```

### 4. Index Book Content

```bash
python scripts/index_book_content.py \
  --book-path ../physical-ai-book/docs \
  --collection physical-ai-book-v1 \
  --chunk-size 250 \
  --overlap 50
```

### 5. Run API Server

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test API

```bash
# Health check
curl http://localhost:8000/v1/health | jq

# Submit query
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "What is sensor fusion?",
    "mode": "full-book",
    "current_page_url": "/docs/module-4/perception"
  }' | jq
```

## Project Structure

```
rag-chatbot/
├── src/
│   ├── agents/          # Agent role implementations
│   ├── api/             # FastAPI endpoints and middleware
│   ├── models/          # Pydantic data models
│   ├── services/        # Business logic (orchestrator, storage)
│   └── config/          # Settings and prompt templates
├── tests/
│   ├── unit/            # Unit tests for agent roles
│   ├── integration/     # API endpoint integration tests
│   └── e2e/             # End-to-end user journey tests
├── scripts/
│   ├── index_book_content.py  # Book content indexing
│   ├── migrate_db.py          # Database schema migrations
│   └── setup_vector_db.py     # Qdrant collection setup
├── pyproject.toml       # Python dependencies and tool config
├── .env.example         # Environment variable template
└── README.md            # This file
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Code Formatting

```bash
# Format code with black
black src/ tests/ scripts/

# Lint code with ruff
ruff check src/ tests/ scripts/

# Type check with mypy
mypy src/
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v
```

## API Endpoints

### POST /v1/query

Submit a chatbot query (full-book or selected-text mode).

**Request**:
```json
{
  "session_id": "uuid",
  "query": "What is sensor fusion?",
  "mode": "full-book",
  "current_page_url": "/docs/module-4/perception"
}
```

**Response**:
```json
{
  "answer": "Sensor fusion is...",
  "citations": [
    {"text": "Module 4: Perception", "url": "/docs/module-4/sensor-fusion#overview"}
  ],
  "mode": "full-book",
  "latency_ms": 2350
}
```

### GET /v1/health

Check service health and dependent service status.

**Response**:
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

## Deployment

### Local Development with Docker Compose (T056)

**Recommended for local development** - spins up backend, Postgres, and Qdrant together:

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and set OPENAI_API_KEY (required)
# Leave other values at defaults for Docker Compose

# 3. Start all services
docker-compose up -d

# 4. Check service health
curl http://localhost:8000/v1/health | jq

# 5. View logs
docker-compose logs -f backend

# 6. Stop services
docker-compose down

# 7. Stop and remove volumes (clean slate)
docker-compose down -v
```

**Services**:
- Backend API: `http://localhost:8000`
- Qdrant UI: `http://localhost:6333/dashboard`
- PostgreSQL: `localhost:5432`

### Docker (Production)

```bash
# Build image
docker build -t rag-chatbot .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e QDRANT_URL=https://your-cluster.qdrant.io \
  -e QDRANT_API_KEY=your_key \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e ALLOWED_ORIGINS=https://your-docusaurus-domain.com \
  rag-chatbot
```

### Render Deployment (T057 - Recommended for Production)

1. **Create Qdrant Cloud Cluster** (free tier)
   - Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/)
   - Create new cluster
   - Note cluster URL and API key

2. **Create Neon Postgres Database** (free tier)
   - Sign up at [neon.tech](https://neon.tech/)
   - Create new project
   - Copy connection string

3. **Deploy to Render**
   - Fork/push this repo to GitHub
   - Go to [render.com](https://render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Configure:
     - **Name**: `rag-chatbot-api`
     - **Region**: Choose closest to your users
     - **Branch**: `main` or `001-rag-chatbot`
     - **Root Directory**: `rag-chatbot`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -e .`
     - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: Free (or paid for production)

4. **Set Environment Variables** (in Render dashboard)
   ```
   OPENAI_API_KEY=sk-proj-...
   OPENAI_MODEL=gpt-4
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small

   QDRANT_URL=https://your-cluster-url.qdrant.io
   QDRANT_API_KEY=your-qdrant-api-key
   QDRANT_COLLECTION_NAME=physical_ai_book

   DATABASE_URL=postgresql://user:pass@host.neon.tech:5432/dbname

   ALLOWED_ORIGINS=https://assadsharif.github.io,https://your-domain.com
   LOG_LEVEL=INFO
   RATE_LIMIT_REQUESTS=10
   ```

5. **Deploy and Index Content**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - SSH into Render service or run locally:
     ```bash
     python scripts/index_book_content.py \
       --book-path ../physical-ai-book/docs \
       --collection physical_ai_book
     ```
   - Access your API at: `https://rag-chatbot-api.onrender.com`

6. **Update Frontend**
   - In `physical-ai-book/.env`:
     ```
     CHATBOT_API_URL=https://rag-chatbot-api.onrender.com/v1
     ```
   - Rebuild and redeploy Docusaurus site

### Railway Deployment (Alternative)

1. **Deploy**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Initialize project
   railway init

   # Link to repo
   railway link

   # Add Postgres and Qdrant plugins
   railway add postgresql

   # Set environment variables
   railway variables set OPENAI_API_KEY=sk-proj-...
   railway variables set QDRANT_URL=https://...
   railway variables set QDRANT_API_KEY=...
   railway variables set ALLOWED_ORIGINS=https://your-domain.com

   # Deploy
   railway up
   ```

2. **Get service URL**
   ```bash
   railway domain
   ```

### Re-Indexing Book Content (T061)

**When to re-index**: Whenever you modify/add content in `physical-ai-book/docs/`:

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Set environment variables (if not in .env)
export OPENAI_API_KEY=your_key
export QDRANT_URL=https://your-cluster.qdrant.io
export QDRANT_API_KEY=your_key

# 3. Run indexing script
python scripts/index_book_content.py \
  --book-path ../physical-ai-book/docs \
  --collection physical_ai_book \
  --chunk-size 250 \
  --overlap 50 \
  --force  # Add --force to overwrite existing collection

# 4. Verify indexing
python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='YOUR_URL', api_key='YOUR_KEY')
info = client.get_collection('physical_ai_book')
print(f'Indexed {info.points_count} chunks')
"
```

**Automation**: Set up GitHub Action to auto-reindex on doc changes:
```yaml
# .github/workflows/reindex-on-docs-change.yml
name: Re-index on Docs Change
on:
  push:
    branches: [main]
    paths: ['physical-ai-book/docs/**']
jobs:
  reindex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          cd rag-chatbot
          pip install -e .
          python scripts/index_book_content.py --force
```

See [Deployment Guide](../specs/001-rag-chatbot/quickstart.md) for detailed instructions.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `QDRANT_URL` | Qdrant Cloud URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `QDRANT_COLLECTION` | Collection name | `physical-ai-book-v1` |
| `POSTGRES_URL` | Neon Postgres connection string | Required |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_QUERIES_PER_MINUTE` | Rate limit per session | `10` |

## Performance Goals

- 95% of queries answered within 3 seconds end-to-end
- Vector retrieval <500ms for 99th percentile
- Support 10 concurrent users initially (free tier constraints)

## Troubleshooting

### "Connection timeout" to Qdrant

- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant Cloud dashboard for cluster status

### "Authentication error" from OpenAI

- Verify `OPENAI_API_KEY` in `.env`
- Ensure billing enabled on OpenAI account

### "No module named 'fastapi'"

- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -e ".[dev]"`

## Documentation

- [Feature Specification](../specs/001-rag-chatbot/spec.md)
- [Architecture Plan](../specs/001-rag-chatbot/plan.md)
- [Data Model](../specs/001-rag-chatbot/data-model.md)
- [API Contract](../specs/001-rag-chatbot/contracts/openapi.yaml)
- [Developer Quickstart](../specs/001-rag-chatbot/quickstart.md)
- [Implementation Tasks](../specs/001-rag-chatbot/tasks.md)

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, see the [specification documentation](../specs/001-rag-chatbot/) or open an issue on GitHub.
