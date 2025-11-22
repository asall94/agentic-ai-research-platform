# Pytest configuration
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["CACHE_ENABLED"] = "False"
os.environ["LOG_LEVEL"] = "ERROR"

# Mock OpenAI globally before any imports
mock_openai_module = MagicMock()
mock_openai_module.__spec__ = MagicMock()
mock_openai_module.__spec__.name = 'openai'
mock_client_instance = MagicMock()

# Create a callable mock for chat.completions.create that returns different responses
def mock_create(*args, **kwargs):
    mock_response = MagicMock()
    mock_message = MagicMock()
    # Default JSON response for agent selection
    mock_message.content = '{"agent": "research_agent", "task": "Execute task"}'
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    return mock_response

mock_client_instance.chat.completions.create = mock_create
mock_openai_module.OpenAI.return_value = mock_client_instance
sys.modules['openai'] = mock_openai_module


@pytest.fixture
def mock_openai_client():
    """Fixture to access the mocked OpenAI client"""
    return mock_client_instance
