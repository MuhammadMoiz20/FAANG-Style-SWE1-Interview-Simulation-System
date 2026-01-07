"""PipelineRun model."""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PipelineStatus(str, Enum):
    """Pipeline execution status."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineRun(Base):
    """
    PipelineRun entity representing a candidate's journey through the interview pipeline.
    
    Tracks the overall state and progress of a candidate through all stages.
    """

    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_profile_id = Column(Integer, ForeignKey("job_profiles.id"), nullable=False)
    
    # Status
    status = Column(SQLEnum(PipelineStatus), nullable=False, default=PipelineStatus.CREATED)
    current_stage = Column(String(100), nullable=True)  # e.g., "resume_screen", "oa", "phone_screen"
    
    # Stage tracking
    stages = Column(JSON, nullable=False, default=list)  # List of stage names in order
    stage_progress = Column(JSON, nullable=False, default=dict)  # Dict[stage_name, state]
    # state: "created", "in_progress", "completed", "gated"
    
    # Metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    candidate = relationship("Candidate", back_populates="pipeline_runs")
    job_profile = relationship("JobProfile", back_populates="pipeline_runs")
    stage_results = relationship("StageResult", back_populates="pipeline_run", cascade="all, delete-orphan")
