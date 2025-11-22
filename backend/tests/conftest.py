# Pytest configuration
import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["CACHE_ENABLED"] = "False"
os.environ["LOG_LEVEL"] = "ERROR"


@pytest.fixture(autouse=True)
def mock_openai_client():
    """Auto-mock OpenAI client for all tests"""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Mocked response"))]
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_openai.return_value = mock_client
        yield mock_client
