"""
Provider Router for AI Abstraction Layer
"""
import structlog
from typing import Type, TypeVar, Optional, Any, Callable
from pydantic import BaseModel
from datetime import datetime
from app.config import settings
from app.llm.base import BaseProvider
from app.llm.groq_provider import GroqProvider
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openai_provider import OpenAIProvider

import asyncio
import time

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class ProviderRouter:
    """Routes requests to the appropriate AI provider, with fallback and circuit breaker support"""
    
    def __init__(self):
        self.providers = []
        self.circuit_breaker = {} # {provider_name: {"failures": 0, "skip_until": 0}}
        
        # Initialize configured providers
        available = {}
        if hasattr(settings, "GEMINI_API_KEY") and settings.GEMINI_API_KEY:
            available["gemini"] = GeminiProvider(api_key=settings.GEMINI_API_KEY)
            
        if settings.GROQ_API_KEY:
            available["groq"] = GroqProvider(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
            
        if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
            available["openai"] = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            
        if hasattr(settings, "OPENROUTER_API_KEY") and settings.OPENROUTER_API_KEY:
            available["openrouter"] = OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY)
            
        # Sort by priority
        priority_list = [p.strip().lower() for p in settings.PROVIDER_PRIORITY.split(",")]
        
        for p in priority_list:
            if p in available:
                provider = available[p]
                self.providers.append(provider)
                self.circuit_breaker[provider.name] = {"failures": 0, "skip_until": 0}
                del available[p]
                
        # Append any remaining available providers
        for provider in available.values():
            self.providers.append(provider)
            self.circuit_breaker[provider.name] = {"failures": 0, "skip_until": 0}
            
        if not self.providers:
            logger.warning("No AI providers configured.")
            
    def _is_provider_available(self, name: str) -> bool:
        cb = self.circuit_breaker.get(name)
        if not cb:
            return True
        if cb["skip_until"] > time.time():
            return False
        return True
        
    def _record_success(self, name: str):
        if name in self.circuit_breaker:
            self.circuit_breaker[name]["failures"] = 0
            
    def _record_failure(self, name: str):
        if name in self.circuit_breaker:
            self.circuit_breaker[name]["failures"] += 1
            if self.circuit_breaker[name]["failures"] >= 3:
                # Trip circuit breaker for 60 seconds
                self.circuit_breaker[name]["skip_until"] = time.time() + 60
                logger.warning(f"Circuit breaker tripped for {name}. Skipping for 60 seconds.")
            
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 2,
        event_callback: Optional[Callable] = None,
        target_agent: Optional[str] = None,
        provider_hint: Optional[str] = None
    ) -> T:
        """Attempt to generate structured output, falling back to secondary providers on failure"""
        last_error = None
        
        providers_to_try = self.providers
        if provider_hint:
            preferred = next((p for p in self.providers if p.name.lower() == provider_hint.lower()), None)
            if preferred:
                providers_to_try = [preferred] + [p for p in self.providers if p != preferred]
                
        for idx, provider in enumerate(providers_to_try):
            if not self._is_provider_available(provider.name):
                logger.info(f"Skipping {provider.name} due to open circuit breaker")
                continue
                
            try:
                if event_callback:
                    event_type = "provider_selected" if idx == 0 else "provider_fallback"
                    await event_callback({
                        "type": event_type,
                        "agent": target_agent or "System",
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": f"Using provider {provider.name} ({provider.model})",
                        "provider": provider.name
                    })
                
                logger.info(f"Attempting generation with {provider.name}")
                result = await asyncio.wait_for(
                    provider.generate_structured(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        response_model=response_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        max_retries=max_retries
                    ),
                    timeout=getattr(settings, "PROVIDER_TIMEOUT", 30)
                )
                self._record_success(provider.name)
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed", error=str(e))
                self._record_failure(provider.name)
                last_error = e
                continue
                
        logger.error("All providers failed to generate structured output")
        if event_callback:
            await event_callback({
                "type": "error",
                "agent": target_agent or "System",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"All LLM providers failed. Last error: {last_error}"
            })
        raise ValueError(f"All providers failed. Last error: {last_error}")

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        event_callback: Optional[Callable] = None,
        target_agent: Optional[str] = None,
        provider_hint: Optional[str] = None
    ) -> str:
        """Attempt to generate text output, falling back to secondary providers on failure"""
        last_error = None
        
        providers_to_try = self.providers
        if provider_hint:
            preferred = next((p for p in self.providers if p.name.lower() == provider_hint.lower()), None)
            if preferred:
                providers_to_try = [preferred] + [p for p in self.providers if p != preferred]
                
        for idx, provider in enumerate(providers_to_try):
            if not self._is_provider_available(provider.name):
                logger.info(f"Skipping {provider.name} due to open circuit breaker")
                continue
                
            try:
                if event_callback:
                    event_type = "provider_selected" if idx == 0 else "provider_fallback"
                    await event_callback({
                        "type": event_type,
                        "agent": target_agent or "System",
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": f"Using provider {provider.name} ({provider.model})",
                        "provider": provider.name
                    })

                logger.info(f"Attempting generation with {provider.name}")
                result = await asyncio.wait_for(
                    provider.generate_text(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    ),
                    timeout=getattr(settings, "PROVIDER_TIMEOUT", 30)
                )
                self._record_success(provider.name)
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed", error=str(e))
                self._record_failure(provider.name)
                last_error = e
                continue
                
        logger.error("All providers failed to generate text output")
        if event_callback:
            await event_callback({
                "type": "error",
                "agent": target_agent or "System",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"All LLM providers failed. Last error: {last_error}"
            })
        raise ValueError(f"All providers failed. Last error: {last_error}")

# Global instance for use across the application
router = ProviderRouter()
