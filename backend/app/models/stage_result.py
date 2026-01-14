"""StageResult model."""

from enum import Enum

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    Index,
)
from sqlalchemy.orm import relationship

from app.database import Base


class StageDecision(str, Enum):
    """Decision outcome for a stage."""

    PROCEED = "proceed"
    HOLD = "hold"
    REJECT = "reject"
    BORDERLINE = "borderline"
    PASS = "pass"
    FAIL = "fail"


class StageResult(Base):
    """
    StageResult entity representing the outcome of a single pipeline stage.
    
    Each stage (resume screen, OA, interview, etc.) produces a result
    with decision, scores, and artifacts.
    """

    __tablename__ = "stage_results"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    pipeline_run_id = Column(Integer, ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Stage identification
    stage_name = Column(String(100), nullable=False, index=True)
    stage_type = Column(String(50), nullable=False, index=True)  # e.g., "resume_screen", "oa", "coding_interview"
    
    # Result
    decision = Column(SQLEnum(StageDecision, name="stagedecision"), nullable=True, index=True)
    
    # Scores and data (flexible JSON)
    raw_scores = Column(JSON, nullable=True)  # Stage-specific scoring data
    strengths = Column(JSON, nullable=False, default=list, server_default="[]")  # List[str]
    concerns = Column(JSON, nullable=False, default=list, server_default="[]")  # List[str]
    
    # Artifacts (transcripts, code, etc.)
    artifacts = Column(JSON, nullable=False, default=dict, server_default="{}")  # Dict[artifact_name, data]
    notes = Column(Text, nullable=True)
    
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
    pipeline_run = relationship("PipelineRun", back_populates="stage_results")
    
    # Composite indexes
    __table_args__ = (
        UniqueConstraint("pipeline_run_id", "stage_name", name="uq_stage_results_pipeline_stage"),
        Index("ix_stage_results_pipeline_type", "pipeline_run_id", "stage_type"),
        Index("ix_stage_results_pipeline_decision", "pipeline_run_id", "decision"),
    )
