from fastapi import APIRouter
from app.services.cache_service import cache_service
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """Get cache statistics"""
    return cache_service.get_cache_stats()


@router.delete("/{topic_hash}")
async def invalidate_cache_entry(topic_hash: str):
    """Invalidate specific cache entry by topic hash"""
    deleted = cache_service.invalidate_cache(topic_hash)
    return {
        "message": f"Invalidated {deleted} cache entries",
        "topic_hash": topic_hash,
        "deleted_count": deleted
    }


@router.delete("/")
async def invalidate_all_cache():
    """Invalidate all cache entries"""
    deleted = cache_service.invalidate_cache()
    return {
        "message": f"Invalidated all cache entries",
        "deleted_count": deleted
    }
