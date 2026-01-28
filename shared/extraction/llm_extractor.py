"""LLM-based job field extraction using Google Gemini."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from shared.extraction.bs4_extractor import DEFAULT_COMPANY, DEFAULT_TITLE, ExtractionResult

LOGGER = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a job posting data extractor. Extract the following fields from the HTML content below.

Return ONLY a valid JSON object with these exact keys:
- title: The job title (string)
- company: The company name (string)
- location: The job location, e.g. "San Francisco, CA" or "Remote" (string or null)
- salary: The salary range if mentioned, e.g. "$100,000 - $150,000/year" (string or null)
- description: A clean text summary of the job description, requirements, and responsibilities (string or null, max 5000 chars)

Rules:
- Extract actual values from the content, do not make up data
- If a field is not found, use null
- For salary, include currency and period if available
- For description, extract the main job duties, requirements, and qualifications
- Remove any HTML tags from the description
- Do not include recruiter names, emails, or phone numbers in any field

HTML Content:
{html}

JSON Response:"""


def _get_genai_client() -> Any:
    """Get the Google Generative AI client."""
    try:
        from google import genai

        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set")

        return genai.Client(api_key=api_key)
    except ImportError as e:
        raise ImportError("google-genai package not installed") from e


def extract_with_llm(html: str, model_name: str = "gemini-1.5-flash") -> ExtractionResult:
    """Extract job fields using LLM.

    Args:
        html: HTML content to extract from
        model_name: Gemini model to use

    Returns:
        ExtractionResult with extracted fields

    Raises:
        RuntimeError: If LLM extraction fails
    """
    # Truncate HTML to avoid token limits (roughly 100k chars for context)
    max_html_len = 80000
    if len(html) > max_html_len:
        LOGGER.warning("Truncating HTML from %d to %d chars", len(html), max_html_len)
        html = html[:max_html_len]

    try:
        client = _get_genai_client()

        prompt = EXTRACTION_PROMPT.format(html=html)
        response = client.models.generate_content(model=model_name, contents=prompt)

        # Extract JSON from response
        response_text = response.text.strip()

        # Handle markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```json"):
                    in_json = True
                    continue
                if line.startswith("```"):
                    in_json = False
                    continue
                if in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        data = json.loads(response_text)
        LOGGER.info("LLM extraction successful")

        return ExtractionResult(
            title=data.get("title") or DEFAULT_TITLE,
            company=data.get("company") or DEFAULT_COMPANY,
            location=data.get("location"),
            salary=data.get("salary"),
            description=data.get("description"),
            source="llm",
        )

    except json.JSONDecodeError as e:
        LOGGER.error("Failed to parse LLM response as JSON: %s", e)
        raise RuntimeError(f"LLM returned invalid JSON: {e}") from e
    except Exception as e:
        LOGGER.error("LLM extraction failed: %s", e)
        raise RuntimeError(f"LLM extraction failed: {e}") from e


__all__ = ["extract_with_llm"]
