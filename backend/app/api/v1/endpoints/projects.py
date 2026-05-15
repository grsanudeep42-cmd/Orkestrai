"""
Project API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.session import get_db
from app.db.models.project import Project
from app.db.models.generated_artifact import GeneratedArtifact
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse
from app.schemas.artifact import ArtifactResponse
from datetime import datetime
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project and start orchestration
    """
    logger.info("Creating new project", name=project_data.name)
    
    # Create project
    project = Project(
        name=project_data.name,
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
    db: AsyncSession = Depends(get_db)
):
    """
    Get project details by ID
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id)
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
    db: AsyncSession = Depends(get_db)
):
    """
    Get all generated artifacts for a project
    """
    # First check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
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
        content_str = art.content if isinstance(art.content, str) else str(art.content)
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
    db: AsyncSession = Depends(get_db)
):
    """
    List all projects with pagination
    """
    # Get total count
    count_result = await db.execute(select(Project))
    total = len(count_result.scalars().all())
    
    # Get paginated projects
    result = await db.execute(
        select(Project)
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
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a project
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id)
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

# Made with Bob
