"""StageResult model."""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
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
    pipeline_run_id = Column(Integer, ForeignKey("pipeline_runs.id"), nullable=False)
    
    # Stage identification
    stage_name = Column(String(100), nullable=False, index=True)
    stage_type = Column(String(50), nullable=False)  # e.g., "resume_screen", "oa", "coding_interview"
    
    # Result
    decision = Column(SQLEnum(StageDecision), nullable=True)
    
    # Scores and data (flexible JSON)
    raw_scores = Column(JSON, nullable=True)  # Stage-specific scoring data
    strengths = Column(JSON, nullable=False, default=list)  # List[str]
    concerns = Column(JSON, nullable=False, default=list)  # List[str]
    
    # Artifacts (transcripts, code, etc.)
    artifacts = Column(JSON, nullable=False, default=dict)  # Dict[artifact_name, data]
    notes = Column(Text, nullable=True)
    
    # Metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    pipeline_run = relationship("PipelineRun", back_populates="stage_results")
