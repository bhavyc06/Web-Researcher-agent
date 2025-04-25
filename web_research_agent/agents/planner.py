"""
planner.py  – light query-analysis component

• classifies query intent: FACT, RECENT, COMPARE
• splits on 'and', 'vs', ',' into sub-queries
"""

from typing import List, Literal
import re, datetime as _dt

Intent = Literal["FACT", "RECENT", "COMPARE", "OTHER"]

_RECENT_WORDS = {"latest", "today", "current", str(_dt.datetime.now().year)}
_COMPARE_WORDS = {"vs", "versus", "compare", "comparison", "difference"}

def detect_intent(query: str) -> Intent:
    q = query.lower()
    if any(w in q for w in _RECENT_WORDS):
        return "RECENT"
    if any(w in q for w in _COMPARE_WORDS):
        return "COMPARE"
    if q.endswith("?") or q.split()[0] in {"who", "what", "when", "where"}:
        return "FACT"
    return "OTHER"

def split_subqueries(query: str) -> List[str]:
    # crude: split on ' and ', ' vs ', commas
    parts = re.split(r"\band\b|,| vs | versus ", query, flags=re.I)
    return [p.strip() for p in parts if len(p.split()) >= 2]
