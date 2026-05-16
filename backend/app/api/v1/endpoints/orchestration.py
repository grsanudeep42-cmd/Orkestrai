"""
Orchestration API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.db.models.project import Project
from app.db.models.user import User
from app.db.models.agent_log import AgentLog
from app.db.models.generated_artifact import GeneratedArtifact
from app.schemas.orchestration import OrchestrationStatus
from app.agents.strategy_agent import StrategyAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.builder_agent import BuilderAgent
from app.agents.github_agent import GitHubAgent
from app.agents.pitch_agent import PitchAgent
from app.agents.audit_agent import AuditAgent
from datetime import datetime
import structlog
import json

logger = structlog.get_logger()

router = APIRouter()

@router.get("/{project_id}/status", response_model=OrchestrationStatus)
async def get_orchestration_status(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get orchestration status for a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    logs_result = await db.execute(
        select(AgentLog)
        .where(AgentLog.project_id == project_id)
        .where(AgentLog.status == "completed")
    )
    completed_logs = logs_result.scalars().all()
    completed_agents = list(set([log.agent_name for log in completed_logs if log.agent_name != "AuditAgent"]))

    all_agents = ["ProductStrategyAgent", "ArchitectureAgent", "BuilderAgent", "GitHubAgent", "PitchAgent"]
    total_agents = len(all_agents)
    progress = int((len(completed_agents) / total_agents) * 100)

    current_agent = None
    if project.status == "orchestrating" and len(completed_agents) < total_agents:
        current_agent = all_agents[len(completed_agents)]

    remaining_agents = [a for a in all_agents if a not in completed_agents]
    
    return OrchestrationStatus(
        project_id=project_id,
        status=project.status,
        current_agent=current_agent,
        progress=progress,
        completed_agents=completed_agents,
        remaining_agents=remaining_agents,
        estimated_completion=None
    )


from fastapi import Request
from app.api.dependencies.rate_limiter import limiter

@router.post("/{project_id}/start")
@limiter.limit("10/minute")
async def start_orchestration(
    project_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start orchestration for a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status == "orchestrating":
        raise HTTPException(status_code=400, detail="Orchestration already in progress")

    if project.status == "completed":
        raise HTTPException(status_code=400, detail="Orchestration already completed. Create a new project to run again.")

    if project.status not in ["pending", "failed"]:
        raise HTTPException(status_code=400, detail=f"Cannot start orchestration: project status is {project.status}")
    
    project.status = "orchestrating"
    project.updated_at = datetime.utcnow()
    await db.commit()
    
    background_tasks.add_task(run_orchestration, project_id, current_user.id)
    
    return {"message": "Orchestration started", "project_id": project_id}


# Formatting functions...
def _format_dict_as_markdown(title: str, data: dict | str) -> str:
    """Fallback basic formatter"""
    if isinstance(data, str):
        return data
    return f"# {title}\n\n```json\n{json.dumps(data, indent=2)}\n```"

def _format_architecture_as_markdown(architecture: dict) -> str:
    return _format_dict_as_markdown("System Architecture", architecture)

def _format_implementation_as_markdown(implementation: dict) -> str:
    return _format_dict_as_markdown("Implementation Plan", implementation)

def _format_strategy_as_markdown(strategy: dict) -> str:
    return _format_dict_as_markdown("Product Strategy", strategy)

def _format_github_as_markdown(github: dict) -> str:
    return _format_dict_as_markdown("GitHub Setup", github)

def _format_pitch_as_markdown(pitch: dict) -> str:
    return _format_dict_as_markdown("Pitch Materials", pitch)


async def execute_agent_with_review(
    agent_name: str,
    generation_func: callable,
    audit_agent: AuditAgent,
    original_user_input: str,
    context: dict,
    event_callback: callable,
    db: AsyncSession,
    project_id: str,
    max_retries: int = 2
) -> dict:
    """Executes an agent and puts it through the Audit review loop"""
    retries = 0
    memory = {
        "audit_feedback": None,
        "shared_context": context,
        "retry_count": 0
    }
    
    while retries <= max_retries:
        if retries > 0:
            await event_callback({
                "type": "agent_retry",
                "agent": agent_name,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Retrying {agent_name} (Attempt {retries}/{max_retries}) based on feedback."
            })
            
        # 1. Generate Output
        result = await generation_func(memory=memory)
        
        # 2. Audit Output
        audit_result = await audit_agent.audit_output(
            agent_name=agent_name,
            agent_output=result,
            original_user_input=original_user_input,
            context=context,
            event_callback=event_callback
        )
        
        # Save audit log
        audit_log = AgentLog(
            project_id=project_id,
            agent_name="AuditAgent",
            action=f"audit_{agent_name}",
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            full_output=audit_result if isinstance(audit_result, dict) else {"markdown_report": str(audit_result)}
        )
        db.add(audit_log)
        await db.commit()
        
        if not audit_result.get("needs_retry", False) or retries == max_retries:
            return result
            
        # Update memory for next retry
        memory["audit_feedback"] = audit_result.get("critique_and_feedback", "")
        memory["retry_count"] = retries + 1
        retries += 1
        
    return result


async def run_orchestration(project_id: str, user_id: str):
    """
    Run the orchestration process with autonomous review loops
    """
    from app.db.session import AsyncSessionLocal
    from app.api.v1.endpoints.websocket import manager
    
    logger.info("Starting orchestration", project_id=project_id, user_id=user_id)
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch project and user
            proj_result = await db.execute(select(Project).where(Project.id == project_id))
            project = proj_result.scalar_one_or_none()
            
            user_result = await db.execute(select(User).where(User.id == user_id))
            current_user = user_result.scalar_one_or_none()
            
            if not project or not current_user:
                logger.error("Project or User not found", project_id=project_id, user_id=user_id)
                return
            
            await manager.broadcast_to_project(
                project_id,
                {
                    "type": "connection_established",
                    "project_id": project_id,
                    "message": "Orchestration started",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            async def on_agent_event(data: dict):
                await manager.broadcast_to_project(project_id, {
                    "project_id": project_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    **data
                })
            
            audit_agent = AuditAgent()
            context = {}
            
            # ===== AGENT 1: Strategy Agent =====
            strategy_agent = StrategyAgent()
            async def run_strategy(memory=None):
                return await strategy_agent.analyze_project(
                    user_input=project.user_input,
                    preferences=project.preferences,
                    memory=memory,
                    event_callback=on_agent_event
                )
                
            strategy_result = await execute_agent_with_review(
                "ProductStrategyAgent", run_strategy, audit_agent, project.user_input, context, on_agent_event, db, project_id
            )
            context["strategy"] = strategy_result
            await on_agent_event({
                "type": "memory_updated",
                "message": "Shared Execution Memory updated with Strategy context",
                "keys": list(context.keys())
            })
            
            strategy_log = AgentLog(project_id=project_id, agent_name="ProductStrategyAgent", action="generate_strategy", status="completed", full_output={"content": strategy_result} if isinstance(strategy_result, str) else strategy_result)
            db.add(strategy_log)
            db.add(GeneratedArtifact(project_id=project_id, generated_by="ProductStrategyAgent", artifact_type="strategy", content={"markdown": strategy_result} if isinstance(strategy_result, str) else strategy_result))
            await db.commit()
            
            # ===== AGENT 2: Architecture Agent =====
            architecture_agent = ArchitectureAgent()
            async def run_architecture(memory=None):
                return await architecture_agent.design_architecture(
                    strategy_output=strategy_result,
                    user_input=project.user_input,
                    preferences=project.preferences,
                    memory=memory,
                    event_callback=on_agent_event
                )
                
            architecture_result = await execute_agent_with_review(
                "ArchitectureAgent", run_architecture, audit_agent, project.user_input, context, on_agent_event, db, project_id
            )
            context["architecture"] = architecture_result
            await on_agent_event({
                "type": "memory_updated",
                "message": "Shared Execution Memory updated with Architecture context",
                "keys": list(context.keys())
            })
            
            arch_log = AgentLog(project_id=project_id, agent_name="ArchitectureAgent", action="design_architecture", status="completed", full_output={"content": architecture_result} if isinstance(architecture_result, str) else architecture_result)
            db.add(arch_log)
            db.add(GeneratedArtifact(project_id=project_id, generated_by="ArchitectureAgent", artifact_type="architecture", content={"markdown": architecture_result} if isinstance(architecture_result, str) else architecture_result))
            await db.commit()
            
            # ===== AGENT 3: Builder Agent =====
            builder_agent = BuilderAgent()
            async def run_builder(memory=None):
                return await builder_agent.generate_implementation_plan(
                    strategy_output=strategy_result,
                    architecture_output=architecture_result,
                    user_input=project.user_input,
                    preferences=project.preferences,
                    memory=memory,
                    event_callback=on_agent_event
                )
                
            implementation_result = await execute_agent_with_review(
                "BuilderAgent", run_builder, audit_agent, project.user_input, context, on_agent_event, db, project_id
            )
            context["implementation"] = implementation_result
            await on_agent_event({
                "type": "memory_updated",
                "message": "Shared Execution Memory updated with Implementation context",
                "keys": list(context.keys())
            })
            
            builder_log = AgentLog(project_id=project_id, agent_name="BuilderAgent", action="generate_implementation_plan", status="completed", full_output=implementation_result)
            db.add(builder_log)
            db.add(GeneratedArtifact(project_id=project_id, generated_by="BuilderAgent", artifact_type="implementation_plan", content=implementation_result))
            await db.commit()
            
            # ===== AGENT 4: GitHub Agent =====
            github_agent = GitHubAgent()
            async def run_github(memory=None):
                return await github_agent.generate_github_recommendations(
                    strategy_output=strategy_result,
                    architecture_output=architecture_result,
                    implementation_output=implementation_result,
                    user_input=project.user_input,
                    preferences=project.preferences,
                    memory=memory,
                    event_callback=on_agent_event,
                    current_user=current_user
                )
                
            github_result = await execute_agent_with_review(
                "GitHubAgent", run_github, audit_agent, project.user_input, context, on_agent_event, db, project_id
            )
            context["github"] = github_result
            await on_agent_event({
                "type": "memory_updated",
                "message": "Shared Execution Memory updated with GitHub context",
                "keys": list(context.keys())
            })
            
            github_log = AgentLog(project_id=project_id, agent_name="GitHubAgent", action="generate_github_recommendations", status="completed", full_output=github_result)
            db.add(github_log)
            db.add(GeneratedArtifact(project_id=project_id, generated_by="GitHubAgent", artifact_type="github_setup", content=github_result))
            await db.commit()
            
            # ===== AGENT 5: Pitch Agent =====
            pitch_agent = PitchAgent()
            async def run_pitch(memory=None):
                return await pitch_agent.generate_pitch_materials(
                    strategy_output=strategy_result,
                    architecture_output=architecture_result,
                    implementation_output=implementation_result,
                    github_output=github_result,
                    user_input=project.user_input,
                    preferences=project.preferences,
                    memory=memory,
                    event_callback=on_agent_event
                )
                
            pitch_result = await execute_agent_with_review(
                "PitchAgent", run_pitch, audit_agent, project.user_input, context, on_agent_event, db, project_id
            )
            
            pitch_log = AgentLog(project_id=project_id, agent_name="PitchAgent", action="generate_pitch_materials", status="completed", full_output=pitch_result)
            db.add(pitch_log)
            db.add(GeneratedArtifact(project_id=project_id, generated_by="PitchAgent", artifact_type="pitch_deck", content=pitch_result))
            await db.commit()
            
            # Update project status
            project.status = "completed"
            project.completed_at = datetime.utcnow()
            project.updated_at = datetime.utcnow()
            await db.commit()
            
            # Broadcast completion
            await manager.broadcast_to_project(
                project_id,
                {
                    "type": "orchestration_complete",
                    "project_id": project_id,
                    "message": "All agents completed successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error("Orchestration failed", project_id=project_id, error=str(e))
            
            try:
                result = await db.execute(
                    select(Project).where(Project.id == project_id)
                )
                project = result.scalar_one_or_none()
                if project:
                    project.status = "failed"
                    project.error_message = str(e)
                    project.updated_at = datetime.utcnow()
                    await db.commit()
                
                await manager.broadcast_to_project(
                    project_id,
                    {
                        "type": "error",
                        "project_id": project_id,
                        "message": f"Orchestration failed: {str(e)}",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as inner_e:
                logger.error("Failed to update project status", error=str(inner_e))
