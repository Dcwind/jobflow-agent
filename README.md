# Jobflow

Job application tracking platform that extracts and organizes job postings from any URL.

## Architecture

```
jobflow-agent/
├── shared/           # Shared Python utilities (extraction, db models)
├── jobflow_api/      # FastAPI backend
├── web/              # Next.js frontend
└── jobflow_mvp/      # Original CLI agent (deprecated)
```

## Quick Start

**Prerequisites:** Python 3.11+, Node.js 20+, uv

```sh
# Start API (port 8000)
uv run --project jobflow_api uvicorn jobflow_api.main:app --reload

# Start frontend (port 3000)
cd web && npm install && npm run dev
```

Open http://localhost:3000, paste job URLs, and extract.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/jobs | Extract jobs from URLs |
| GET | /api/jobs | List jobs (paginated) |
| GET | /api/jobs/{id} | Get single job |
| PATCH | /api/jobs/{id} | Update job fields |
| PATCH | /api/jobs/{id}/flag | Flag for review |
| DELETE | /api/jobs/{id} | Delete job |
| GET | /api/jobs/export | Download CSV |

Swagger UI: http://localhost:8000/docs

## Extraction Pipeline

1. **BeautifulSoup** — Fast, parses JSON-LD + meta tags
2. **Playwright** — Fallback for JS-rendered pages
3. **LLM** — Fallback for complex layouts (requires GOOGLE_API_KEY)

PII (emails, phones, LinkedIn URLs) is filtered before storage.

## Testing

```sh
# Shared package (15 tests)
uv run --project shared pytest shared/tests/ -v

# API (26 tests)
uv run --project jobflow_api pytest jobflow_api/tests/ -v
```

## Deployment (Railway)

The repo includes Dockerfiles for both services.

**API Service:**
- Root directory: `/` (needs access to shared/)
- Dockerfile: `jobflow_api/Dockerfile`
- Environment variables:
  - `DATABASE_URL` — SQLite path (default: `sqlite:///./data/jobs.db`)
  - `CORS_ORIGINS` — Frontend URL (e.g., `https://your-frontend.railway.app`)
  - `GOOGLE_API_KEY` — Optional, for LLM fallback

**Frontend Service:**
- Root directory: `web/`
- Dockerfile: `web/Dockerfile`
- Build args:
  - `NEXT_PUBLIC_API_URL` — API URL (e.g., `https://your-api.railway.app`)

**Railway Setup:**
1. Create new project
2. Add two services from the same repo
3. Configure root directories and environment variables
4. Add persistent volume for SQLite (mount at `/app/data`)

## Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | API | Gemini API key for LLM features |
| `DATABASE_URL` | API | SQLite connection string |
| `CORS_ORIGINS` | API | Allowed frontend origins (comma-separated) |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend API URL |

## License

MIT
