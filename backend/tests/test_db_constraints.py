"""Database constraint and enum tests."""

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Candidate, JobProfile, PipelineRun, StageResult
from app.models.pipeline_run import PipelineStatus
from app.models.stage_result import StageDecision
from app.services.pipeline_planner import PipelinePlanner


def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _set_sqlite_pragma)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _create_candidate(db):
    candidate = Candidate(email="db@example.com", name="DB User")
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def _create_job_profile(db):
    job_profile = JobProfile(
        role="Engineer",
        company="DB Corp",
        raw_description="Test role",
        must_haves=["Python"],
        nice_to_haves=["SQL"],
        core_competencies=["Coding"],
        interview_style_bias={"speed": 0.5},
    )
    db.add(job_profile)
    db.commit()
    db.refresh(job_profile)
    return job_profile


def _create_pipeline_run(db, candidate_id, job_profile_id):
    stages = PipelinePlanner.STANDARD_STAGES
    pipeline_run = PipelineRun(
        candidate_id=candidate_id,
        job_profile_id=job_profile_id,
        status=PipelineStatus.CREATED,
        stages=stages,
        stage_progress={stage: "created" for stage in stages},
    )
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)
    return pipeline_run


def test_stage_result_unique_constraint(db_session):
    """StageResult should be unique per pipeline_run_id + stage_name."""
    candidate = _create_candidate(db_session)
    job_profile = _create_job_profile(db_session)
    pipeline_run = _create_pipeline_run(db_session, candidate.id, job_profile.id)

    first = StageResult(
        pipeline_run_id=pipeline_run.id,
        stage_name="resume_screen",
        stage_type="resume_screen",
        decision=StageDecision.PASS,
    )
    db_session.add(first)
    db_session.commit()

    duplicate = StageResult(
        pipeline_run_id=pipeline_run.id,
        stage_name="resume_screen",
        stage_type="resume_screen",
        decision=StageDecision.PASS,
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cascade_delete_removes_pipeline_and_stage_results(db_session):
    """Deleting a candidate should cascade to pipeline runs and stage results."""
    candidate = _create_candidate(db_session)
    job_profile = _create_job_profile(db_session)
    pipeline_run = _create_pipeline_run(db_session, candidate.id, job_profile.id)

    stage_result = StageResult(
        pipeline_run_id=pipeline_run.id,
        stage_name="resume_screen",
        stage_type="resume_screen",
        decision=StageDecision.PASS,
    )
    db_session.add(stage_result)
    db_session.commit()

    db_session.delete(candidate)
    db_session.commit()

    assert db_session.query(PipelineRun).count() == 0
    assert db_session.query(StageResult).count() == 0


def test_enum_values_persist_lowercase(db_session):
    """Enum values should persist in lowercase."""
    candidate = _create_candidate(db_session)
    job_profile = _create_job_profile(db_session)
    pipeline_run = _create_pipeline_run(db_session, candidate.id, job_profile.id)

    stage_result = StageResult(
        pipeline_run_id=pipeline_run.id,
        stage_name="resume_screen",
        stage_type="resume_screen",
        decision=StageDecision.PASS,
    )
    db_session.add(stage_result)
    db_session.commit()

    status_value = db_session.execute(
        text("SELECT status FROM pipeline_runs WHERE id = :id"),
        {"id": pipeline_run.id},
    ).scalar_one()
    decision_value = db_session.execute(
        text("SELECT decision FROM stage_results WHERE id = :id"),
        {"id": stage_result.id},
    ).scalar_one()

    assert status_value == "created"
    assert decision_value == "pass"
