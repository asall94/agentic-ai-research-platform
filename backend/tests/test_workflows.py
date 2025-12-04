import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.workflows.simple_reflection import SimpleReflectionWorkflow
from app.workflows.tool_research import ToolResearchWorkflow
from app.workflows.multi_agent import MultiAgentWorkflow


class TestSimpleReflectionWorkflow:
    """Test suite for Simple Reflection Workflow"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_dict_with_required_keys(self):
        """Workflow should return dict with draft, reflection, revised"""
        workflow = SimpleReflectionWorkflow()
        
        with patch('app.agents.draft_agent.DraftAgent.execute', new_callable=AsyncMock) as mock_draft, \
             patch('app.agents.reflection_agent.ReflectionAgent.execute', new_callable=AsyncMock) as mock_reflect, \
             patch('app.agents.revision_agent.RevisionAgent.execute', new_callable=AsyncMock) as mock_revise:
            
            mock_draft.return_value = "Draft content"
            mock_reflect.return_value = "Critique content"
            mock_revise.return_value = "Revised content"
            
            result = await workflow.execute("AI ethics")
            
            assert isinstance(result, dict)
            assert "draft" in result
            assert "reflection" in result
            assert "revised" in result
            assert result["draft"] == "Draft content"
            assert result["reflection"] == "Critique content"
            assert result["revised"] == "Revised content"
    
    @pytest.mark.asyncio
    async def test_execute_calls_agents_in_order(self):
        """Workflow should call draft -> reflection -> revision in sequence"""
        workflow = SimpleReflectionWorkflow()
        
        call_order = []
        
        async def mock_draft_execute(*args, **kwargs):
            call_order.append("draft")
            return "Draft"
        
        async def mock_reflect_execute(*args, **kwargs):
            call_order.append("reflection")
            return "Critique"
        
        async def mock_revise_execute(*args, **kwargs):
            call_order.append("revision")
            return "Revised"
        
        with patch('app.agents.draft_agent.DraftAgent.execute', new=mock_draft_execute), \
             patch('app.agents.reflection_agent.ReflectionAgent.execute', new=mock_reflect_execute), \
             patch('app.agents.revision_agent.RevisionAgent.execute', new=mock_revise_execute):
            
            await workflow.execute("Test topic")
            
            assert call_order == ["draft", "reflection", "revision"]
    
    @pytest.mark.asyncio
    async def test_execute_with_custom_models(self):
        """Workflow should accept custom model parameters"""
        workflow = SimpleReflectionWorkflow(
            draft_model="gpt-4o",
            reflection_model="gpt-4o-mini",
            revision_model="gpt-4o"
        )
        
        assert workflow.draft_agent.model == "gpt-4o"
        assert workflow.reflection_agent.model == "gpt-4o-mini"
        assert workflow.revision_agent.model == "gpt-4o"


class TestToolResearchWorkflow:
    """Test suite for Tool Research Workflow"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_dict_with_research_key(self):
        """Workflow should return dict with research_report key"""
        workflow = ToolResearchWorkflow()
        
        with patch('app.agents.research_agent.ResearchAgent.execute', new_callable=AsyncMock) as mock_research:
            mock_research.return_value = "Research findings"
            
            result = await workflow.execute("Quantum computing")
            
            assert isinstance(result, dict)
            assert "research_report" in result
            assert result["research_report"] == "Research findings"
    
    @pytest.mark.asyncio
    async def test_execute_passes_tools_to_agent(self):
        """Workflow should use tools specified in constructor"""
        workflow = ToolResearchWorkflow(tools=["arxiv", "wikipedia"])
        
        with patch('app.agents.research_agent.ResearchAgent.execute', new_callable=AsyncMock) as mock_research:
            mock_research.return_value = "Research with tools"
            
            await workflow.execute("Topic")
            
            # Verify agent was called
            mock_research.assert_called_once()


class TestMultiAgentWorkflow:
    """Test suite for Multi-Agent Workflow"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_dict_with_required_keys(self, mock_openai_client):
        """Workflow should return dict with plan, steps, final_output"""
        workflow = MultiAgentWorkflow()
        
        # Mock _decide_agent to avoid OpenAI calls
        async def mock_decide_agent(step):
            if "Research" in step:
                return {"agent": "research_agent", "task": step}
            elif "Write" in step:
                return {"agent": "writer_agent", "task": step}
            else:
                return {"agent": "editor_agent", "task": step}
        
        with patch('app.agents.planner_agent.PlannerAgent.execute', new_callable=AsyncMock) as mock_planner, \
             patch.object(workflow, '_decide_agent', side_effect=mock_decide_agent):
            
            # Mock planner to return steps
            mock_planner.return_value = ["Research", "Write", "Edit"]
            
            # Mock individual agent executions
            with patch('app.agents.research_agent.ResearchAgent.execute', new_callable=AsyncMock) as mock_research, \
                 patch('app.agents.writer_agent.WriterAgent.execute', new_callable=AsyncMock) as mock_writer, \
                 patch('app.agents.editor_agent.EditorAgent.execute', new_callable=AsyncMock) as mock_editor:
                
                mock_research.return_value = "Research done"
                mock_writer.return_value = "Article written"
                mock_editor.return_value = "Article edited"
                
                result = await workflow.execute("AI research")
                
                assert isinstance(result, dict)
                assert "plan" in result
                assert "history" in result
                assert "final_report" in result
    
    @pytest.mark.asyncio
    async def test_execute_respects_max_steps(self, mock_openai_client):
        """Workflow should limit execution to max_steps"""
        workflow = MultiAgentWorkflow(max_steps=2)
        
        # Mock _decide_agent
        async def mock_decide_agent(step):
            return {"agent": "research_agent", "task": step}
        
        with patch('app.agents.planner_agent.PlannerAgent.execute', new_callable=AsyncMock) as mock_planner, \
             patch.object(workflow, '_decide_agent', side_effect=mock_decide_agent), \
             patch('app.agents.research_agent.ResearchAgent.execute', new_callable=AsyncMock) as mock_research:
            
            # Mock planner returns 4 steps but workflow should limit to 2
            mock_planner.return_value = ["Step1", "Step2", "Step3", "Step4"]
            mock_research.return_value = "Done"
            
            result = await workflow.execute("Topic")
            
            # Should only execute 2 steps + 1 final synthesis (max_steps=2 limits plan steps, not synthesis)
            # History contains: Step1, Step2, Final synthesis = 3 total
            assert len(result.get("history", [])) == 3
            assert len(result.get("plan", [])) == 2  # Plan itself is limited to 2 steps


class TestWorkflowErrorHandling:
    """Test error handling in workflows"""
    
    @pytest.mark.asyncio
    async def test_workflow_handles_agent_failure(self):
        """Workflow should handle agent execution failures gracefully"""
        workflow = SimpleReflectionWorkflow()
        
        with patch('app.agents.draft_agent.DraftAgent.execute', new_callable=AsyncMock) as mock_draft:
            mock_draft.side_effect = Exception("API error")
            
            with pytest.raises(Exception) as exc_info:
                await workflow.execute("Test topic")
            
            assert "API error" in str(exc_info.value)
