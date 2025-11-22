import logging
import time
from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricsService:
    """Track RAG agent metrics: latency, tokens, cache hits, costs"""
    
    def __init__(self):
        self.metrics_file = Path("metrics.json")
        self.session_metrics = []
    
    def track_workflow(
        self,
        workflow_type: str,
        topic: str,
        execution_time: float,
        cache_hit: bool,
        tokens_used: Optional[int] = None,
        cost_estimate: Optional[float] = None,
        steps_count: Optional[int] = None,
        agents_used: Optional[list] = None
    ) -> Dict:
        """Track single workflow execution metrics"""
        
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_type": workflow_type,
            "topic": topic[:100],  # Truncate long topics
            "execution_time_seconds": round(execution_time, 2),
            "cache_hit": cache_hit,
            "tokens_used": tokens_used,
            "cost_usd": cost_estimate,
            "steps_count": steps_count,
            "agents_used": agents_used or []
        }
        
        self.session_metrics.append(metric)
        self._save_metric(metric)
        
        logger.info(
            f"Workflow tracked: {workflow_type} | "
            f"Time: {execution_time:.2f}s | "
            f"Cache: {'HIT' if cache_hit else 'MISS'} | "
            f"Tokens: {tokens_used or 'N/A'}"
        )
        
        return metric
    
    def _save_metric(self, metric: Dict):
        """Append metric to JSON file"""
        try:
            # Load existing metrics
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = []
            
            # Append new metric
            metrics.append(metric)
            
            # Save back
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save metric: {e}")
    
    def get_summary(self) -> Dict:
        """Get aggregated metrics summary"""
        try:
            if not self.metrics_file.exists():
                return {"total_requests": 0}
            
            with open(self.metrics_file, 'r') as f:
                metrics = json.load(f)
            
            if not metrics:
                return {"total_requests": 0}
            
            cache_hits = sum(1 for m in metrics if m.get("cache_hit"))
            total_time = sum(m.get("execution_time_seconds", 0) for m in metrics)
            total_tokens = sum(m.get("tokens_used", 0) for m in metrics if m.get("tokens_used"))
            total_cost = sum(m.get("cost_usd", 0) for m in metrics if m.get("cost_usd"))
            
            return {
                "total_requests": len(metrics),
                "cache_hit_rate": round(cache_hits / len(metrics) * 100, 1) if metrics else 0,
                "avg_execution_time_seconds": round(total_time / len(metrics), 2) if metrics else 0,
                "total_tokens_used": total_tokens,
                "total_cost_usd": round(total_cost, 4),
                "cost_savings_from_cache": round(
                    cache_hits * (total_cost / max(len(metrics) - cache_hits, 1)),
                    4
                ) if metrics else 0,
                "workflows_by_type": self._count_by_field(metrics, "workflow_type"),
                "recent_requests": metrics[-10:]  # Last 10
            }
        
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {"error": str(e)}
    
    def _count_by_field(self, metrics: list, field: str) -> Dict:
        """Count occurrences by field value"""
        counts = {}
        for m in metrics:
            value = m.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts


# Global instance
metrics_service = MetricsService()
