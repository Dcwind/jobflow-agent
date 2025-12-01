"""CSV persistence utilities for job scrape results."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import pandas as pd

DATA_PATH_ENV = "JOBFLOW_JOBS_CSV"
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_DEFAULT_PATH = _DATA_DIR / "jobs.csv"


def _resolve_csv_path() -> Path:
    override = os.environ.get(DATA_PATH_ENV)
    return Path(override).expanduser() if override else _DEFAULT_PATH


def write_to_csv_tool(data: Dict[str, str]) -> Path:
    """Append a structured job entry to the jobs.csv file."""

    csv_path = _resolve_csv_path()
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "title": data.get("title", "Unknown Title"),
        "company": data.get("company", "Unknown"),
    }

    df = pd.DataFrame([payload])
    header = not csv_path.exists()
    df.to_csv(csv_path, mode="a", header=header, index=False)
    return csv_path


__all__ = ["write_to_csv_tool", "DATA_PATH_ENV"]
