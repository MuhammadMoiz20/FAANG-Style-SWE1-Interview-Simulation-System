"""Pipeline service functions."""

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Candidate, JobProfile, PipelineRun, StageResult
from app.models.pipeline_run import (
    ACTIVE_PIPELINE_STATUSES,
    TERMINAL_PIPELINE_STATUSES,
    PipelineStatus,
)
from app.schemas.stage_result import StageResultCompleteRequest
from app.services.pipeline_planner import PipelinePlanner


def start_pipeline_run(
    db: Session, candidate_id: int, job_profile_id: int
) -> Tuple[PipelineRun, bool]:
    """Start a pipeline run, returning (run, created)."""
    planner = PipelinePlanner()
    try:
        with db.begin():
            candidate = (
                db.query(Candidate)
                .filter(Candidate.id == candidate_id)
                .with_for_update()
                .first()
            )
            if not candidate:
                raise HTTPException(status_code=404, detail="Candidate not found")

            job_profile = (
                db.query(JobProfile)
                .filter(JobProfile.id == job_profile_id)
                .with_for_update()
                .first()
            )
            if not job_profile:
                raise HTTPException(status_code=404, detail="Job profile not found")

            existing = (
                db.query(PipelineRun)
                .filter(
                    PipelineRun.candidate_id == candidate_id,
                    PipelineRun.job_profile_id == job_profile_id,
                    PipelineRun.status.in_(ACTIVE_PIPELINE_STATUSES),
                )
                .with_for_update()
                .first()
            )
            if existing:
                return existing, False

            stages, stage_progress = planner.plan_pipeline(job_profile, candidate)
            pipeline_run = PipelineRun(
                candidate_id=candidate_id,
                job_profile_id=job_profile_id,
                status=PipelineStatus.CREATED,
                stages=stages,
                stage_progress=stage_progress,
                current_stage=None,
            )
            db.add(pipeline_run)
            db.flush()
            return pipeline_run, True
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(PipelineRun)
            .filter(
                PipelineRun.candidate_id == candidate_id,
                PipelineRun.job_profile_id == job_profile_id,
                PipelineRun.status.in_(ACTIVE_PIPELINE_STATUSES),
            )
            .first()
        )
        if existing:
            return existing, False
        raise


