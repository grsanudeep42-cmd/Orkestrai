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
    Start or resume orchestration for a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status == "completed":
        raise HTTPException(status_code=400, detail="Orchestration already completed. Create a new project to run again.")

    # We allow "orchestrating" to be re-started in case the background task died
    if project.status == "orchestrating":
        # If updated in last 30 seconds, it might be truly active
        if (datetime.utcnow() - project.updated_at).total_seconds() < 30:
            return {"message": "Orchestration is already active", "project_id": project_id}
    
    project.status = "orchestrating"
    project.updated_at = datetime.utcnow()
    await db.commit()
    
    background_tasks.add_task(run_orchestration, project_id, current_user.id)
    
    return {"message": "Orchestration started/resumed", "project_id": project_id}


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
    Run the orchestration process with autonomous review loops.
    Supports resuming from existing artifacts.
    """
    from app.db.session import AsyncSessionLocal
    from app.api.v1.endpoints.websocket import manager
    
    logger.info("Starting/Resuming orchestration", project_id=project_id, user_id=user_id)
    
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
            
            # Fetch existing artifacts to support resuming
            artifacts_result = await db.execute(
                select(GeneratedArtifact).where(GeneratedArtifact.project_id == project_id)
            )
            existing_artifacts = {a.artifact_type: a.content for a in artifacts_result.scalars().all()}
            
            await manager.broadcast_to_project(
                project_id,
                {
                    "type": "connection_established",
                    "project_id": project_id,
                    "message": "Orchestration resumed" if existing_artifacts else "Orchestration started",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            async def on_agent_event(data: dict):
                # Update project updated_at to indicate activity
                try:
                    # We need to refresh the project object because it might be detached or updated elsewhere
                    # For simplicity in this background task, we'll just try to update it
                    project.updated_at = datetime.utcnow()
                    await db.commit()
                except Exception as update_err:
                    logger.warning(f"Failed to update project heartbeat: {update_err}")
                
                await manager.broadcast_to_project(project_id, {
                    "project_id": project_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    **data
                })
            
            # Prepare API keys from user profile
            api_keys = {
                "openai": current_user.openai_key,
                "gemini": current_user.gemini_key,
                "groq": current_user.groq_key,
                "openrouter": current_user.openrouter_key,
                "bob": current_user.bob_key
            }
            
            audit_agent = AuditAgent(api_keys=api_keys)
            context = {}
            
            # Populate context from existing artifacts
            for atype, content in existing_artifacts.items():
                if atype == "strategy":
                    context["strategy"] = content.get("markdown") if isinstance(content, dict) else content
                elif atype == "architecture":
                    context["architecture"] = content.get("markdown") if isinstance(content, dict) else content
                elif atype == "implementation_plan":
                    context["implementation"] = content
                elif atype == "github_setup":
                    context["github"] = content
                elif atype == "pitch_deck":
                    context["pitch"] = content

            # ===== AGENT 1: Strategy Agent =====
            strategy_result = context.get("strategy")
            if not strategy_result:
                strategy_agent = StrategyAgent(api_keys=api_keys)
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
                
                strategy_log = AgentLog(project_id=project_id, agent_name="ProductStrategyAgent", action="generate_strategy", status="completed", full_output={"content": strategy_result} if isinstance(strategy_result, str) else strategy_result)
                db.add(strategy_log)
                db.add(GeneratedArtifact(project_id=project_id, generated_by="ProductStrategyAgent", artifact_type="strategy", content={"markdown": strategy_result} if isinstance(strategy_result, str) else strategy_result))
                await db.commit()
            else:
                await on_agent_event({
                    "type": "agent_skip",
                    "agent": "ProductStrategyAgent",
                    "message": "Strategy already exists, resuming from next step."
                })

            # ===== AGENT 2: Architecture Agent =====
            architecture_result = context.get("architecture")
            if not architecture_result:
                architecture_agent = ArchitectureAgent(api_keys=api_keys)
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
                
                arch_log = AgentLog(project_id=project_id, agent_name="ArchitectureAgent", action="design_architecture", status="completed", full_output={"content": architecture_result} if isinstance(architecture_result, str) else architecture_result)
                db.add(arch_log)
                db.add(GeneratedArtifact(project_id=project_id, generated_by="ArchitectureAgent", artifact_type="architecture", content={"markdown": architecture_result} if isinstance(architecture_result, str) else architecture_result))
                await db.commit()
            else:
                await on_agent_event({
                    "type": "agent_skip",
                    "agent": "ArchitectureAgent",
                    "message": "Architecture already exists, resuming from next step."
                })

            # ===== AGENT 3: Builder Agent =====
            implementation_result = context.get("implementation")
            if not implementation_result:
                builder_agent = BuilderAgent(api_keys=api_keys)
                async def run_builder(memory=None):
                    return await builder_agent.generate_implementation_plan(
                        strategy_output=strategy_result,
                        architecture_output=architecture_result,
                        user_input=project.user_input,
                        preferences=project.preferences,
                        memory=memory,
                        event_callback=on_agent_event,
                        project_id=project_id
                    )
                    
                implementation_result = await execute_agent_with_review(
                    "BuilderAgent", run_builder, audit_agent, project.user_input, context, on_agent_event, db, project_id
                )
                context["implementation"] = implementation_result
                
                builder_log = AgentLog(project_id=project_id, agent_name="BuilderAgent", action="generate_implementation_plan", status="completed", full_output=implementation_result)
                db.add(builder_log)
                db.add(GeneratedArtifact(project_id=project_id, generated_by="BuilderAgent", artifact_type="implementation_plan", content=implementation_result))
                await db.commit()
            else:
                await on_agent_event({
                    "type": "agent_skip",
                    "agent": "BuilderAgent",
                    "message": "Implementation plan already exists, resuming from next step."
                })

            # ===== AGENT 4: GitHub Agent =====
            github_result = context.get("github")
            if not github_result:
                github_agent = GitHubAgent(api_keys=api_keys)
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
                
                github_log = AgentLog(project_id=project_id, agent_name="GitHubAgent", action="generate_github_recommendations", status="completed", full_output=github_result)
                db.add(github_log)
                db.add(GeneratedArtifact(project_id=project_id, generated_by="GitHubAgent", artifact_type="github_setup", content=github_result))
                await db.commit()
            else:
                await on_agent_event({
                    "type": "agent_skip",
                    "agent": "GitHubAgent",
                    "message": "GitHub setup already exists, resuming from next step."
                })

            # ===== AGENT 5: Pitch Agent =====
            pitch_result = context.get("pitch")
            if not pitch_result:
                pitch_agent = PitchAgent(api_keys=api_keys)
                async def run_pitch(memory=None):
                    return await pitch_agent.generate_pitch_materials(
                        strategy_output=strategy_result,
                        architecture_output=architecture_result,
                        implementation_output=implementation_result,
                        github_output=github_result,
                        user_input=project.user_input,
                        preferences=project.preferences,
                        memory=memory,
                        event_callback=on_agent_event,
                        project_id=project_id
                    )
                    
                pitch_result = await execute_agent_with_review(
                    "PitchAgent", run_pitch, audit_agent, project.user_input, context, on_agent_event, db, project_id
                )
                
                pitch_log = AgentLog(project_id=project_id, agent_name="PitchAgent", action="generate_pitch_materials", status="completed", full_output=pitch_result)
                db.add(pitch_log)
                db.add(GeneratedArtifact(project_id=project_id, generated_by="PitchAgent", artifact_type="pitch_deck", content=pitch_result))
                await db.commit()
            else:
                await on_agent_event({
                    "type": "agent_skip",
                    "agent": "PitchAgent",
                    "message": "Pitch deck already exists."
                })
            
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
