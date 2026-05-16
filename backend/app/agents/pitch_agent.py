"""
Pitch Agent - Generates an HTML presentation deck
"""
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import structlog
import json
import os
import uuid
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

logger = structlog.get_logger()

class PitchAgent(BaseAgent):
    """Pitch Agent for generating HTML presentations"""
    
    def __init__(self):
        self.system_prompt = """You are an elite Startup Founder and Storyteller.
You MUST generate a complete HTML presentation with MULTIPLE slides covering:
1) Title slide - Project name and tagline
2) Problem Statement - The pain point being addressed
3) Market Opportunity - TAM, SAM, SOM analysis
4) Solution - How your product solves the problem
5) Core Features - Key functionality and differentiators
6) Tech Stack - Technology choices and architecture
7) Business Model - Revenue streams and pricing
8) Team and Roadmap - Milestones and go-to-market plan

Each slide must be a separate scrollable section. Include navigation arrows between slides. Use a dark theme with modern typography. Include JavaScript for basic slide navigation (left/right arrows). The presentation MUST NOT use generic placeholder text; derive data from the project inputs. Do NOT generate a single landing page.

Return ONLY raw HTML. No JSON wrapper. No markdown code fences. No explanation. Start your response with <!DOCTYPE html> and end with </html>."""
    
    async def generate_pitch_materials(
        self, 
        strategy_output: Dict[str, Any] | str,
        architecture_output: Dict[str, Any] | str,
        implementation_output: Dict[str, Any],
        github_output: Dict[str, Any],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate pitch materials as an HTML file
        """
        start_time = datetime.utcnow()
        project_id = memory.get("project_id", str(uuid.uuid4())) if memory else str(uuid.uuid4())
        
        try:
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "PitchAgent",
                    "timestamp": start_time.isoformat()
                })
            
            memory_context = self.format_memory(memory)
            safe_input = self.sanitize_input(user_input)
            
            strategy_text = strategy_output if isinstance(strategy_output, str) else json.dumps(strategy_output)

            user_prompt = f"""Based on the project data, create a stunning HTML presentation deck.

PROJECT IDEA:
{safe_input}

PRODUCT STRATEGY:
{strategy_text[:1000]}

IMPLEMENTATION RESULTS:
Code generated: {implementation_output.get("files_generated", 0)} files
GitHub Repo: {github_output.get("repository_url", "")}

Generate the full HTML content.
"""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "PitchAgent",
                    "message": "Designing HTML presentation deck...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for PitchAgent")
            
            raw_response = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                target_agent="PitchAgent",
                temperature=0.6,
                max_tokens=8000,
                event_callback=event_callback
            )

            html = raw_response.strip()
            if html.startswith('```'):
                html = html.split('\n', 1)[1].rsplit('```', 1)[0].strip()
                
            if not html or "<html" not in html.lower():
                raise ValueError("Response does not contain valid HTML.")
            
            # Save HTML file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            static_dir = os.path.join(base_dir, "static", "generated")
            os.makedirs(static_dir, exist_ok=True)
            html_filename = f"{project_id}_pitch.html"
            html_path = os.path.join(static_dir, html_filename)
            with open(html_path, "w") as f:
                f.write(html)
            
            html_url = f"/static/generated/{html_filename}"

            output_data = {
                "presentation_url": html_url,
                "message": "HTML pitch deck generated successfully."
            }
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "PitchAgent",
                    "data": output_data,
                    "timestamp": end_time.isoformat()
                })
            
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "PitchAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info("Pitch materials complete", duration_ms=duration_ms)
            return output_data
            
        except Exception as e:
            logger.error("Pitch materials failed", error=str(e))
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "PitchAgent",
                    "error": str(e),
                    "details": "Failed to generate pitch materials",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            fallback = self._create_fallback_pitch(strategy_output, f"Error: {str(e)}")
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            static_dir = os.path.join(base_dir, "static", "generated")
            os.makedirs(static_dir, exist_ok=True)
            html_filename = f"{project_id}_pitch_fallback.html"
            html_path = os.path.join(static_dir, html_filename)
            with open(html_path, "w") as f:
                f.write(fallback.get("html_content", "<html></html>"))
                
            return {
                "presentation_url": f"/static/generated/{html_filename}",
                "message": "Fallback generated."
            }
    
    def _create_fallback_pitch(self, strategy_output: Dict[str, Any] | str, raw_output: str = "") -> Dict[str, Any]:
        """Create fallback pitch"""
        return {
            "html_content": "<html><body style='background: #111; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh;'><h1>Generated Pitch Deck</h1></body></html>"
        }