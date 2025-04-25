"""
scraper_tool.py
---------------
Pure-BS4 scraper (no newspaper3k, no lxml).

• GETs the URL
• extracts <p> text via html.parser
• truncates to MAX_CHARS
"""
from typing import Optional
import requests
from bs4 import BeautifulSoup
from ..config import MAX_CHARS

_HEADERS = {"User-Agent": "Mozilla/5.0 (WebResearchAgent/1.0)"}

def fetch_article_text(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join(paragraphs)
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "...[truncated]"
        return text
    except Exception:
        return None
