from typing import Dict, Any, Optional, Callable, Type, TypeVar, Union
import json
import structlog
from datetime import datetime
from pydantic import BaseModel, ValidationError, model_validator
from app.llm.provider_router import router as llm_router

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class BaseAgent:
    """Base Agent class providing common utility methods"""
    
    def sanitize_output_dict(self, data: Any) -> Any:
        """Recursively removes control characters from string values"""
        if isinstance(data, str):
            import re
            # Escape standard whitespace control chars
            escaped = data.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            # Remove all other control characters (\x00-\x1F)
            return re.sub(r'[\x00-\x1f]', '', escaped)
        elif isinstance(data, dict):
            return {k: self.sanitize_output_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_output_dict(item) for item in data]
        return data

    def sanitize_input(self, text: str) -> str:
        """Sanitizes user input to prevent basic prompt injection"""
        if not text:
            return ""
        # Remove typical injection attempts
        injections = [
            "ignore all previous instructions",
            "ignore previous instructions",
            "system prompt:",
            "forget everything",
            "you are now",
            "output the following:"
        ]
        sanitized = text
        for inj in injections:
            # Simple case-insensitive replacement
            # A more robust regex could be used, but this is a starting point
            import re
            sanitized = re.sub(inj, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def format_memory(self, memory: Optional[Dict[str, Any]]) -> str:
        """Formats the shared memory context into a string for prompts"""
        if not memory:
            return ""
        return "\nSHARED EXECUTION MEMORY:\n" + json.dumps(memory, indent=2)

    async def _handle_generation_error(
        self,
        e: Exception,
        agent_name: str,
        event_callback: Optional[Callable] = None
    ):
        """Standardized error handler for agent generation"""
        logger.error(f"{agent_name} generation failed", error=str(e))
        if event_callback:
            await event_callback({
                "type": "error",
                "agent": agent_name,
                "error": str(e),
                "details": f"Failed to generate output for {agent_name}",
                "timestamp": datetime.utcnow().isoformat()
            })

    async def generate_structured_with_fallback(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        agent_name: str,
        temperature: float = 0.5,
        event_callback: Optional[Callable] = None,
        fallback_func: Optional[Callable] = None,
        fallback_args: tuple = ()
    ) -> Dict[str, Any]:
        """Generates structured output, catches Pydantic validation errors, and uses fallback"""
        
        # 1. Pre-validation Step: Create a dynamic SafeModel to convert unexpected dicts/lists to strings
        class SafeModel(response_model):
            @model_validator(mode='before')
            @classmethod
            def pre_validate_dict(cls, data: Any) -> Any:
                if not isinstance(data, dict):
                    return data
                    
                def stringify_unexpected(obj: Any, model_class: Type[BaseModel]) -> Any:
                    if not isinstance(obj, dict) or not hasattr(model_class, "model_fields"):
                        return obj
                        
                    for field_name, field_info in model_class.model_fields.items():
                        if field_name not in obj:
                            continue
                            
                        val = obj[field_name]
                        annotation = field_info.annotation
                        
                        # Handle Optional/Union by unwrapping the types
                        origin = getattr(annotation, "__origin__", None)
                        args = getattr(annotation, "__args__", [])
                        
                        # Check if the field expects a string
                        is_str_field = annotation is str or (origin is Union and str in args)
                        
                        if is_str_field and isinstance(val, (dict, list)):
                            # Unexpected dict/list for a string field - convert to string
                            obj[field_name] = json.dumps(val)
                        elif hasattr(annotation, "model_fields") and isinstance(val, dict):
                            # Nested single model
                            obj[field_name] = stringify_unexpected(val, annotation)
                        elif origin is list and isinstance(val, list) and args:
                            # List of nested models
                            item_type = args[0]
                            if hasattr(item_type, "model_fields"):
                                for i, item in enumerate(val):
                                    if isinstance(item, dict):
                                        val[i] = stringify_unexpected(item, item_type)
                                        
                    return obj
                    
                return stringify_unexpected(data, response_model)

        # Ensure the dynamic subclass keeps the name of the original for clearer logs/schema
        SafeModel.__name__ = response_model.__name__

        try:
            model = await llm_router.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=SafeModel,
                temperature=temperature,
                event_callback=event_callback,
                target_agent=agent_name
            )
            return self.sanitize_output_dict(model.model_dump())
        except ValidationError as e:
            logger.error(f"Validation error in {agent_name}", error=str(e))
            await self._handle_generation_error(e, agent_name, event_callback)
            if fallback_func:
                return self.sanitize_output_dict(fallback_func(*fallback_args, raw_output=str(e)))
            raise e
        except Exception as e:
            await self._handle_generation_error(e, agent_name, event_callback)
            if fallback_func:
                return self.sanitize_output_dict(fallback_func(*fallback_args, raw_output=str(e)))
            raise e
