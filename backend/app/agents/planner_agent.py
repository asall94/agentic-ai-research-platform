from .base_agent import BaseAgent
from openai import OpenAI
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Agent for creating plans (from Q5)"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = None):
        super().__init__(model, temperature or settings.PLANNER_TEMPERATURE)
        self.client = OpenAI()
    
    async def execute(self, topic: str, **kwargs) -> list:
        """Generate a research plan as a list of steps"""
        
        user_prompt = f"""
You are a planning agent responsible for organizing a research workflow with multiple intelligent agents.

🧠 Available agents:
- A research agent who can search the web, Wikipedia, and arXiv.
- A writer agent who can draft research summaries.
- An editor agent who can reflect and revise the drafts.

🎯 Your job is to write a clear, step-by-step research plan **as a valid Python list**, where each step is a string.
Each step should be atomic, executable, and must rely only on the capabilities of the above agents.

🚫 DO NOT include irrelevant tasks like "create CSV", "set up a repo", "install packages", etc.
✅ DO include real research-related tasks (e.g., search, summarize, draft, revise).
✅ DO assume tool use is available.
✅ DO NOT include explanation text — return ONLY the Python list.
✅ The final step should be to generate a Markdown document containing the complete research report.

Topic: "{topic}"
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=self.temperature,
            )
            
            steps_str = response.choices[0].message.content.strip()
            steps = ast.literal_eval(steps_str)
            
            self.log_execution(topic, f"Generated {len(steps)} steps")
            return steps
            
        except Exception as e:
            logger.error(f"Planner agent error: {e}")
            raise
