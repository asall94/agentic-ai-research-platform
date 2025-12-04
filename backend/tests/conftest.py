# Pytest configuration
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_addoption(parser):
    """Add custom pytest options"""
    parser.addoption("--e2e", action="store_true", help="Run E2E tests with real API calls")
    parser.addoption("--deepeval", action="store_true", help="Run DeepEval quality tests")


def pytest_configure(config):
    """Configure test environment and register markers"""
    is_e2e = config.getoption("--e2e", default=False)
    is_deepeval = config.getoption("--deepeval", default=False)
    
    if is_e2e or is_deepeval:
        # Real API tests - don't override env vars if already set
        if "OPENAI_API_KEY" not in os.environ or os.environ.get("OPENAI_API_KEY", "").startswith("test"):
            # Load from .env if exists
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except:
                pass
    else:
        # Unit tests - use mocks, override any existing API keys
        os.environ["OPENAI_API_KEY"] = "test-mock-key-for-unit-tests"
        os.environ["TAVILY_API_KEY"] = "test-mock-key-for-unit-tests"
        
    os.environ["CACHE_ENABLED"] = "False"
    os.environ["LOG_LEVEL"] = "ERROR"
    
    # Register markers
    config.addinivalue_line("markers", "e2e: End-to-end tests with real API calls")
    config.addinivalue_line("markers", "deepeval: DeepEval quality assessment tests")


def pytest_collection_modifyitems(config, items):
    """Skip tests and setup mocks based on markers"""
    skip_e2e = pytest.mark.skip(reason="Use --e2e to run E2E tests")
    skip_deepeval = pytest.mark.skip(reason="Use --deepeval to run DeepEval tests")
    
    is_e2e = config.getoption("--e2e", default=False)
    is_deepeval = config.getoption("--deepeval", default=False)
    is_unit_test = not (is_e2e or is_deepeval)
    
    for item in items:
        if "e2e" in item.keywords and not is_e2e:
            item.add_marker(skip_e2e)
        if "deepeval" in item.keywords and not is_deepeval:
            item.add_marker(skip_deepeval)
    
    # Mock OpenAI only for unit tests
    if is_unit_test:
        # Mock OpenAI globally before any imports
        mock_openai_module = MagicMock()
        mock_openai_module.__spec__ = MagicMock()
        mock_openai_module.__spec__.name = 'openai'
        
        # Create shared mock response that tests can modify
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '{"agent": "research_agent", "task": "Execute task"}'
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        # Create mock client instance
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create = MagicMock(return_value=mock_response)
        
        # Store response reference for fixture access
        mock_openai_module._test_response = mock_response
        mock_openai_module.OpenAI.return_value = mock_client_instance
        sys.modules['openai'] = mock_openai_module
        
        # Mock opencensus to avoid Application Insights dependency in tests
        mock_opencensus = MagicMock()
        sys.modules['opencensus'] = mock_opencensus
        sys.modules['opencensus.ext'] = MagicMock()
        sys.modules['opencensus.ext.azure'] = MagicMock()
        sys.modules['opencensus.ext.azure.log_exporter'] = MagicMock()
        sys.modules['opencensus.ext.azure.metrics_exporter'] = MagicMock()
        sys.modules['opencensus.ext.fastapi'] = MagicMock()
        sys.modules['opencensus.stats'] = MagicMock()
        sys.modules['opencensus.stats.aggregation'] = MagicMock()
        sys.modules['opencensus.stats.measure'] = MagicMock()
        sys.modules['opencensus.stats.stats'] = MagicMock()
        sys.modules['opencensus.stats.view'] = MagicMock()
        sys.modules['opencensus.tags'] = MagicMock()
        sys.modules['opencensus.tags.tag_map'] = MagicMock()


@pytest.fixture
def mock_openai_client():
    """Fixture to access the mocked OpenAI client (only for unit tests)"""
    if 'openai' in sys.modules:
        # Return the entire mock module so tests can access create()
        return sys.modules['openai']
    return None
