"""
Application Insights configuration and initialization.
"""
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
from app.core.config import settings

logger = logging.getLogger(__name__)

# Metrics measures
request_measure = measure_module.MeasureFloat("request_duration", "Request duration in ms", "ms")
error_measure = measure_module.MeasureInt("errors", "Number of errors", "1")
workflow_duration_measure = measure_module.MeasureFloat("workflow_duration", "Workflow execution time", "s")
cache_hit_measure = measure_module.MeasureInt("cache_hits", "Cache hit count", "1")


def setup_app_insights():
    """
    Configure Application Insights telemetry.
    Returns True if successfully configured, False otherwise.
    """
    if not settings.APPINSIGHTS_ENABLED:
        logger.info("Application Insights disabled via configuration")
        return False
    
    if not settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
        logger.warning("Application Insights connection string not configured")
        return False
    
    try:
        # Configure logging exporter
        azure_handler = AzureLogHandler(
            connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING
        )
        azure_handler.setLevel(logging.INFO)
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(azure_handler)
        
        # Configure metrics exporter
        exporter = metrics_exporter.new_metrics_exporter(
            connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING
        )
        
        # Create views for custom metrics
        stats = stats_module.stats
        view_manager = stats.view_manager
        
        # Request duration view
        request_view = view_module.View(
            "request_duration_view",
            "Request duration distribution",
            ["endpoint", "status"],
            request_measure,
            aggregation_module.DistributionAggregation([50, 100, 200, 500, 1000, 2000, 5000])
        )
        view_manager.register_view(request_view)
        
        # Error count view
        error_view = view_module.View(
            "error_count_view",
            "Error count by type",
            ["error_type", "endpoint"],
            error_measure,
            aggregation_module.CountAggregation()
        )
        view_manager.register_view(error_view)
        
        # Workflow duration view
        workflow_view = view_module.View(
            "workflow_duration_view",
            "Workflow execution time distribution",
            ["workflow_type", "cache_hit"],
            workflow_duration_measure,
            aggregation_module.DistributionAggregation([1, 5, 10, 30, 60, 120, 300])
        )
        view_manager.register_view(workflow_view)
        
        # Cache hit view
        cache_view = view_module.View(
            "cache_hit_view",
            "Cache hit count",
            ["workflow_type"],
            cache_hit_measure,
            aggregation_module.CountAggregation()
        )
        view_manager.register_view(cache_view)
        
        # Register exporter
        view_manager.register_exporter(exporter)
        
        logger.info("Application Insights configured successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure Application Insights: {e}")
        return False


def track_request(endpoint: str, duration_ms: float, status: int):
    """Track HTTP request metrics"""
    if not settings.APPINSIGHTS_ENABLED:
        return
    
    try:
        mmap = stats_module.stats.stats_recorder.new_measurement_map()
        tmap = tag_map_module.TagMap()
        tmap.insert("endpoint", endpoint)
        tmap.insert("status", str(status))
        
        mmap.measure_float_put(request_measure, duration_ms)
        mmap.record(tmap)
    except Exception as e:
        logger.debug(f"Failed to track request metric: {e}")


def track_error(error_type: str, endpoint: str):
    """Track error occurrence"""
    if not settings.APPINSIGHTS_ENABLED:
        return
    
    try:
        mmap = stats_module.stats.stats_recorder.new_measurement_map()
        tmap = tag_map_module.TagMap()
        tmap.insert("error_type", error_type)
        tmap.insert("endpoint", endpoint)
        
        mmap.measure_int_put(error_measure, 1)
        mmap.record(tmap)
    except Exception as e:
        logger.debug(f"Failed to track error metric: {e}")


def track_workflow(workflow_type: str, duration_seconds: float, cache_hit: bool):
    """Track workflow execution metrics"""
    if not settings.APPINSIGHTS_ENABLED:
        return
    
    try:
        mmap = stats_module.stats.stats_recorder.new_measurement_map()
        tmap = tag_map_module.TagMap()
        tmap.insert("workflow_type", workflow_type)
        tmap.insert("cache_hit", "true" if cache_hit else "false")
        
        mmap.measure_float_put(workflow_duration_measure, duration_seconds)
        mmap.record(tmap)
        
        if cache_hit:
            cache_mmap = stats_module.stats.stats_recorder.new_measurement_map()
            cache_tmap = tag_map_module.TagMap()
            cache_tmap.insert("workflow_type", workflow_type)
            cache_mmap.measure_int_put(cache_hit_measure, 1)
            cache_mmap.record(cache_tmap)
            
    except Exception as e:
        logger.debug(f"Failed to track workflow metric: {e}")
