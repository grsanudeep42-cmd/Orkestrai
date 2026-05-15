"""
Architecture Agent - Designs system architecture and technical specifications
Uses Groq API for fast LLM inference
"""
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import json
from groq import Groq
from app.config import settings
import structlog

logger = structlog.get_logger()


class ArchitectureAgent:
    """Architecture Agent for designing system architecture using Groq"""
    
    def __init__(self):
        """Initialize the Architecture Agent with Groq"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not set in environment")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        
        self.system_prompt = """You are a senior software architect with 15+ years of experience 
in designing scalable, production-ready systems. You excel at choosing optimal tech stacks, 
designing database schemas, and creating clean API structures.

Your role is to transform product requirements into detailed technical architecture that 
developers can immediately implement. You focus on best practices, scalability, and maintainability."""
    
    async def design_architecture(
        self, 
        strategy_output: Dict[str, Any],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Design system architecture based on strategy
        
        Args:
            strategy_output: Output from Strategy Agent
            user_input: Original user input
            preferences: Optional user preferences
            event_callback: Optional callback for real-time events
            
        Returns:
            Dictionary containing architecture design
        """
        start_time = datetime.utcnow()
        
        try:
            # Emit start event
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "ArchitectureAgent",
                    "timestamp": start_time.isoformat()
                })
            
            # Create the architecture prompt
            user_prompt = f"""Based on the following product strategy, design a comprehensive system architecture:

PROJECT IDEA:
{user_input}

PRODUCT STRATEGY:
{json.dumps(strategy_output, indent=2)}

USER PREFERENCES:
{json.dumps(preferences or {}, indent=2)}

Design a complete system architecture including:
1. **Tech Stack**: Recommended frontend, backend, database, and deployment technologies
2. **Database Schema**: Tables, fields, relationships, and indexes
3. **API Structure**: RESTful endpoints with methods, paths, and descriptions
4. **Frontend Architecture**: Pages, components, and state management approach
5. **System Design**: High-level architecture diagram description
6. **Security Considerations**: Authentication, authorization, and data protection
7. **Scalability Plan**: How the system can scale

Format your response as a valid JSON object with these exact keys:
- tech_stack: object with {{frontend, backend, database, deployment, additional_tools}}
- database_schema: object with {{tables: array of {{name, fields, relationships}}}}
- api_endpoints: array of {{method, path, description, request_body, response}}
- frontend_structure: object with {{pages, components, state_management}}
- system_design: string (Mermaid diagram or description)
- security: object with {{authentication, authorization, data_protection}}
- scalability: array of strings

Be specific, practical, and focus on technologies that enable rapid development."""
            
            # Emit thinking event
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "ArchitectureAgent",
                    "message": "Designing system architecture and selecting tech stack...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Call Groq API
            logger.info("Calling Groq API for architecture", model=self.model)
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=3000,
                top_p=1,
                stream=False
            )
            
            result = chat_completion.choices[0].message.content
            
            # Parse the result
            try:
                result_str = str(result)
                start_idx = result_str.find('{')
                end_idx = result_str.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = result_str[start_idx:end_idx]
                    architecture_output = json.loads(json_str)
                else:
                    architecture_output = self._create_fallback_architecture(strategy_output, result_str)
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse JSON from Groq response", error=str(e))
                architecture_output = self._create_fallback_architecture(strategy_output, str(result))
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Emit output event
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "ArchitectureAgent",
                    "data": architecture_output,
                    "timestamp": end_time.isoformat()
                })
            
            # Emit complete event
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
            # Emit error event
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "ArchitectureAgent",
                    "error": str(e),
                    "details": "Failed to design system architecture",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Return fallback architecture
            return self._create_fallback_architecture(strategy_output, f"Error: {str(e)}")
    
    def _create_fallback_architecture(self, strategy_output: Dict[str, Any], raw_output: str) -> Dict[str, Any]:
        """Create a fallback architecture when JSON parsing fails or API errors occur"""
        project_name = strategy_output.get("project_name", "Project")
        
        return {
            "tech_stack": {
                "frontend": ["Next.js 14", "React", "Tailwind CSS", "TypeScript"],
                "backend": ["FastAPI", "Python 3.11+", "SQLAlchemy"],
                "database": "PostgreSQL",
                "deployment": ["Vercel (Frontend)", "Railway (Backend)"],
                "additional_tools": ["Redis (Caching)", "WebSocket (Real-time)"]
            },
            "database_schema": {
                "tables": [
                    {
                        "name": "users",
                        "fields": [
                            {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY"},
                            {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                            {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"}
                        ],
                        "relationships": []
                    },
                    {
                        "name": "items",
                        "fields": [
                            {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY"},
                            {"name": "user_id", "type": "UUID", "constraints": "FOREIGN KEY"},
                            {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                            {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"}
                        ],
                        "relationships": ["FOREIGN KEY (user_id) REFERENCES users(id)"]
                    }
                ]
            },
            "api_endpoints": [
                {
                    "method": "POST",
                    "path": "/api/v1/auth/register",
                    "description": "Register new user",
                    "request_body": {"email": "string", "password": "string"},
                    "response": {"user_id": "string", "token": "string"}
                },
                {
                    "method": "GET",
                    "path": "/api/v1/items",
                    "description": "List all items",
                    "request_body": None,
                    "response": {"items": "array"}
                },
                {
                    "method": "POST",
                    "path": "/api/v1/items",
                    "description": "Create new item",
                    "request_body": {"name": "string"},
                    "response": {"item": "object"}
                }
            ],
            "frontend_structure": {
                "pages": [
                    "/ (Landing page)",
                    "/auth/login (Login page)",
                    "/dashboard (Main dashboard)",
                    "/items/[id] (Item detail page)"
                ],
                "components": [
                    "Header (Navigation)",
                    "ItemCard (Display item)",
                    "ItemForm (Create/edit item)",
                    "Layout (Page wrapper)"
                ],
                "state_management": "React Context API or Zustand for global state"
            },
            "system_design": f"""
# {project_name} System Architecture

## High-Level Architecture
```
[Frontend (Next.js)] <--> [API Gateway] <--> [Backend (FastAPI)] <--> [Database (PostgreSQL)]
                                                      |
                                                      v
                                              [Cache (Redis)]
```

## Component Interaction
1. User interacts with Next.js frontend
2. Frontend makes API calls to FastAPI backend
3. Backend processes requests and queries PostgreSQL
4. Results cached in Redis for performance
5. Real-time updates via WebSocket
""",
            "security": {
                "authentication": "JWT tokens with refresh mechanism",
                "authorization": "Role-based access control (RBAC)",
                "data_protection": "Encrypted passwords (bcrypt), HTTPS only, SQL injection prevention"
            },
            "scalability": [
                "Horizontal scaling with load balancer",
                "Database read replicas for read-heavy operations",
                "Redis caching for frequently accessed data",
                "CDN for static assets",
                "Microservices architecture for future growth"
            ],
            "raw_analysis": raw_output[:500] if raw_output else "No output available"
        }

# Made with Bob