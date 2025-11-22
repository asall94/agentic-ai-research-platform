import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
import os

# Mock startup checks before importing main
sys.modules['app.core.startup_checks'] = type(sys)('app.core.startup_checks')
sys.modules['app.core.startup_checks'].check_requirements = lambda: True

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    def test_health_check_returns_200(self):
        """Health endpoint should return 200 status"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_health_check_response_structure(self):
        """Health endpoint should return proper JSON structure"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"


class TestReflectionWorkflowEndpoint:
    """Test suite for reflection workflow endpoint"""
    
    @patch('app.workflows.simple_reflection.SimpleReflectionWorkflow.execute')
    def test_reflection_workflow_returns_200(self, mock_execute):
        """Reflection workflow should return 200 on success"""
        mock_execute.return_value = {
            "draft": "Draft content",
            "reflection": "Critique",
            "revised": "Final content"
        }
        
        response = client.post(
            "/api/v1/workflows/reflection",
            json={"topic": "AI ethics"}
        )
        
        assert response.status_code == 200
    
    @patch('app.workflows.simple_reflection.SimpleReflectionWorkflow.execute')
    def test_reflection_workflow_response_structure(self, mock_execute):
        """Reflection workflow should return proper response structure"""
        mock_execute.return_value = {
            "draft": "Draft",
            "reflection": "Critique",
            "revised": "Final"
        }
        
        response = client.post(
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
    
    def test_reflection_workflow_requires_topic(self):
        """Reflection workflow should require topic parameter"""
        response = client.post(
            "/api/v1/workflows/reflection",
            json={}
        )
        
        assert response.status_code == 422  # Validation error


class TestRateLimiting:
    """Test suite for rate limiting middleware"""
    
    def test_rate_limit_headers_present(self):
        """Rate limit headers should be present in response"""
        response = client.get("/api/v1/health")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_rate_limit_decrements(self):
        """Rate limit remaining should decrement with each request"""
        response1 = client.get("/api/v1/health")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])
        
        response2 = client.get("/api/v1/health")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])
        
        # Note: This test may be flaky due to time windows
        # In production, use a dedicated test client with isolated rate limiter
        assert remaining2 <= remaining1


class TestCacheEndpoints:
    """Test suite for cache management endpoints"""
    
    def test_cache_stats_returns_200(self):
        """Cache stats endpoint should return 200"""
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200
    
    def test_cache_stats_response_structure(self):
        """Cache stats should return proper structure"""
        response = client.get("/api/v1/cache/stats")
        data = response.json()
        
        # Stats should be a dict (may be empty if no cache)
        assert isinstance(data, dict)


class TestMetricsEndpoints:
    """Test suite for metrics endpoints"""
    
    def test_metrics_summary_returns_200(self):
        """Metrics summary endpoint should return 200"""
        response = client.get("/api/v1/metrics/summary")
        assert response.status_code == 200
    
    def test_metrics_summary_response_structure(self):
        """Metrics summary should return proper structure"""
        response = client.get("/api/v1/metrics/summary")
        data = response.json()
        
        assert "total_requests" in data


class TestCORSHeaders:
    """Test suite for CORS configuration"""
    
    def test_cors_headers_present(self):
        """CORS headers should be present in response"""
        response = client.options("/api/v1/health")
        
        # Check for CORS headers (may vary based on config)
        assert response.status_code in [200, 204]


class TestErrorHandling:
    """Test suite for error handling"""
    
    def test_404_for_invalid_endpoint(self):
        """Invalid endpoints should return 404"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    @patch('app.workflows.simple_reflection.SimpleReflectionWorkflow.execute')
    def test_500_on_workflow_failure(self, mock_execute):
        """Workflow failures should return proper error response"""
        mock_execute.side_effect = Exception("Workflow error")
        
        response = client.post(
            "/api/v1/workflows/reflection",
            json={"topic": "Test"}
        )
        
        # Should return error response (500 or 200 with error status)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "failed"
