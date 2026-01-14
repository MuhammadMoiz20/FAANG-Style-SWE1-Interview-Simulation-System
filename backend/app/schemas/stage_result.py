"""StageResult schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.stage_result import StageDecision


class StageResultCompleteRequest(BaseModel):
    """Request to complete a pipeline stage."""

    decision: Optional[StageDecision] = Field(default=None, description="Stage decision outcome")
    raw_scores: Optional[Dict[str, Any]] = Field(default=None, description="Raw scoring payload")
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stage_type: Optional[str] = Field(default=None, description="Stage type override")


class StageResultResponse(BaseModel):
    """Stage result response."""

    id: int
    pipeline_run_id: int
    stage_name: str
    stage_type: str
    decision: Optional[StageDecision] = None
    raw_scores: Optional[Dict[str, Any]] = None
    strengths: List[str]
    concerns: List[str]
    artifacts: Dict[str, Any]
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
