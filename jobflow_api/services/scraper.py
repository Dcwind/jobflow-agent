"""Job scraping service."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from shared.db.models import Job
from shared.extraction import extract_job
from shared.extraction.pii_filter import filter_pii
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from pydantic import HttpUrl

LOGGER = logging.getLogger(__name__)


def scrape_and_store_job(
    db: Session,
    url: str,
    use_playwright: bool = True,
    use_llm_fallback: bool = True,
    use_llm_validation: bool = False,
    check_robots: bool = True,
) -> tuple[Job | None, str | None]:
    """Scrape a job URL and store in database.

    Args:
        db: Database session
        url: Job posting URL
        use_playwright: Enable Playwright fallback
        use_llm_fallback: Enable LLM extraction fallback
        use_llm_validation: Enable LLM validation
        check_robots: Check robots.txt before scraping

    Returns:
        Tuple of (Job instance or None, error message or None)
    """
    url_str = str(url)
    LOGGER.info("Processing job URL: %s", url_str)

    # Check if URL already exists
    existing = db.query(Job).filter(Job.url == url_str).first()
    if existing:
        LOGGER.info("Job already exists: %s", url_str)
        return existing, None

    # Extract job data
    try:
        result, metrics = extract_job(
            url_str,
            use_playwright=use_playwright,
            use_llm_fallback=use_llm_fallback,
            use_llm_validation=use_llm_validation,
            check_robots=check_robots,
        )
    except Exception as e:
        LOGGER.error("Extraction failed for %s: %s", url_str, e)
        return None, f"Extraction failed: {e}"

    if not result:
        LOGGER.warning("No extraction result for %s", url_str)
        return None, "Failed to extract job data from URL"

    # Create job record
    job = Job(
        url=url_str,
        title=result.title,
        company=result.company,
        location=result.location,
        salary=result.salary,
        description=result.description,
        extraction_method=result.source,
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
        LOGGER.info("Job stored: id=%d, title=%s", job.id, job.title)
        return job, None
    except IntegrityError:
        db.rollback()
        # Race condition - job was added by another request
        existing = db.query(Job).filter(Job.url == url_str).first()
        if existing:
            return existing, None
        return None, "Failed to store job (database error)"
    except Exception as e:
        db.rollback()
        LOGGER.error("Failed to store job: %s", e)
        return None, f"Database error: {e}"


def scrape_multiple_jobs(
    db: Session,
    urls: list[HttpUrl],
    use_playwright: bool = True,
    use_llm_fallback: bool = True,
    use_llm_validation: bool = False,
    check_robots: bool = True,
) -> list[tuple[str, Job | None, str | None]]:
    """Scrape multiple job URLs.

    Args:
        db: Database session
        urls: List of job URLs
        use_playwright: Enable Playwright fallback
        use_llm_fallback: Enable LLM extraction fallback
        use_llm_validation: Enable LLM validation
        check_robots: Check robots.txt before scraping

    Returns:
        List of (url, job or None, error or None) tuples
    """
    results = []
    for url in urls:
        url_str = str(url)
        job, error = scrape_and_store_job(
            db,
            url_str,
            use_playwright=use_playwright,
            use_llm_fallback=use_llm_fallback,
            use_llm_validation=use_llm_validation,
            check_robots=check_robots,
        )
        results.append((url_str, job, error))
    return results


def parse_job_from_text(text: str) -> dict[str, str | None]:
    """Extract job fields from description text using LLM.

    Args:
        text: Job description text

    Returns:
        Dict with extracted title, company, location, salary (any can be None)
    """
    import json
    import os

    LOGGER.info("Parsing job fields from text (%d chars)", len(text))

    # Try LLM extraction
    try:
        from google import genai

        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            LOGGER.warning("No API key for LLM parsing")
            return {"title": None, "company": None, "location": None, "salary": None}

        client = genai.Client(api_key=api_key)

        prompt = f"""Extract job posting fields from this text. Return ONLY a JSON object with these keys:
- title: The job title (string or null)
- company: The company name (string or null)
- location: The job location (string or null)
- salary: The salary/compensation if mentioned (string or null)

Text:
{text[:8000]}

JSON:"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

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
        LOGGER.info("Parsed fields: %s", data)
        return {
            "title": data.get("title"),
            "company": data.get("company"),
            "location": data.get("location"),
            "salary": data.get("salary"),
        }

    except Exception as e:
        LOGGER.warning("LLM parsing failed: %s", e)
        return {"title": None, "company": None, "location": None, "salary": None}


def create_manual_job(
    db: Session,
    title: str,
    company: str,
    location: str | None = None,
    salary: str | None = None,
    description: str | None = None,
    url: str | None = None,
) -> tuple[Job | None, str | None]:
    """Create a job from manual entry (no scraping).

    Args:
        db: Database session
        title: Job title
        company: Company name
        location: Job location (optional)
        salary: Salary info (optional)
        description: Job description (optional, PII will be filtered)
        url: Source URL (optional, placeholder generated if omitted)

    Returns:
        Tuple of (Job instance or None, error message or None)
    """
    # Generate placeholder URL if none provided
    if not url:
        url = f"manual://{uuid.uuid4().hex[:12]}"

    LOGGER.info("Creating manual job: %s at %s", title, company)

    # Check for duplicate URL
    existing = db.query(Job).filter(Job.url == url).first()
    if existing:
        LOGGER.info("Job with URL already exists: %s", url)
        return None, "Job with this URL already exists"

    # Apply PII filter to description
    if description:
        description = filter_pii(description)

    job = Job(
        url=url,
        title=title,
        company=company,
        location=location,
        salary=salary,
        description=description,
        extraction_method="manual",
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
        LOGGER.info("Manual job stored: id=%d, title=%s", job.id, job.title)
        return job, None
    except IntegrityError:
        db.rollback()
        return None, "Job with this URL already exists"
    except Exception as e:
        db.rollback()
        LOGGER.error("Failed to store manual job: %s", e)
        return None, f"Database error: {e}"
