"""BeautifulSoup-based job field extraction with JSON-LD support."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from typing import Any

import trafilatura
from bs4 import BeautifulSoup

DEFAULT_TITLE = "Unknown Title"
DEFAULT_COMPANY = "Unknown"


@dataclass
class ExtractionResult:
    """Result of job field extraction."""

    title: str
    company: str
    location: str | None
    salary: str | None
    description: str | None
    source: str = "bs4"

    def is_complete(self) -> bool:
        """Check if essential fields are present."""
        return (
            self.title != DEFAULT_TITLE
            and self.company != DEFAULT_COMPANY
            and self.title.strip() != ""
            and self.company.strip() != ""
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "salary": self.salary,
            "description": self.description,
            "extraction_method": self.source,
        }


def _parse_json_ld(soup: BeautifulSoup) -> dict[str, Any] | None:
    """Extract JobPosting schema from JSON-LD if present."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            # Handle single object or array
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        return item
            elif isinstance(data, dict):
                if data.get("@type") == "JobPosting":
                    return data
                # Check @graph array
                graph = data.get("@graph", [])
                for item in graph:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        return item
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def _extract_title(soup: BeautifulSoup, json_ld: dict | None) -> str:
    """Extract job title."""
    # Try JSON-LD first
    if json_ld and json_ld.get("title"):
        return str(json_ld["title"]).strip()

    # Try og:title meta
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    # Fall back to page title
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return DEFAULT_TITLE


def _extract_company(soup: BeautifulSoup, json_ld: dict | None) -> str:
    """Extract company name."""
    # Try JSON-LD hiringOrganization
    if json_ld:
        hiring_org = json_ld.get("hiringOrganization")
        if isinstance(hiring_org, dict) and hiring_org.get("name"):
            return str(hiring_org["name"]).strip()
        if isinstance(hiring_org, str):
            return hiring_org.strip()

    # Try common meta tags
    meta_keys = [
        ("meta", {"property": "og:site_name"}),
        ("meta", {"name": "company"}),
        ("meta", {"name": "author"}),
        ("meta", {"name": "twitter:site"}),
    ]
    for tag_name, attrs in meta_keys:
        node = soup.find(tag_name, attrs=attrs)
        if node and node.get("content"):
            content = node["content"].strip()
            if content and content != "@":  # Skip Twitter handles
                return content

    # Try data-company attribute
    company_tag = soup.find(attrs={"data-company": True})
    if company_tag:
        return str(company_tag.get("data-company")).strip()

    return DEFAULT_COMPANY


def _location_from_place(place: dict) -> str | None:
    """Extract location string from a Place object."""
    address = place.get("address", {})
    if isinstance(address, dict):
        parts = [
            address.get("addressLocality"),
            address.get("addressRegion"),
            address.get("addressCountry"),
        ]
        location = ", ".join(p for p in parts if p)
        if location:
            return location
    return None


def _extract_location(soup: BeautifulSoup, json_ld: dict | None) -> str | None:
    """Extract job location."""
    # Try JSON-LD jobLocation
    if json_ld:
        job_location = json_ld.get("jobLocation")
        if isinstance(job_location, list):
            # Handle array of Place objects
            locations = []
            for place in job_location:
                if isinstance(place, dict):
                    loc = _location_from_place(place)
                    if loc:
                        locations.append(loc)
            if locations:
                return "; ".join(locations)
        elif isinstance(job_location, dict):
            loc = _location_from_place(job_location)
            if loc:
                return loc
        elif isinstance(job_location, str):
            return job_location.strip()

    # Try common class patterns
    location_patterns = ["location", "job-location", "jobLocation", "job_location"]
    for pattern in location_patterns:
        node = soup.find(attrs={"class": re.compile(pattern, re.I)})
        if node:
            text = node.get_text(strip=True)
            if text and len(text) < 200:  # Reasonable length
                return text

    # Try meta tags
    for attr in [{"name": "location"}, {"property": "place:location"}]:
        node = soup.find("meta", attrs=attr)
        if node and node.get("content"):
            return node["content"].strip()

    return None


