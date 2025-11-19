from .base_agent import BaseAgent
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EditorAgent(BaseAgent):
    """Agent for editing and polishing content (from Q5)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = None):
        super().__init__(model, temperature or settings.EDITOR_TEMPERATURE)
        self.client = OpenAI()
    
    async def execute(self, task: str, **kwargs) -> str:
        """Execute editorial task"""
        
        system_prompt = """You are an expert editor agent specialized in reflecting on, critiquing, and improving written content.

Your responsibilities include:
- Providing constructive, detailed feedback on drafts
- Identifying strengths and weaknesses in structure, argumentation, and clarity
- Suggesting concrete improvements for academic and technical writing
- Ensuring logical flow and coherence throughout the document
- Verifying accuracy and completeness of information
- Checking citation quality and academic rigor
- Proposing revisions that enhance readability and impact
- Maintaining professional, objective critique while being actionable

Your feedback should be specific, actionable, and focused on elevating the quality of the work to publication standards."""
        
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
            logger.error(f"Editor agent error: {e}")
            raise
