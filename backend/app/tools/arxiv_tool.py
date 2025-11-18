import arxiv
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def arxiv_search_tool(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search arXiv for academic papers.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of paper dictionaries
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in search.results():
            results.append({
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d"),
                "summary": paper.summary,
                "url": paper.entry_id,
                "pdf_url": paper.pdf_url if hasattr(paper, 'pdf_url') else None
            })
        
        logger.info(f"arXiv search for '{query}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"arXiv search error: {e}")
        return [{"error": str(e)}]


# Tool definition for OpenAI function calling
arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "Search arXiv for academic papers and preprints",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for academic papers"
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
