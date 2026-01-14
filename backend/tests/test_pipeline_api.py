"""Test pipeline API endpoints."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Candidate, JobProfile, PipelineRun, StageResult
from app.models.pipeline_run import PipelineStatus
from app.services.pipeline_planner import PipelinePlanner


def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture()
def test_client():
    """Provide a TestClient with an isolated in-memory database."""
    previous_env = os.environ.get("PIPELINE_ADVANCE_HELPER_ENABLED")
    os.environ["PIPELINE_ADVANCE_HELPER_ENABLED"] = "true"
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _set_sqlite_pragma)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    if previous_env is None:
        os.environ.pop("PIPELINE_ADVANCE_HELPER_ENABLED", None)
    else:
        os.environ["PIPELINE_ADVANCE_HELPER_ENABLED"] = previous_env


def create_candidate(db):
    """Create a candidate record for tests."""
    candidate = Candidate(email="test@example.com", name="Test Candidate")
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def create_job_profile(db):
    """Create a job profile record for tests."""
    job_profile = JobProfile(
        role="Software Engineer I",
        company="Test Corp",
        raw_description="Test job description",
        must_haves=["Python"],
        nice_to_haves=["React"],
        core_competencies=["Coding"],
        interview_style_bias={"speed": 0.7},
    )
    db.add(job_profile)
    db.commit()
    db.refresh(job_profile)
    return job_profile


def create_candidate_and_job_profile(db):
    """Create candidate and job profile records for tests."""
    candidate = create_candidate(db)
    job_profile = create_job_profile(db)
    return candidate, job_profile


def create_pipeline_run(
    db,
    candidate_id,
    job_profile_id,
    status=PipelineStatus.CREATED,
    current_stage=None,
    stage_progress=None,
):
    """Create a pipeline run with optional overrides."""
    stages = PipelinePlanner.STANDARD_STAGES
    if stage_progress is None:
        stage_progress = {stage: "created" for stage in stages}
    pipeline_run = PipelineRun(
        candidate_id=candidate_id,
        job_profile_id=job_profile_id,
        status=status,
        stages=stages,
        stage_progress=stage_progress,
        current_stage=current_stage,
    )
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)
    return pipeline_run


def test_start_pipeline_creates_run(test_client):
    """POST /pipeline/start should create a pipeline run with planned stages."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)

    response = client.post(
        "/pipeline/start",
        json={"candidate_id": candidate.id, "job_profile_id": job_profile.id},
    )

    assert response.status_code == 201
    data = response.json()
    expected_stages = PipelinePlanner.STANDARD_STAGES
    expected_progress = {stage: "created" for stage in expected_stages}

    assert data["candidate_id"] == candidate.id
    assert data["job_profile_id"] == job_profile.id
    assert data["status"] == PipelineStatus.CREATED.value
    assert data["current_stage"] is None
    assert data["stages"] == expected_stages
    assert data["stage_progress"] == expected_progress

    with session_factory() as db:
        pipeline_run = db.get(PipelineRun, data["id"])
        assert pipeline_run is not None
        assert pipeline_run.stages == expected_stages
        assert pipeline_run.stage_progress == expected_progress


