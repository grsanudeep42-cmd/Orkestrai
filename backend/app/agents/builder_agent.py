"""
Builder Agent - Generates implementation plans and code structure
Uses Groq API for fast LLM inference
"""
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import json
from groq import Groq
from app.config import settings
import structlog

logger = structlog.get_logger()


class BuilderAgent:
    """Builder Agent for generating implementation plans using Groq"""
    
    def __init__(self):
        """Initialize the Builder Agent with Groq"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not set in environment")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        
        self.system_prompt = """You are a senior full-stack developer with 12+ years of experience 
in rapid prototyping and production-ready code generation. You excel at creating clean, 
maintainable code structures and comprehensive implementation plans.

Your role is to transform architecture designs into actionable implementation plans with 
folder structures, module breakdowns, and deployment strategies. You focus on best practices, 
code organization, and developer experience."""
    
    async def generate_implementation_plan(
        self, 
        strategy_output: Dict[str, Any],
        architecture_output: Dict[str, Any],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate implementation plan based on strategy and architecture
        
        Args:
            strategy_output: Output from Strategy Agent
            architecture_output: Output from Architecture Agent
            user_input: Original user input
            preferences: Optional user preferences
            event_callback: Optional callback for real-time events
            
        Returns:
            Dictionary containing implementation plan
        """
        start_time = datetime.utcnow()
        
        try:
            # Emit start event
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "BuilderAgent",
                    "timestamp": start_time.isoformat()
                })
            
            # Create the implementation prompt
            user_prompt = f"""Based on the product strategy and system architecture, create a comprehensive implementation plan:

PROJECT IDEA:
{user_input}

PRODUCT STRATEGY:
{json.dumps(strategy_output, indent=2)}

SYSTEM ARCHITECTURE:
{json.dumps(architecture_output, indent=2)}

Create a detailed implementation plan including:
1. **Folder Structure**: Complete directory tree for frontend and backend
2. **Backend Modules**: Key Python modules/files with their responsibilities
3. **Frontend Components**: React components and their purposes
4. **Implementation Phases**: Step-by-step development phases with priorities
5. **Deployment Plan**: Steps to deploy the application
6. **Development Setup**: Commands and configuration needed
7. **Testing Strategy**: Unit tests, integration tests, and E2E tests

Format your response as a valid JSON object with these exact keys:
- folder_structure: object with {{backend, frontend}}
- backend_modules: array of {{path, purpose, key_functions}}
- frontend_components: array of {{path, purpose, props}}
- implementation_phases: array of {{phase, tasks, priority, estimated_hours}}
- deployment_plan: object with {{steps, platforms, environment_variables}}
- development_setup: object with {{backend_commands, frontend_commands, prerequisites}}
- testing_strategy: object with {{unit_tests, integration_tests, e2e_tests}}

Be specific, actionable, and focus on getting a working MVP quickly."""
            
            # Emit thinking event
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "BuilderAgent",
                    "message": "Creating implementation plan and folder structure...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Call Groq API
            logger.info("Calling Groq API for implementation plan", model=self.model)
            
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
                    implementation_output = json.loads(json_str)
                else:
                    implementation_output = self._create_fallback_implementation(
                        strategy_output, architecture_output, result_str
                    )
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse JSON from Groq response", error=str(e))
                implementation_output = self._create_fallback_implementation(
                    strategy_output, architecture_output, str(result)
                )
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Emit output event
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "BuilderAgent",
                    "data": implementation_output,
                    "timestamp": end_time.isoformat()
                })
            
            # Emit complete event
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "BuilderAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info("Implementation plan complete", duration_ms=duration_ms)
            return implementation_output
            
        except Exception as e:
            logger.error("Implementation plan generation failed", error=str(e))
            # Emit error event
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "BuilderAgent",
                    "error": str(e),
                    "details": "Failed to generate implementation plan",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Return fallback implementation
            return self._create_fallback_implementation(
                strategy_output, architecture_output, f"Error: {str(e)}"
            )
    
    def _create_fallback_implementation(
        self, 
        strategy_output: Dict[str, Any],
        architecture_output: Dict[str, Any],
        raw_output: str
    ) -> Dict[str, Any]:
        """Create a fallback implementation plan when JSON parsing fails or API errors occur"""
        project_name = strategy_output.get("project_name", "project")
        tech_stack = architecture_output.get("tech_stack", {})
        
        return {
            "folder_structure": {
                "backend": [
                    "app/",
                    "app/__init__.py",
                    "app/main.py",
                    "app/config.py",
                    "app/api/",
                    "app/api/v1/",
                    "app/api/v1/endpoints/",
                    "app/models/",
                    "app/schemas/",
                    "app/services/",
                    "app/db/",
                    "app/core/",
                    "tests/",
                    "requirements.txt",
                    ".env.example",
                    "README.md"
                ],
                "frontend": [
                    "src/",
                    "src/app/",
                    "src/app/page.tsx",
                    "src/app/layout.tsx",
                    "src/components/",
                    "src/components/ui/",
                    "src/lib/",
                    "src/hooks/",
                    "src/types/",
                    "public/",
                    "package.json",
                    "tsconfig.json",
                    "tailwind.config.ts",
                    ".env.local.example",
                    "README.md"
                ]
            },
            "backend_modules": [
                {
                    "path": "app/main.py",
                    "purpose": "FastAPI application entry point",
                    "key_functions": ["create_app", "setup_middleware", "include_routers"]
                },
                {
                    "path": "app/api/v1/endpoints/items.py",
                    "purpose": "Item CRUD endpoints",
                    "key_functions": ["create_item", "get_items", "update_item", "delete_item"]
                },
                {
                    "path": "app/models/item.py",
                    "purpose": "Item database model",
                    "key_functions": ["Item class with SQLAlchemy"]
                },
                {
                    "path": "app/services/item_service.py",
                    "purpose": "Business logic for items",
                    "key_functions": ["create", "get_all", "get_by_id", "update", "delete"]
                }
            ],
            "frontend_components": [
                {
                    "path": "src/app/page.tsx",
                    "purpose": "Landing page",
                    "props": "None"
                },
                {
                    "path": "src/components/ItemCard.tsx",
                    "purpose": "Display individual item",
                    "props": "item: Item, onEdit: function, onDelete: function"
                },
                {
                    "path": "src/components/ItemForm.tsx",
                    "purpose": "Create/edit item form",
                    "props": "item?: Item, onSubmit: function, onCancel: function"
                },
                {
                    "path": "src/components/ui/Button.tsx",
                    "purpose": "Reusable button component",
                    "props": "children, onClick, variant, disabled"
                }
            ],
            "implementation_phases": [
                {
                    "phase": "Phase 1: Setup & Infrastructure",
                    "tasks": [
                        "Initialize backend with FastAPI",
                        "Initialize frontend with Next.js",
                        "Set up database connection",
                        "Configure environment variables",
                        "Set up basic routing"
                    ],
                    "priority": "high",
                    "estimated_hours": 4
                },
                {
                    "phase": "Phase 2: Core Features",
                    "tasks": [
                        "Implement database models",
                        "Create API endpoints",
                        "Build frontend components",
                        "Implement state management",
                        "Connect frontend to backend"
                    ],
                    "priority": "high",
                    "estimated_hours": 8
                },
                {
                    "phase": "Phase 3: Polish & Deploy",
                    "tasks": [
                        "Add error handling",
                        "Implement loading states",
                        "Add form validation",
                        "Write tests",
                        "Deploy to production"
                    ],
                    "priority": "medium",
                    "estimated_hours": 6
                }
            ],
            "deployment_plan": {
                "steps": [
                    "1. Set up PostgreSQL database on Railway",
                    "2. Deploy backend to Railway with environment variables",
                    "3. Deploy frontend to Vercel",
                    "4. Configure CORS and API URLs",
                    "5. Test production deployment",
                    "6. Set up monitoring and logging"
                ],
                "platforms": {
                    "backend": "Railway",
                    "frontend": "Vercel",
                    "database": "Railway PostgreSQL"
                },
                "environment_variables": [
                    "DATABASE_URL",
                    "SECRET_KEY",
                    "CORS_ORIGINS",
                    "NEXT_PUBLIC_API_URL"
                ]
            },
            "development_setup": {
                "backend_commands": [
                    "cd backend",
                    "python -m venv venv",
                    "source venv/bin/activate",
                    "pip install -r requirements.txt",
                    "cp .env.example .env",
                    "# Edit .env with your credentials",
                    "uvicorn app.main:app --reload"
                ],
                "frontend_commands": [
                    "cd frontend",
                    "npm install",
                    "cp .env.local.example .env.local",
                    "# Edit .env.local with API URL",
                    "npm run dev"
                ],
                "prerequisites": [
                    "Python 3.11+",
                    "Node.js 18+",
                    "PostgreSQL 14+",
                    "Git"
                ]
            },
            "testing_strategy": {
                "unit_tests": [
                    "Test individual service functions",
                    "Test API endpoint logic",
                    "Test React component rendering",
                    "Use pytest for backend, Jest for frontend"
                ],
                "integration_tests": [
                    "Test API endpoints with database",
                    "Test frontend-backend integration",
                    "Test authentication flow",
                    "Use pytest-asyncio for async tests"
                ],
                "e2e_tests": [
                    "Test complete user workflows",
                    "Test critical paths",
                    "Use Playwright or Cypress",
                    "Run in CI/CD pipeline"
                ]
            },
            "raw_analysis": raw_output[:500] if raw_output else "No output available"
        }

# Made with Bob