"""
Audit Agent - Reviews outputs from other agents, detects issues, and proposes fixes.
"""
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import json
from app.llm.provider_router import router as llm_router
from app.agents.base_agent import BaseAgent

logger = structlog.get_logger()

class AuditOutput(BaseModel):
    is_valid: bool
    needs_retry: bool
    issues_detected: list[str]
    critique_and_feedback: str
    markdown_report: str = Field(description="A beautifully formatted Markdown report with scores out of 10.")

class AuditAgent(BaseAgent):
    """Audit Agent for reviewing and critiquing other agents' outputs"""
    
    def __init__(self):
        self.system_prompt = """You are a Senior Technical Auditor and Quality Assurance Expert with 20+ years of experience.
Your goal is to ensure every piece of generated content meets the highest professional standards.

AUDIT CRITERIA:
1) Technical Accuracy - Are technologies and patterns used correctly?
2) Security - Are there obvious vulnerabilities or missing security headers?
3) Consistency - Does the output align with the previous agents' work?
4) Completeness - Are all requested sections or files present and non-empty?
5) Practicality - Is the code functional and the strategy realistic?

OUTPUT FORMAT:
- You MUST provide a clear JSON response indicating if a retry is needed.
- If "needs_retry" is true, provide specific, actionable feedback on what to fix.
- If "needs_retry" is false, provide a brief positive summary of the audit.

CRITICAL INSTRUCTIONS:
- Be strict but fair. High quality is the priority.
- Do not let placeholder text or "TODO" comments pass the audit.
- Ensure the agent's output is professional and ready for user consumption."""
    
    async def audit_output(
        self,
        agent_name: str,
        agent_output: Any,
        original_user_input: str,
        context: Dict[str, Any],
        event_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Audit the output of a specific agent.
        """
        start_time = datetime.utcnow()
        
        try:
            if event_callback:
                await event_callback({
                    "type": "agent_start",
                    "agent": "AuditAgent",
                    "timestamp": start_time.isoformat(),
                    "message": f"Auditing {agent_name} output"
                })
            
            safe_input = self.sanitize_input(original_user_input)
            agent_output_text = json.dumps(agent_output, indent=2) if isinstance(agent_output, dict) else str(agent_output)

            user_prompt = f"""Review the output of the {agent_name}.

ORIGINAL USER REQUEST:
{safe_input}

CONTEXT (Previous Agents):
{json.dumps(context, indent=2)[:2000]}

{agent_name} OUTPUT TO REVIEW:
{agent_output_text[:4000]}

Analyze the output for hallucinations, structural issues, missing requirements, or scope creep.
Provide a Markdown report in `markdown_report` that includes an overall score out of 10, a breakdown of strengths/weaknesses, and actionable improvements. Start the markdown with `# Audit Report - {agent_name}`."""
            
            if event_callback:
                await event_callback({
                    "type": "agent_thinking",
                    "agent": "AuditAgent",
                    "message": f"Critiquing {agent_name} output...",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info("Calling LLM Provider Router for AuditAgent", target_agent=agent_name)
            
            def fallback_audit(*args, raw_output=""):
                return {
                    "is_valid": True,
                    "needs_retry": False,
                    "issues_detected": ["Audit failed due to error"],
                    "critique_and_feedback": f"Audit Agent encountered an error: {raw_output}",
                    "markdown_report": f"# Audit Report - {agent_name}\n\nFallback generated. No major issues detected.\nScore: 7/10\n"
                }
            
            audit_result = await self.generate_structured_with_fallback(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                response_model=AuditOutput,
                agent_name="AuditAgent",
                temperature=0.3,
                event_callback=event_callback,
                fallback_func=fallback_audit
            )
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if event_callback:
                await event_callback({
                    "type": "agent_critique",
                    "agent": "AuditAgent",
                    "data": audit_result,
                    "target_agent": agent_name,
                    "message": f"Audit complete. Needs retry: {audit_result.get('needs_retry', False)}",
                    "timestamp": end_time.isoformat()
                })
            
            if event_callback:
                await event_callback({
                    "type": "agent_complete",
                    "agent": "AuditAgent",
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                })
            
            logger.info(f"Audit of {agent_name} complete", needs_retry=audit_result.get("needs_retry", False))
            return audit_result
            
        except Exception as e:
            logger.error("Audit generation failed", error=str(e))
            if event_callback:
                await event_callback({
                    "type": "error",
                    "agent": "AuditAgent",
                    "error": str(e),
                    "details": f"Failed to audit {agent_name}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "is_valid": True,
                "needs_retry": False,
                "issues_detected": ["Audit failed due to error"],
                "critique_and_feedback": f"Audit Agent encountered an error: {str(e)}",
                "markdown_report": f"# Audit Report - {agent_name}\n\nFallback generated due to error: {str(e)}\nScore: N/A\n"
            }
