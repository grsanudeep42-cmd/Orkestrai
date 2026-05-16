"""
Agent log database model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid


class AgentLog(Base):
    """Agent execution log model"""
    
    __tablename__ = "agent_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # 'started', 'thinking', 'completed', 'failed'
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    agent_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AgentLog(id={self.id}, agent={self.agent_name}, status={self.status})>"

# Made with Bob
