"""Location extraction using geotext library."""

from __future__ import annotations

import re

from geotext import GeoText


def extract_location_from_text(text: str) -> str | None:
    """Extract location from text using geotext.

    Prioritizes: cities > countries
    """
    if not text:
        return None

    places = GeoText(text)

    # Prefer cities (more specific)
    if places.cities:
        return places.cities[0]

    # Fall back to countries
    if places.countries:
        return places.countries[0]

    return None


def extract_location_from_title(title: str) -> str | None:
    """Extract location from title, checking parentheses first.

    Many job titles include location in parentheses:
    - "AI Engineer Associate (Stockholm / Hybrid)"
    - "Software Developer (Remote - USA)"
    """
    if not title:
        return None

    # Check parentheses first: (Stockholm / Hybrid)
    paren_match = re.search(r"\(([^)]+)\)", title)
    if paren_match:
        paren_content = paren_match.group(1)
        loc = extract_location_from_text(paren_content)
        if loc:
            return loc

    # Check full title
    return extract_location_from_text(title)


__all__ = ["extract_location_from_text", "extract_location_from_title"]
