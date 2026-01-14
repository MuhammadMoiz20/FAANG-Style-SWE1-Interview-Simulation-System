"""PipelineRun model."""

from enum import Enum

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, CheckConstraint, func, Index, text
from sqlalchemy.orm import relationship

from app.database import Base


class PipelineStatus(str, Enum):
    """Pipeline execution status.

    States:
        CREATED: Pipeline run has been created but not started
        IN_PROGRESS: Pipeline is actively being executed
        COMPLETED: Pipeline finished successfully (all stages completed)
        FAILED: Pipeline failed due to an error
        CANCELLED: Pipeline was cancelled before completion
    """

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


ACTIVE_PIPELINE_STATUSES = (
    PipelineStatus.CREATED.value,
    PipelineStatus.IN_PROGRESS.value,
)
TERMINAL_PIPELINE_STATUSES = (
    PipelineStatus.COMPLETED.value,
    PipelineStatus.FAILED.value,
    PipelineStatus.CANCELLED.value,
)


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
    status = Column(
        SQLEnum(PipelineStatus, name="pipelinestatus"),
        nullable=False,
        default=PipelineStatus.CREATED,
        server_default=text("'created'"),
        index=True,
    )
    current_stage = Column(String(100), nullable=True, index=True)  # e.g., "resume_screen", "oa", "phone_screen"
    
    # Stage tracking
    stages = Column(JSON, nullable=False, default=list, server_default="[]")  # List of stage names in order
    stage_progress = Column(JSON, nullable=False, default=dict, server_default="{}")  # Dict[stage_name, state]
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
    # passive_deletes relies on DB-level ON DELETE CASCADE to remove related rows.
    stage_results = relationship("StageResult", back_populates="pipeline_run", cascade="all, delete-orphan", passive_deletes=True)
    
    # Composite indexes and constraints
    # Note: A check constraint that current_stage must be in stages would be
    # database-specific (PostgreSQL supports checking jsonb_array_elements).
    # Application-level validation is enforced in pipeline_service.
    __table_args__ = (
        Index("ix_pipeline_runs_candidate_status", "candidate_id", "status"),
        Index("ix_pipeline_runs_job_profile_status", "job_profile_id", "status"),
        Index(
            "uq_pipeline_runs_candidate_job_active",
            "candidate_id",
            "job_profile_id",
            unique=True,
            sqlite_where=text("status IN ('created', 'in_progress')"),
            postgresql_where=text("status IN ('created', 'in_progress')"),
        ),
    )
