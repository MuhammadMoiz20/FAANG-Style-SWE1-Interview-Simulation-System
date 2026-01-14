"""Concurrency-focused tests."""

import threading

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Candidate, JobProfile, PipelineRun
from app.models.pipeline_run import PipelineStatus
from app.services.pipeline_planner import PipelinePlanner
from app.services.pipeline_service import advance_pipeline_run, start_pipeline_run


def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _create_engine(tmp_path):
    db_path = tmp_path / "concurrency.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    event.listen(engine, "connect", _set_sqlite_pragma)
    return engine


def _seed_candidate_and_job_profile(session):
    candidate = Candidate(email="conc@example.com", name="Concurrent User")
    job_profile = JobProfile(
        role="Engineer",
        company="Concurrency Inc",
        raw_description="Test role",
        must_haves=["Python"],
        nice_to_haves=["SQL"],
        core_competencies=["Coding"],
        interview_style_bias={"speed": 0.5},
    )
    session.add(candidate)
    session.add(job_profile)
    session.commit()
    session.refresh(candidate)
    session.refresh(job_profile)
    return candidate, job_profile


def test_concurrent_start_returns_single_run(tmp_path):
    """Concurrent starts should create a single active pipeline run."""
    engine = _create_engine(tmp_path)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as db:
        candidate, job_profile = _seed_candidate_and_job_profile(db)

    barrier = threading.Barrier(2)
    results = [None, None]

    def worker(idx):
        with SessionLocal() as db:
            barrier.wait()
            run, _created = start_pipeline_run(db, candidate.id, job_profile.id)
            results[idx] = run.id

    threads = [threading.Thread(target=worker, args=(idx,)) for idx in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results[0] == results[1]
    with SessionLocal() as db:
        count = (
            db.query(PipelineRun)
            .filter(
                PipelineRun.candidate_id == candidate.id,
                PipelineRun.job_profile_id == job_profile.id,
                PipelineRun.status.in_(
                    [PipelineStatus.CREATED.value, PipelineStatus.IN_PROGRESS.value]
                ),
            )
            .count()
        )
        assert count == 1


def test_concurrent_advance_only_moves_once(tmp_path):
    """Concurrent advance calls should not skip stages."""
    engine = _create_engine(tmp_path)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as db:
        candidate, job_profile = _seed_candidate_and_job_profile(db)
        stages = PipelinePlanner.STANDARD_STAGES
        stage_progress = {stage: "created" for stage in stages}
        stage_progress[stages[0]] = "completed"
        pipeline_run = PipelineRun(
            candidate_id=candidate.id,
            job_profile_id=job_profile.id,
            status=PipelineStatus.IN_PROGRESS,
            stages=stages,
            stage_progress=stage_progress,
            current_stage=stages[0],
        )
        db.add(pipeline_run)
        db.commit()
        db.refresh(pipeline_run)
        pipeline_id = pipeline_run.id

    barrier = threading.Barrier(2)
    successes = []
    failures = []

    def worker():
        with SessionLocal() as db:
            barrier.wait()
            try:
                run = advance_pipeline_run(db, pipeline_id)
                successes.append(run.current_stage)
            except HTTPException as exc:
                failures.append(exc.status_code)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(successes) == 1
    assert len(failures) == 1
    assert failures[0] == 409

    with SessionLocal() as db:
        updated = db.get(PipelineRun, pipeline_id)
        assert updated.current_stage == PipelinePlanner.STANDARD_STAGES[1]
