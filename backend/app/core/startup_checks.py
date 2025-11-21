import logging
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def check_requirements():
    """Check all system requirements before starting the application."""
    errors = []
    warnings = []
    
    # Check Python version
    if sys.version_info < (3, 10):
        errors.append(f"Python 3.10+ required. Current: {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Check optional but recommended environment variables
    optional_env_vars = ["TAVILY_API_KEY"]
    for var in optional_env_vars:
        if not os.getenv(var):
            warnings.append(f"Missing optional environment variable: {var}")
    
    # Check Redis availability if cache is enabled
    cache_enabled = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    if cache_enabled:
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            r = redis.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
            logger.info(f"Redis connection successful: {redis_url}")
        except ImportError:
            errors.append("Redis package not installed. Run: pip install redis")
        except Exception as e:
            warnings.append(f"Redis not available: {e}. Caching will be disabled.")
    
    # Check sentence-transformers if cache is enabled
    if cache_enabled:
        try:
            import sentence_transformers
        except ImportError:
            errors.append("sentence-transformers not installed. Run: pip install sentence-transformers")
    
    # Check core dependencies
    required_packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "openai": "OpenAI",
        "pydantic": "Pydantic",
        "python_dotenv": "python-dotenv"
    }
    
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            errors.append(f"{name} not installed. Run: pip install -r requirements.txt")
    
    # Print results
    if errors:
        logger.error("Startup checks failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    if warnings:
        logger.warning("Startup warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    logger.info("All critical startup checks passed")
    return True
