import os

import requests

from backend.config import TOP_WEB_RESULTS


def search_web(query: str, max_results: int = TOP_WEB_RESULTS) -> list[dict]:
    """Tavily web search fallback; returns [{title, url, content}], [] if no key/error."""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        return []
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": tavily_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        print(f"[web_search] request failed: {exc}")
        return []
    if resp.status_code != 200:
        print(f"[web_search] Tavily error {resp.status_code}: {resp.text[:300]}")
        return []
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        }
        for r in resp.json().get("results", [])
    ]