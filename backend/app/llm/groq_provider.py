"""
Groq AI Provider
"""
import json
import structlog
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError
from groq import AsyncGroq
from app.config import settings
from app.llm.base import BaseProvider

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class GroqProvider(BaseProvider):
    """Groq API Provider using AsyncGroq"""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self._name = "Groq"
        self.model = model
        self.client = AsyncGroq(api_key=api_key, timeout=30.0)
        
    @property
    def name(self) -> str:
        return self._name

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
                chat_completion = await self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": full_system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                    stream=False
                )
                
                content = chat_completion.choices[0].message.content
                if not content:
                    raise ValueError("Empty response received from Groq")
                    
                # Validate with Pydantic (allowing unescaped control chars like \n in strings)
                parsed_data = json.loads(content, strict=False)
                result = response_model.model_validate(parsed_data)
                return result
                
            except (ValidationError, ValueError) as e:
                logger.warning(f"Validation error on attempt {attempt+1}/{max_retries+1}", error=str(e), provider=self.name)
                last_error = e
                # Provide feedback to the model for the next retry if applicable
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
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )
        return chat_completion.choices[0].message.content or ""
