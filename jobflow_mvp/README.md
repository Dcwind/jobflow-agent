# Jobflow Agent MVP

An enterprise-ready scaffold for a Job Application Tracker Agent powered by Google's Agent Development Kit (ADK). The MVP ingests a single job posting URL, extracts headline fields, and appends the record to a structured CSV datastore for future orchestration.

## Architecture

- **main.py** – CLI entry point that triggers the job scraping workflow through `JobScraperAgent`.
- **agents/job_scraper_agent.py** – Encapsulates the ADK agent with tool registrations (fetch, extract, write) and a local fallback execution path.
- **tools/** – Modular tool implementations used by the agent:
  - `fetch_webpage_tool` uses ADK WebFetch when available, otherwise `requests`.
  - `extract_job_fields_tool` leverages BeautifulSoup heuristics to capture title & company.
  - `write_to_csv_tool` appends timestamped rows to `data/jobs.csv` via pandas.
- **data/jobs.csv** – Append-only storage for captured job leads (auto-created on demand).
- **tests/** – Pytest-based smoke tests verifying parsing behavior and CSV creation.

## Tech Stack

- Python 3.11
- Google ADK (`google-generativeai` / `adk` packages)
- Requests, BeautifulSoup4, Pandas
- Tooling: uv, Ruff, Mypy, Pytest, Pre-commit

## Getting Started

1. **Install uv** (once): `pip install uv` or use Astral’s curl installer.
2. **Sync dependencies** from the repository root so uv can locate this package:
   ```sh
   cd /workspaces/jobflow-agent            # repo root
   uv sync --project jobflow_mvp
   ```
3. **Set ADK credentials** (Gemini key):
   ```sh
   export GOOGLE_API_KEY="<your key>"
   ```
4. **Run the agent (preferred)**:
   ```sh
   uv run --project jobflow_mvp python -m jobflow_mvp.main "https://example.com/job-posting"
   ```
   Using `--project jobflow_mvp` ensures the interpreter loads this package even if you run from the repo root. The CLI prints a success message and appends the job entry to `data/jobs.csv` (created if missing). Override the CSV location during development/testing with `JOBFLOW_DATA_PATH=/tmp/jobs.csv`.

> Legacy shortcut: `cd jobflow_mvp && uv run python main.py ...` also works but requires adjusting `PYTHONPATH`; the module-based invocation above is the more portable, “industry standard” approach.

## Development Workflow

- `uv run ruff check .` – static analysis
- `uv run ruff format .` – auto-format
- `uv run mypy .` – strict typing
- `uv run pytest` – run the tests
- `uv run pre-commit run --all-files` – checks identical to CI

A GitHub Actions workflow (`.github/workflows/ci.yml`) mirrors the above steps for every push and pull request.

## How to Extend

- **Additional fields**: add new parsing heuristics inside `extract_job_fields_tool` and persist columns by updating `write_to_csv_tool`.
- **Multi-agent orchestration**: compose new ADK agents and register them within `agents/`, then orchestrate them via a controller script or workflow engine.
- **Data sinks**: swap the CSV tool with a database writer (e.g., BigQuery, Postgres) by implementing a new tool module and plugging it into the agent.
- **Web automation**: create tools for authentication, pagination, or ATS integrations.

## Next Steps

1. **Fit Score Agent** – evaluate applicants vs. job requirements and rank opportunities.
2. **Tracker Agent** – monitor application statuses, recruiter responses, and reminders.
3. **Multi-agent Orchestration** – coordinate scraping, enrichment, and follow-ups via a task router (e.g., event-driven or DAG-based controller).

By starting with this MVP scaffold you can immediately ingest job postings with consistent tooling, then evolve toward a fully automated enterprise job tracking platform.
