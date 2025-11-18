import wikipedia
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


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
        # Search for pages
        search_results = wikipedia.search(query, results=max_results)
        
        results = []
        for title in search_results:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                results.append({
                    "title": page.title,
                    "summary": wikipedia.summary(title, sentences=3, auto_suggest=False),
                    "url": page.url,
                    "content": page.content[:1000]  # First 1000 chars
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
