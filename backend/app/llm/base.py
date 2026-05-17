"""
Base AI Provider Abstraction
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, TypeVar, Tuple
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class UsageStats(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    provider: str = ""
    model: str = ""

class BaseProvider(ABC):
    """Abstract base class for AI providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
        
    @abstractmethod
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Tuple[T, UsageStats]:
        """
        Generate structured output adhering to a Pydantic schema
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Tuple[str, UsageStats]:
        """
        Generate raw text output
        """
        pass
