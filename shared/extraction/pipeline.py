"""Extraction pipeline with fallback chain."""

from __future__ import annotations

import ipaddress
import logging
import socket
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

import requests

from shared.extraction.bs4_extractor import ExtractionResult, extract_with_bs4
from shared.extraction.pii_filter import filter_pii_from_result
from shared.extraction.robots_checker import is_allowed as robots_allowed

LOGGER = logging.getLogger(__name__)

# Minimum confidence threshold for accepting extraction
MIN_CONFIDENCE = 0.6

# User agent for requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class ExtractionMetrics:
    """Metrics about the extraction process."""

    fetch_method: Literal["requests", "playwright"]
    extraction_method: Literal["bs4", "llm"]
    validation_run: bool
    confidence: float
    fallbacks_used: int


def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, or otherwise unsafe."""
    try:
        addr = ipaddress.ip_address(ip_str)
        return (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        )
    except ValueError:
        return False


def _is_valid_url(url: str) -> bool:
    """Check if URL is valid and safe to fetch (SSRF prevention)."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Block known dangerous hostnames
        if hostname in ("localhost", "metadata.google.internal"):
            return False

        # Resolve hostname and check all resulting IPs
        try:
            addrinfo = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            return False

        for _family, _type, _proto, _canonname, sockaddr in addrinfo:
            ip_str = sockaddr[0]
            if _is_private_ip(ip_str):
                return False

        return True
    except Exception:
        return False


def _fetch_with_requests(url: str, timeout: int = 15) -> str | None:
    """Fetch URL using requests library."""
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        LOGGER.warning("requests fetch failed: %s", e)
        return None


def _fetch_with_playwright(url: str) -> str | None:
    """Fetch URL using Playwright for JS rendering."""
    try:
        from shared.extraction.playwright_fetch import fetch_with_playwright

        return fetch_with_playwright(url)
    except Exception as e:
        LOGGER.warning("Playwright fetch failed: %s", e)
        return None


def _extract_with_llm(html: str, api_key: str | None = None) -> ExtractionResult | None:
    """Extract using LLM as fallback."""
    try:
        from shared.extraction.llm_extractor import extract_with_llm

        return extract_with_llm(html, api_key=api_key)
    except Exception as e:
        from shared.extraction.llm_extractor import RateLimitError

        if isinstance(e, RateLimitError):
            raise  # Let rate limits propagate to the caller
        LOGGER.warning("LLM extraction failed: %s", e)
        return None


def _validate_with_llm(result: ExtractionResult, page_title: str | None) -> tuple[bool, float]:
    """Validate extraction quality using LLM.

    Returns:
        Tuple of (is_valid, confidence)
    """
    try:
        from shared.extraction.quality_check import validate_extraction

        quality = validate_extraction(result, page_title)
        return quality.is_valid, quality.confidence
    except Exception as e:
        LOGGER.warning("LLM validation failed, assuming valid: %s", e)
        return True, 0.5


def extract_job(
    url: str,
    use_playwright: bool = True,
    use_llm_fallback: bool = True,
    use_llm_validation: bool = True,
    apply_pii_filter: bool = True,
    check_robots: bool = True,
    gemini_api_key: str | None = None,
) -> tuple[ExtractionResult | None, ExtractionMetrics]:
    """Extract job fields from URL using fallback chain.

    Pipeline:
    0. Check robots.txt compliance
    1. Fetch with requests → extract with BS4
    2. If poor quality → fetch with Playwright → extract with BS4
    3. If still poor → extract with LLM
    4. Optionally validate with LLM
    5. Apply PII filtering

    Args:
        url: Job posting URL
        use_playwright: Whether to try Playwright for JS-rendered pages
        use_llm_fallback: Whether to use LLM extraction as fallback
        use_llm_validation: Whether to validate extraction with LLM
        apply_pii_filter: Whether to filter PII from description
        check_robots: Whether to check robots.txt before scraping

    Returns:
        Tuple of (extraction result or None, metrics)
    """
    if not _is_valid_url(url):
        LOGGER.error("Invalid or unsafe URL: %s", url)
        return None, ExtractionMetrics(
            fetch_method="requests",
            extraction_method="bs4",
            validation_run=False,
            confidence=0.0,
            fallbacks_used=0,
        )

    # Step 0: Check robots.txt compliance
    if check_robots and not robots_allowed(url):
        LOGGER.warning("Robots.txt disallows scraping: %s", url)
        return None, ExtractionMetrics(
            fetch_method="requests",
            extraction_method="bs4",
            validation_run=False,
            confidence=0.0,
            fallbacks_used=0,
        )

    metrics = ExtractionMetrics(
        fetch_method="requests",
        extraction_method="bs4",
        validation_run=False,
        confidence=0.0,
        fallbacks_used=0,
    )

    # Step 1: Fetch with requests
    LOGGER.info("Fetching with requests: %s", url)
    html = _fetch_with_requests(url)

    # Step 2: Extract with BS4
    result: ExtractionResult | None = None
    if html:
        result = extract_with_bs4(html, url)
        LOGGER.info("BS4 extraction: title=%s, company=%s", result.title, result.company)

        # Check if extraction is complete
        if result.is_complete():
            metrics.confidence = 0.8
        else:
            metrics.confidence = 0.3

    # Step 3: If poor quality, try Playwright
    if use_playwright and (not html or not result or not result.is_complete()):
        LOGGER.info("Trying Playwright fallback")
        metrics.fallbacks_used += 1
        playwright_html = _fetch_with_playwright(url)

        if playwright_html:
            metrics.fetch_method = "playwright"
            html = playwright_html
            result = extract_with_bs4(html, url)
            LOGGER.info("Playwright + BS4: title=%s, company=%s", result.title, result.company)

            if result.is_complete():
                metrics.confidence = 0.75
            else:
                metrics.confidence = 0.4

    # Step 4: If still poor, try LLM extraction
    if use_llm_fallback and html and (not result or not result.is_complete()):
        LOGGER.info("Trying LLM extraction fallback")
        metrics.fallbacks_used += 1
        llm_result = _extract_with_llm(html, api_key=gemini_api_key)

        if llm_result and llm_result.is_complete():
            result = llm_result
            metrics.extraction_method = "llm"
            metrics.confidence = 0.7

    # Step 5: Validate with LLM
    if use_llm_validation and result and result.is_complete():
        LOGGER.info("Running LLM validation")
        metrics.validation_run = True
        is_valid, confidence = _validate_with_llm(result, result.title)
        if is_valid:
            metrics.confidence = max(metrics.confidence, confidence)
        else:
            LOGGER.warning("LLM validation flagged issues")
            metrics.confidence = min(metrics.confidence, 0.4)

    # Step 6: Apply PII filter
    if apply_pii_filter and result:
        result = filter_pii_from_result(result)

    if result:
        result = ExtractionResult(
            title=result.title,
            company=result.company,
            location=result.location,
            salary=result.salary,
            description=result.description,
            source=f"{metrics.fetch_method}+{metrics.extraction_method}",
        )

    return result, metrics


__all__ = ["extract_job", "ExtractionMetrics"]
