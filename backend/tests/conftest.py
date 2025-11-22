# Pytest configuration
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["CACHE_ENABLED"] = "False"
os.environ["LOG_LEVEL"] = "ERROR"