def test_start_pipeline_missing_candidate_returns_404(test_client):
    """POST /pipeline/start should 404 for missing candidate."""
    client, session_factory = test_client
    with session_factory() as db:
        job_profile = create_job_profile(db)

    response = client.post(
        "/pipeline/start",
        json={"candidate_id": 9999, "job_profile_id": job_profile.id},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"


def test_start_pipeline_missing_job_profile_returns_404(test_client):
    """POST /pipeline/start should 404 for missing job profile."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate = create_candidate(db)

    response = client.post(
        "/pipeline/start",
        json={"candidate_id": candidate.id, "job_profile_id": 9999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job profile not found"


def test_start_pipeline_negative_ids_rejected(test_client):
    """POST /pipeline/start should reject negative IDs."""
    client, _session_factory = test_client
    response = client.post(
        "/pipeline/start",
        json={"candidate_id": -1, "job_profile_id": -2},
    )
    assert response.status_code == 422


def test_get_pipeline_returns_data(test_client):
    """GET /pipeline/{id} should return pipeline data."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)

    create_response = client.post(
        "/pipeline/start",
        json={"candidate_id": candidate.id, "job_profile_id": job_profile.id},
    )
    pipeline_id = create_response.json()["id"]

    response = client.get(f"/pipeline/{pipeline_id}")

    assert response.status_code == 200
    data = response.json()
    expected_stages = PipelinePlanner.STANDARD_STAGES
    expected_progress = {stage: "created" for stage in expected_stages}

    assert data["id"] == pipeline_id
    assert data["candidate_id"] == candidate.id
    assert data["job_profile_id"] == job_profile.id
    assert data["status"] == PipelineStatus.CREATED.value
    assert data["stages"] == expected_stages
    assert data["stage_progress"] == expected_progress


def test_start_pipeline_idempotent_returns_existing(test_client):
    """POST /pipeline/start should return existing run for active candidate/job profile."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)

    first = client.post(
        "/pipeline/start",
        json={"candidate_id": candidate.id, "job_profile_id": job_profile.id},
    )
    second = client.post(
        "/pipeline/start",
        json={"candidate_id": candidate.id, "job_profile_id": job_profile.id},
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    with session_factory() as db:
        runs = (
            db.query(PipelineRun)
            .filter(
                PipelineRun.candidate_id == candidate.id,
                PipelineRun.job_profile_id == job_profile.id,
                PipelineRun.status.in_(
                    [PipelineStatus.CREATED.value, PipelineStatus.IN_PROGRESS.value]
                ),
            )
            .all()
        )
        assert len(runs) == 1


def test_advance_pipeline_happy_path(test_client):
    """POST /pipeline/{id}/advance should move to first stage."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(db, candidate.id, job_profile.id)

    response = client.post(f"/pipeline/{pipeline_run.id}/advance")

    assert response.status_code == 200
    data = response.json()
    assert data["current_stage"] == PipelinePlanner.STANDARD_STAGES[0]
    assert data["stage_progress"][PipelinePlanner.STANDARD_STAGES[0]] == "in_progress"
    assert data["status"] == PipelineStatus.IN_PROGRESS.value


def test_advance_pipeline_current_stage_not_completed(test_client):
    """Advance should fail if current stage is not completed."""
    client, session_factory = test_client
    stages = PipelinePlanner.STANDARD_STAGES
    stage_progress = {stage: "created" for stage in stages}
    stage_progress[stages[0]] = "in_progress"
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(
            db,
            candidate.id,
            job_profile.id,
            status=PipelineStatus.IN_PROGRESS,
            current_stage=stages[0],
            stage_progress=stage_progress,
        )

    response = client.post(f"/pipeline/{pipeline_run.id}/advance")

    assert response.status_code == 409
    assert response.json()["detail"] == "Current stage not completed"


def test_advance_pipeline_invalid_current_stage(test_client):
    """Advance should fail on invalid current_stage values."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(
            db,
            candidate.id,
            job_profile.id,
            current_stage="unknown_stage",
        )

    response = client.post(f"/pipeline/{pipeline_run.id}/advance")

    assert response.status_code == 400
    assert response.json()["detail"] == "Pipeline current stage is invalid"


def test_advance_pipeline_past_final_stage(test_client):
    """Advance should fail when already at final stage."""
    client, session_factory = test_client
    stages = PipelinePlanner.STANDARD_STAGES
    stage_progress = {stage: "created" for stage in stages}
    stage_progress[stages[-1]] = "completed"
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(
            db,
            candidate.id,
            job_profile.id,
            status=PipelineStatus.IN_PROGRESS,
            current_stage=stages[-1],
            stage_progress=stage_progress,
        )

    response = client.post(f"/pipeline/{pipeline_run.id}/advance")

    assert response.status_code == 400
    assert response.json()["detail"] == "Pipeline already at final stage"


def test_advance_pipeline_already_completed(test_client):
    """Advance should fail for completed pipelines."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(
            db,
            candidate.id,
            job_profile.id,
            status=PipelineStatus.COMPLETED,
        )

    response = client.post(f"/pipeline/{pipeline_run.id}/advance")

    assert response.status_code == 400
    assert response.json()["detail"] == "Pipeline already completed"


