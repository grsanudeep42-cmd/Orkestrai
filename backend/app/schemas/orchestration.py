"""
Orchestration Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class OrchestrationStatus(BaseModel):
    """Schema for orchestration status"""
    project_id: str
    status: str  # 'orchestrating', 'completed', 'failed'
    current_agent: Optional[str] = None
    progress: int  # 0-100
    completed_agents: list[str]
    remaining_agents: list[str]
    estimated_completion: Optional[datetime] = None


class OrchestrationEvent(BaseModel):
    """Schema for WebSocket orchestration events"""
    type: str  # 'agent_start', 'agent_thinking', 'agent_output', 'agent_complete', 'orchestration_complete', 'error', 'agent_critique', 'agent_retry'
    project_id: str
    agent: Optional[str] = None
    target_agent: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    timestamp: datetime
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    details: Optional[str] = None