def advance_pipeline_run(db: Session, pipeline_id: int) -> PipelineRun:
    """Advance a pipeline run to the next stage."""
    planner = PipelinePlanner()
    with db.begin():
        pipeline_run = (
            db.query(PipelineRun)
            .filter(PipelineRun.id == pipeline_id)
            .with_for_update()
            .first()
        )
        if not pipeline_run:
            raise HTTPException(status_code=404, detail="Pipeline run not found")

        if pipeline_run.status in TERMINAL_PIPELINE_STATUSES:
            raise HTTPException(status_code=400, detail="Pipeline already completed")

        if pipeline_run.current_stage is not None and pipeline_run.current_stage not in pipeline_run.stages:
            raise HTTPException(status_code=400, detail="Pipeline current stage is invalid")

        if pipeline_run.current_stage is not None:
            current_state = pipeline_run.stage_progress.get(pipeline_run.current_stage, "created")
            if current_state != "completed":
                raise HTTPException(status_code=409, detail="Current stage not completed")

        next_stage = planner.get_next_stage(pipeline_run.stages, pipeline_run.current_stage)
        if next_stage is None:
            raise HTTPException(status_code=400, detail="Pipeline already at final stage")

        try:
            updated_progress = planner.update_stage_state(
                dict(pipeline_run.stage_progress), next_stage, "in_progress"
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        pipeline_run.stage_progress = updated_progress
        pipeline_run.current_stage = next_stage
        pipeline_run.status = PipelineStatus.IN_PROGRESS

        if pipeline_run.started_at is None:
            pipeline_run.started_at = datetime.now(timezone.utc)

    db.refresh(pipeline_run)
    return pipeline_run


def complete_stage_result(
    db: Session,
    pipeline_id: int,
    stage_name: str,
    request: StageResultCompleteRequest,
) -> StageResult:
    """Complete a stage and upsert its StageResult."""
    planner = PipelinePlanner()
    now = datetime.now(timezone.utc)
    with db.begin():
        pipeline_run = (
            db.query(PipelineRun)
            .filter(PipelineRun.id == pipeline_id)
            .with_for_update()
            .first()
        )
        if not pipeline_run:
            raise HTTPException(status_code=404, detail="Pipeline run not found")

        if stage_name not in pipeline_run.stages:
            raise HTTPException(status_code=400, detail="Stage not part of pipeline")

        if pipeline_run.status in TERMINAL_PIPELINE_STATUSES:
            raise HTTPException(status_code=400, detail="Pipeline already completed")

        if pipeline_run.current_stage != stage_name:
            raise HTTPException(status_code=409, detail="Stage completion out of order")

        stage_state = pipeline_run.stage_progress.get(stage_name, "created")
        if stage_state not in ("in_progress", "completed"):
            raise HTTPException(status_code=409, detail="Stage is not in progress")

        if stage_state != "completed":
            try:
                pipeline_run.stage_progress = planner.update_stage_state(
                    dict(pipeline_run.stage_progress), stage_name, "completed"
                )
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

        if pipeline_run.started_at is None:
            pipeline_run.started_at = now

        if stage_name == pipeline_run.stages[-1]:
            pipeline_run.status = PipelineStatus.COMPLETED
            if pipeline_run.completed_at is None:
                pipeline_run.completed_at = request.completed_at or now
        else:
            pipeline_run.status = PipelineStatus.IN_PROGRESS

        payload = request.model_dump(exclude_unset=True)
        stage_type = payload.pop("stage_type", None) or stage_name

        if "completed_at" not in payload and stage_state != "completed":
            payload["completed_at"] = now

        insert_values: Dict[str, Any] = {
            "pipeline_run_id": pipeline_run.id,
            "stage_name": stage_name,
            "stage_type": stage_type,
            **payload,
        }

        update_values: Dict[str, Any] = dict(payload)
        if "stage_type" in request.model_fields_set:
            update_values["stage_type"] = stage_type

        _upsert_stage_result(db, insert_values, update_values)

    stage_result = (
        db.query(StageResult)
        .filter(
            StageResult.pipeline_run_id == pipeline_id,
            StageResult.stage_name == stage_name,
        )
        .first()
    )
    if not stage_result:
        raise HTTPException(status_code=500, detail="Stage result persistence failed")

    return stage_result


def _upsert_stage_result(
    db: Session, insert_values: Dict[str, Any], update_values: Dict[str, Any]
) -> None:
    """Dialect-aware StageResult upsert based on (pipeline_run_id, stage_name)."""
    dialect = db.bind.dialect.name
    if dialect == "postgresql":
        insert_stmt = pg_insert(StageResult).values(**insert_values)
        if update_values:
            update_stmt = {key: insert_stmt.excluded[key] for key in update_values}
            stmt = insert_stmt.on_conflict_do_update(
                index_elements=["pipeline_run_id", "stage_name"],
                set_=update_stmt,
            )
        else:
            stmt = insert_stmt.on_conflict_do_nothing(
                index_elements=["pipeline_run_id", "stage_name"]
            )
        db.execute(stmt)
        db.flush()
        return

    if dialect == "sqlite":
        insert_stmt = sqlite_insert(StageResult).values(**insert_values)
        if update_values:
            update_stmt = {key: insert_stmt.excluded[key] for key in update_values}
            stmt = insert_stmt.on_conflict_do_update(
                index_elements=["pipeline_run_id", "stage_name"],
                set_=update_stmt,
            )
        else:
            stmt = insert_stmt.on_conflict_do_nothing(
                index_elements=["pipeline_run_id", "stage_name"]
            )
        db.execute(stmt)
        db.flush()
        return

    existing = (
        db.query(StageResult)
        .filter(
            StageResult.pipeline_run_id == insert_values["pipeline_run_id"],
            StageResult.stage_name == insert_values["stage_name"],
        )
        .first()
    )
    if existing:
        for key, value in update_values.items():
            setattr(existing, key, value)
    else:
        db.add(StageResult(**insert_values))
    db.flush()
