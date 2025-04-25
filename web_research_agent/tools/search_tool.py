"""
search_tool.py  – robust, key-free web search
---------------------------------------------

1. `duckduckgo-search` JSON API (fast, no scraping).
2. DuckDuckGo HTML scrape (requests + bs4) if the library fails OR 0 hits.
3. Wikipedia search API last-ditch fallback.

Returns a list of dicts: {title, href, body}
"""

from typing import List, Dict
import urllib.parse, requests, bs4
from ..config import SEARCH_LIMIT, DDG_SAFE

# ──────────────────────────────────────────────────────────────
# 1️⃣  Preferred: use duckduckgo-search library
try:
    from duckduckgo_search import DDGS          # pip install duckduckgo-search
    _HAS_DDGS = True
except Exception:
    _HAS_DDGS = False


def _lib_search(q: str, n: int) -> List[Dict]:
    out: List[Dict] = []
    with DDGS() as ddgs:
        for r in ddgs.text(q, safesearch=DDG_SAFE, max_results=n):
            out.append({k: r.get(k) for k in ("title", "href", "body")})
    return out


# ──────────────────────────────────────────────────────────────
# 2️⃣  HTML scraper fallback
_UA = {
    "User-Agent": "Mozilla/5.0 (WebResearchAgent/1.0)",
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean(href: str) -> str:
    # strip DDG redirect wrapper
    if "uddg=" in href:
        href = href.split("uddg=", 1)[-1]
    return urllib.parse.unquote(href)


def _html_search(q: str, n: int) -> List[Dict]:
    url = f"https://duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
    html = requests.get(url, headers=_UA, timeout=10).text
    soup = bs4.BeautifulSoup(html, "html.parser")

    hits: List[Dict] = []
    for res in soup.select("div.result"):
        if len(hits) >= n:
            break
        a = res.select_one("a.result__a")
        if not a:
            continue
        snippet_tag = res.select_one(".result__snippet")
        hits.append(
            {
                "title": a.get_text(" ", strip=True),
                "href": _clean(a["href"]),
                "body": snippet_tag.get_text(" ", strip=True) if snippet_tag else "",
            }
        )
    return hits


# ──────────────────────────────────────────────────────────────
# 3️⃣  Wikipedia API fallback (guaranteed non-empty for factual queries)
def _wiki_search(q: str, n: int) -> List[Dict]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": q,
        "srlimit": str(n),
        "format": "json",
    }
    j = requests.get("https://en.wikipedia.org/w/api.php", params=params, timeout=10).json()
    hits: List[Dict] = []
    for item in j.get("query", {}).get("search", []):
        title = item["title"]
        snippet = bs4.BeautifulSoup(item["snippet"], "html.parser").get_text(" ", strip=True)
        href = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        hits.append({"title": title, "href": href, "body": snippet})
    return hits[:n]


# ──────────────────────────────────────────────────────────────
def search_web(query: str, limit: int = SEARCH_LIMIT) -> List[Dict]:
    """Return up to `limit` results via library → HTML → Wikipedia."""
    # 1 library
    if _HAS_DDGS:
        try:
            res = _lib_search(query, limit)
            if res:
                return res
        except Exception:
            pass

    # 2 HTML
    try:
        res = _html_search(query, limit)
        if res:
            return res
    except Exception:
        pass

    # 3 Wikipedia
    try:
        return _wiki_search(query, limit)
    except Exception:
        return []
