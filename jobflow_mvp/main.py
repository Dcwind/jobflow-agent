"""Entry point for the Jobflow MVP."""

from __future__ import annotations

import argparse
import sys

from jobflow_mvp.agents.job_scraper_agent import JobScraperAgent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Jobflow Agent MVP")
    parser.add_argument("url", help="Job posting URL to ingest")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Execute the agent workflow."""

    args = parse_args(argv)
    agent = JobScraperAgent()
    result = agent.run(args.url)

    title = result.get("title", "Unknown")
    company = result.get("company", "Unknown")
    message = f"Saved job '{title}' at '{company}' to the tracker."
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
