# Migrate from Nixpacks to Dockerfile

## Context

Currently using Nixpacks (`nixpacks.toml` + `railway.json`) for Railway deployment.
Nixpacks is deprecated/maintenance-only, so migrating to Dockerfile for platform-agnostic deployment.

---

## Current Setup

**Files to replace:**
- `nixpacks.toml` — Nixpacks config
- `railway.json` — Points to Nixpacks builder

**Dependencies:**
- Python 3.11+
- uv for package management
- Playwright + Chromium for JS-rendered pages
- SQLite (data persisted via volume mount)

---

## Implementation

### Step 1: Create Dockerfile

Create `Dockerfile` at project root:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY shared/pyproject.toml shared/
COPY jobflow_api/pyproject.toml jobflow_api/

# Install dependencies
RUN uv sync --project jobflow_api

# Install Playwright browsers
RUN uv run --project jobflow_api playwright install chromium --with-deps

# Copy source code
COPY shared/ shared/
COPY jobflow_api/ jobflow_api/

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uv", "run", "--project", "jobflow_api", "uvicorn", "jobflow_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Update railway.json

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "watchPatterns": ["shared/**", "jobflow_api/**", "Dockerfile"]
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Step 3: Add .dockerignore

```
.git
.gitignore
.claude
.mypy_cache
.ruff_cache
.pytest_cache
__pycache__
*.pyc
*.pyo
.venv
*/.venv
web/
jobflow_mvp/
*.md
Makefile
nixpacks.toml
```

### Step 4: Delete nixpacks.toml

Remove the deprecated config file.

---

## Files to Modify

| File | Action |
|------|--------|
| `Dockerfile` | Create (new) |
| `.dockerignore` | Create (new) |
| `railway.json` | Update builder to DOCKERFILE |
| `nixpacks.toml` | Delete |

---

## Verification

1. Build locally: `docker build -t jobflow-api .`
2. Run locally: `docker run -p 8000:8000 -v $(pwd)/data:/app/data jobflow-api`
3. Test health: `curl http://localhost:8000/health`
4. Deploy to Railway and verify production works

---

## Notes

- Playwright browsers are installed during build (~400MB added to image)
- SQLite data persists via Railway volume mount at `/app/data`
- No changes to application code needed
