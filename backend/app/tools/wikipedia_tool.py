import wikipedia
import time
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def _retry(func, retries: int = 3, delay: float = 1.0):
    """Retry a callable on SSL/connection errors with exponential backoff."""
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            err = str(e)
            if attempt < retries - 1 and any(k in err for k in ("SSL", "Connection", "EOF", "timeout")):
                time.sleep(delay * (2 ** attempt))
                continue
            raise


def wikipedia_search_tool(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search Wikipedia for articles.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of article dictionaries
    """
    try:
        # Search for pages with retry on SSL/network errors
        search_results = _retry(lambda: wikipedia.search(query, results=max_results))
        
        results = []
        for title in search_results:
            try:
                page = _retry(lambda t=title: wikipedia.page(t, auto_suggest=False))
                results.append({
                    "title": page.title,
                    "summary": _retry(lambda t=title: wikipedia.summary(t, sentences=3, auto_suggest=False)),
                    "url": page.url,
                    "content": page.content[:1000]
                })
            except wikipedia.exceptions.DisambiguationError as e:
                # If disambiguation, take first option
                try:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                    results.append({
                        "title": page.title,
                        "summary": wikipedia.summary(e.options[0], sentences=3, auto_suggest=False),
                        "url": page.url,
                        "content": page.content[:1000]
                    })
                except:
                    continue
            except:
                continue
        
        logger.info(f"Wikipedia search for '{query}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return [{"error": str(e)}]


# Tool definition for OpenAI function calling
wikipedia_tool_def = {
    "type": "function",
    "function": {
        "name": "wikipedia_search_tool",
        "description": "Search Wikipedia for encyclopedic knowledge and summaries",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for Wikipedia articles"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}
