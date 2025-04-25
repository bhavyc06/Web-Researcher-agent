"""
Pipeline:
1 Plan  2 Search  3 Scrape  4 Analyse  5 Synthesise
Writes a minimal MCP-style JSON trace for full transparency.
"""
from pathlib import Path
from typing import List, Dict
import uuid, json, time, logging

from .tools.search_tool import search_web
from .tools.scraper_tool import fetch_article_text
from .tools.news_tool   import fetch_recent_news
from .agents.analyzer   import summarise
from .agents.synthesizer import synthesise

LOG = logging.getLogger("WebResearchAgent")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

class Trace:
    def __init__(self, query: str):
        self.id     = str(uuid.uuid4())
        self.start  = time.time()
        self.query  = query
        self.events: List[Dict] = []

    def log(self, role: str, kind: str, data: Dict):
        self.events.append({
            "ts": round(time.time() - self.start, 3),
            "role": role,
            "type": kind,
            "data": data
        })

    def save(self, path: Path):
        path.write_text(json.dumps({
            "id": self.id,
            "query": self.query,
            "events": self.events
        }, indent=2))

def run_research_pipeline(user_query: str, use_news: bool = True) -> Dict:
    trace = Trace(user_query)
    trace.log("user", "query", {"text": user_query})

    # 1 Search
    try:
        results = search_web(user_query)
        trace.log("tool", "search_web", {"hits": len(results)})
    except Exception as e:
        trace.log("error", "search_web", {"err": str(e)})
        results = []

    # 2 News
    news_hits = []
    if use_news:
        try:
            news_hits = fetch_recent_news(user_query, max_items=5)
            trace.log("tool", "news_rss", {"hits": len(news_hits)})
        except Exception as e:
            trace.log("error", "news_rss", {"err": str(e)})

    urls   = [r["href"] for r in results if r.get("href")] + [n["link"] for n in news_hits]
    titles = [r["title"] for r in results] + [n["title"] for n in news_hits]

    # 3 Scrape + 4 Analyse
    article_summaries: List[Dict] = []
    for url, title in zip(urls, titles):
        try:
            text = fetch_article_text(url)
            trace.log("tool", "fetch_article", {"url": url, "chars": len(text) if text else 0})
            if not text:
                continue
            summary = summarise(text)
            article_summaries.append({"url": url, "title": title, "summary": summary})
            trace.log("agent", "summary", {"url": url, "preview": summary[:120]})
        except Exception as e:
            trace.log("error", "scrape_or_sum", {"url": url, "err": str(e)})

    # 5 Synthesise
    report = synthesise(article_summaries, user_query)
    trace.log("agent", "final_answer", {"chars": len(report)})

    # Save MCP-style trace
    tpath = Path(f"execution_trace_{trace.id}.json")
    trace.save(tpath)

    return {"report": report, "trace_path": str(tpath)}
