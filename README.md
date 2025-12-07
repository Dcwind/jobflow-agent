# Jobflow Agent Workspace

This repository houses the Jobflow Agent MVP alongside future iterations. The current implementation lives under `jobflow_mvp/` and provides a single-agent workflow that ingests a job posting URL, extracts headline details, and persists them to `data/jobs.csv`. The surrounding tooling (uv, pre-commit, Ruff, Mypy, Pytest) is in place for production-quality evolution.

## Repository Layout

- `jobflow_mvp/` – Python package for the MVP agent, tools, tests, and CI config.
- `jobflow_mvp/data/` – Runtime artifact (`jobs.csv`) created on demand.
- `jobflow_mvp/.github/workflows/ci.yml` – GitHub Actions pipeline for linting, typing, tests, and hooks.
- Additional folders (e.g., `jobflow_fit_score/`, `jobflow_tracker/`) can be added later to host new agents while keeping each iteration scoped.

## Running the MVP

```sh
cd /workspaces/jobflow-agent           # repo root
make sync                              # installs deps via uv
export GOOGLE_API_KEY="<your key>"     # ADK credentials
make run URL="https://example.com/job"
```

`make run` wraps `uv run --project jobflow_mvp python -m jobflow_mvp.main ...`, keeping commands short while still using the package-local virtual environment. Each run prints the scraped title/company and appends a timestamped row to `jobflow_mvp/data/jobs.csv`.

## Development Commands

All quality gates mirror CI; run them from the repo root:

```sh
make lint
make fmt
make type
make test
make precommit
```

## Extending Beyond the MVP

- **New agents**: create sibling packages (e.g., `jobflow_fit_score`, `jobflow_tracker`) with their own `pyproject.toml` files and register them in CI.
- **Shared libraries**: add a `libs/` or `shared/` folder for utilities that multiple agents consume.
- **Data sinks**: replace or augment the CSV writer with database connectors or API integrations.
- **Orchestration**: add an orchestrator package to coordinate multi-agent workflows, then wire it into CLI/CI just like the MVP.

This structure keeps the MVP isolated while giving you room to iterate rapidly on new capabilities.
