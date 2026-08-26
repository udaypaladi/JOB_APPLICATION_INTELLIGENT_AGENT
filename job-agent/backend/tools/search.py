"""
Thin wrapper around Tavily so the rest of the codebase doesn't care which
search provider is behind it. Swap the implementation here if you switch
to SerpAPI later — nothing else needs to change.
"""
from tavily import TavilyClient

client = TavilyClient()  # reads TAVILY_API_KEY from env


def search_company(company_name: str, max_results: int = 8) -> list[dict]:
    """
    Runs a small batch of targeted queries rather than one generic query —
    each angle (news, culture, tech stack) surfaces different results.
    Returns a flat list of {title, url, content} dicts for downstream chunking.
    """
    queries = [
        f"{company_name} company news 2026",
        f"{company_name} engineering tech stack",
        f"{company_name} company culture employee reviews",
        f"{company_name} funding recent",
    ]

    results = []
    for q in queries:
        resp = client.search(query=q, max_results=max_results // len(queries) + 1)
        for r in resp.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            })
    return results
