"""
Orchestration API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.project import Project
from app.db.models.agent_log import AgentLog
from app.db.models.generated_artifact import GeneratedArtifact
from app.schemas.orchestration import OrchestrationStatus
from app.agents.strategy_agent import StrategyAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.builder_agent import BuilderAgent
from datetime import datetime
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/{project_id}/status", response_model=OrchestrationStatus)
async def get_orchestration_status(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get orchestration status for a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get completed agents
    logs_result = await db.execute(
        select(AgentLog)
        .where(AgentLog.project_id == project_id)
        .where(AgentLog.status == "completed")
    )
    completed_logs = logs_result.scalars().all()
    completed_agents = [log.agent_name for log in completed_logs]
    
    # Calculate progress
    total_agents = 5  # Strategy, Architecture, Code, GitHub, Pitch
    progress = int((len(completed_agents) / total_agents) * 100)
    
    # Determine current agent
    current_agent = None
    if project.status == "orchestrating":
        if len(completed_agents) == 0:
            current_agent = "ProductStrategyAgent"
        elif len(completed_agents) == 1:
            current_agent = "ArchitectureAgent"
        elif len(completed_agents) == 2:
            current_agent = "CodeBuilderAgent"
        elif len(completed_agents) == 3:
            current_agent = "GitHubAgent"
        elif len(completed_agents) == 4:
            current_agent = "PitchAgent"
    
    # Remaining agents
    all_agents = ["ProductStrategyAgent", "ArchitectureAgent", "CodeBuilderAgent", "GitHubAgent", "PitchAgent"]
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


@router.post("/{project_id}/start")
async def start_orchestration(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start orchestration for a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status == "orchestrating":
        raise HTTPException(status_code=400, detail="Orchestration already in progress")

    if project.status == "completed":
        raise HTTPException(status_code=400, detail="Orchestration already completed. Create a new project to run again.")

    # Reset status for pending or failed projects
    if project.status not in ["pending", "failed"]:
        raise HTTPException(status_code=400, detail=f"Cannot start orchestration: project status is {project.status}")
    
    # Update project status
    project.status = "orchestrating"
    project.updated_at = datetime.utcnow()
    await db.commit()
    
    # Start orchestration in background
    background_tasks.add_task(run_orchestration, project_id)
    
    return {"message": "Orchestration started", "project_id": project_id}


def _format_architecture_as_markdown(architecture: dict) -> str:
    """Format architecture dictionary as markdown"""
    md = f"# System Architecture\n\n"
    
    if "tech_stack" in architecture:
        md += "## Tech Stack\n\n"
        tech = architecture['tech_stack']
        if isinstance(tech, dict):
            for category, items in tech.items():
                md += f"### {category.replace('_', ' ').title()}\n"
                if isinstance(items, list):
                    for item in items:
                        md += f"- {item}\n"
                else:
                    md += f"- {items}\n"
                md += "\n"
    
    if "database_schema" in architecture:
        md += "## Database Schema\n\n"
        schema = architecture['database_schema']
        if isinstance(schema, dict) and 'tables' in schema:
            for table in schema['tables']:
                if isinstance(table, dict):
                    md += f"### {table.get('name', 'Table')}\n"
                    if 'fields' in table:
                        md += "**Fields:**\n"
                        for field in table['fields']:
                            if isinstance(field, dict):
                                md += f"- `{field.get('name')}` ({field.get('type')}) {field.get('constraints', '')}\n"
                    md += "\n"
    
    if "api_endpoints" in architecture:
        md += "## API Endpoints\n\n"
        endpoints = architecture['api_endpoints']
        if isinstance(endpoints, list):
            for endpoint in endpoints:
                if isinstance(endpoint, dict):
                    md += f"### {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}\n"
                    md += f"{endpoint.get('description', '')}\n\n"
    
    if "system_design" in architecture:
        md += "## System Design\n\n"
        md += f"{architecture['system_design']}\n\n"
    
    return md


def _format_implementation_as_markdown(implementation: dict) -> str:
    """Format implementation dictionary as markdown"""
    md = f"# Implementation Plan\n\n"
    
    if "folder_structure" in implementation:
        md += "## Folder Structure\n\n"
        structure = implementation['folder_structure']
        if isinstance(structure, dict):
            for section, items in structure.items():
                md += f"### {section.title()}\n```\n"
                if isinstance(items, list):
                    for item in items:
                        md += f"{item}\n"
                md += "```\n\n"
    
    if "implementation_phases" in implementation:
        md += "## Implementation Phases\n\n"
        phases = implementation['implementation_phases']
        if isinstance(phases, list):
            for phase in phases:
                if isinstance(phase, dict):
                    md += f"### {phase.get('phase', 'Phase')}\n"
                    md += f"**Priority:** {phase.get('priority', 'medium')}\n"
                    md += f"**Estimated Hours:** {phase.get('estimated_hours', 'TBD')}\n\n"
                    if 'tasks' in phase:
                        md += "**Tasks:**\n"
                        for task in phase['tasks']:
                            md += f"- {task}\n"
                    md += "\n"
    
    if "deployment_plan" in implementation:
        md += "## Deployment Plan\n\n"
        deploy = implementation['deployment_plan']
        if isinstance(deploy, dict) and 'steps' in deploy:
            for step in deploy['steps']:
                md += f"{step}\n"
            md += "\n"
    
    return md


def _format_strategy_as_markdown(strategy: dict) -> str:
    """Format strategy dictionary as markdown"""
    md = f"# {strategy.get('project_name', 'Project Strategy')}\n\n"
    
    if "problem_statement" in strategy:
        md += f"## Problem Statement\n\n{strategy['problem_statement']}\n\n"
    
    if "target_users" in strategy:
        md += "## Target Users\n\n"
        users = strategy['target_users']
        if isinstance(users, str):
            users = [users]
        for user in users:
            md += f"- {user}\n"
        md += "\n"
    
    if "core_features" in strategy:
        md += "## Core Features\n\n"
        features = strategy['core_features']
        if isinstance(features, str):
            features = [{"name": "Features", "user_story": features}]
        for feature in features:
            if isinstance(feature, str):
                feature = {"name": feature}
            md += f"### {feature.get('name', 'Feature')}\n"
            md += f"**Priority:** {feature.get('priority', 'medium')}\n\n"
            md += f"**User Story:** {feature.get('user_story', '')}\n\n"
            if 'acceptance_criteria' in feature:
                md += "**Acceptance Criteria:**\n"
                criteria_list = feature['acceptance_criteria']
                if isinstance(criteria_list, str):
                    criteria_list = [criteria_list]
                for criteria in criteria_list:
                    md += f"- {criteria}\n"
            md += "\n"
    
    if "mvp_scope" in strategy:
        md += "## MVP Scope\n\n"
        items = strategy['mvp_scope']
        if isinstance(items, str):
            items = [items]
        for item in items:
            md += f"- {item}\n"
        md += "\n"
    
    if "tech_constraints" in strategy:
        md += "## Technical Constraints\n\n"
        constraints = strategy['tech_constraints']
        if isinstance(constraints, str):
            constraints = [constraints]
        for constraint in constraints:
            md += f"- {constraint}\n"
        md += "\n"
    
    if "success_metrics" in strategy:
        md += "## Success Metrics\n\n"
        metrics = strategy['success_metrics']
        if isinstance(metrics, str):
            metrics = [metrics]
        for metric in metrics:
            md += f"- {metric}\n"
        md += "\n"
    
    return md


async def run_orchestration(project_id: str):
    """
    Run the orchestration process (background task)
    """
    from app.db.session import AsyncSessionLocal
    from app.api.v1.endpoints.websocket import manager
    
    logger.info("Starting orchestration", project_id=project_id)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get project
            result = await db.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            
            if not project:
                logger.error("Project not found", project_id=project_id)
                return
            
            # Broadcast connection established
            await manager.broadcast_to_project(
                project_id,
                {
                    "type": "connection_established",
                    "project_id": project_id,
                    "message": "Orchestration started",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Initialize Strategy Agent with event callbacks
            async def on_agent_event(data: dict):
                """Callback to broadcast agent events via WebSocket"""
                await manager.broadcast_to_project(project_id, {
                    "project_id": project_id,
                    "agent": "ProductStrategyAgent",
                    "timestamp": datetime.utcnow().isoformat(),
                    **data
                })
            
            # ===== AGENT 1: Strategy Agent =====
            strategy_agent = StrategyAgent()
            logger.info("Running Strategy Agent", project_id=project_id)
            
            strategy_result = await strategy_agent.analyze_project(
                user_input=project.user_input,
                preferences=project.preferences,
                event_callback=on_agent_event
            )
            
            # Save strategy agent log
            strategy_log = AgentLog(
                project_id=project_id,
                agent_name="ProductStrategyAgent",
                action="generate_strategy",
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                output_preview=str(strategy_result)[:500] if strategy_result else None,
                full_output=strategy_result
            )
            db.add(strategy_log)
            
            # Save strategy artifact
            if strategy_result:
                strategy_md = _format_strategy_as_markdown(strategy_result)
                strategy_artifact = GeneratedArtifact(
                    project_id=project_id,
                    generated_by="ProductStrategyAgent",
                    artifact_type="strategy",
                    content=strategy_md
                )
                db.add(strategy_artifact)
            
            await db.commit()
            
            # ===== AGENT 2: Architecture Agent =====
            architecture_agent = ArchitectureAgent()
            logger.info("Running Architecture Agent", project_id=project_id)
            
            architecture_result = await architecture_agent.design_architecture(
                strategy_output=strategy_result,
                user_input=project.user_input,
                preferences=project.preferences,
                event_callback=on_agent_event
            )
            
            # Save architecture agent log
            architecture_log = AgentLog(
                project_id=project_id,
                agent_name="ArchitectureAgent",
                action="design_architecture",
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                output_preview=str(architecture_result)[:500] if architecture_result else None,
                full_output=architecture_result
            )
            db.add(architecture_log)
            
            # Save architecture artifact
            if architecture_result:
                architecture_md = _format_architecture_as_markdown(architecture_result)
                architecture_artifact = GeneratedArtifact(
                    project_id=project_id,
                    generated_by="ArchitectureAgent",
                    artifact_type="architecture",
                    content=architecture_md
                )
                db.add(architecture_artifact)
            
            await db.commit()
            
            # ===== AGENT 3: Builder Agent =====
            builder_agent = BuilderAgent()
            logger.info("Running Builder Agent", project_id=project_id)
            
            implementation_result = await builder_agent.generate_implementation_plan(
                strategy_output=strategy_result,
                architecture_output=architecture_result,
                user_input=project.user_input,
                preferences=project.preferences,
                event_callback=on_agent_event
            )
            
            # Save builder agent log
            builder_log = AgentLog(
                project_id=project_id,
                agent_name="BuilderAgent",
                action="generate_implementation_plan",
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                output_preview=str(implementation_result)[:500] if implementation_result else None,
                full_output=implementation_result
            )
            db.add(builder_log)
            
            # Save implementation artifact
            if implementation_result:
                implementation_md = _format_implementation_as_markdown(implementation_result)
                implementation_artifact = GeneratedArtifact(
                    project_id=project_id,
                    generated_by="BuilderAgent",
                    artifact_type="implementation_plan",
                    content=implementation_md
                )
                db.add(implementation_artifact)
            
            # Update project status to completed
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
            
            logger.info("Orchestration completed successfully - 3 agents executed", project_id=project_id)
            
        except Exception as e:
            logger.error("Orchestration failed", project_id=project_id, error=str(e))
            
            # Update project status to failed
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
                
                # Broadcast error
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

# Made with Bob
