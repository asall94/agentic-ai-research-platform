"""
DeepEval quality metrics for workflow outputs
Run: pytest tests/test_deepeval_quality.py -v -s --deepeval
"""
import pytest
import os
from deepeval import assert_test
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from app.workflows.simple_reflection import SimpleReflectionWorkflow
from app.workflows.tool_research import ToolResearchWorkflow
from app.workflows.multi_agent import MultiAgentWorkflow


@pytest.fixture(scope="module")
def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not configured")


# Custom GEval metrics for our workflows
coherence_metric = GEval(
    name="Coherence",
    criteria="Determine if the output is logically structured and easy to follow",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.6
)

depth_metric = GEval(
    name="Analytical Depth",
    criteria="Assess if the analysis goes beyond surface-level observations with specific examples",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.5
)

improvement_metric = GEval(
    name="Revision Improvement",
    criteria="Evaluate if the revised version addresses critiques and improves upon the draft",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.6
)


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_reflection_workflow_coherence(check_api_key):
    """Test if reflection workflow produces coherent output"""
    workflow = SimpleReflectionWorkflow()
    topic = "Should governments regulate cryptocurrency markets?"
    
    result = await workflow.execute(topic)
    
    test_case = LLMTestCase(
        input=topic,
        actual_output=result["revised"]
    )
    
    assert_test(test_case, [coherence_metric])


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_reflection_workflow_relevance(check_api_key):
    """Test answer relevancy to input topic"""
    workflow = SimpleReflectionWorkflow()
    topic = "Benefits of remote work for tech companies"
    
    result = await workflow.execute(topic)
    
    relevancy = AnswerRelevancyMetric(threshold=0.7)
    
    test_case = LLMTestCase(
        input=topic,
        actual_output=result["revised"]
    )
    
    assert_test(test_case, [relevancy])


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_reflection_improves_draft(check_api_key):
    """Test if revision actually improves based on reflection"""
    workflow = SimpleReflectionWorkflow()
    topic = "Impact of social media on mental health"
    
    result = await workflow.execute(topic)
    
    test_case = LLMTestCase(
        input=f"Draft: {result['draft']}\nCritique: {result['reflection']}",
        actual_output=result["revised"]
    )
    
    assert_test(test_case, [improvement_metric])


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_tool_research_faithfulness(check_api_key):
    """Test if research output is faithful to retrieved sources"""
    workflow = ToolResearchWorkflow(tools=["arxiv", "wikipedia"])
    topic = "Latest developments in quantum computing"
    
    result = await workflow.execute(topic)
    
    # DeepEval faithfulness requires context (retrieved docs)
    # Mock context for test - in real scenario, capture tool outputs
    mock_context = [
        "Quantum computers use qubits which can be in superposition",
        "Recent advances include error correction and topological qubits"
    ]
    
    faithfulness = FaithfulnessMetric(threshold=0.5)
    
    test_case = LLMTestCase(
        input=topic,
        actual_output=result["research_report"],
        retrieval_context=mock_context
    )
    
    assert_test(test_case, [faithfulness])


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_tool_research_no_hallucination(check_api_key):
    """Test research output for hallucinations"""
    workflow = ToolResearchWorkflow(tools=["wikipedia"])
    topic = "History of the Python programming language"
    
    result = await workflow.execute(topic)
    
    # Context should come from actual tool execution
    mock_context = [
        "Python was created by Guido van Rossum in 1991",
        "Python emphasizes code readability with significant whitespace"
    ]
    
    hallucination = HallucinationMetric(threshold=0.5)
    
    test_case = LLMTestCase(
        input=topic,
        actual_output=result["research_report"],
        context=mock_context
    )
    
    assert_test(test_case, [hallucination])


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_multi_agent_analytical_depth(check_api_key):
    """Test if multi-agent output has analytical depth"""
    workflow = MultiAgentWorkflow(max_steps=3)
    topic = "Ethical implications of AI in healthcare"
    
    result = await workflow.execute(topic)
    
    test_case = LLMTestCase(
        input=topic,
        actual_output=result["final_report"]
    )
    
    assert_test(test_case, [depth_metric, coherence_metric])


@pytest.mark.deepeval
@pytest.mark.asyncio
async def test_multi_agent_plan_quality(check_api_key):
    """Test quality of planner's execution plan"""
    workflow = MultiAgentWorkflow(max_steps=2)
    topic = "Future of renewable energy"
    
    result = await workflow.execute(topic)
    
    plan_quality = GEval(
        name="Plan Quality",
        criteria="Evaluate if the plan breaks down the research into logical, actionable steps",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.6
    )
    
    plan_text = "\n".join(result["plan"])
    
    test_case = LLMTestCase(
        input=topic,
        actual_output=plan_text
    )
    
    assert_test(test_case, [plan_quality])


@pytest.mark.deepeval
@pytest.mark.asyncio  
async def test_comparative_workflow_quality(check_api_key):
    """Compare quality across all three workflows on same topic"""
    topic = "Challenges of space exploration"
    
    reflection_wf = SimpleReflectionWorkflow()
    research_wf = ToolResearchWorkflow(tools=["wikipedia"])
    multi_wf = MultiAgentWorkflow(max_steps=2)
    
    r1 = await reflection_wf.execute(topic)
    r2 = await research_wf.execute(topic)
    r3 = await multi_wf.execute(topic)
    
    relevancy = AnswerRelevancyMetric(threshold=0.6)
    
    # Test all three outputs
    for name, output in [
        ("Reflection", r1["revised"]),
        ("Research", r2["research_report"]),
        ("Multi-Agent", r3["final_report"])
    ]:
        test_case = LLMTestCase(input=topic, actual_output=output)
        print(f"\nTesting {name} workflow...")
        assert_test(test_case, [relevancy])
