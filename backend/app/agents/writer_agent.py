from .base_agent import BaseAgent
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Agent for writing and drafting content (from Q5)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 1.0):
        super().__init__(model, temperature)
        self.client = OpenAI()
    
    async def execute(self, task: str, **kwargs) -> str:
        """Execute writing task"""
        
        system_prompt = """You are an expert writing agent specialized in generating well-structured academic and technical content.

Your capabilities include:
- Drafting comprehensive research reports and summaries
- Expanding outlines into detailed, well-argued content
- Summarizing complex information clearly and concisely
- Maintaining academic tone and rigorous methodology
- Organizing information with clear structure (introduction, body, conclusion)
- Incorporating citations and references appropriately
- Ensuring clarity, coherence, and logical flow

Always produce high-quality, publication-ready content that meets academic standards."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                temperature=self.temperature,
            )
            
            result = response.choices[0].message.content
            self.log_execution(task, result)
            return result
            
        except Exception as e:
            logger.error(f"Writer agent error: {e}")
            raise
