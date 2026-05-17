"""
Provider Router for AI Abstraction Layer
"""
import structlog
from typing import Type, TypeVar, Optional, Any, Callable, Dict
from pydantic import BaseModel
from datetime import datetime
from app.config import settings
from app.llm.base import BaseProvider
from app.llm.groq_provider import GroqProvider
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.bob_provider import BobProvider

import asyncio
import time

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class ProviderRouter:
    """Routes requests to the appropriate AI provider, with fallback and circuit breaker support"""
    
    def __init__(self):
        self.circuit_breaker = {} # {provider_name: {"failures": 0, "skip_until": 0}}
        
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
        if name not in self.circuit_breaker:
            self.circuit_breaker[name] = {"failures": 0, "skip_until": 0}
        self.circuit_breaker[name]["failures"] += 1
        if self.circuit_breaker[name]["failures"] >= 3:
            # Trip circuit breaker for 60 seconds
            self.circuit_breaker[name]["skip_until"] = time.time() + 60
            logger.warning(f"Circuit breaker tripped for {name}. Skipping for 60 seconds.")
            
    def _get_providers(self, api_keys: Dict[str, str]) -> list[BaseProvider]:
        """Create provider instances based on provided API keys"""
        providers = []
        
        # Initialize providers if keys are present
        if api_keys.get("gemini"):
            providers.append(GeminiProvider(api_key=api_keys["gemini"]))
        if api_keys.get("groq"):
            providers.append(GroqProvider(api_key=api_keys["groq"], model=settings.GROQ_MODEL))
        if api_keys.get("openai"):
            providers.append(OpenAIProvider(api_key=api_keys["openai"]))
        if api_keys.get("openrouter"):
            providers.append(OpenRouterProvider(api_key=api_keys["openrouter"]))
        if api_keys.get("bob"):
            providers.append(BobProvider(api_key=api_keys["bob"]))
            
        # Sort by priority if defined in settings
        priority_list = [p.strip().lower() for p in settings.PROVIDER_PRIORITY.split(",")]
        
        sorted_providers = []
        for p in priority_list:
            found = next((provider for provider in providers if provider.name.lower() == p), None)
            if found:
                sorted_providers.append(found)
                providers.remove(found)
        
        # Add remaining
        sorted_providers.extend(providers)
        return sorted_providers

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        api_keys: Dict[str, str],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 2,
        event_callback: Optional[Callable] = None,
        target_agent: Optional[str] = None,
        provider_hint: Optional[str] = None
    ) -> T:
        """Attempt to generate structured output, falling back to secondary providers on failure"""
        last_error = None
        
        providers = self._get_providers(api_keys)
        if not providers:
            raise ValueError("No AI providers configured. Please add your API keys in Settings.")

        providers_to_try = providers
        if provider_hint:
            preferred = next((p for p in providers if p.name.lower() == provider_hint.lower()), None)
            if preferred:
                providers_to_try = [preferred] + [p for p in providers if p != preferred]
                
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
                result, stats = await asyncio.wait_for(
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
                
                # Trace usage
                logger.info("LLM Usage Trace", 
                    agent=target_agent,
                    provider=stats.provider,
                    model=stats.model,
                    prompt_tokens=stats.prompt_tokens,
                    completion_tokens=stats.completion_tokens,
                    total_tokens=stats.total_tokens
                )
                
                if event_callback:
                    await event_callback({
                        "type": "usage_stats",
                        "agent": target_agent,
                        "provider": stats.provider,
                        "model": stats.model,
                        "usage": stats.model_dump(),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                return result
            except Exception as e:
                error_msg = str(e)
                is_token_error = any(code in error_msg for code in ["401", "402", "429", "Unauthorized", "Payment Required", "Too Many Requests"])
                
                if is_token_error:
                    log_message = f"{provider.name} API Tokens are finished or invalid, retrying with next one!"
                    logger.warning(log_message, provider=provider.name)
                    if event_callback:
                        await event_callback({
                            "type": "provider_error",
                            "agent": target_agent or "System",
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": log_message,
                            "provider": provider.name,
                            "is_token_error": True
                        })
                else:
                    logger.warning(f"Provider {provider.name} failed", error=error_msg)
                
                self._record_failure(provider.name)
                last_error = e
                continue
                
        logger.error("All providers failed to generate structured output")
        error_detail = str(last_error)
        is_final_token_error = any(code in error_detail for code in ["401", "402", "429", "Unauthorized", "Payment Required", "Too Many Requests"])
        
        if event_callback:
            final_msg = "Your API Tokens are finished, please update them!" if is_final_token_error else f"All LLM providers failed. Last error: {last_error}"
            await event_callback({
                "type": "error",
                "agent": target_agent or "System",
                "timestamp": datetime.utcnow().isoformat(),
                "message": final_msg,
                "is_token_exhausted": is_final_token_error
            })
        
        if is_final_token_error:
            raise ValueError("Your API Tokens are finished, please update them!")
        raise ValueError(f"All providers failed. Last error: {last_error}")

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        api_keys: Dict[str, str],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        event_callback: Optional[Callable] = None,
        target_agent: Optional[str] = None,
        provider_hint: Optional[str] = None
    ) -> str:
        """Attempt to generate text output, falling back to secondary providers on failure"""
        last_error = None
        
        providers = self._get_providers(api_keys)
        if not providers:
            raise ValueError("No AI providers configured. Please add your API keys in Settings.")

        providers_to_try = providers
        if provider_hint:
            preferred = next((p for p in providers if p.name.lower() == provider_hint.lower()), None)
            if preferred:
                providers_to_try = [preferred] + [p for p in providers if p != preferred]
                
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
                result, stats = await asyncio.wait_for(
                    provider.generate_text(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    ),
                    timeout=getattr(settings, "PROVIDER_TIMEOUT", 30)
                )
                self._record_success(provider.name)
                
                # Trace usage
                logger.info("LLM Usage Trace", 
                    agent=target_agent,
                    provider=stats.provider,
                    model=stats.model,
                    prompt_tokens=stats.prompt_tokens,
                    completion_tokens=stats.completion_tokens,
                    total_tokens=stats.total_tokens
                )
                
                if event_callback:
                    await event_callback({
                        "type": "usage_stats",
                        "agent": target_agent,
                        "provider": stats.provider,
                        "model": stats.model,
                        "usage": stats.model_dump(),
                        "timestamp": datetime.utcnow().isoformat()
                    })

                return result
            except Exception as e:
                error_msg = str(e)
                is_token_error = any(code in error_msg for code in ["401", "402", "429", "Unauthorized", "Payment Required", "Too Many Requests"])
                
                if is_token_error:
                    log_message = f"{provider.name} API Tokens are finished or invalid, retrying with next one!"
                    logger.warning(log_message, provider=provider.name)
                    if event_callback:
                        await event_callback({
                            "type": "provider_error",
                            "agent": target_agent or "System",
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": log_message,
                            "provider": provider.name,
                            "is_token_error": True
                        })
                else:
                    logger.warning(f"Provider {provider.name} failed", error=error_msg)
                
                self._record_failure(provider.name)
                last_error = e
                continue
                
        logger.error("All providers failed to generate text output")
        error_detail = str(last_error)
        is_final_token_error = any(code in error_detail for code in ["401", "402", "429", "Unauthorized", "Payment Required", "Too Many Requests"])
        
        if event_callback:
            final_msg = "Your API Tokens are finished, please update them!" if is_final_token_error else f"All LLM providers failed. Last error: {last_error}"
            await event_callback({
                "type": "error",
                "agent": target_agent or "System",
                "timestamp": datetime.utcnow().isoformat(),
                "message": final_msg,
                "is_token_exhausted": is_final_token_error
            })
            
        if is_final_token_error:
            raise ValueError("Your API Tokens are finished, please update them!")
        raise ValueError(f"All providers failed. Last error: {last_error}")

# Global instance for use across the application
router = ProviderRouter()
