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
| POST | /api/jobs/manual | Create job manually |
| POST | /api/jobs/parse | Extract fields from text (LLM) |
| GET | /api/jobs | List jobs (paginated) |
| GET | /api/jobs/{id} | Get single job |
| PATCH | /api/jobs/{id} | Update job fields |
| PATCH | /api/jobs/{id}/flag | Flag for review |
| DELETE | /api/jobs/{id} | Delete job |
| DELETE | /api/jobs | Delete all user jobs |
| GET | /api/jobs/export | Download CSV |

Swagger UI: http://localhost:8000/docs

## Extraction Pipeline

1. **BeautifulSoup** — Fast, parses JSON-LD + meta tags
2. **Playwright** — Fallback for JS-rendered pages
3. **LLM** — Fallback for complex layouts (requires GOOGLE_API_KEY)

PII (emails, phones, LinkedIn URLs) is filtered before storage.

## Compliance

Built with enterprise-grade compliance in mind:

| Feature | Regulation | Description |
|---------|------------|-------------|
| **Robots.txt checking** | CFAA | Respects `robots.txt` directives; blocks scraping of sites that disallow it |
| **PII filtering** | GDPR | Strips emails, phone numbers, names, and LinkedIn URLs before storage |
| **Rate limiting** | ToS | Configurable request limits to avoid overloading target sites |
| **Honest User-Agent** | Best practice | Identifies as `JobflowBot/1.0` when checking robots.txt |

Sites that block scraping (e.g., LinkedIn) are automatically rejected. Use manual entry for those.

Set `CHECK_ROBOTS=false` to disable robots.txt checking (not recommended for production).

## Testing

```sh
# Shared package (15 tests)
uv run --project shared pytest shared/tests/ -v

# API (19 tests)
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
| `CHECK_ROBOTS` | API | Check robots.txt before scraping (default: `true`) |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend API URL |

## License

MIT
