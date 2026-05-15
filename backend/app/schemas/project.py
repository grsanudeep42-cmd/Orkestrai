"""
Project Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    user_input: str = Field(..., min_length=1)
    preferences: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list response"""
    projects: list[ProjectResponse]
    total: int
    limit: int
    offset: int

# Made with Bob
