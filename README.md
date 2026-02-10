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

## Deployment

Production runs on **Railway** (API + PostgreSQL) and **Vercel** (frontend).

### Railway (Backend + Database)

1. Create project, add PostgreSQL database
2. Add service from repo (Dockerfile: `jobflow_api/Dockerfile`)
3. Connect Postgres to the service (auto-injects `DATABASE_URL`)
4. Set environment variables (see table below)
5. After first deploy: `railway run alembic stamp head` to sync migrations

### Vercel (Frontend)

1. Import repo, set root directory to `web/`
2. Set environment variables (see table below)
3. Add Google OAuth callback URL: `https://your-app.vercel.app/api/auth/callback/google`

## Environment Variables

### Railway (API)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Auto | PostgreSQL connection (auto-injected by Railway) |
| `CORS_ORIGINS` | Yes | Frontend URL, e.g., `["https://your-app.vercel.app"]` |
| `API_KEY` | Yes | Shared secret for Vercel → Railway auth |
| `GOOGLE_API_KEY` | No | Gemini API key for LLM extraction |

### Vercel (Frontend)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL **public** URL (for Better Auth) |
| `BACKEND_URL` | Yes | Railway API URL |
| `API_KEY` | Yes | Must match Railway's `API_KEY` |
| `BETTER_AUTH_SECRET` | Yes | Random secret for session signing |
| `NEXT_PUBLIC_APP_URL` | Yes | Vercel app URL (for OAuth callbacks) |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | No | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | No | GitHub OAuth client secret |

## License

MIT
