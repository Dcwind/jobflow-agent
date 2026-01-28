"""Job scraping service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from shared.db.models import Job
from shared.extraction import extract_job
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
