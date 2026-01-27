"""PII filtering utilities for job data."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.extraction.bs4_extractor import ExtractionResult

# Patterns to detect and redact PII
PII_PATTERNS = [
    # Email addresses
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
    # Phone numbers - various formats
    (r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]"),
    # UK phone numbers
    (r"\b(?:\+44|0)\s?\d{2,4}\s?\d{3,4}\s?\d{3,4}\b", "[PHONE]"),
    # International phone with country code
    (r"\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b", "[PHONE]"),
    # LinkedIn profile URLs
    (r"linkedin\.com/in/[A-Za-z0-9_-]+/?", "[LINKEDIN]"),
    # Slack/Discord handles
    (r"@[A-Za-z0-9_]{3,}", "[HANDLE]"),
]

# Patterns for contact section lines to remove entirely (data minimization)
# These should be specific to recruiter/hiring contact sections, not general text
CONTACT_LINE_PATTERNS = [
    # "For questions, feel free to [Name]" or "For questions, contact [Name]" pattern
    r"^(?:for\s+)?questions?,?\s+(?:please\s+)?(?:feel\s+free\s+to|contact|reach\s+out\s+to|email)\s+[A-Z][a-z]+.*$",
    # "Contact: [Name]" or "Recruiter: [Name]" header pattern
    r"^\s*(?:contact|recruiter|hiring\s+manager|point\s+of\s+contact)\s*:\s*[A-Z].*$",
    # "Apply to [Name] at..." pattern
    r"^(?:please\s+)?(?:apply|send\s+(?:your\s+)?(?:resume|cv|application))\s+to\s+[A-Z][a-z]+.*$",
]


def _remove_contact_lines(text: str) -> str:
    """Remove entire lines that appear to be contact information sections."""
    lines = text.splitlines()
    filtered_lines = []
    for line in lines:
        is_contact_line = any(
            re.match(pattern, line, flags=re.IGNORECASE)
            for pattern in CONTACT_LINE_PATTERNS
        )
        if not is_contact_line:
            filtered_lines.append(line)
    return "\n".join(filtered_lines)


def filter_pii(text: str | None) -> str | None:
    """Remove PII from text.

    Args:
        text: Text to filter

    Returns:
        Filtered text with PII redacted
    """
    if not text:
        return text

    filtered = text

    # Remove entire contact section lines first
    filtered = _remove_contact_lines(filtered)

    # Then redact any remaining PII patterns
    for pattern, replacement in PII_PATTERNS:
        filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)

    return filtered


def filter_pii_from_result(result: ExtractionResult) -> ExtractionResult:
    """Apply PII filtering to extraction result.

    Args:
        result: Extraction result to filter

    Returns:
        New ExtractionResult with PII filtered
    """
    from shared.extraction.bs4_extractor import ExtractionResult

    return ExtractionResult(
        title=result.title,  # Don't filter title
        company=result.company,  # Don't filter company
        location=result.location,  # Don't filter location
        salary=result.salary,  # Don't filter salary
        description=filter_pii(result.description),  # Filter description
        source=result.source,
    )


__all__ = ["filter_pii", "filter_pii_from_result"]
