from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app, requests_per_window: int = 100, window_seconds: int = 900):
        super().__init__(app)
        self.requests_per_window = requests_per_window  # Default: 100 requests
        self.window_seconds = window_seconds  # Default: 15 minutes
        self.client_requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/api/v1/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Clean old requests and check limit
        current_time = time.time()
        self._clean_old_requests(client_ip, current_time)
        
        # Check if rate limit exceeded
        request_count = len(self.client_requests[client_ip])
        if request_count >= self.requests_per_window:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.requests_per_window} requests per {self.window_seconds // 60} minutes",
                    "retry_after": self._get_retry_after(client_ip, current_time)
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(self._get_window_reset(client_ip, current_time))),
                    "Retry-After": str(self._get_retry_after(client_ip, current_time))
                }
            )
        
        # Add current request
        self.client_requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_window - len(self.client_requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(self._get_window_reset(client_ip, current_time)))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, client_ip: str, current_time: float):
        """Remove requests outside the current time window"""
        cutoff_time = current_time - self.window_seconds
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if req_time > cutoff_time
        ]
    
    def _get_window_reset(self, client_ip: str, current_time: float) -> float:
        """Get timestamp when rate limit window resets"""
        if not self.client_requests[client_ip]:
            return current_time + self.window_seconds
        oldest_request = min(self.client_requests[client_ip])
        return oldest_request + self.window_seconds
    
    def _get_retry_after(self, client_ip: str, current_time: float) -> int:
        """Get seconds until client can retry"""
        reset_time = self._get_window_reset(client_ip, current_time)
        return max(1, int(reset_time - current_time))
