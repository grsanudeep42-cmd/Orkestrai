"""
Generated artifact database model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid


class GeneratedArtifact(Base):
    """Generated artifact model for storing agent outputs"""
    
    __tablename__ = "generated_artifacts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'strategy', 'architecture', 'code', 'github', 'pitch'
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(100), nullable=False)  # Agent name
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    file_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    def __repr__(self) -> str:
        return f"<GeneratedArtifact(id={self.id}, type={self.artifact_type}, by={self.generated_by})>"

# Made with Bob
