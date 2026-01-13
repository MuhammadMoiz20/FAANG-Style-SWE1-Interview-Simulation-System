"""PipelineRun model."""

from enum import Enum

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, func, Index
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
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_profile_id = Column(Integer, ForeignKey("job_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(PipelineStatus, name="pipelinestatus"), nullable=False, default=PipelineStatus.CREATED, index=True)
    current_stage = Column(String(100), nullable=True, index=True)  # e.g., "resume_screen", "oa", "phone_screen"
    
    # Stage tracking
    stages = Column(JSON, nullable=False, server_default="[]")  # List of stage names in order
    stage_progress = Column(JSON, nullable=False, server_default="{}")  # Dict[stage_name, state]
    # state: "created", "in_progress", "completed", "gated"
    
    # Metadata
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    # Relationships
    candidate = relationship("Candidate", back_populates="pipeline_runs")
    job_profile = relationship("JobProfile", back_populates="pipeline_runs")
    stage_results = relationship("StageResult", back_populates="pipeline_run", cascade="all, delete-orphan")
    
    # Composite indexes
    __table_args__ = (
        Index("ix_pipeline_runs_candidate_status", "candidate_id", "status"),
        Index("ix_pipeline_runs_job_profile_status", "job_profile_id", "status"),
    )