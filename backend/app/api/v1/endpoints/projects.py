"""
Project API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import io
import zipfile
import json
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.db.models.project import Project
from app.db.models.user import User
from app.db.models.agent_log import AgentLog
from app.db.models.generated_artifact import GeneratedArtifact
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse
from app.schemas.artifact import ArtifactResponse
from app.schemas.agent import AgentLogResponse
from datetime import datetime
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project and start orchestration
    """
    logger.info("Creating new project", name=project_data.name, user=current_user.username)
    
    # Create project
    project = Project(
        name=project_data.name,
        user_id=current_user.id,
        description=project_data.description,
        user_input=project_data.user_input,
        preferences=project_data.preferences,
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    logger.info("Project created", project_id=project.id, name=project.name)
    
    # TODO: Trigger orchestration in background task
    
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project details by ID
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    return project


@router.get("/{project_id}/artifacts", response_model=List[ArtifactResponse])
async def get_project_artifacts(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all generated artifacts for a project
    """
    # First check if project exists and belongs to user
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
        
    art_result = await db.execute(
        select(GeneratedArtifact)
        .where(GeneratedArtifact.project_id == project_id)
        .order_by(GeneratedArtifact.generated_at.asc())
    )
    artifacts = art_result.scalars().all()
    
    response = []
    for art in artifacts:
        if isinstance(art.content, dict):
            if "markdown" in art.content:
                content_str = art.content["markdown"]
            else:
                content_str = json.dumps(art.content)
        else:
            content_str = str(art.content)
            
        file_path = "strategy.md" if art.artifact_type == "strategy" else f"{art.artifact_type}.txt"
        response.append(
            ArtifactResponse(
                id=art.id,
                project_id=art.project_id,
                agent_name=art.generated_by,
                artifact_type=art.artifact_type,
                file_path=file_path,
                content=content_str,
                created_at=art.generated_at.isoformat()
            )
        )
        
    return response


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all projects for the current user with pagination
    """
    # Get total count for user
    count_result = await db.execute(select(Project).where(Project.user_id == current_user.id))
    total = len(count_result.scalars().all())
    
    # Get paginated projects
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    projects = result.scalars().all()
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        limit=limit,
        offset=offset
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    await db.delete(project)
    await db.commit()
    
    logger.info("Project deleted", project_id=project_id)
    
    return None


@router.get("/{project_id}/download")
async def download_project_code(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and stream a ZIP file of the project code from the database
    """
    # 1. Verify project exists
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Get code artifacts
    art_result = await db.execute(
        select(GeneratedArtifact)
        .where(GeneratedArtifact.project_id == project_id)
        .where(GeneratedArtifact.artifact_type == "implementation_plan")
    )
    artifact = art_result.scalar_one_or_none()
    
    # Safety check for content type
    files = []
    if artifact and isinstance(artifact.content, dict):
        files = artifact.content.get("files", [])
    
    if not files:
        # Try finding any artifact with files
        all_art_result = await db.execute(
            select(GeneratedArtifact)
            .where(GeneratedArtifact.project_id == project_id)
        )
        all_artifacts = all_art_result.scalars().all()
        for a in all_artifacts:
            if isinstance(a.content, dict) and a.content.get("files"):
                files.extend(a.content.get("files"))
        
        if not files:
            raise HTTPException(status_code=404, detail="No code files found for this project. Legacy projects might not support memory-efficient download.")

    # 3. Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_obj in files:
            path = file_obj.get("path")
            content = file_obj.get("content", "")
            if path and content:
                zip_file.writestr(path, content)
    
    zip_buffer.seek(0)
    
    # 4. Stream response
    filename = f"{project.name.lower().replace(' ', '-')}-code.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{project_id}/pitch")
async def get_project_pitch(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Serve the generated pitch deck as raw HTML from the database
    """
    art_result = await db.execute(
        select(GeneratedArtifact)
        .where(GeneratedArtifact.project_id == project_id)
        .where(GeneratedArtifact.artifact_type == "pitch_deck")
    )
    artifact = art_result.scalar_one_or_none()
    
    if not artifact or not artifact.content.get("html_content"):
        raise HTTPException(status_code=404, detail="Pitch deck not found")

    return Response(
        content=artifact.content.get("html_content"),
        media_type="text/html"
    )


from app.agents.github_agent import GitHubAgent


@router.get("/{project_id}/logs", response_model=List[AgentLogResponse])
async def get_project_logs(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical orchestration logs for a project
    """
    # First check if project exists and belongs to user
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    log_result = await db.execute(
        select(AgentLog)
        .where(AgentLog.project_id == project_id)
        .order_by(AgentLog.started_at.asc())
    )
    logs = log_result.scalars().all()
    return logs


@router.post("/{project_id}/github-retry")
async def retry_github_integration(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retry the GitHub integration phase for a project
    """
    # 1. Verify project exists and belongs to user
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Get necessary artifacts for GitHubAgent
    art_result = await db.execute(
        select(GeneratedArtifact).where(GeneratedArtifact.project_id == project_id)
    )
    artifacts = art_result.scalars().all()
    
    strategy = next((a.content for a in artifacts if a.artifact_type == "strategy"), None)
    architecture = next((a.content for a in artifacts if a.artifact_type == "architecture"), None)
    implementation = next((a.content for a in artifacts if a.artifact_type == "implementation_plan"), None)
    
    if not implementation:
        raise HTTPException(status_code=400, detail="Cannot retry GitHub: Project implementation not found")

    # 3. Initialize GitHub Agent
    github_agent = GitHubAgent()
    
    # Define a simple log callback
    async def log_event(event):
        logger.info("GitHub Retry Event", project_id=project_id, event=event)
        # Optionally save to AgentLog table
        if event["type"] == "agent_output":
            log = AgentLog(
                project_id=project_id,
                agent_name="GitHubAgent",
                action="github_retry",
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                full_output=event["data"]
            )
            db.add(log)

    # 4. Run Agent
    try:
        github_result = await github_agent.generate_github_recommendations(
            strategy_output=strategy or "Strategy missing",
            architecture_output=architecture or "Architecture missing",
            implementation_output=implementation,
            user_input=project.user_input,
            current_user=current_user,
            event_callback=log_event
        )
        
        # 5. Update or create the github_setup artifact
        existing_github_art = next((a for a in artifacts if a.artifact_type == "github_setup"), None)
        if existing_github_art:
            existing_github_art.content = github_result
            existing_github_art.generated_at = datetime.utcnow()
        else:
            db.add(GeneratedArtifact(
                project_id=project_id,
                generated_by="GitHubAgent",
                artifact_type="github_setup",
                content=github_result
            ))
            
        await db.commit()
        return github_result
    except Exception as e:
        logger.error("GitHub retry failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"GitHub retry failed: {str(e)}")

# Made with Bob
