"""Pipeline router."""

from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Candidate, JobProfile, PipelineRun
from app.models.pipeline_run import PipelineStatus
from app.schemas.pipeline import PipelineResponse, PipelineStartRequest
from app.services.pipeline_planner import PipelinePlanner

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/start", response_model=PipelineResponse, status_code=201)
async def start_pipeline(
    request: PipelineStartRequest,
    db: Session = Depends(get_db),
):
    """
    Start a new pipeline run for a candidate and job profile.
    
    This creates a PipelineRun with planned stages and initializes
    the state machine for tracking progress.
    """
    # Validate candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Validate job profile exists
    job_profile = db.query(JobProfile).filter(JobProfile.id == request.job_profile_id).first()
    if not job_profile:
        raise HTTPException(status_code=404, detail="Job profile not found")
    
    # Plan the pipeline
    planner = PipelinePlanner()
    stages, stage_progress = planner.plan_pipeline(job_profile, candidate)
    
    # Create pipeline run
    pipeline_run = PipelineRun(
        candidate_id=request.candidate_id,
        job_profile_id=request.job_profile_id,
        status=PipelineStatus.CREATED,
        stages=stages,
        stage_progress=stage_progress,
        current_stage=None,
    )
    
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)
    
    return pipeline_run


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
):
    """Get pipeline run by ID."""
    pipeline_run = db.query(PipelineRun).filter(PipelineRun.id == pipeline_id).first()
    if not pipeline_run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    return pipeline_run


@router.post("/{pipeline_id}/advance", response_model=PipelineResponse)
async def advance_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
):
    """
    Advance pipeline to next stage.
    
    This is a helper endpoint for testing stage progression.
    In production, stages advance based on stage results.
    """
    pipeline_run = db.query(PipelineRun).filter(PipelineRun.id == pipeline_id).first()
    if not pipeline_run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    planner = PipelinePlanner()
    
    # Get next stage
    next_stage = planner.get_next_stage(pipeline_run.stages, pipeline_run.current_stage)
    
    if next_stage is None:
        raise HTTPException(status_code=400, detail="Pipeline already at final stage")
    
    # Update pipeline
    pipeline_run.current_stage = next_stage
    pipeline_run.status = PipelineStatus.IN_PROGRESS
    
    # Update stage state to in_progress
    pipeline_run.stage_progress = planner.update_stage_state(
        pipeline_run.stage_progress, next_stage, "in_progress"
    )
    
    if pipeline_run.started_at is None:
        from datetime import datetime
        pipeline_run.started_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(pipeline_run)
    
    return pipeline_run
