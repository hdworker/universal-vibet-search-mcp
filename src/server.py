"""Universal VibeT Search MCP — free multi-engine web search via FastMCP.

Based on the web_search tool from Vibe-Trading (MIT License):
https://github.com/HKUDS/Vibe-Trading

Uses ddgs (DuckDuckGo Search) as a metasearch aggregator to query
multiple free engines (DuckDuckGo, Google, Bing, Brave, Mojeek, Yahoo)
without requiring any API keys.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("Universal VibeT Search")

_MAX_ATTEMPTS = 3
_BACKOFF_BASE_SECONDS = 0.8


def _do_search(query: str, max_results: int) -> dict[str, Any]:
    """Execute the search with retry."""
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return {
                "status": "error",
                "error": "Web search package not installed. Run: pip install ddgs",
            }

    last_error: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            with DDGS() as client:
                raw = list(client.text(query, max_results=max_results))
        except Exception as exc:
            last_error = exc
            if "no results" in str(exc).lower():
                return {
                    "status": "ok",
                    "query": query,
                    "results": [],
                    "note": "No results found for this query.",
                }
            logger.warning("search attempt %d/%d failed: %s", attempt, _MAX_ATTEMPTS, exc)
            if attempt < _MAX_ATTEMPTS:
                time.sleep(_BACKOFF_BASE_SECONDS * attempt)
            continue

        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in raw
        ]
        return {
            "status": "ok",
            "query": query,
            "results": results,
        }

    return {
        "status": "error",
        "error": (
            f"Web search failed after {_MAX_ATTEMPTS} attempts: {last_error}. "
            "Free search engines rate-limit aggressively from cloud/shared IPs — "
            "retry shortly or try a different query."
        ),
    }


@mcp.tool()
def web_search(
    query: str,
    max_results: int = 5,
) -> str:
    """Search the web across free engines (DuckDuckGo, Google, Bing, Brave, Mojeek, Yahoo).

    No API keys required. Returns top results with title, URL, and snippet.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (default 5, max 10).
    """
    max_results = min(max(1, max_results), 10)
    result = _do_search(query, max_results)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def web_search_news(
    query: str,
    max_results: int = 5,
) -> str:
    """Search recent news across free engines.

    No API keys required. Returns news results with title, URL, snippet, and date.

    Args:
        query: News search query string.
        max_results: Maximum number of results to return (default 5, max 10).
    """
    max_results = min(max(1, max_results), 10)

    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return json.dumps({
                "status": "error",
                "error": "Web search package not installed. Run: pip install ddgs",
            }, ensure_ascii=False)
        supports_backend = False

    last_error: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            with DDGS() as client:
                raw = list(client.news(query, max_results=max_results))
        except Exception as exc:
            last_error = exc
            if "no results" in str(exc).lower():
                return json.dumps({
                    "status": "ok",
                    "query": query,
                    "results": [],
                    "note": "No news results found for this query.",
                }, ensure_ascii=False)
            logger.warning("news search attempt %d/%d failed: %s", attempt, _MAX_ATTEMPTS, exc)
            if attempt < _MAX_ATTEMPTS:
                time.sleep(_BACKOFF_BASE_SECONDS * attempt)
            continue

        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("body", ""),
                "date": r.get("date", ""),
                "source": r.get("source", ""),
            }
            for r in raw
        ]
        return json.dumps({
            "status": "ok",
            "query": query,
            "results": results,
        }, ensure_ascii=False, indent=2)

    return json.dumps({
        "status": "error",
        "error": f"News search failed after {_MAX_ATTEMPTS} attempts: {last_error}",
    }, ensure_ascii=False)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
