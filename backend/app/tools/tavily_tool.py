try:
    from tavily import TavilyClient
except ImportError:
    # If tavily not installed, create dummy
    class TavilyClient:
        def __init__(self, *args, **kwargs):
            pass
        def search(self, *args, **kwargs):
            return {"results": []}
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


def tavily_search_tool(
    query: str,
    max_results: int = 5,
    include_images: bool = False
) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        include_images: Whether to include images
        
    Returns:
        List of search result dictionaries
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            logger.warning("Tavily API key not found")
            return [{"error": "Tavily API key not configured"}]
        
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            include_images=include_images
        )
        
        results = []
        for item in response.get("results", []):
            result = {
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
                "score": item.get("score", 0.0)
            }
            if include_images and "images" in item:
                result["images"] = item["images"]
            results.append(result)
        
        logger.info(f"Tavily search for '{query}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return [{"error": str(e)}]


# Tool definition for OpenAI function calling
tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "Search the web for recent information using Tavily",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for web content"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include images in results",
                    "default": False
                }
            },
            "required": ["query"]
        }
    }
}
