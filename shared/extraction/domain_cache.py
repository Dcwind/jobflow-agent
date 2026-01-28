"""Domain-based company name cache for scalable extraction."""

from __future__ import annotations

import re
from urllib.parse import urlparse

# In-memory cache (replace with Redis/DB for production multi-user)
_domain_company_cache: dict[str, str] = {}


def get_domain(url: str) -> str | None:
    """Extract domain from URL (without www)."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain if domain else None
    except Exception:
        return None


def get_cached_company(domain: str) -> str | None:
    """Get company name from cache."""
    return _domain_company_cache.get(domain)


def cache_company(domain: str, company: str) -> None:
    """Cache company name for domain."""
    if domain and company and company != "Unknown":
        _domain_company_cache[domain] = company


def company_from_domain(domain: str) -> str:
    """Derive company name from domain (e.g., predli.com -> Predli)."""
    if not domain:
        return "Unknown"
    # Get first part before TLD
    parts = domain.split(".")
    if parts:
        name = parts[0]
        # Handle common patterns like jobs.company.com or careers.company.com
        if name in ("jobs", "careers", "hiring", "recruit", "work") and len(parts) > 2:
            name = parts[1]
        # Remove job-related suffixes
        name = re.sub(r"(jobs|careers|hiring|recruit)", "", name, flags=re.I)
        name = name.strip("-_")
        if name:
            return name.title()
    return "Unknown"


__all__ = ["get_domain", "get_cached_company", "cache_company", "company_from_domain"]
