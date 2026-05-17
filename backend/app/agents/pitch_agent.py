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
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)
        self.system_prompt = """You are an elite Startup Founder, Product Designer, and Storyteller.
Your goal is to generate a stunning, professional, and self-contained HTML presentation deck.

PRESENTATION STRUCTURE:
1) Title slide - Compelling project name and high-impact tagline.
2) Problem Statement - Clearly articulate the pain point being addressed.
3) Market Opportunity - TAM, SAM, SOM analysis with realistic data estimates.
4) Solution - How this product uniquely solves the problem.
5) Core Features - Key functionality and technical differentiators.
6) Tech Stack - Technology choices, architecture, and why they were selected.
7) Business Model - Revenue streams, pricing strategy, and go-to-market plan.
8) Roadmap - Future milestones and vision.

TECHNICAL REQUIREMENTS:
- Return ONLY raw HTML. No JSON wrapper. No markdown code fences.
- Use a modern, dark-themed CSS (e.g., Tailwind-like utility classes or custom professional CSS).
- Include JavaScript for smooth slide-to-slide navigation (using keyboard arrows and on-screen buttons).
- Use professional typography (e.g., Inter, System Fonts).
- Ensure the presentation is fully responsive and looks great on all screens.
- Derive all data from the project inputs; do NOT use generic placeholders.

Start your response with <!DOCTYPE html> and end with </html>."""
    
    async def generate_pitch_materials(
        self, 
        strategy_output: Dict[str, Any] | str,
        architecture_output: Dict[str, Any] | str,
        implementation_output: Dict[str, Any],
        github_output: Dict[str, Any],
        user_input: str,
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate pitch materials as an HTML content string
        """
        start_time = datetime.utcnow()
        
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

            user_prompt = f"""Create a world-class pitch deck for the following project:

PROJECT IDEA:
{safe_input}

PRODUCT STRATEGY:
{strategy_text[:1500]}

IMPLEMENTATION HIGHLIGHTS:
- Codebase: {implementation_output.get("files_generated", 0)} professional source files generated.
- GitHub Integration: {github_output.get("repository_url", "Prepared for deployment")}.

Generate the complete, self-contained HTML presentation now."""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "PitchAgent",
                    "message": "Crafting the professional presentation deck...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            raw_response = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                api_keys=self.api_keys,
                target_agent="PitchAgent",
                temperature=0.4,
                max_tokens=8000,
                event_callback=event_callback
            )

            html = raw_response.strip()
            if html.startswith('```'):
                html = html.split('\n', 1)[1].rsplit('```', 1)[0].strip()
                
            if not html or "<html" not in html.lower():
                raise ValueError("Generated response is not valid HTML.")
            
            output_data = {
                "html_content": html,
                "message": "Professional HTML pitch deck generated successfully."
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
            
            raise e
    
    def _create_fallback_pitch(self, strategy_output: Dict[str, Any] | str, raw_output: str = "") -> Dict[str, Any]:
        """Create fallback pitch"""
        return {
            "html_content": "<html><body style='background: #111; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh;'><h1>Generated Pitch Deck</h1></body></html>"
        }