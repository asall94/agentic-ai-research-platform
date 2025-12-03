from .base_agent import BaseAgent
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ReflectionAgent(BaseAgent):
    """Agent for reflecting on drafts (from Q2)"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = None):
        super().__init__(model, temperature or settings.REFLECTION_TEMPERATURE)
        self.client = OpenAI()
    
    async def execute(self, draft: str, **kwargs) -> str:
        """Provide constructive feedback on a draft"""
        
        prompt = f"""You are an expert essay editor and critic. Your task is to provide constructive, detailed feedback on the following essay draft.

Essay Draft:
{draft}

Please analyze this essay critically and provide feedback addressing the following aspects:

1. **Structure and Organization**: 
   - Is the essay well-organized with clear introduction, body, and conclusion?
   - Are transitions between paragraphs smooth and logical?
   - Does each paragraph focus on a single main idea?

2. **Clarity and Coherence**:
   - Is the writing clear and easy to understand?
   - Are there any confusing or ambiguous statements?
   - Does the argument flow logically from start to finish?

3. **Strength of Argument**:
   - Is the thesis statement clear and compelling?
   - Are the arguments well-supported with evidence or examples?
   - Are counterarguments addressed appropriately?
   - Is the reasoning sound and convincing?

4. **Writing Style and Quality**:
   - Is the tone appropriate for an academic essay?
   - Are there issues with grammar, vocabulary, or sentence structure?
   - Is the language precise and effective?
   - Are there any repetitive phrases or ideas?

5. **Overall Impression**:
   - What are the essay's main strengths?
   - What are the most important areas for improvement?

**IMPORTANT: Provide your feedback in the SAME LANGUAGE as the essay** (if essay is in French, respond in French; if in English, respond in English, etc.).

Provide your feedback in paragraph form, being critical but constructive. Focus on specific issues and suggest concrete improvements."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            
            result = response.choices[0].message.content
            self.log_execution("Reflection on draft", result)
            return result
            
        except Exception as e:
            logger.error(f"Reflection agent error: {e}")
            raise
