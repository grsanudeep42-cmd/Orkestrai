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
        self.system_prompt = """You are an elite Startup Founder, VC, and Lead Product Designer.
Your goal is to generate a world-class, high-conversion HTML pitch deck.

DESIGN SYSTEM:
- Framework: Tailwind CSS (<script src="https://cdn.tailwindcss.com"></script>)
- Typography: Inter (Google Fonts)
- Aesthetic: Modern Cyberpunk/SaaS. Use Slate-950 for backgrounds, Indigo-500 for primary actions, and Cyan-400 for accents.
- Icons: Use inline SVGs for professional icons (e.g., Lucide style).

SLIDE STRUCTURE (8-10 SLIDES):
1. **Hero**: Project name, futuristic tagline, "Built with OrkestrAI" badge.
2. **The Problem**: High-impact visualization of the pain point.
3. **The Solution**: How the product solves it, with a "magical" feel.
4. **Market Opportunity**: TAM/SAM/SOM with clean SVG charts.
5. **Core Features**: Feature grid with glassmorphism cards.
6. **Technical Edge**: Deep dive into the architecture and AI integration.
7. **Business Model**: Monetization and growth loops.
8. **Roadmap**: Interactive timeline showing the future vision.
9. **The Team/Closing**: Call to action and "Get Started" link.

TECHNICAL SPECS:
- Return ONLY raw HTML. No Markdown fences.
- MUST include Keyboard Navigation (Left/Right arrows) and On-screen controls.
- Use smooth CSS transitions (`transition-all`, `duration-500`).
- Ensure all content is project-specific. NO generic text.
- Use a fixed layout with a "Slides" container that scales to fit.

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
            
            # Use fallback mechanism
            fallback_output = self._create_fallback_pitch(
                strategy_output=strategy_output,
                raw_output=str(e)
            )
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "PitchAgent",
                    "data": fallback_output,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "PitchAgent",
                    "duration_ms": 0,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            return fallback_output
    
    def _create_fallback_pitch(self, strategy_output: Dict[str, Any] | str, raw_output: str = "") -> Dict[str, Any]:
        """Create fallback pitch"""
        return {
            "html_content": "<html><body style='background: #111; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh;'><h1>Generated Pitch Deck</h1></body></html>"
        }