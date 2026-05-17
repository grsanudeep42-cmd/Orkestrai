"""
Builder Agent - Generates actual code files and packages them into a zip archive
"""
from typing import Dict, Any, Callable, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel
import structlog
import json
import zipfile
import io
import os
import uuid
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

logger = structlog.get_logger()

class FileDefinition(BaseModel):
    path: str
    description: str

class ArchitectureFileTree(BaseModel):
    files: List[FileDefinition]

class BuilderAgent(BaseAgent):
    """Builder Agent for generating real code scaffold"""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)
        self.boilerplates = self._load_boilerplates()
        self.system_prompt = f"""You are an elite Senior Principal Software Engineer and System Architect. 
You write production-ready, clean, and functional code that prioritizes security, robustness, and maintainability.

CORE RESPONSIBILITIES:
1) Clean Code - Functional, modular, and DRY (Don't Repeat Yourself) principles.
2) Security First - Use Pydantic for input validation, password hashing (e.g., passlib), and sanitization to prevent injection.
3) Robust Error Handling - Explicit try/except blocks and standardized error responses.
4) Comprehensive Documentation - Clear docstrings, comments for complex logic, and a detailed README.
5) Seamless Integration - Ensure backend and frontend are perfectly connected.

BOILERPLATE FOUNDATION (USE THESE AS STARTING POINTS):
- Backend Main: {self.boilerplates.get('fastapi_main', 'Standard FastAPI setup')}
- Frontend Page: {self.boilerplates.get('nextjs_page', 'Standard Next.js page')}
- Docker Compose: {self.boilerplates.get('docker_compose', 'Standard docker-compose')}

CRITICAL INSTRUCTIONS:
- You MUST generate REAL CODE files for a complete project scaffold.
- DO NOT use placeholders, TODOs, or pseudocode.
- Use best practices for the chosen stack (e.g., async/await for Python, type safety in TypeScript).
- Implement explicit authentication and authorization flows (e.g., JWT).
- STICK RIGIDLY to the provided Architectural Specifications.
- Return files using this exact delimiter format:

===FILE: path/to/file.py===
file content here
===FILE: path/to/other/file.js===
other content here
===END===

- Be concise but complete. Do not truncate files."""

    def _load_boilerplates(self) -> Dict[str, str]:
        """Load boilerplate templates from the filesystem"""
        templates = {}
        base_path = os.path.join(os.path.dirname(__file__), "boilerplates")
        try:
            if os.path.exists(base_path):
                mapping = {
                    "fastapi_main": "fastapi_main.py.tmpl",
                    "nextjs_page": "nextjs_page.tsx.tmpl",
                    "docker_compose": "docker-compose.yml.tmpl",
                    "backend_dockerfile": "backend-Dockerfile.tmpl",
                    "backend_requirements": "backend-requirements.txt.tmpl",
                    "frontend_dockerfile": "frontend-Dockerfile.tmpl",
                    "frontend_package_json": "frontend-package.json.tmpl",
                    "gitignore": "gitignore.tmpl",
                    "readme": "README.md.tmpl"
                }
                for key, filename in mapping.items():
                    file_path = os.path.join(base_path, filename)
                    if os.path.exists(file_path):
                        with open(file_path, "r") as f:
                            templates[key] = f.read()
            return templates
        except Exception as e:
            logger.warning(f"Failed to load boilerplates: {e}")
            return {}

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

            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "BuilderAgent",
                    "message": "Step 1: Planning file architecture...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            tree_prompt = f"""You are a strict parser. Based on the following Architectural Specifications, list EVERY file that needs to be created.
Do not generate code, only the file paths and a brief description of what goes in them.

ARCHITECTURAL SPECIFICATIONS:
{arch_text}

Provide the output strictly conforming to the JSON schema."""

            file_tree_result = await llm_router.generate_structured(
                system_prompt="You extract file trees from architecture documents.",
                user_prompt=tree_prompt,
                response_model=ArchitectureFileTree,
                api_keys=self.api_keys,
                target_agent="BuilderAgent",
                temperature=0.1
            )
            
            parsed_files = []
            files_to_generate = []
            
            # Phase 2: Programmatic Boilerplate Injection
            for file_def in file_tree_result.files:
                path = file_def.path
                if "backend/main.py" in path and "fastapi_main" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["fastapi_main"]})
                elif ("page.tsx" in path or "page.js" in path) and "nextjs_page" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["nextjs_page"]})
                elif "docker-compose.yml" in path and "docker_compose" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["docker_compose"]})
                elif "backend/Dockerfile" in path and "backend_dockerfile" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["backend_dockerfile"]})
                elif "backend/requirements.txt" in path and "backend_requirements" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["backend_requirements"]})
                elif "frontend/Dockerfile" in path and "frontend_dockerfile" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["frontend_dockerfile"]})
                elif "frontend/package.json" in path and "frontend_package_json" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["frontend_package_json"]})
                elif ".gitignore" in path and "gitignore" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["gitignore"]})
                elif "README.md" in path and "readme" in self.boilerplates:
                    parsed_files.append({"path": path, "content": self.boilerplates["readme"]})
                else:
                    files_to_generate.append(file_def)
            
            # Phase 3: Chunked Code Generation
            if files_to_generate:
                if event_callback:
                    await event_callback({
                        "type": "agent_thinking",
                        "agent": "BuilderAgent",
                        "message": f"Step 2: Generating code for {len(files_to_generate)} files in chunks...",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                chunk_size = 5
                for i in range(0, len(files_to_generate), chunk_size):
                    chunk = files_to_generate[i:i + chunk_size]
                    chunk_files_str = "\n".join([f"- {f.path}: {f.description}" for f in chunk])
                    
                    code_prompt = f"""You are an elite Senior Principal Software Engineer. 
Generate the ACTUAL code for the following files:
{chunk_files_str}

PROJECT IDEA:
{safe_input}

STRATEGY & GOALS:
{strategy_text}

ARCHITECTURAL SPECIFICATIONS:
{arch_text}

Return files using this exact delimiter format:
===FILE: path/to/file.py===
file content here
===END===
"""
                    
                    raw_response = await llm_router.generate_text(
                        system_prompt=self.system_prompt,
                        user_prompt=code_prompt,
                        api_keys=self.api_keys,
                        target_agent="BuilderAgent",
                        temperature=0.1,
                        max_tokens=8000,
                        event_callback=None,
                        provider_hint="bob"
                    )
            

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
            
            # Use fallback mechanism
            fallback_output = self._create_fallback_implementation(
                strategy_output=strategy_output,
                architecture_output=architecture_output,
                raw_output=str(e)
            )
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "BuilderAgent",
                    "data": fallback_output,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "BuilderAgent",
                    "duration_ms": 0,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return fallback_output
    
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