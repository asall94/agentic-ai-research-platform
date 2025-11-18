from .base_agent import BaseAgent
from openai import OpenAI
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent for conducting research with tools (from Q3/Q5)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 1.0):
        super().__init__(model, temperature)
        self.client = OpenAI()
    
    async def execute(self, task: str, tools: list = None, **kwargs) -> str:
        """Execute research task using available tools"""
        
        if tools is None:
            from app.tools import arxiv_search_tool, tavily_search_tool, wikipedia_search_tool
            tools = [arxiv_search_tool, tavily_search_tool, wikipedia_search_tool]
        
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_turns=6
            )
            
            result = response.choices[0].message.content
            self.log_execution(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Research agent error: {e}")
            raise
