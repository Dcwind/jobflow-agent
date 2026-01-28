"""LLM-based quality validation for extracted job data."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

from shared.extraction.bs4_extractor import ExtractionResult

LOGGER = logging.getLogger(__name__)

VALIDATION_PROMPT = """You are a data quality validator. Check if the extracted job posting data makes sense.

Extracted Data:
- Title: {title}
- Company: {company}
- Location: {location}
- Salary: {salary}

Original Page Title: {page_title}

Evaluate the quality and return a JSON object with:
- is_valid: boolean - true if the data looks reasonable for a job posting
- confidence: float (0.0 to 1.0) - how confident you are in the extraction
- issues: list of strings - any problems found (empty if none)
- suggestions: object with corrected values if you can infer better ones (optional fields only)

Quality checks to perform:
1. Title should be a job title, not a company name or generic text
2. Company should be a company/organization name
3. Location should be a place or "Remote"
4. Salary should be in a reasonable format with currency

Return ONLY valid JSON, no other text.

JSON Response:"""


@dataclass
class QualityResult:
    """Result of quality validation."""

    is_valid: bool
    confidence: float
    issues: list[str]
    suggestions: dict[str, str]


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


def validate_extraction(
    result: ExtractionResult,
    page_title: str | None = None,
    model_name: str = "gemini-1.5-flash",
) -> QualityResult:
    """Validate extracted job data using LLM.

    Args:
        result: The extraction result to validate
        page_title: Original page title for reference
        model_name: Gemini model to use

    Returns:
        QualityResult with validation outcome
    """
    try:
        client = _get_genai_client()

        prompt = VALIDATION_PROMPT.format(
            title=result.title,
            company=result.company,
            location=result.location or "Not found",
            salary=result.salary or "Not found",
            page_title=page_title or "Not available",
        )

        response = client.models.generate_content(model=model_name, contents=prompt)
        response_text = response.text.strip()

        # Handle markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```json") or line.startswith("```"):
                    in_json = not in_json if line == "```" else True
                    continue
                if in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        data = json.loads(response_text)
        LOGGER.info(
            "Quality validation complete: valid=%s, confidence=%.2f",
            data.get("is_valid"),
            data.get("confidence", 0),
        )

        return QualityResult(
            is_valid=data.get("is_valid", False),
            confidence=float(data.get("confidence", 0.0)),
            issues=data.get("issues", []),
            suggestions=data.get("suggestions", {}),
        )

    except Exception as e:
        LOGGER.warning("Quality validation failed, assuming valid: %s", e)
        # Fail open - if validation fails, don't block the extraction
        return QualityResult(
            is_valid=True,
            confidence=0.5,
            issues=[f"Validation error: {e}"],
            suggestions={},
        )


def apply_suggestions(result: ExtractionResult, quality: QualityResult) -> ExtractionResult:
    """Apply quality suggestions to extraction result.

    Args:
        result: Original extraction result
        quality: Quality validation result with suggestions

    Returns:
        Updated extraction result
    """
    if not quality.suggestions:
        return result

    return ExtractionResult(
        title=quality.suggestions.get("title", result.title),
        company=quality.suggestions.get("company", result.company),
        location=quality.suggestions.get("location", result.location),
        salary=quality.suggestions.get("salary", result.salary),
        description=result.description,  # Don't modify description
        source=f"{result.source}+validated",
    )


__all__ = ["validate_extraction", "apply_suggestions", "QualityResult"]
