"""
orchestrator.py
===============

Main pipeline controller:

0.  Plan – detect intent / split sub-queries
1.  Search – web + optional RSS
2.  Scrape  – download & clean pages
3.  Analyse – extractive summary
4.  Detect contradictions (numeric)
5.  Synthesise – fuse summaries into final answer

Every step is logged to a minimal MCP-style JSON trace.
"""

from __future__ import annotations

import json, re, time, uuid, logging
from pathlib import Path
from collections import defaultdict
from math import log
from typing import Dict, List

from .config import SEARCH_LIMIT
from .tools.search_tool import search_web
from .tools.scraper_tool import fetch_article_text
from .tools.news_tool import fetch_recent_news
from .agents.analyzer import summarise
from .agents.synthesizer import synthesise
from .agents.planner import detect_intent, split_subqueries

LOG = logging.getLogger("WebResearchAgent")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


class Trace:
    """Lightweight Execution trace, MCP-style."""

    def __init__(self, query: str):
        self.id = str(uuid.uuid4())
        self.start = time.time()
        self.query = query
        self.events: List[Dict] = []

    def log(self, role: str, kind: str, data: Dict):
        self.events.append(
            {
                "ts": round(time.time() - self.start, 3),
                "role": role,
                "type": kind,
                "data": data,
            }
        )

    def save(self, path: Path):
        path.write_text(json.dumps({"id": self.id, "query": self.query, "events": self.events}, indent=2))


# ---------------------------------------------------------------------------


def _score_relevance(hit: Dict, query_terms: set[str]) -> float:
    """Very small BM25-ish score based on term frequency."""
    body = (hit.get("title", "") + " " + hit.get("body", "")).lower()
    tf = sum(body.count(t) for t in query_terms)
    return tf * log(len(body) + 1)


def _detect_contradictions(summaries: List[Dict]) -> Dict[str, List[str]]:
    """Find identical 3+-digit numbers appearing in >1 source."""
    seen: defaultdict[str, List[str]] = defaultdict(list)
    for art in summaries:
        nums = re.findall(r"\b\d{3,}\b", art["summary"])
        for num in nums:
            seen[num].append(art["title"])
    return {k: v for k, v in seen.items() if len(v) > 1}


# ---------------------------------------------------------------------------


def run_research_pipeline(user_query: str, use_news: bool = True) -> Dict:
    """
    Execute the end-to-end research pipeline; return
    {"report": <plain text>, "trace_path": <file str>}
    """
    trace = Trace(user_query)
    trace.log("user", "query", {"text": user_query})

    # 0 ── PLAN ───────────────────────────────────────────────────────────
    intent = detect_intent(user_query)
    sub_qs = split_subqueries(user_query) or [user_query]
    trace.log("agent", "plan", {"intent": intent, "sub_queries": sub_qs})

    # 1 ── SEARCH ────────────────────────────────────────────────────────
    search_hits: List[Dict] = []
    for sub in sub_qs:
        search_hits.extend(search_web(sub, limit=SEARCH_LIMIT))
    trace.log("tool", "search_web", {"hits": len(search_hits)})

    # optional news
    news_hits: List[Dict] = []
    if use_news:
        news_hits = fetch_recent_news(user_query, max_items=5)
        trace.log("tool", "news_rss", {"hits": len(news_hits)})

    # combined & relevance-ranked
    q_terms = set(user_query.lower().split())
    ranked = sorted(search_hits, key=lambda h: _score_relevance(h, q_terms), reverse=True)[:SEARCH_LIMIT]

    urls = [h["href"] for h in ranked if h.get("href")] + [n["link"] for n in news_hits]
    titles = [h["title"] for h in ranked] + [n["title"] for n in news_hits]

    # 2–3 ── SCRAPE + ANALYSE ────────────────────────────────────────────
    article_summaries: List[Dict] = []
    for url, title in zip(urls, titles):
        text = fetch_article_text(url)
        trace.log("tool", "fetch_article", {"url": url, "chars": len(text) if text else 0})
        if not text:
            continue
        summ = summarise(text)
        article_summaries.append({"url": url, "title": title, "summary": summ})
        trace.log("agent", "summary", {"url": url, "preview": summ[:120]})

    # 4 ── CONTRADICTION SCAN ────────────────────────────────────────────
    contradict = _detect_contradictions(article_summaries)

    # 5 ── SYNTHESISE ────────────────────────────────────────────────────
    report = synthesise(article_summaries, user_query)
    if contradict:
        report += "\n\n⚠️  Possible contradictory figures:\n"
        for num, srcs in contradict.items():
            report += f"  • {num} mentioned by: {', '.join(srcs[:3])}\n"

    trace.log("agent", "final_answer", {"chars": len(report)})

    # ── save trace
    trace_path = Path(f"execution_trace_{trace.id}.json")
    trace.save(trace_path)

    return {"report": report, "trace_path": str(trace_path)}
