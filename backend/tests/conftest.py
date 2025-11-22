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
mock_client_instance = MagicMock()
mock_response = MagicMock()
mock_message = MagicMock()
mock_message.content = "Mocked response"
mock_choice = MagicMock()
mock_choice.message = mock_message
mock_response.choices = [mock_choice]
mock_client_instance.chat.completions.create.return_value = mock_response
mock_openai_module.OpenAI.return_value = mock_client_instance
sys.modules['openai'] = mock_openai_module


@pytest.fixture
def mock_openai_client():
    """Fixture to access the mocked OpenAI client"""
    return mock_client_instance
