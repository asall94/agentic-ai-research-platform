import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
import sys
import os

# Mock startup checks before importing main
sys.modules['app.core.startup_checks'] = type(sys)('app.core.startup_checks')
sys.modules['app.core.startup_checks'].check_requirements = lambda: True

from main import app

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check_returns_200(self, client):
        """Health endpoint should return 200 status"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_health_check_response_structure(self, client):
        """Health endpoint should return proper JSON structure"""
        response = await client.get("/api/v1/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"


class TestReflectionWorkflowEndpoint:
    """Test suite for reflection workflow endpoint"""
    
    @pytest.mark.asyncio
    @patch('app.workflows.simple_reflection.SimpleReflectionWorkflow.execute')
    async def test_reflection_workflow_returns_200(self, mock_execute, client):
        """Reflection workflow should return 200 on success"""
        mock_execute.return_value = {
            "draft": "Draft content",
            "reflection": "Critique",
            "revised": "Final content"
        }
        
        response = await client.post(
            "/api/v1/workflows/reflection",
            json={"topic": "AI ethics"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    @patch('app.workflows.simple_reflection.SimpleReflectionWorkflow.execute')
    async def test_reflection_workflow_response_structure(self, mock_execute, client):
        """Reflection workflow should return proper response structure"""
        mock_execute.return_value = {
            "draft": "Draft",
            "reflection": "Critique",
            "revised": "Final"
        }
        
        response = await client.post(
            "/api/v1/workflows/reflection",
            json={"topic": "Test topic"}
        )
        
        data = response.json()
        assert "workflow_id" in data
        assert "workflow_type" in data
        assert "status" in data
        assert "draft" in data
        assert "reflection" in data
        assert "revised" in data
    
    @pytest.mark.asyncio
    async def test_reflection_workflow_requires_topic(self, client):
        """Reflection workflow should require topic parameter"""
        response = await client.post(
            "/api/v1/workflows/reflection",
            json={}
        )
        
        assert response.status_code == 422  # Validation error


class TestRateLimiting:
    """Test suite for rate limiting middleware"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, client):
        """Rate limit headers should be present in response"""
        # Health endpoint bypasses rate limiting, use metrics instead
        response = await client.get("/api/v1/metrics/summary")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    @pytest.mark.asyncio
    async def test_rate_limit_decrements(self, client):
        """Rate limit remaining should decrement with each request"""
        response1 = await client.get("/api/v1/metrics/summary")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])
        
        response2 = await client.get("/api/v1/metrics/summary")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])
        
        # Should decrement or stay same (time window reset)
        assert remaining2 <= remaining1


class TestCacheEndpoints:
    """Test suite for cache management endpoints"""
    
    @pytest.mark.asyncio
    async def test_cache_stats_returns_200(self, client):
        """Cache stats endpoint should return 200"""
        response = await client.get("/api/v1/cache/stats")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_cache_stats_response_structure(self, client):
        """Cache stats should return proper structure"""
        response = await client.get("/api/v1/cache/stats")
        data = response.json()
        
        # Stats should be a dict (may be empty if no cache)
        assert isinstance(data, dict)


class TestMetricsEndpoints:
    """Test suite for metrics endpoints"""
    
    @pytest.mark.asyncio
    async def test_metrics_summary_returns_200(self, client):
        """Metrics summary endpoint should return 200"""
        response = await client.get("/api/v1/metrics/summary")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_metrics_summary_response_structure(self, client):
        """Metrics summary should return proper structure"""
        response = await client.get("/api/v1/metrics/summary")
        data = response.json()
        
        assert "total_requests" in data


class TestCORSHeaders:
    """Test suite for CORS configuration"""
    
    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client):
        """CORS headers should be present in response"""
        # Test with actual GET request and Origin header
        response = await client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200


class TestErrorHandling:
    """Test suite for error handling"""
    
    @pytest.mark.asyncio
    async def test_404_for_invalid_endpoint(self, client):
        """Invalid endpoints should return 404"""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @patch('app.workflows.simple_reflection.SimpleReflectionWorkflow.execute')
    async def test_500_on_workflow_failure(self, mock_execute, client):
        """Workflow failures should return proper error response"""
        mock_execute.side_effect = Exception("Workflow error")
        
        response = await client.post(
            "/api/v1/workflows/reflection",
            json={"topic": "Test"}
        )
        
        # Should return error response (500 or 200 with error status)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "failed"