def _extract_salary(soup: BeautifulSoup, json_ld: dict | None) -> str | None:
    """Extract salary information."""
    # Try JSON-LD baseSalary
    if json_ld:
        base_salary = json_ld.get("baseSalary")
        if isinstance(base_salary, dict):
            value = base_salary.get("value", {})
            currency = base_salary.get("currency", "")
            if isinstance(value, dict):
                min_val = value.get("minValue")
                max_val = value.get("maxValue")
                unit = value.get("unitText", "YEAR")
                if min_val and max_val:
                    return f"{currency} {min_val:,} - {max_val:,} / {unit}".strip()
                elif min_val:
                    return f"{currency} {min_val:,} / {unit}".strip()
            elif isinstance(value, (int, float)):
                return f"{currency} {value:,}".strip()

    # Try regex in page text
    salary_patterns = [
        r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*(?:per|/|a)\s*(?:year|yr|annum|hour|hr))?",
        r"£[\d,]+(?:\s*[-–]\s*£[\d,]+)?(?:\s*(?:per|/|a)\s*(?:year|annum))?",
        r"€[\d,]+(?:\s*[-–]\s*€[\d,]+)?(?:\s*(?:per|/|a)\s*(?:year|annum))?",
    ]
    text = soup.get_text()
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(0).strip()

    # Try salary-related class names
    salary_class_patterns = ["salary", "compensation", "pay"]
    for pattern in salary_class_patterns:
        node = soup.find(attrs={"class": re.compile(pattern, re.I)})
        if node:
            text = node.get_text(strip=True)
            if text and len(text) < 100 and re.search(r"[\d$£€]", text):
                return text

    return None


def _clean_description(text: str) -> str:
    """Unescape HTML entities, strip tags, and clean up whitespace."""
    # Unescape HTML entities (handles &lt;p&gt; etc.)
    text = html.unescape(text)
    # Strip HTML tags if present
    if "<" in text:
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
    # Clean up excessive whitespace while preserving paragraphs
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    return text[:10000] if text else ""


def _extract_description(
    soup: BeautifulSoup, json_ld: dict | None, raw_html: str | None = None
) -> str | None:
    """Extract job description using multiple strategies.

    Pipeline:
    1. JSON-LD structured data (most reliable)
    2. CSS selectors for common job description containers
    3. Trafilatura content extraction (works on any page structure)
    """
    # Strategy 1: Try JSON-LD description
    if json_ld and json_ld.get("description"):
        desc = _clean_description(str(json_ld["description"]))
        if desc:
            return desc

    # Strategy 2: Try common description containers (in order of specificity)
    selectors = [
        "[class*='job-description']",
        "[class*='jobDescription']",
        "[class*='description']",
        "[id*='job-description']",
        "[id*='description']",
        "article",
        "[role='main']",
        "main",
    ]
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            text = _clean_description(node.get_text(separator="\n", strip=True))
            if len(text) > 200:  # Meaningful description length
                return text

    # Strategy 3: Use trafilatura for automatic content extraction
    if raw_html:
        extracted = trafilatura.extract(raw_html, include_comments=False, include_tables=False)
        if extracted and len(extracted) > 200:
            return _clean_description(extracted)

    return None


def extract_with_bs4(html: str) -> ExtractionResult:
    """Extract job fields using BeautifulSoup, JSON-LD, and trafilatura."""
    soup = BeautifulSoup(html or "", "html.parser")
    json_ld = _parse_json_ld(soup)

    return ExtractionResult(
        title=_extract_title(soup, json_ld),
        company=_extract_company(soup, json_ld),
        location=_extract_location(soup, json_ld),
        salary=_extract_salary(soup, json_ld),
        description=_extract_description(soup, json_ld, html),
        source="bs4",
    )


__all__ = ["extract_with_bs4", "ExtractionResult"]
