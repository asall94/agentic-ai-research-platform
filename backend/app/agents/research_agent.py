from .base_agent import BaseAgent
from openai import OpenAI
from app.core.config import settings
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent for conducting research with tools (from Q3/Q5)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = None):
        super().__init__(model, temperature or settings.RESEARCH_TEMPERATURE)
        self.client = OpenAI()
    
    async def execute(self, task: str, tools: list = None, **kwargs) -> str:
        """Execute research task using available tools"""
        
        if tools is None:
            from app.tools.arxiv_tool import arxiv_tool_def
            from app.tools.tavily_tool import tavily_tool_def
            from app.tools.wikipedia_tool import wikipedia_tool_def
            tools = [arxiv_tool_def, tavily_tool_def, wikipedia_tool_def]
        
        # Allow empty tools list for testing
        if tools == []:
            tools = None
        
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        prompt = f"""You are an expert research assistant with access to multiple research tools.

🔧 Available Tools:
- arxiv_search_tool: Search academic papers and preprints from arXiv
- tavily_search_tool: Perform general web searches for recent information
- wikipedia_search_tool: Access encyclopedic knowledge and summaries

📅 Current Date: {current_time}

🎯 Task: {task}

Instructions:
- Use the appropriate tools to gather comprehensive information
- Synthesize findings from multiple sources when relevant
- Provide accurate, well-sourced responses
- Include citations and references when available
- Be thorough and academic in your research approach"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": self.model,
                "messages": messages
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            # First response - may have tool calls
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            
            # If no tools or no tool calls, return content directly
            if not tools or not hasattr(message, 'tool_calls') or not message.tool_calls:
                result = message.content
                self.log_execution(task, result)
                return result
            
            # Handle tool calls - for now, return a summary since we can't execute them in streaming
            # In a real implementation, you'd execute the tools and continue the conversation
            result = f"Research agent attempted to use tools but tool execution is not yet implemented in streaming mode. Tool calls: {len(message.tool_calls)}"
            self.log_execution(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Research agent error: {e}")
            raise

