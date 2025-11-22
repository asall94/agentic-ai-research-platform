import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
import traceback


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base log structure
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        
        # Add workflow context if present
        if hasattr(record, "workflow_id"):
            log_data["workflow_id"] = record.workflow_id
        if hasattr(record, "workflow_type"):
            log_data["workflow_type"] = record.workflow_type
        
        # Add user context if present
        if hasattr(record, "client_ip"):
            log_data["client_ip"] = record.client_ip
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_json_logging(log_level: str = "INFO") -> None:
    """Configure JSON logging for the application"""
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create JSON handler for stdout
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(json_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


class StructuredLogger:
    """Helper class for structured logging with context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log(self, level: int, message: str, **kwargs):
        """Log with structured context"""
        extra_data = {k: v for k, v in kwargs.items() if v is not None}
        
        # Create LogRecord with extra data
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(structured)",
            0,
            message,
            (),
            None
        )
        
        # Attach extra data
        if extra_data:
            record.extra_data = extra_data
        
        # Attach context from kwargs
        for key in ["correlation_id", "workflow_id", "workflow_type", "client_ip"]:
            if key in kwargs:
                setattr(record, key, kwargs[key])
        
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
