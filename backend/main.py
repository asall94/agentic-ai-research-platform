from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from dotenv import load_dotenv

from app.api.routes import workflows, health, cache, metrics
from app.core.config import settings
from app.core.startup_checks import check_requirements
from app.core.logging_config import setup_json_logging, StructuredLogger
from app.middleware import RateLimiter, LoggingMiddleware

# Load environment variables
load_dotenv()

# Configure JSON logging
setup_json_logging(settings.LOG_LEVEL)
logger = StructuredLogger(__name__)

# Run startup checks
if not check_requirements():
    logger.error("Application cannot start due to failed requirements checks")
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("Shutting down application")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-agent research platform with reflection, tool usage, and orchestration",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware (before rate limiter)
app.add_middleware(LoggingMiddleware)

# Rate limiting
app.add_middleware(
    RateLimiter,
    requests_per_window=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(cache.router, prefix="/api/v1/cache", tags=["cache"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
