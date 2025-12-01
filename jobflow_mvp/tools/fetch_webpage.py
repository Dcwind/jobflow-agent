"""Utilities for retrieving raw HTML content from job postings."""

from __future__ import annotations

import logging
from typing import Optional

import requests

LOGGER = logging.getLogger(__name__)


def _fetch_with_adk(url: str) -> Optional[str]:
    """Attempt to fetch the page via the Google ADK WebFetch helper when available."""

    try:
        from google.generativeai import web  # type: ignore
    except Exception:  # pragma: no cover - only used when ADK is installed
        return None

    fetch_fn = getattr(web, "fetch_url", None)
    if fetch_fn is None:
        return None

    try:
        response = fetch_fn(url)
    except Exception as err:  # pragma: no cover - network/ADK specific behavior
        LOGGER.warning("ADK WebFetch failed for %s: %s", url, err)
        return None

    if isinstance(response, str):
        return response

    text_attr = getattr(response, "text", None)
    if text_attr:
        return text_attr

    content = getattr(response, "content", None)
    return content if isinstance(content, str) else None


def fetch_webpage_tool(url: str) -> str:
    """Fetch a web page and return the HTML source.

    Parameters
    ----------
    url:
        The job posting URL to request.

    Returns
    -------
    str
        The HTML body as a string.

    Raises
    ------
    ValueError
        If the URL is blank.
    requests.HTTPError
        When the HTTP request fails.
    """

    if not url:
        raise ValueError("A non-empty URL is required")

    adk_html = _fetch_with_adk(url)
    if adk_html:
        return adk_html

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as err:
        raise RuntimeError(f"Unable to fetch URL {url!r}: {err}") from err

    response.raise_for_status()
    return response.text


__all__ = ["fetch_webpage_tool"]
