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
        self.system_prompt = """You are an elite Startup Founder, Venture Capitalist, and Lead Product Designer.
Your goal is to generate a world-class, premium, and interactive HTML pitch deck that wows investors and users at first glance.

DESIGN SYSTEM & AESTHETIC:
- CSS Framework: Tailwind CSS (<script src="https://cdn.tailwindcss.com"></script>)
- Typography: Inter (Google Fonts - <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">)
- Theme: Premium Cyberpunk/SaaS Dark Mode.
  * Backgrounds: Deep space/midnight gradients (`bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950`).
  * Primary Actions: Indigo/violet glow (`bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.4)]`).
  * Accents & Highlights: Cyan neon (`text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]`), Magenta/Pink neon (`text-pink-500 drop-shadow-[0_0_8px_rgba(236,72,153,0.5)]`).
- Elements: Glassmorphic cards (`bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all duration-300`).
- Animations: Subtle glowing animations, pulsing lights, and hover-triggered micro-interactions.

SLIDE DECK FUNCTIONALITY (REQUIRED JAVASCRIPT INCLUDED):
- Keyboard Navigation: Support Left/Right arrows, Spacebar, PageUp/PageDown.
- On-screen Navigation: Include floating sleek futuristic buttons (Left, Right) with keyboard hints.
- Slide Progress Indicator: A glowing progress bar at the very top or bottom of the screen, with bubble indicators for active slide status.
- State Management: Hide inactive slides using CSS class `hidden`, show active slide with a smooth scale/fade-in animation (`animate-fade-in` or similar transition).

SLIDE STRUCTURE (8-10 HIGH-IMPACT SLIDES):
1. **Hero Slide (The Hook)**: Project name, a high-impact futuristic tagline, a glowing "Built with OrkestrAI" developer badge, and a call to action.
2. **The Problem (The Pain)**: Clean grid/comparison comparing the old, slow, painful manual way to run a business vs modern AI. Use high-contrast layouts.
3. **The Solution (The Magic)**: The core breakthrough. A simulated beautiful modern product screenshot or mock UI dashboard representing the solution.
4. **Market Opportunity**: Visually stunning TAM / SAM / SOM opportunity slide with customized SVG concentric circles, showing exponential growth potential.
5. **Technical Edge**: A premium architecture flow diagram built with inline SVGs showing AI orchestration, frontend/backend separation, and agentic workflows.
6. **Core Features**: A 3x3 interactive card grid highlighting features using beautiful glassmorphism cards and custom inline SVGs for icons.
7. **Business Model & TAM**: Monetization, SaaS pricing tiers, and growth loops shown in a beautiful side-by-side card comparison.
8. **Interactive Roadmap**: A chronological horizontal timeline with status checks (Completed, In Progress, Future) showing future vision.
9. **Call To Action (Close)**: Pitch closing, direct links to the generated GitHub repository, a "Get Started" button, and team details.

TECHNICAL SPECIFICATION:
- Return ONLY raw HTML. DO NOT wrap in Markdown code fences (e.g. ```html).
- The presentation must be completely self-contained. All styles, custom animations, SVGs, and JavaScript must be inline or embedded.
- Ensure all text is hyper-customized to the specific Project Strategy and Idea provided. DO NOT use placeholders, "Lorem Ipsum", or generic text.
- Standard Slide Aspect Ratio: Optimize for widescreen (16:9) presentation using a clean centring container.

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