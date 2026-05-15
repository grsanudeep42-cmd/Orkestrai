"""
Product Strategy Agent - Transforms ideas into structured product requirements
Uses Groq API for fast LLM inference
"""
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import json
from groq import Groq
from app.config import settings
import structlog

logger = structlog.get_logger()


class StrategyAgent:
    """Product Strategy Agent for analyzing project ideas using Groq"""
    
    def __init__(self):
        """Initialize the Strategy Agent with Groq"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not set in environment")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        
        self.system_prompt = """You are an expert product strategist with 10+ years of experience 
in startup MVPs and rapid prototyping. You excel at extracting core problems, 
identifying target users, and defining clear feature priorities.

Your role is to transform vague project ideas into structured product requirements and MVP scope.
You analyze projects to create comprehensive product strategies that teams can immediately act upon."""
    
    async def analyze_project(
        self, 
        user_input: str, 
        preferences: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze user input and generate product strategy
        
        Args:
            user_input: The user's project description
            preferences: Optional user preferences
            event_callback: Optional callback for real-time events
            
        Returns:
            Dictionary containing strategy output
        """
        start_time = datetime.utcnow()
        
        try:
            # Emit start event
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "ProductStrategyAgent",
                    "timestamp": start_time.isoformat()
                })
            
            # Create the analysis prompt
            user_prompt = f"""Analyze the following project idea and create a comprehensive product strategy:

PROJECT IDEA:
{user_input}

USER PREFERENCES:
{json.dumps(preferences or {}, indent=2)}

Your analysis must include:
1. **Problem Statement**: Clear articulation of the problem being solved
2. **Target Users**: Specific user personas and their needs
3. **Core Features**: 5-8 essential features with priority levels (high/medium/low)
4. **MVP Scope**: What should be built first for a working prototype
5. **User Stories**: 3-5 key user stories with acceptance criteria
6. **Tech Constraints**: Any technical considerations or requirements

Format your response as a valid JSON object with these exact keys:
- project_name: string
- problem_statement: string
- target_users: array of strings
- core_features: array of objects with {{name, priority, user_story, acceptance_criteria}}
- mvp_scope: array of strings
- tech_constraints: array of strings
- success_metrics: array of strings

Be specific, actionable, and focused on rapid MVP development."""
            
            # Emit thinking event
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "ProductStrategyAgent",
                    "message": "Analyzing project requirements and defining MVP scope...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Call Groq API
            logger.info("Calling Groq API", model=self.model)
            
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
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            result = chat_completion.choices[0].message.content
            
            # Parse the result
            try:
                # Try to extract JSON from the result
                result_str = str(result)
                # Find JSON content between curly braces
                start_idx = result_str.find('{')
                end_idx = result_str.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = result_str[start_idx:end_idx]
                    strategy_output = json.loads(json_str)
                else:
                    # Fallback: create structured output
                    strategy_output = self._create_fallback_strategy(user_input, result_str)
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse JSON from Groq response", error=str(e))
                # Fallback: create structured output from text
                strategy_output = self._create_fallback_strategy(user_input, str(result))
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Emit output event
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "ProductStrategyAgent",
                    "data": strategy_output,
                    "timestamp": end_time.isoformat()
                })
            
            # Emit complete event
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "ProductStrategyAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info("Strategy analysis complete", duration_ms=duration_ms)
            return strategy_output
            
        except Exception as e:
            logger.error("Strategy analysis failed", error=str(e))
            # Emit error event
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "ProductStrategyAgent",
                    "error": str(e),
                    "details": "Failed to analyze project requirements",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Return fallback strategy instead of raising
            return self._create_fallback_strategy(user_input, f"Error: {str(e)}")
    
    def _create_fallback_strategy(self, user_input: str, raw_output: str) -> Dict[str, Any]:
        """Create a fallback strategy structure when JSON parsing fails or API errors occur"""
        return {
            "project_name": "Generated Project",
            "problem_statement": f"Building a solution based on: {user_input[:200]}...",
            "target_users": ["End users", "Developers", "Business stakeholders"],
            "core_features": [
                {
                    "name": "Core Functionality",
                    "priority": "high",
                    "user_story": "As a user, I want to use the main features",
                    "acceptance_criteria": ["Feature works as expected", "User can complete tasks"]
                },
                {
                    "name": "User Interface",
                    "priority": "high",
                    "user_story": "As a user, I want an intuitive interface",
                    "acceptance_criteria": ["UI is responsive", "Navigation is clear"]
                },
                {
                    "name": "Data Management",
                    "priority": "medium",
                    "user_story": "As a user, I want to manage my data",
                    "acceptance_criteria": ["Data persists", "CRUD operations work"]
                }
            ],
            "mvp_scope": [
                "Basic user interface",
                "Core functionality implementation",
                "Data persistence",
                "Essential user workflows"
            ],
            "tech_constraints": [
                "Must be web-based",
                "Should be scalable",
                "Needs to be maintainable"
            ],
            "success_metrics": [
                "User can complete core tasks",
                "System is stable",
                "Performance is acceptable"
            ],
            "raw_analysis": raw_output[:500] if raw_output else "No output available"
        }

# Made with Bob
