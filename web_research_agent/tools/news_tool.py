"""Very small RSS news search via feedparser (open-source)."""
from typing import List, Dict
import feedparser

RSS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

def fetch_recent_news(topic: str, max_items: int = 10) -> List[Dict]:
    topic_l = topic.lower()
    hits: List[Dict] = []
    for url in RSS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            blob = (entry.get("title", "") + entry.get("summary", "")).lower()
            if topic_l in blob:
                hits.append({
                    "title": entry.get("title"),
                    "link":  entry.get("link"),
                    "summary": entry.get("summary", "")[:200]
                })
            if len(hits) >= max_items:
                return hits
    return hits
