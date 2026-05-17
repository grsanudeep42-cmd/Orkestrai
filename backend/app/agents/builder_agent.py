"""
Builder Agent - Generates actual code files and packages them into a zip archive
"""
from typing import Dict, Any, Callable, Optional, List, Union
from datetime import datetime
import structlog
import json
import zipfile
import io
import os
import uuid
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

logger = structlog.get_logger()

class BuilderAgent(BaseAgent):
    """Builder Agent for generating real code scaffold"""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)
        self.system_prompt = """You are an elite Senior Principal Software Engineer and System Architect. 
You write production-ready, clean, and functional code that prioritizes security, robustness, and maintainability.

CORE RESPONSIBILITIES:
1) Clean Code - Functional, modular, and DRY (Don't Repeat Yourself) principles.
2) Security First - Use Pydantic for input validation, password hashing (e.g., passlib), and sanitization to prevent injection.
3) Robust Error Handling - Explicit try/except blocks and standardized error responses.
4) Comprehensive Documentation - Clear docstrings, comments for complex logic, and a detailed README.
5) Seamless Integration - Ensure backend and frontend are perfectly connected.

CRITICAL INSTRUCTIONS:
- You MUST generate REAL CODE files for a complete project scaffold.
- Do NOT use placeholders, TODOs, or pseudocode.
- Use best practices for the chosen stack (e.g., async/await for Python, type safety in TypeScript).
- Implement explicit authentication and authorization flows (e.g., JWT).
- Return files using this exact delimiter format:

===FILE: path/to/file.py===
file content here
===FILE: path/to/other/file.js===
other content here
===END===

- Be concise but complete. Do not truncate files."""
    async def generate_implementation_plan(
        self, 
        strategy_output: Union[str, Dict[str, Any]],
        architecture_output: Union[str, Dict[str, Any]],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate actual code based on strategy and architecture
        """
        start_time = datetime.utcnow()

        try:
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "BuilderAgent",
                    "timestamp": start_time.isoformat()
                })

            memory_context = self.format_memory(memory)
            safe_input = self.sanitize_input(user_input)

            strategy_text = strategy_output if isinstance(strategy_output, str) else json.dumps(strategy_output)
            arch_text = architecture_output if isinstance(architecture_output, str) else json.dumps(architecture_output)

            user_prompt = f"""Generate a high-quality, production-ready codebase for the following project:

    PROJECT IDEA:
    {safe_input}

    STRATEGY & GOALS:
    {strategy_text}

    ARCHITECTURAL SPECIFICATIONS:
    {arch_text}

    USER PREFERENCES:
    {json.dumps(preferences or {})}
    {memory_context}

    REQUIRED CODE STANDARDS:
    1. **Security**: Implement Pydantic validation for all API models, secure password hashing, and JWT-based authentication.
    2. **Error Handling**: Use global exception handlers and explicit try/except blocks in critical paths.
    3. **Naming**: Follow snake_case for Python and camelCase for TypeScript/JavaScript, consistent with the architecture.
    4. **Validation**: All user-provided data must be validated and sanitized before processing or storage.

    REQUIRED FILES:
    - Backend: Main entry point, Pydantic schemas, database models (SQLAlchemy), API routes, security utils, requirements.txt, and a Dockerfile.
    - Frontend: Main page, API client, reusable components, TypeScript types, package.json, and a Dockerfile.
    - Infrastructure: docker-compose.yml for orchestration, .env.example, and a comprehensive README.md with setup instructions.

    Ensure the code is functional, modular, and matches the architecture perfectly. Provide the actual files now."""            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "BuilderAgent",
                    "message": "Generating production-ready code files...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            raw_response = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                api_keys=self.api_keys,
                target_agent="BuilderAgent",
                temperature=0.2,
                max_tokens=8000,
                event_callback=event_callback
            )
            
            parsed_files = []
            if "===FILE:" in raw_response:
                chunks = raw_response.split("===FILE:")
                for chunk in chunks[1:]:
                    if not chunk.strip():
                        continue
                        
                    if "===END===" in chunk:
                        chunk = chunk.split("===END===")[0]
                        
                    lines = chunk.split('\n', 1)
                    if len(lines) >= 2:
                        path_line = lines[0].strip()
                        if path_line.endswith("==="):
                            path_line = path_line[:-3].strip()
                        content = lines[1].strip()
                        
                        if content.startswith("```"):
                            content = content.split('\n', 1)[-1] if '\n' in content else ""
                        if content.endswith("```"):
                            content = content.rsplit('\n', 1)[0] if '\n' in content else ""
                        
                        if content:
                            content += '\n'
                        
                        if path_line and content:
                            parsed_files.append({"path": path_line, "content": content})
            
            if not parsed_files:
                raise ValueError("No code files were parsed from the response.")
                
            safe_output = {
                "message": f"Successfully generated {len(parsed_files)} code files.",
                "files_generated": len(parsed_files),
                "file_tree": [f["path"] for f in parsed_files],
                "files": parsed_files
            }
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "BuilderAgent",
                    "data": safe_output,
                    "timestamp": end_time.isoformat()
                })
            
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "BuilderAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            return safe_output
            
        except Exception as e:
            logger.error("Implementation plan generation failed", error=str(e))
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "BuilderAgent",
                    "error": str(e),
                    "details": "Failed to generate codebase",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            raise e
    
    def _create_fallback_implementation(
        self, 
        strategy_output: Union[str, Dict[str, Any]],
        architecture_output: Union[str, Dict[str, Any]],
        raw_output: str = ""
    ) -> Dict[str, Any]:
        """Create a fallback implementation codebase"""
        logger.warning(f"Fallback triggered for BuilderAgent. Raw error/output: {raw_output}")
        
        return {
            "message": "Generated fallback codebase due to processing error.",
            "files": [
                {
                    "path": "backend/main.py",
                    "content": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}\n"
                },
                {
                    "path": "backend/requirements.txt",
                    "content": "fastapi\nuvicorn\n"
                },
                {
                    "path": "frontend/package.json",
                    "content": "{\n  \"name\": \"frontend\",\n  \"version\": \"0.1.0\",\n  \"scripts\": {\n    \"dev\": \"next dev\"\n  }\n}"
                },
                {
                    "path": "frontend/src/app/page.tsx",
                    "content": "export default function Home() {\n  return <div>Welcome to the App</div>;\n}\n"
                },
                {
                    "path": "README.md",
                    "content": "# Generated Project\n\nRun backend with `uvicorn main:app --reload`.\nRun frontend with `npm run dev`.\n"
                }
            ]
        }