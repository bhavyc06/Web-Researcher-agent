"""
Simple extractive summariser using word-frequency scoring.
Lightweight: spaCy blank + sentencizer only (no large model).
"""
from typing import List
from collections import Counter
import spacy

_nlp = spacy.blank("en")
_nlp.add_pipe("sentencizer")

def summarise(text: str, max_sentences: int = 3) -> str:
    doc = _nlp(text)
    sents: List[str] = [s.text for s in doc.sents]
    if len(sents) <= max_sentences:
        return text

    words = [tok.text.lower() for tok in doc if tok.is_alpha and not tok.is_stop]
    freq  = Counter(words)

    scored = [(sum(freq.get(w.lower(), 0) for w in sent.split()), sent) for sent in sents]
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
    # keep original order
    ordered = [sent for _, sent in sorted(top, key=lambda x: sents.index(x[1]))]
    return " ".join(ordered)
