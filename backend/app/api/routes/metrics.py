from fastapi import APIRouter
from app.services.metrics_service import metrics_service

router = APIRouter()


@router.get("/summary")
async def get_metrics_summary():
    """Get aggregated RAG agent metrics"""
    return metrics_service.get_summary()


@router.delete("/")
async def reset_metrics():
    """Reset all metrics (delete metrics.json)"""
    try:
        if metrics_service.metrics_file.exists():
            metrics_service.metrics_file.unlink()
            return {"status": "success", "message": "Metrics reset"}
        return {"status": "success", "message": "No metrics to reset"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
