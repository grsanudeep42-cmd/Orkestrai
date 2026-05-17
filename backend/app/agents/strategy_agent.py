"""
Product Strategy Agent - Transforms ideas into structured product requirements
"""
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import json
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

logger = structlog.get_logger()

# StrategyOutput model is removed as we are returning raw markdown

class StrategyAgent(BaseAgent):
    """Product Strategy Agent for analyzing project ideas"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__(api_keys)
        self.system_prompt = """You are an elite Product Strategy Consultant and Startup Advisor. 
Your goal is to transform a project idea into a comprehensive, actionable product strategy.

CORE RESPONSIBILITIES:
1) Executive Summary - High-level vision and "The Big Why".
2) User Personas - Define 2-3 detailed target user profiles.
3) Value Proposition - Unique selling points and competitive advantages.
4) Feature Roadmap - Categorized into MVP, Phase 2, and Future Vision.
5) Security & Compliance - Explicitly address data protection, authentication, and authorization.
6) Scalability & Performance - Technical considerations for growth and high traffic.
7) Monetization & Payments - Realistic revenue models and payment integration strategy (e.g., Stripe, PayPal).
8) Go-to-Market Plan - Initial launch and growth strategy.

CRITICAL INSTRUCTIONS:
- Be specific, data-driven, and creative. Avoid generic business jargon.
- If the project idea is vague, use your expertise to fill in logical, high-value gaps.
- Ensure the output is structured as professional Markdown.
- Focus on quality over quantity; every section must provide real strategic value."""
    
    async def analyze_project(
        self, 
        user_input: str, 
        preferences: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable] = None
    ) -> str:
        """
        Analyze user input and generate product strategy in Markdown
        """
        start_time = datetime.utcnow()
        
        try:
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "ProductStrategyAgent",
                    "timestamp": start_time.isoformat()
                })
            
            memory_context = self.format_memory(memory)
            safe_input = self.sanitize_input(user_input)

            user_prompt = f"""Analyze the following project idea and create an elite product strategy:

PROJECT IDEA:
{safe_input}

USER PREFERENCES:
{preferences or {}}
{memory_context}

Your analysis must include:
1. **Executive Summary**: High-level overview
2. **Problem & Market Opportunity**: Clear articulation of the problem with derived real numbers
3. **Target Users**: Specific user personas and their needs
4. **Core Features**: 5-8 essential features with priority levels and user stories
5. **Security & Data Privacy**: Detailed strategy for authentication (OAuth2/JWT), authorization (RBAC), and data encryption.
6. **Scalability & Payments**: Infrastructure growth plan and payment processing integration (e.g., Stripe).
7. **MVP Scope**: Ruthlessly prioritized scope for a working prototype
8. **Tech Stack Recommendation**: With specific justification for each choice (Frontend, Backend, DB, DevOps).
9. **Success Metrics**: With specific targets
10. **Competitive Landscape**: Naming real competitors
11. **Risks & Mitigations**: Potential challenges

IMPORTANT: Your entire output MUST be in cleanly formatted Markdown. DO NOT wrap it in JSON. Start directly with `# <Project Name> - Product Strategy`."""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "ProductStrategyAgent",
                    "message": "Analyzing project requirements and defining MVP scope...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for StrategyAgent")
            
            strategy_output = await llm_router.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                api_keys=self.api_keys,
                temperature=0.7,
                event_callback=event_callback,
                target_agent="ProductStrategyAgent",
                provider_hint="groq"
            )
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if event_callback:
                await event_callback({
                    "type": "agent_output",
                    "agent": "ProductStrategyAgent",
                    "data": strategy_output,
                    "timestamp": end_time.isoformat()
                })
            
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
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "ProductStrategyAgent",
                    "error": str(e),
                    "details": "Failed to analyze project requirements",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            raise e
    
    def _create_fallback_strategy(self, user_input: str, raw_output: str = "") -> str:
        """Create a fallback strategy structure in Markdown"""
        return f"""# Generated Project - Product Strategy

## Problem Statement
Building a solution based on: {user_input[:200]}...

## Target Users
- End users
- Developers
- Business stakeholders

## Core Features
1. **Core Functionality** (High Priority)
   - As a user, I want to use the main features
   - Acceptance Criteria: Feature works as expected, User can complete tasks

## MVP Scope
- Basic user interface
- Core functionality implementation

## Tech Constraints
- Must be web-based

## Success Metrics
- User can complete core tasks

*Raw analysis error: {raw_output[:500] if raw_output else "No output available"}*
"""
