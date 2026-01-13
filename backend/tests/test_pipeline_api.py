"""Test pipeline API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Candidate, JobProfile, PipelineRun
from app.services.pipeline_planner import PipelinePlanner


@pytest.fixture()
def test_client():
    """Provide a TestClient with an isolated in-memory database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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
    assert data["status"] == "CREATED"
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
    assert data["status"] == "CREATED"
    assert data["stages"] == expected_stages
    assert data["stage_progress"] == expected_progress
