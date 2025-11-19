from .base_agent import BaseAgent
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RevisionAgent(BaseAgent):
    """Agent for revising drafts based on feedback (from Q2)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = None):
        super().__init__(model, temperature or settings.REVISION_TEMPERATURE)
        self.client = OpenAI()
    
    async def execute(self, original_draft: str, reflection: str, **kwargs) -> str:
        """Revise a draft based on feedback"""
        
        prompt = f"""You are an expert essay writer tasked with revising an essay based on constructive feedback.

Original Essay Draft:
{original_draft}

Feedback and Critique:
{reflection}

Your task is to rewrite the essay, incorporating all the feedback provided above. Ensure that you:

1. **Address all issues** mentioned in the feedback
2. **Improve structure and organization** where needed
3. **Enhance clarity and coherence** of arguments
4. **Strengthen the thesis and supporting evidence**
5. **Refine writing style** for better flow and readability
6. **Fix any grammatical or stylistic issues** identified
7. **Maintain the original topic and intent** while improving quality

Write the complete revised essay now. Output only the final revised essay, without any meta-commentary or explanations."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            
            result = response.choices[0].message.content
            self.log_execution("Revision of draft", result)
            return result
            
        except Exception as e:
            logger.error(f"Revision agent error: {e}")
            raise
