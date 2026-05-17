"""
Architecture Agent - Designs system architecture and technical specifications
"""
from typing import Dict, Any, Callable, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import json
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

logger = structlog.get_logger()

# ArchitectureOutput models removed for raw markdown output

class ArchitectureAgent(BaseAgent):
    """Architecture Agent for designing system architecture"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)
        self.system_prompt = """You are an elite Principal Staff Engineer and System Architect. 
Your goal is to design a scalable, robust, and modern system architecture based on a product strategy.

CORE RESPONSIBILITIES:
1) System Overview - High-level architectural pattern (e.g., Microservices, Monolithic, Serverless).
2) Data Model - Detailed entity-relationship definitions with consistent naming conventions (snake_case for tables/columns).
3) API Design - RESTful endpoints with consistent naming, comprehensive error handling specifications, and clear request/response formats.
4) Security Architecture - Detailed JWT/OAuth2 implementation, Role-Based Access Control (RBAC), and input validation strategies.
5) Component Breakdown - Specific responsibilities for backend, frontend, and external services.
6) Infrastructure & DevOps - Hosting (e.g., Vercel + AWS), CI/CD, and monitoring recommendations.

CRITICAL INSTRUCTIONS:
- Use consistent, professional naming conventions across all layers (DB, API, Code).
- Explicitly define error handling patterns (e.g., global exception handlers, standardized error response bodies).
- Be hyper-specific about security measures (e.g., CORS policies, secure cookie flags, rate limiting).
- Ensure the architecture is realistic, modern, and implementable.
- Use professional Markdown.
- Provide a clear mapping from strategy requirements to technical components."""

    async def design_architecture(
        self, 
        strategy_output: Union[str, Dict[str, Any]],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> str:
        """
        Design system architecture based on strategy
        """
        start_time = datetime.utcnow()
        
        try:
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "ArchitectureAgent",
                    "timestamp": start_time.isoformat()
                })
            
            memory_context = self.format_memory(memory)
            safe_input = self.sanitize_input(user_input)

            strategy_text = strategy_output if isinstance(strategy_output, str) else json.dumps(strategy_output, indent=2)

            user_prompt = f"""Based on the following product strategy, design a comprehensive system architecture:

PROJECT IDEA:
{safe_input}

PRODUCT STRATEGY:
{strategy_text}

USER PREFERENCES:
{json.dumps(preferences or {}, indent=2)}
{memory_context}

Design a complete system architecture including:
1. **Full Folder/File Structure**: Provide a complete tree with every file listed, following professional layout standards.
2. **Tech Stack**: Derived from the strategy recommendation, with specific versions if possible.
3. **Database Schema**: All tables (snake_case), fields, relationships, and indexing strategy.
4. **RESTful API Design**: All routes, methods, and standardized request/response shapes. Include a dedicated section on Error Handling & Validation.
5. **Security & Auth**: Detailed JWT/OAuth2 flow, RBAC, and data sanitization strategies.
6. **Frontend Architecture**: Component hierarchy, state management (e.g., Redux, Context API), and routing.
7. **Environment & DevOps**: List all required variables and describe the Docker + CI/CD setup.

IMPORTANT: Your entire output MUST be in cleanly formatted Markdown. DO NOT wrap it in JSON. Use code blocks for file trees and schemas. Ensure consistency in naming conventions throughout."""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "ArchitectureAgent",
                    "message": "Designing system architecture and selecting tech stack...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for ArchitectureAgent")
            
            architecture_result = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                api_keys=self.api_keys,
                temperature=0.3,
                event_callback=event_callback,
                target_agent="ArchitectureAgent"
            )

            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "ArchitectureAgent",
                    "data": architecture_output,
                    "timestamp": end_time.isoformat()
                })
            
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "ArchitectureAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info("Architecture design complete", duration_ms=duration_ms)
            return architecture_output
            
        except Exception as e:
            logger.error("Architecture design failed", error=str(e))
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "ArchitectureAgent",
                    "error": str(e),
                    "details": "Failed to design system architecture",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            raise e
    
    def _create_fallback_architecture(self, strategy_output: Union[str, Dict[str, Any]], raw_output: str = "") -> str:
        """Create a fallback architecture in Markdown"""
        project_name = strategy_output.get("project_name", "Project") if isinstance(strategy_output, dict) else "Project"
        
        return f"""# {project_name} - Architecture Design

## Folder Structure
```text
project/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── package.json
    └── src/
```

## Tech Stack
- Frontend: Next.js, React, Tailwind CSS
- Backend: FastAPI, PostgreSQL
- Deployment: Docker

## Database Schema
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);
```

## API Endpoints
- `POST /api/v1/auth/register` - Register new user

*Raw analysis error: {raw_output[:500] if raw_output else "No output available"}*
"""