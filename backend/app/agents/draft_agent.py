from .base_agent import BaseAgent
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DraftAgent(BaseAgent):
    """Agent for generating initial drafts (from Q2)"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = None):
        super().__init__(model, temperature or settings.DRAFT_TEMPERATURE)
        self.client = OpenAI()
    
    async def execute(self, topic: str, **kwargs) -> str:
        """Generate a draft essay on the given topic"""
        
        prompt = f"""You are an expert essay writer. Write a complete, well-structured essay on the following topic:

Topic: {topic}

Your essay should:
- Have a clear introduction with a thesis statement
- Include 3-4 body paragraphs with supporting arguments and evidence
- Conclude with a summary and final thoughts
- Be approximately 500-700 words
- Use formal academic tone
- **Respond in the same language as the topic** (if topic is in French, respond in French; if in English, respond in English, etc.)

Write the complete essay now."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            
            result = response.choices[0].message.content
            self.log_execution(topic, result)
            return result
            
        except Exception as e:
            logger.error(f"Draft agent error: {e}")
            raise
