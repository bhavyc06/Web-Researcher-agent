"""
synthesizer.py
==============

Combine per-article summaries into a concise plain-text answer.
Uses HuggingFace `t5-small` (≈240 MB, CPU-friendly).

Returns text with numbered citations plus legend.
"""

from __future__ import annotations

from typing import List, Dict
from transformers import pipeline
from tqdm import tqdm
from ..config import HF_SUMMARY_MODEL

# Lazy global so we download the model only once
_summary_pipe = None


def _get_pipe():
    global _summary_pipe
    if _summary_pipe is None:
        _summary_pipe = pipeline("summarization", model=HF_SUMMARY_MODEL, device=-1, framework="pt")
    return _summary_pipe


def synthesise(summaries: List[Dict], user_query: str) -> str:
    """
    summaries: list of {"title", "url", "summary"}
    Returns: plain-text report with inline citations and legend.
    """
    if not summaries:
        return "Sorry, no useful information was found."

    # tag each summary for later citation
    tagged = [f"[{i+1}] {item['summary']}" for i, item in enumerate(summaries)]
    merged = " ".join(tagged)

    # Abstractive fusion via T5-small if text is long
    if len(merged) > 800:
        merged = _get_pipe()(merged, max_length=200, min_length=60, do_sample=False)[0]["summary_text"]

    legend = "\n".join(f"[{i+1}] {item['title']} — {item['url']}" for i, item in enumerate(summaries))

    return f"{merged}\n\nSources\n-------\n{legend}"
