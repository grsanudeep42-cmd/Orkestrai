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
    
    def __init__(self):
        self.system_prompt = """You are an elite Principal Staff Engineer and System Architect. 
Your goal is to design a scalable, robust, and modern system architecture based on a product strategy.

CORE RESPONSIBILITIES:
1) System Overview - High-level architectural pattern (e.g., Microservices, Monolithic, Serverless).
2) Data Model - Detailed entity-relationship definitions and database choice.
3) API Design - Core endpoints, request/response formats, and authentication strategy (e.g., JWT with HttpOnly cookies).
4) Component Breakdown - Specific responsibilities for backend, frontend, and external services.
5) Infrastructure & DevOps - Hosting (e.g., Vercel + AWS), CI/CD, and monitoring recommendations.
6) Security & Scalability - How the system handles growth and protects data.

CRITICAL INSTRUCTIONS:
- Be hyper-specific. Specify exact frameworks, libraries, and protocols.
- Ensure the architecture is realistic, modern, and implementable.
- Use professional Markdown.
- Provide a clear mapping from strategy requirements to technical components.
- NEVER use generic placeholder text.
- If you receive feedback from the AuditAgent, you must correct your course immediately."""
    
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
1. **Full Folder/File Structure**: Provide a complete tree with every file listed.
2. **Tech Stack**: Derived from the strategy recommendation.
3. **Database Schema**: All tables, fields, and relationships.
4. **API Endpoints**: All routes, methods, request/response shapes.
5. **Frontend Architecture**: Page structure and component hierarchy.
6. **Environment Variables**: List all required variables.
7. **Docker Setup**: Describe the Docker and deployment setup.

IMPORTANT: Your entire output MUST be in cleanly formatted Markdown. DO NOT wrap it in JSON. Use code blocks for file trees and schemas."""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "ArchitectureAgent",
                    "message": "Designing system architecture and selecting tech stack...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for ArchitectureAgent")
            
            architecture_output = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
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
            
            return self._create_fallback_architecture(strategy_output, f"Error: {str(e)}")
    
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