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
    
    def __init__(self):
        self.system_prompt = """You are an elite Senior Principal Software Engineer. 
You write actual, functional, production-ready code. 
- You MUST generate REAL CODE files, not a plan, not pseudocode, and not TODOs.
- Provide the complete file content for each file requested.
- Return files using this exact delimiter format:

===FILE: path/to/file.py===
file content here
===FILE: path/to/other/file.js===
other content here
===END===

- Ensure the backend and frontend code actually work and map to the architecture.
- If you receive feedback from the AuditAgent, correct your course immediately."""
    
    async def generate_implementation_plan(
        self, 
        strategy_output: Union[str, Dict[str, Any]],
        architecture_output: Union[str, Dict[str, Any]],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate actual code based on strategy and architecture
        """
        start_time = datetime.utcnow()
        project_id = memory.get("project_id", str(uuid.uuid4())) if memory else str(uuid.uuid4())
        
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

            user_prompt = f"""Based on the product strategy and system architecture, generate the ACTUAL CODE FILES for a complete scaffold:

PROJECT IDEA:
{safe_input}

PRODUCT STRATEGY:
{strategy_text}

SYSTEM ARCHITECTURE:
{arch_text}

USER PREFERENCES:
{json.dumps(preferences or {})}
{memory_context}

You must generate the ACTUAL CODE FILES for the project. 
Do not provide a plan. Provide the functional code.
Generate at minimum:
- Backend: main.py, models, routes, config, requirements.txt, Dockerfile
- Frontend: page.tsx, components, hooks, package.json, Dockerfile
- Root: docker-compose.yml, .env.example, README.md

Ensure the code is robust and follows the architecture precisely."""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "BuilderAgent",
                    "message": "Generating actual code files and creating project scaffold...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for BuilderAgent")
            
            # Use generate_text for generation with high max_tokens to prevent truncation
            raw_response = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                target_agent="BuilderAgent",
                temperature=0.2,
                max_tokens=8000,
                event_callback=event_callback
            )
            
            # Parse the raw response using string splitting on ===FILE:
            parsed_files = []
            if "===FILE:" in raw_response:
                chunks = raw_response.split("===FILE:")
                for chunk in chunks[1:]:  # Skip everything before the first file
                    if not chunk.strip():
                        continue
                        
                    if "===END===" in chunk:
                        chunk = chunk.split("===END===")[0]
                        
                    lines = chunk.split('\n', 1)
                    if len(lines) >= 2:
                        path_line = lines[0].strip()
                        if path_line.endswith("==="):
                            path_line = path_line[:-3].strip()
                        content = lines[1]
                        
                        # Strip markdown backticks from the content if present
                        content = content.strip()
                        if content.startswith("```"):
                            # Remove the first line (e.g., ```python)
                            content = content.split('\n', 1)[-1] if '\n' in content else ""
                        if content.endswith("```"):
                            # Remove the last line (e.g., ```)
                            content = content.rsplit('\n', 1)[0] if '\n' in content else ""
                            
                        # Ensure content ends with a newline
                        if content:
                            content += '\n'
                        
                        if path_line and content:
                            parsed_files.append({"path": path_line, "content": content})
            
            if not parsed_files:
                raise ValueError("No files parsed from LLM response.")
                
            generated_data = {
                "message": f"Successfully generated {len(parsed_files)} files.",
                "files": parsed_files
            }
            
            # Post process to zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_obj in generated_data.get("files", []):
                    zip_file.writestr(file_obj["path"], file_obj["content"])
            
            # Save zip file to static directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            static_dir = os.path.join(base_dir, "static", "generated")
            os.makedirs(static_dir, exist_ok=True)
            zip_filename = f"{project_id}.zip"
            zip_path = os.path.join(static_dir, zip_filename)
            with open(zip_path, "wb") as f:
                f.write(zip_buffer.getvalue())
            
            zip_url = f"/static/generated/{zip_filename}"
            
            # Create final output dict
            safe_output = {
                "message": generated_data.get("message", "Successfully generated codebase"),
                "files_generated": len(generated_data.get("files", [])),
                "zip_url": zip_url,
                "file_tree": [f["path"] for f in generated_data.get("files", [])],
                "zip_path": zip_path,  # for other agents like GitHubAgent
                "files": generated_data.get("files", [])
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
            
            logger.info("Implementation code generation complete", duration_ms=duration_ms)
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
            
            # In case of failure, return fallback zip logic
            fallback_data = self._create_fallback_implementation(strategy_output, architecture_output, f"Error: {str(e)}")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_obj in fallback_data.get("files", []):
                    zip_file.writestr(file_obj["path"], file_obj["content"])
            
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            static_dir = os.path.join(base_dir, "static", "generated")
            os.makedirs(static_dir, exist_ok=True)
            zip_filename = f"{project_id}_fallback.zip"
            zip_path = os.path.join(static_dir, zip_filename)
            with open(zip_path, "wb") as f:
                f.write(zip_buffer.getvalue())
            
            return {
                "message": fallback_data.get("message", "Fallback generated"),
                "files_generated": len(fallback_data.get("files", [])),
                "zip_url": f"/static/generated/{zip_filename}",
                "file_tree": [f["path"] for f in fallback_data.get("files", [])],
                "zip_path": zip_path,
                "files": fallback_data.get("files", [])
            }
    
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