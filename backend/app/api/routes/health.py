from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings
from datetime import datetime

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    tools_available = {
        "arxiv": settings.ENABLE_ARXIV,
        "tavily": settings.ENABLE_TAVILY and bool(settings.TAVILY_API_KEY),
        "wikipedia": settings.ENABLE_WIKIPEDIA
    }
    
    models_configured = {
        "draft": settings.DEFAULT_DRAFT_MODEL,
        "reflection": settings.DEFAULT_REFLECTION_MODEL,
        "research": settings.DEFAULT_RESEARCH_MODEL,
        "writer": settings.DEFAULT_WRITER_MODEL,
        "editor": settings.DEFAULT_EDITOR_MODEL,
        "planner": settings.DEFAULT_PLANNER_MODEL
    }
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        tools_available=tools_available,
        models_configured=models_configured
    )
