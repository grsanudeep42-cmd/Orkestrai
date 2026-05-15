"""
Artifact Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Any, Dict, Union
from pydantic import BaseModel


class ArtifactResponse(BaseModel):
    """Schema for artifact response matching frontend GeneratedArtifact interface"""
    id: str
    project_id: str
    agent_name: str
    artifact_type: str
    file_path: str
    content: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

# Made with Bob
