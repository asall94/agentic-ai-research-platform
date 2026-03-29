"""Utility to filter collected sources to those actually referenced in the final output."""
import re
from urllib.parse import urlparse


def strip_inline_links(text: str) -> str:
    """Remove markdown inline links [text](url) -> text, keeping only the label."""
    if not text:
        return text
    return re.sub(r'\[([^\]]+)\]\(https?://[^\)]+\)', r'\1', text)


def filter_relevant_sources(sources: list, report_text: str) -> list:
    """
    Return only the sources whose content is traceable in the report.
    Matching strategy (in order):
      1. URL domain appears in report text
      2. Any significant word (>4 chars) from the source title appears in report text
    Falls back to all sources if none match, to avoid empty source lists.
    """
    if not sources or not report_text:
        return sources

    report_lower = report_text.lower()
    relevant = []

    for source in sources:
        url = source.get("url", "")
        title = source.get("title", "")

        # Match on domain (e.g. "arxiv.org", "en.wikipedia.org")
        domain = ""
        try:
            domain = urlparse(url).netloc.replace("www.", "")
        except Exception:
            pass

        # Match on significant title words (skip short/common words)
        title_words = [w for w in title.lower().split() if len(w) > 4]

        if (domain and domain in report_lower) or any(w in report_lower for w in title_words):
            relevant.append(source)

    return relevant if relevant else sources
