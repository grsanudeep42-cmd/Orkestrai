"""
Agent Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class AgentLogResponse(BaseModel):
    """Schema for agent log response"""
    id: str
    project_id: str
    agent_name: str
    action: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    output_preview: Optional[str] = None
    full_output: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AgentStatus(BaseModel):
    """Schema for agent status"""
    name: str
    role: str
    description: str
    status: str  # 'active', 'idle', 'error'
    capabilities: list[str]
    tools: list[str]
    average_execution_time_ms: Optional[int] = None

# Made with Bob
