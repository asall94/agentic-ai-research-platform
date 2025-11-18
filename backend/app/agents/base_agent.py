from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def execute(self, task: str, **kwargs) -> str:
        """Execute the agent's task"""
        pass
    
    def log_execution(self, task: str, result: str):
        """Log agent execution"""
        self.logger.info(f"Executed task: {task[:100]}...")
        self.logger.debug(f"Result: {result[:200]}...")
