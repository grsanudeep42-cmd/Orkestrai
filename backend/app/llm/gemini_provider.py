"""
Gemini AI Provider
"""
import json
import httpx
import structlog
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError
from app.llm.base import BaseProvider

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class GeminiProvider(BaseProvider):
    """Gemini API Provider using httpx.AsyncClient with OpenAI compatibility layer"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        self._name = "Gemini"
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        
    @property
    def name(self) -> str:
        return self._name

    async def _make_request(self, messages: list, temperature: float, max_tokens: int, json_mode: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected response format from Gemini: {data}")

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 2
    ) -> T:
        """Generate structured output validated by Pydantic"""
        schema = response_model.model_json_schema()
        schema_instruction = (
            "\n\nYou MUST return a valid JSON object. "
            "Do NOT wrap it in markdown block quotes like ```json ... ```. "
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
                
                content = await self._make_request(
                    messages=messages, 
                    temperature=temperature, 
                    max_tokens=max_tokens,
                    json_mode=True
                )
                
                if not content:
                    raise ValueError("Empty response received from Gemini")
                    
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                    
                # Validate with Pydantic (allowing unescaped control chars like \n in strings)
                parsed_data = json.loads(content, strict=False)
                result = response_model.model_validate(parsed_data)
                return result
                
            except (ValidationError, ValueError) as e:
                logger.warning(f"Validation error on attempt {attempt+1}/{max_retries+1}", error=str(e), provider=self.name)
                last_error = e
                user_prompt += f"\n\nYour previous response failed validation with error: {str(e)}. Please fix the JSON and try again."
            except Exception as e:
                logger.error(f"API error on attempt {attempt+1}/{max_retries+1}", error=str(e), provider=self.name)
                raise e
                
        raise ValueError(f"Failed to generate structured output after {max_retries + 1} attempts. Last error: {last_error}")

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
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
