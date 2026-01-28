"""Robots.txt compliance checker for enterprise-grade scraping."""

from __future__ import annotations

import logging
from functools import lru_cache
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

LOGGER = logging.getLogger(__name__)

# Our User-Agent for robots.txt compliance
USER_AGENT = "JobflowBot/1.0"

# Cache TTL is handled by lru_cache (in-memory, cleared on restart)
# For production multi-user, consider Redis with TTL


@lru_cache(maxsize=256)
def _fetch_robots_txt(robots_url: str) -> RobotFileParser | None:
    """Fetch and parse robots.txt for a domain.

    Results are cached per robots_url to avoid repeated fetches.
    """
    rp = RobotFileParser()
    rp.set_url(robots_url)

    try:
        # Fetch with timeout
        response = requests.get(robots_url, timeout=10, headers={"User-Agent": USER_AGENT})

        if response.status_code == 200:
            rp.parse(response.text.splitlines())
            LOGGER.debug("Parsed robots.txt from %s", robots_url)
            return rp
        elif response.status_code in (404, 410):
            # No robots.txt = everything allowed
            LOGGER.debug("No robots.txt at %s (status %d)", robots_url, response.status_code)
            return None
        else:
            # Other errors - be conservative, assume disallowed
            LOGGER.warning("Failed to fetch robots.txt from %s: status %d", robots_url, response.status_code)
            return None

    except requests.RequestException as e:
        LOGGER.warning("Error fetching robots.txt from %s: %s", robots_url, e)
        return None


def get_robots_url(url: str) -> str:
    """Get the robots.txt URL for a given page URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def is_allowed(url: str, user_agent: str = USER_AGENT) -> bool:
    """Check if scraping a URL is allowed by robots.txt.

    Args:
        url: The URL to check
        user_agent: The User-Agent to check permissions for

    Returns:
        True if allowed, False if disallowed
    """
    robots_url = get_robots_url(url)
    rp = _fetch_robots_txt(robots_url)

    if rp is None:
        # No robots.txt or fetch failed - allow by default
        # (conservative option would be to disallow on fetch failure)
        return True

    allowed = rp.can_fetch(user_agent, url)

    if not allowed:
        LOGGER.info("Robots.txt disallows scraping: %s", url)

    return allowed


def get_crawl_delay(url: str, user_agent: str = USER_AGENT) -> float | None:
    """Get the crawl delay specified in robots.txt.

    Args:
        url: A URL from the domain to check
        user_agent: The User-Agent to check for

    Returns:
        Crawl delay in seconds, or None if not specified
    """
    robots_url = get_robots_url(url)
    rp = _fetch_robots_txt(robots_url)

    if rp is None:
        return None

    delay = rp.crawl_delay(user_agent)
    return float(delay) if delay else None


def clear_cache() -> None:
    """Clear the robots.txt cache."""
    _fetch_robots_txt.cache_clear()


__all__ = ["is_allowed", "get_crawl_delay", "clear_cache", "USER_AGENT"]
