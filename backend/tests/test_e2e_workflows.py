"""
End-to-End tests for workflows with real OpenAI API calls
Run with: pytest tests/test_e2e_workflows.py -v -s --e2e
"""
import pytest
import os
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
async def test_workflow_quality_comparative():
    """Compare outputs from different workflows on same topic"""
    topic = "Impact of artificial intelligence on employment"
    
    research = ToolResearchWorkflow()
    multi_agent = MultiAgentWorkflow()
    
    r2 = await research.execute(topic, tools=["wikipedia"])
    r3 = await multi_agent.execute(topic, max_steps=2)
    
    # Outputs should differ
    assert r2["research_report"] != r3["final_report"], "Research and Multi-Agent outputs identical"
    
    # All should be substantial
    assert len(r2["research_report"]) > 150
    assert len(r3["final_report"]) > 150
    
    print(f"\nComparative Quality Test:")
    print(f"Research output: {len(r2['research_report'])} chars")
    print(f"Multi-Agent output: {len(r3['final_report'])} chars")
