"""Playwright-based fetcher for JavaScript-rendered pages."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Browser

LOGGER = logging.getLogger(__name__)

# Global browser instance for reuse
_browser: Browser | None = None
_playwright = None


async def _get_browser() -> Browser:
    """Get or create a shared browser instance."""
    global _browser, _playwright
    if _browser is None:
        from playwright.async_api import async_playwright

        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
        )
    return _browser


async def fetch_with_playwright_async(url: str, timeout_ms: int = 30000) -> str:
    """Fetch page HTML after JavaScript rendering.

    Args:
        url: Page URL to fetch
        timeout_ms: Maximum wait time in milliseconds

    Returns:
        Rendered HTML content

    Raises:
        RuntimeError: If page fails to load
    """
    browser = await _get_browser()
    page = await browser.new_page()

    try:
        LOGGER.info("Fetching with Playwright: %s", url)
        await page.goto(url, wait_until="networkidle", timeout=timeout_ms)

        # Wait a bit for any lazy-loaded content
        await page.wait_for_timeout(1000)

        html = await page.content()
        LOGGER.info("Playwright fetch successful, HTML length: %d", len(html))
        return html

    except Exception as e:
        LOGGER.warning("Playwright fetch failed for %s: %s", url, e)
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    finally:
        await page.close()


def fetch_with_playwright(url: str, timeout_ms: int = 30000) -> str:
    """Synchronous wrapper for Playwright fetch.

    Args:
        url: Page URL to fetch
        timeout_ms: Maximum wait time in milliseconds

    Returns:
        Rendered HTML content
    """
    return asyncio.run(fetch_with_playwright_async(url, timeout_ms))


async def close_browser() -> None:
    """Close the shared browser instance."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None


__all__ = ["fetch_with_playwright", "fetch_with_playwright_async", "close_browser"]
