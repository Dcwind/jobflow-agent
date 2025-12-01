"""HTML parsing helpers for deriving structured job fields."""

from __future__ import annotations

from typing import Dict

from bs4 import BeautifulSoup

DEFAULT_TITLE = "Unknown Title"
DEFAULT_COMPANY = "Unknown"


META_COMPANY_KEYS = (
    ("meta", {"property": "og:site_name"}),
    ("meta", {"name": "company"}),
    ("meta", {"name": "og:site_name"}),
    ("meta", {"name": "twitter:site"}),
)


def _extract_company(soup: BeautifulSoup) -> str:
    for tag_name, attrs in META_COMPANY_KEYS:
        node = soup.find(tag_name, attrs=attrs)
        if node and node.get("content"):
            return node["content"].strip()

    company_tag = soup.find(attrs={"data-company": True})
    if company_tag:
        return str(company_tag.get("data-company")).strip()

    return DEFAULT_COMPANY


def extract_job_fields_tool(html: str) -> Dict[str, str]:
    """Return structured job metadata from HTML."""

    soup = BeautifulSoup(html or "", "html.parser")
    title = (
        soup.title.string.strip() if soup.title and soup.title.string else DEFAULT_TITLE
    )
    company = _extract_company(soup)

    return {"title": title or DEFAULT_TITLE, "company": company or DEFAULT_COMPANY}


__all__ = ["extract_job_fields_tool"]
