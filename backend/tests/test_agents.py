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
    async def test_execute_returns_string(self):
        """Draft agent should return draft content as string"""
        agent = DraftAgent(model="gpt-4o-mini")
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Draft about AI ethics"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("AI ethics")
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_topic(self):
        """Draft agent should handle empty topic gracefully"""
        agent = DraftAgent(model="gpt-4o-mini")
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Please provide a topic"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("")
            assert isinstance(result, str)


class TestReflectionAgent:
    """Test suite for ReflectionAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_with_draft(self):
        """Reflection agent should critique draft content"""
        agent = ReflectionAgent(model="gpt-4o-mini")
        draft = "AI ethics is important for responsible development."
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Critique: Needs more depth"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("AI ethics", draft=draft)
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_execute_requires_draft(self):
        """Reflection agent should require draft parameter"""
        agent = ReflectionAgent(model="gpt-4o-mini")
        
        # Should work with draft
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Critique"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("topic", draft="some draft")
            assert isinstance(result, str)


class TestRevisionAgent:
    """Test suite for RevisionAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_with_draft_and_reflection(self):
        """Revision agent should revise based on draft and critique"""
        agent = RevisionAgent(model="gpt-4o-mini")
        draft = "Original draft"
        reflection = "Needs improvement"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Improved draft"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("topic", draft=draft, reflection=reflection)
            
            assert isinstance(result, str)
            assert len(result) > 0


class TestResearchAgent:
    """Test suite for ResearchAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_research_results(self):
        """Research agent should return research findings"""
        agent = ResearchAgent(model="gpt-4o-mini")
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Research findings on quantum computing"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("Quantum computing applications")
            
            assert isinstance(result, str)
            assert len(result) > 0


class TestWriterAgent:
    """Test suite for WriterAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_with_context(self):
        """Writer agent should generate content from context"""
        agent = WriterAgent(model="gpt-4o-mini")
        context = "Research shows quantum computing is advancing rapidly"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Article about quantum computing"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("Write article", context=context)
            
            assert isinstance(result, str)


class TestEditorAgent:
    """Test suite for EditorAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_edits_content(self):
        """Editor agent should refine content"""
        agent = EditorAgent(model="gpt-4o-mini")
        draft = "This is a rough draft with some errors."
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="This is a polished draft."))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("Edit this", draft=draft)
            
            assert isinstance(result, str)


class TestPlannerAgent:
    """Test suite for PlannerAgent"""
    
    @pytest.mark.asyncio
    async def test_execute_returns_plan_list(self):
        """Planner agent should return list of steps"""
        agent = PlannerAgent(model="gpt-4o-mini")
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='["Step 1", "Step 2", "Step 3"]'))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await agent.execute("Create research plan")
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_execute_handles_max_steps(self):
        """Planner agent should respect max_steps parameter"""
        agent = PlannerAgent(model="gpt-4o-mini")
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='["Step 1", "Step 2"]'))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
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