def test_complete_stage_happy_path(test_client):
    """Completing a stage should upsert StageResult and update progress."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(db, candidate.id, job_profile.id)

    advance_response = client.post(f"/pipeline/{pipeline_run.id}/advance")
    assert advance_response.status_code == 200
    stage_name = advance_response.json()["current_stage"]

    complete_response = client.post(
        f"/pipeline/{pipeline_run.id}/stages/{stage_name}/complete",
        json={"decision": "pass", "notes": "Looks good"},
    )

    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["pipeline_run_id"] == pipeline_run.id
    assert data["stage_name"] == stage_name
    assert data["decision"] == "pass"

    with session_factory() as db:
        updated = db.get(PipelineRun, pipeline_run.id)
        assert updated.stage_progress[stage_name] == "completed"
        stage_results = (
            db.query(StageResult)
            .filter(StageResult.pipeline_run_id == pipeline_run.id)
            .all()
        )
        assert len(stage_results) == 1


def test_complete_stage_invalid_stage(test_client):
    """Completing a non-existent stage should return 400."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(db, candidate.id, job_profile.id)

    response = client.post(
        f"/pipeline/{pipeline_run.id}/stages/invalid_stage/complete",
        json={"decision": "pass"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Stage not part of pipeline"


def test_complete_stage_out_of_order(test_client):
    """Completing a stage before it is current should return 409."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(db, candidate.id, job_profile.id)

    response = client.post(
        f"/pipeline/{pipeline_run.id}/stages/{PipelinePlanner.STANDARD_STAGES[0]}/complete",
        json={"decision": "pass"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Stage completion out of order"


def test_complete_stage_idempotent(test_client):
    """Completing the same stage twice should not create duplicates."""
    client, session_factory = test_client
    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        pipeline_run = create_pipeline_run(db, candidate.id, job_profile.id)

    advance_response = client.post(f"/pipeline/{pipeline_run.id}/advance")
    stage_name = advance_response.json()["current_stage"]

    first = client.post(
        f"/pipeline/{pipeline_run.id}/stages/{stage_name}/complete",
        json={"decision": "pass"},
    )
    second = client.post(
        f"/pipeline/{pipeline_run.id}/stages/{stage_name}/complete",
        json={"decision": "pass"},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    with session_factory() as db:
        stage_results = (
            db.query(StageResult)
            .filter(StageResult.pipeline_run_id == pipeline_run.id)
            .all()
        )
        assert len(stage_results) == 1


def test_negative_pipeline_id_rejected(test_client):
    """Negative pipeline IDs should be rejected by validation."""
    client, _session_factory = test_client
    response = client.get("/pipeline/-1")
    assert response.status_code == 422


def test_zero_pipeline_id_rejected(test_client):
    """Zero pipeline ID should be rejected by validation."""
    client, _session_factory = test_client
    response = client.get("/pipeline/0")
    assert response.status_code == 422


def test_start_pipeline_zero_id_returns_422(test_client):
    """ID of 0 should be rejected by validation."""
    client, _session_factory = test_client
    response = client.post(
        "/pipeline/start",
        json={"candidate_id": 0, "job_profile_id": 1},
    )
    assert response.status_code == 422


def test_complete_final_stage_marks_pipeline_completed(test_client):
    """Completing the final stage should set pipeline status to COMPLETED."""
    client, session_factory = test_client
    stages = PipelinePlanner.STANDARD_STAGES

    with session_factory() as db:
        candidate, job_profile = create_candidate_and_job_profile(db)
        # Advance through all stages to the last one
        pipeline_run = create_pipeline_run(db, candidate.id, job_profile.id)

    # Advance to and complete all stages except the last
    for stage in stages[:-1]:
        client.post(f"/pipeline/{pipeline_run.id}/advance")
        client.post(
            f"/pipeline/{pipeline_run.id}/stages/{stage}/complete",
            json={"decision": "pass"},
        )

    # Advance to final stage
    advance_response = client.post(f"/pipeline/{pipeline_run.id}/advance")
    final_stage = advance_response.json()["current_stage"]
    assert final_stage == stages[-1]

    # Complete final stage
    complete_response = client.post(
        f"/pipeline/{pipeline_run.id}/stages/{final_stage}/complete",
        json={"decision": "pass"},
    )
    assert complete_response.status_code == 200

    # Verify pipeline is completed
    with session_factory() as db:
        pipeline = db.get(PipelineRun, pipeline_run.id)
        assert pipeline.status == PipelineStatus.COMPLETED.value
        assert pipeline.completed_at is not None


def test_get_pipeline_not_found(test_client):
    """GET /pipeline/{id} should return 404 for non-existent pipeline."""
    client, _session_factory = test_client
    response = client.get("/pipeline/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pipeline run not found"


def test_advance_pipeline_not_found(test_client):
    """Advance should return 404 for non-existent pipeline."""
    client, _session_factory = test_client
    response = client.post("/pipeline/99999/advance")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pipeline run not found"


def test_complete_stage_pipeline_not_found(test_client):
    """Complete stage should return 404 for non-existent pipeline."""
    client, _session_factory = test_client
    response = client.post("/pipeline/99999/stages/resume_screen/complete")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pipeline run not found"
