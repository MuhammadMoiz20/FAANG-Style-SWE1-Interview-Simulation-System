"""Pipeline schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineStartRequest(BaseModel):
    """Request to start a new pipeline run."""

    candidate_id: int = Field(..., description="Candidate ID")
    job_profile_id: int = Field(..., description="Job profile ID")


class PipelineResponse(BaseModel):
    """Pipeline run response."""

    id: int
    candidate_id: int
    job_profile_id: int
    status: str
    current_stage: Optional[str] = None
    stages: List[str]
    stage_progress: Dict[str, str]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
