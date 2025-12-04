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
    
    for item in items:
        if "e2e" in item.keywords and not is_e2e:
            item.add_marker(skip_e2e)
        if "deepeval" in item.keywords and not is_deepeval:
            item.add_marker(skip_deepeval)


@pytest.fixture(autouse=True)
def mock_openai_client(request):
    """Fixture to mock OpenAI client for all unit tests (not E2E or DeepEval)"""
    # Skip mocking for E2E and DeepEval tests
    if 'e2e' in request.keywords or 'deepeval' in request.keywords:
        yield None
        return
    
    # Patch OpenAI in all agent modules
    patches = [
        patch('app.agents.draft_agent.OpenAI'),
        patch('app.agents.reflection_agent.OpenAI'),
        patch('app.agents.revision_agent.OpenAI'),
        patch('app.agents.research_agent.OpenAI'),
        patch('app.agents.writer_agent.OpenAI'),
        patch('app.agents.editor_agent.OpenAI'),
        patch('app.agents.planner_agent.OpenAI'),
        patch('app.workflows.multi_agent.OpenAI'),
    ]
    
    # Create mock response
    mock_message = Mock()
    mock_message.content = "Test response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    
    # Configure mock client
    mock_client_instance = Mock()
    mock_client_instance.chat.completions.create.return_value = mock_response
    
    # Start all patches
    mocks = []
    for p in patches:
        mock_openai = p.start()
        mock_openai.return_value = mock_client_instance
        mock_openai._test_response = mock_response
        mock_openai._test_client = mock_client_instance
        mocks.append(mock_openai)
    
    yield mocks[0]  # Return first mock for tests to access
    
    # Stop all patches
    for p in patches:
        p.stop()
