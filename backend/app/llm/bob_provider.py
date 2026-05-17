"""
Bob AI Provider - Specialized high-performance LLM
"""
import json
import httpx
import structlog
from typing import Type, TypeVar, Optional, Any, Tuple
from pydantic import BaseModel, ValidationError
from app.llm.base import BaseProvider, UsageStats

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class BobProvider(BaseProvider):
    """Bob API Provider using httpx.AsyncClient (OpenAI-compatible)"""
    
    def __init__(self, api_key: str, model: str = "bob-pro-v1"):
        self._name = "Bob"
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.bob.ai/v1/chat/completions" # Placeholder URL
        
    @property
    def name(self) -> str:
        return self._name

    async def _make_request(self, messages: list, temperature: float, max_tokens: int, json_mode: bool = False) -> Tuple[str, UsageStats]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Client": "OrkestrAI"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                stats = UsageStats(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    provider=self.name,
                    model=self.model
                )
                return content, stats
            else:
                raise ValueError(f"Unexpected response format from Bob API: {data}")

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 2
    ) -> Tuple[T, UsageStats]:
        """Generate structured output validated by Pydantic"""
        schema = response_model.model_json_schema()
        schema_instruction = (
            "\n\nYou MUST return a valid JSON object. "
            f"The JSON object must strictly adhere to the following JSON schema:\n{json.dumps(schema)}"
        )
        full_system_prompt = system_prompt + schema_instruction
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                messages = [
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                content, stats = await self._make_request(
                    messages=messages, 
                    temperature=temperature, 
                    max_tokens=max_tokens,
                    json_mode=True
                )
                
                if not content:
                    raise ValueError("Empty response received from Bob API")
                    
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                    
                parsed_data = json.loads(content, strict=False)
                result = response_model.model_validate(parsed_data)
                return result, stats
                
            except (ValidationError, ValueError) as e:
                logger.warning(f"Validation error on attempt {attempt+1}/{max_retries+1}", error=str(e), provider=self.name)
                last_error = e
                user_prompt += f"\n\nYour previous response failed validation with error: {str(e)}. Please fix the JSON and try again."
            except Exception as e:
                logger.error(f"API error on attempt {attempt+1}/{max_retries+1}", error=str(e), provider=self.name)
                raise e
                
        raise ValueError(f"Failed to generate structured output from Bob API after {max_retries + 1} attempts. Last error: {last_error}")

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Tuple[str, UsageStats]:
        """Generate raw text output"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return await self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
