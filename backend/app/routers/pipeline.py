"""Pipeline router."""

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PipelineRun
from app.schemas.pipeline import PipelineResponse, PipelineStartRequest
from app.schemas.stage_result import StageResultCompleteRequest, StageResultResponse
from app.services.pipeline_service import advance_pipeline_run, complete_stage_result, start_pipeline_run

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/start", response_model=PipelineResponse, status_code=201)
async def start_pipeline(
    request: PipelineStartRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Start a new pipeline run for a candidate and job profile.
    
    This creates a PipelineRun with planned stages and initializes
    the state machine for tracking progress.
    """
    pipeline_run, created = start_pipeline_run(
        db, request.candidate_id, request.job_profile_id
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return pipeline_run


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    """Get pipeline run by ID."""
    pipeline_run = db.query(PipelineRun).filter(PipelineRun.id == pipeline_id).first()
    if not pipeline_run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    return pipeline_run


@router.post("/{pipeline_id}/advance", response_model=PipelineResponse)
async def advance_pipeline(
    pipeline_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    """
    Advance pipeline to next stage.
    
    This is a helper endpoint for testing stage progression.
    In production, stages advance based on stage results.
    """
    pipeline_run = advance_pipeline_run(db, pipeline_id)
    return pipeline_run


@router.post(
    "/{pipeline_id}/stages/{stage_name}/complete",
    response_model=StageResultResponse,
)
async def complete_pipeline_stage(
    pipeline_id: int = Path(gt=0),
    stage_name: str = Path(min_length=1, max_length=100),
    request: StageResultCompleteRequest | None = None,
    db: Session = Depends(get_db),
):
    """
    Complete a pipeline stage and upsert its StageResult.

    Enforces stage ordering, persists results, and updates pipeline progress.
    """
    if request is None:
        request = StageResultCompleteRequest()
    stage_result = complete_stage_result(db, pipeline_id, stage_name, request)
    return stage_result
