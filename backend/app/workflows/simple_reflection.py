from app.agents import DraftAgent, ReflectionAgent, RevisionAgent
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SimpleReflectionWorkflow:
    """Simple reflection workflow (Q2): Draft → Critique → Revision"""
    
    def __init__(
        self,
        draft_model: str = None,
        reflection_model: str = None,
        revision_model: str = None
    ):
        self.draft_agent = DraftAgent(
            model=draft_model or settings.DEFAULT_DRAFT_MODEL
        )
        self.reflection_agent = ReflectionAgent(
            model=reflection_model or settings.DEFAULT_REFLECTION_MODEL
        )
        self.revision_agent = RevisionAgent(
            model=revision_model or settings.DEFAULT_DRAFT_MODEL
        )
    
    async def execute(self, topic: str) -> dict:
        """Execute the reflection workflow"""
        
        logger.info(f"Starting simple reflection workflow for: {topic}")
        
        # Step 1: Generate draft
        logger.info("Step 1: Generating draft...")
        draft = await self.draft_agent.execute(topic)
        
        # Step 2: Reflect on draft
        logger.info("Step 2: Reflecting on draft...")
        reflection = await self.reflection_agent.execute(draft)
        
        # Step 3: Revise based on feedback
        logger.info("Step 3: Revising draft...")
        revised = await self.revision_agent.execute(draft, reflection)
        
        logger.info("Simple reflection workflow completed")
        
        return {
            "draft": draft,
            "reflection": reflection,
            "revised": revised
        }
