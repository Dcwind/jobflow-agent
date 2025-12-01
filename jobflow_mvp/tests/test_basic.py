"""Basic smoke tests for the MVP."""

from __future__ import annotations

from jobflow_mvp import main
from jobflow_mvp.tools import extract_job_fields as extract_module
from jobflow_mvp.tools.write_to_csv import DATA_PATH_ENV


def test_main_creates_csv(monkeypatch, tmp_path) -> None:
    sample_html = """
    <html>
        <head>
            <title>Principal Engineer</title>
            <meta name="company" content="ACME" />
        </head>
        <body>Test</body>
    </html>
    """

    jobs_csv = tmp_path / "jobs.csv"
    monkeypatch.setenv(DATA_PATH_ENV, str(jobs_csv))
    monkeypatch.setattr(
        "jobflow_mvp.agents.job_scraper_agent.fetch_webpage_tool",
        lambda url: sample_html,
        raising=False,
    )
    monkeypatch.setattr(
        "jobflow_mvp.agents.job_scraper_agent.extract_job_fields_tool",
        lambda html: {"title": "Principal Engineer", "company": "ACME"},
        raising=False,
    )

    exit_code = main.main(["https://example.com/job"])  # type: ignore[arg-type]
    assert exit_code == 0
    assert jobs_csv.exists()
    assert jobs_csv.read_text().count("ACME") >= 1


def test_extract_job_fields_returns_expected_keys() -> None:
    html = """
    <html>
        <head>
            <title>Staff SWE</title>
            <meta property="og:site_name" content="ExampleCorp" />
        </head>
    </html>
    """

    result = extract_module.extract_job_fields_tool(html)
    assert set(result.keys()) == {"title", "company"}
    assert result["title"] == "Staff SWE"
    assert result["company"] == "ExampleCorp"
