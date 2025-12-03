"""
End-to-End tests for workflows with real OpenAI API calls
Run with: pytest tests/test_e2e_workflows.py -v -s --e2e
"""
import pytest
import os
from app.workflows.simple_reflection import SimpleReflectionWorkflow
from app.workflows.tool_research import ToolResearchWorkflow
from app.workflows.multi_agent import MultiAgentWorkflow


@pytest.fixture(scope="module")
def check_openai_key():
    """Verify OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-proj-"):
        pytest.skip("OpenAI API key not configured or invalid")
    return api_key


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_reflection_workflow_real_execution(check_openai_key):
    """Test reflection workflow with real OpenAI API"""
    workflow = SimpleReflectionWorkflow(
        draft_model="gpt-4o-mini",
        reflection_model="gpt-4o-mini", 
        revision_model="gpt-4o-mini"
    )
    
    topic = "Should social media platforms moderate political content?"
    result = await workflow.execute(topic)
    
    # Structure validation
    assert isinstance(result, dict)
    assert "draft" in result
    assert "reflection" in result
    assert "revised" in result
    
    # Content validation
    assert len(result["draft"]) > 100, "Draft too short"
    assert len(result["reflection"]) > 50, "Reflection too short"
    assert len(result["revised"]) > 100, "Revision too short"
    
    # Topic relevance check (basic keyword matching)
    topic_keywords = ["social media", "moderate", "political", "content"]
    draft_lower = result["draft"].lower()
    matches = sum(1 for kw in topic_keywords if kw in draft_lower)
    assert matches >= 2, f"Draft not relevant to topic (only {matches}/4 keywords found)"
    
    print(f"\nReflection Workflow Results:")
    print(f"Draft length: {len(result['draft'])} chars")
    print(f"Reflection length: {len(result['reflection'])} chars")
    print(f"Revised length: {len(result['revised'])} chars")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_tool_research_workflow_real_execution(check_openai_key):
    """Test tool research workflow with real tools"""
    workflow = ToolResearchWorkflow(
        research_model="gpt-4o-mini"
    )
    
    topic = "Recent advances in quantum computing"
    tools = ["arxiv", "wikipedia"]
    
    result = await workflow.execute(topic, tools=tools)
    
    # Structure validation
    assert isinstance(result, dict)
    assert "research_report" in result
    
    # Content validation
    report = result["research_report"]
    assert len(report) > 200, "Research report too short"
    
    # Tool usage verification
    report_lower = report.lower()
    assert "quantum" in report_lower, "Research doesn't mention quantum"
    
    print(f"\nTool Research Results:")
    print(f"Report length: {len(report)} chars")
    print(f"First 200 chars: {report[:200]}...")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_agent_workflow_real_execution(check_openai_key):
    """Test multi-agent workflow with real agents"""
    workflow = MultiAgentWorkflow(
        planner_model="gpt-4o-mini",
        research_model="gpt-4o-mini",
        writer_model="gpt-4o-mini",
        editor_model="gpt-4o-mini"
    )
    
    topic = "Benefits and risks of gene editing"
    
    result = await workflow.execute(topic, max_steps=3)
    
    # Structure validation
    assert isinstance(result, dict)
    assert "plan" in result
    assert "history" in result
    assert "final_report" in result
    
    # Plan validation
    assert isinstance(result["plan"], list)
    assert len(result["plan"]) > 0, "No plan steps generated"
    
    # History validation
    assert isinstance(result["history"], list)
    assert len(result["history"]) <= 3, "Too many execution steps"
    
    # Final report validation
    assert len(result["final_report"]) > 200, "Final report too short"
    
    print(f"\nMulti-Agent Results:")
    print(f"Plan steps: {len(result['plan'])}")
    print(f"Execution history: {len(result['history'])} steps")
    print(f"Final report length: {len(result['final_report'])} chars")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_cache_workflow_semantic_matching(check_openai_key):
    """Test semantic cache hit on similar queries"""
    from app.services.cache_service import cache_service
    
    if not cache_service.enabled:
        pytest.skip("Cache not enabled")
    
    workflow = SimpleReflectionWorkflow()
    
    # First execution - should cache
    topic1 = "What are the benefits of renewable energy?"
    result1 = await workflow.execute(topic1)
    cache_service.store_result(topic1, "reflection", result1)
    
    # Similar query - should hit cache (similarity > 0.95)
    topic2 = "What are the advantages of renewable energy sources?"
    cached = cache_service.get_cached_result(topic2, "reflection")
    
    assert cached is not None, "Similar query should hit cache"
    assert cached["draft"] == result1["draft"], "Cached content should match"
    
    print(f"\nCache semantic matching works!")
    print(f"Original: '{topic1}'")
    print(f"Similar: '{topic2}'")
    print(f"Cache hit: YES")


@pytest.mark.e2e  
@pytest.mark.asyncio
async def test_workflow_quality_comparative():
    """Compare outputs from different workflows on same topic"""
    topic = "Impact of artificial intelligence on employment"
    
    # Run all three workflows
    reflection = SimpleReflectionWorkflow()
    research = ToolResearchWorkflow()
    multi_agent = MultiAgentWorkflow()
    
    r1 = await reflection.execute(topic)
    r2 = await research.execute(topic, tools=["wikipedia"])
    r3 = await multi_agent.execute(topic, max_steps=2)
    
    # All should produce different content
    assert r1["revised"] != r2["research_report"], "Reflection and Research outputs identical"
    assert r1["revised"] != r3["final_report"], "Reflection and Multi-Agent outputs identical"
    
    # All should be substantial
    assert len(r1["revised"]) > 150
    assert len(r2["research_report"]) > 150
    assert len(r3["final_report"]) > 150
    
    print(f"\nComparative Quality Test:")
    print(f"Reflection output: {len(r1['revised'])} chars")
    print(f"Research output: {len(r2['research_report'])} chars")
    print(f"Multi-Agent output: {len(r3['final_report'])} chars")
