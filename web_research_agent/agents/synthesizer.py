"""
Combine individual article summaries into a single answer.
Uses HuggingFace `t5-small` – very light (≈240 MB) and CPU-friendly.
"""
from typing import List, Dict
from transformers import pipeline
from tqdm import tqdm
from ..config import HF_SUMMARY_MODEL

# Lazy instantiation (download once)
_summary_pipe = None

def _get_pipe():
    global _summary_pipe
    if _summary_pipe is None:
        _summary_pipe = pipeline(
            "summarization",
            model=HF_SUMMARY_MODEL,
            device=-1,           # CPU
            framework="pt"
        )
    return _summary_pipe

def synthesise(summaries: List[Dict], user_query: str) -> str:
    """
    summaries = [{title,url,summary}]
    Returns plain-text report with numbered citations.
    """
    if not summaries:
        return "Sorry, no useful information was found."

    tagged = [f"[{i+1}] {item['summary']}" for i, item in enumerate(summaries)]
    merged = " ".join(tagged)

    # t5-small handles ~512 tokens – OK for our truncated text
    if len(merged) > 1000:
        merged = _get_pipe()(merged, max_length=200, min_length=60,
                             do_sample=False)[0]["summary_text"]

    legend = "\n".join(
        f"[{i+1}] {item['title']} — {item['url']}"
        for i, item in enumerate(summaries)
    )

    return f"{merged}\n\nSources\n-------\n{legend}"
