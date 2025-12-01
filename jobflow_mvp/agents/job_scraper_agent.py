"""Job scraper agent that coordinates HTML fetching and parsing."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from jobflow_mvp.tools.extract_job_fields import extract_job_fields_tool
from jobflow_mvp.tools.fetch_webpage import fetch_webpage_tool
from jobflow_mvp.tools.write_to_csv import write_to_csv_tool

LOGGER = logging.getLogger(__name__)
_AGENT_INSTRUCTIONS = (
    "You are an enterprise job scraping assistant."
    " Given a job posting URL, fetch the page, read the title and company,"
    " and respond with a JSON object matching {title: str, company: str}."
)


def _build_adk_agent() -> Optional[Any]:
    """Instantiate an ADK agent if the SDK is available."""

    try:
        from google.ai.generativelanguage import agents as gl_agents  # type: ignore
    except Exception:
        try:
            from google.generativeai import agent as gl_agents  # type: ignore
        except Exception:
            return None

    AgentClass = getattr(gl_agents, "Agent", None)
    if AgentClass is None:
        return None

    tools = {
        "fetch_webpage_tool": fetch_webpage_tool,
        "extract_job_fields_tool": extract_job_fields_tool,
    }

    try:
        return AgentClass(
            model="gemini-1.5-flash",
            instructions=_AGENT_INSTRUCTIONS,
            tools=tools,
        )
    except Exception as err:  # pragma: no cover - depends on ADK availability
        LOGGER.warning("Falling back to local agent due to ADK init error: %s", err)
        return None


class JobScraperAgent:
    """High-level agent orchestrating the MVP workflow."""

    def __init__(self) -> None:
        self._adk_agent = _build_adk_agent()

    def run(self, job_url: str) -> Dict[str, str]:
        """Execute the scrape workflow using ADK when available."""

        if not job_url:
            raise ValueError("job_url must be provided")

        if self._adk_agent is not None:
            try:
                response = self._adk_agent.run(job_url=job_url)
                parsed = self._parse_agent_response(response)
                if parsed:
                    self._record_result(parsed, job_url)
                    return parsed
            except Exception as err:  # pragma: no cover - ADK specific
                LOGGER.warning("ADK execution failed, using local fallback: %s", err)

        html = fetch_webpage_tool(job_url)
        fields = extract_job_fields_tool(html)
        self._record_result(fields, job_url)
        return fields

    @staticmethod
    def _record_result(data: Dict[str, str], job_url: str) -> None:
        payload = {
            "title": data.get("title", "Unknown"),
            "company": data.get("company", "Unknown"),
            "url": job_url,
        }
        write_to_csv_tool(payload)

    @staticmethod
    def _parse_agent_response(response: Any) -> Optional[Dict[str, str]]:
        if isinstance(response, dict):
            title = response.get("title")
            company = response.get("company")
            if title and company:
                return {"title": str(title), "company": str(company)}

        content = getattr(response, "output", None)
        if isinstance(content, dict):
            title = content.get("title")
            company = content.get("company")
            if title and company:
                return {"title": str(title), "company": str(company)}

        return None


__all__ = ["JobScraperAgent"]
