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
    
    async def execute(self, task: str, tools: list = None, tool_func_mapping: dict = None, **kwargs) -> str:
        """Execute research task using available tools with full execution support"""
        
        # Setup tools and functions
        if tools is None:
            from app.tools.arxiv_tool import arxiv_tool_def, arxiv_search_tool
            from app.tools.tavily_tool import tavily_tool_def, tavily_search_tool
            from app.tools.wikipedia_tool import wikipedia_tool_def, wikipedia_search_tool
            
            tools = [arxiv_tool_def, tavily_tool_def, wikipedia_tool_def]
            tool_func_mapping = {
                "arxiv_search_tool": arxiv_search_tool,
                "tavily_search_tool": tavily_search_tool,
                "wikipedia_search_tool": wikipedia_search_tool
            }
        
        # Allow empty tools list for testing
        if tools == []:
            tools = None
            tool_func_mapping = None
        
        current_time = datetime.now().strftime('%Y-%m-%d')
        
        prompt = f"""You are an expert research assistant with access to multiple research tools.

Available Tools:
- arxiv_search_tool: Search academic papers and preprints from arXiv
- tavily_search_tool: Perform general web searches for recent information
- wikipedia_search_tool: Access encyclopedic knowledge and summaries

Current Date: {current_time}

Task: {task}

Instructions:
- Use the appropriate tools to gather comprehensive information
- Synthesize findings from multiple sources when relevant
- Provide accurate, well-sourced responses
- Include citations and references when available
- Be thorough and academic in your research approach
- **CRITICAL: Respond in the SAME LANGUAGE as the task** (French task → French response, English task → English response, etc.)"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # First API call - may return tool_calls
            kwargs_api = {
                "model": self.model,
                "messages": messages
            }
            if tools:
                kwargs_api["tools"] = tools
                kwargs_api["tool_choice"] = "auto"
            
            # Get initial response
            response = self.client.chat.completions.create(**kwargs_api)
            message = response.choices[0].message
            
            # If tools were used, need to execute them manually (SDK doesn't auto-execute)
            if tools and hasattr(message, 'tool_calls') and message.tool_calls:
                # Execute tools and continue conversation
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    if func_name in tool_func_mapping:
                        tool_result = tool_func_mapping[func_name](**func_args)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)
                        })
                
                # Get final response after tool execution
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                result = final_response.choices[0].message.content
            else:
                result = message.content
            
            self.log_execution(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Research agent error: {e}")
            raise

