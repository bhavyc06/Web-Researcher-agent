"""
Central configuration (all env-overrideable).  No paid APIs used.
"""
import os

# DuckDuckGo search settings
DDG_REGION   = os.getenv("DDG_REGION", "wt-wt")
DDG_SAFE     = os.getenv("DDG_SAFE",   "moderate")
SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT", "5"))

# HuggingFace summarisation model (extremely small)
HF_SUMMARY_MODEL = os.getenv("HF_SUMMARY_MODEL", "t5-small")

# Max chars kept per scraped article
MAX_CHARS = 8_000
