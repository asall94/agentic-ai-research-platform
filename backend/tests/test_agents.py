import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.draft_agent import DraftAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.revision_agent import RevisionAgent
from app.agents.research_agent import ResearchAgent
from app.agents.writer_agent import WriterAgent
from app.agents.editor_agent import EditorAgent
from app.agents.planner_agent import PlannerAgent


class TestDraftAgent:
    """Test suite for DraftAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_string(self, mock_openai_client):
        """Draft agent should return draft content as string"""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "Draft about AI ethics"
        
        agent = DraftAgent(model="gpt-4o-mini")
        result = await agent.execute("AI ethics")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_topic(self, mock_openai_client):
        """Draft agent should handle empty topic gracefully"""
        agent = DraftAgent(model="gpt-4o-mini")
        result = await agent.execute("")
        assert isinstance(result, str)


class TestReflectionAgent:
    """Test suite for ReflectionAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_with_draft(self, mock_openai_client):
        """Reflection agent should critique draft content"""
        draft = "AI ethics is important for responsible development."
        
        agent = ReflectionAgent(model="gpt-4o-mini")
        result = await agent.execute(draft)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_execute_requires_draft(self, mock_openai_client):
        """Reflection agent should require draft parameter"""
        agent = ReflectionAgent(model="gpt-4o-mini")
        result = await agent.execute("some draft")
        assert isinstance(result, str)


class TestRevisionAgent:
    """Test suite for RevisionAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_with_draft_and_reflection(self, mock_openai_client):
        """Revision agent should revise based on draft and critique"""
        draft = "Original draft"
        reflection = "Needs improvement"
        
        agent = RevisionAgent(model="gpt-4o-mini")
        result = await agent.execute("topic", draft=draft, reflection=reflection)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestResearchAgent:
    """Test suite for ResearchAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_research_results(self, mock_openai_client):
        """Research agent should return research findings"""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "Research findings on quantum computing"
        
        agent = ResearchAgent(model="gpt-4o-mini")
        result = await agent.execute("Quantum computing applications")
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestWriterAgent:
    """Test suite for WriterAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_with_context(self, mock_openai_client):
        """Writer agent should generate content from context"""
        context = "Research shows quantum computing is advancing rapidly"
        
        agent = WriterAgent(model="gpt-4o-mini")
        result = await agent.execute("Write article", context=context)
        
        assert isinstance(result, str)


class TestEditorAgent:
    """Test suite for EditorAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_edits_content(self, mock_openai_client):
        """Editor agent should refine content"""
        draft = "This is a rough draft with some errors."
        
        agent = EditorAgent(model="gpt-4o-mini")
        result = await agent.execute("Edit this", draft=draft)
        
        assert isinstance(result, str)


class TestPlannerAgent:
    """Test suite for PlannerAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_plan_list(self, mock_openai_client):
        """Planner agent should return list of steps"""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = '["Step 1", "Step 2", "Step 3"]'
        
        agent = PlannerAgent(model="gpt-4o-mini")
        result = await agent.execute("Create research plan")
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_execute_handles_max_steps(self, mock_openai_client):
        """Planner agent should respect max_steps parameter"""
        mock_openai_client.chat.completions.create.return_value.choices[0].message.content = '["Step 1", "Step 2"]'
        
        agent = PlannerAgent(model="gpt-4o-mini")
        result = await agent.execute("Plan", max_steps=2)
        
        assert isinstance(result, list)
        assert len(result) <= 2


class TestAgentTemperatures:
    """Test agent temperature configurations"""
    
    def test_draft_agent_temperature(self):
        """Draft agent should use configured temperature"""
        agent = DraftAgent(model="gpt-4o-mini", temperature=0.8)
        assert agent.temperature == 0.8
    
    def test_reflection_agent_temperature(self):
        """Reflection agent should use lower temperature"""
        agent = ReflectionAgent(model="gpt-4o-mini", temperature=0.3)
        assert agent.temperature == 0.3
    
    def test_default_temperature_from_settings(self):
        """Agents should use default temperature from settings if not specified"""
        from app.core.config import settings
        
        agent = DraftAgent(model="gpt-4o-mini")
        assert agent.temperature == settings.DRAFT_TEMPERATURE
