from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import time
import logging
from app.core.logging_config import StructuredLogger
from app.core.app_insights import track_request, track_error

logger = StructuredLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation IDs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Extract client info
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        start_time = time.time()
        logger.info(
            f"{request.method} {request.url.path}",
            correlation_id=correlation_id,
            client_ip=client_ip,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            duration = time.time() - start_time
            logger.info(
                f"Response {response.status_code}",
                correlation_id=correlation_id,
                client_ip=client_ip,
                status_code=response.status_code,
                duration_seconds=round(duration, 3)
            )
            
            # Track in Application Insights
            track_request(
                endpoint=request.url.path,
                duration_ms=duration * 1000,
                status=response.status_code
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                correlation_id=correlation_id,
                client_ip=client_ip,
                duration_seconds=round(duration, 3),
                exc_info=True
            )
            
            # Track error in Application Insights
            track_error(
                error_type=type(e).__name__,
                endpoint=request.url.path
            )
            
            raise
