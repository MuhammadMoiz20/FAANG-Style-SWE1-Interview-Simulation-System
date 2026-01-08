"""Test pipeline planner service."""

from app.models.candidate import Candidate
from app.models.job_profile import JobProfile
from app.services.pipeline_planner import PipelinePlanner


def test_plan_pipeline():
    """Test basic pipeline planning."""
    planner = PipelinePlanner()
    
    # Mock objects
    job_profile = JobProfile(
        role="Software Engineer I",
        company="Test Corp",
        raw_description="Test description",
        must_haves=["Python", "CS Degree"],
        nice_to_haves=["React"],
        core_competencies=["Coding", "Communication"],
        interview_style_bias={"speed": 0.7},
    )
    
    candidate = Candidate(
        email="test@example.com",
        name="Test User",
    )
    
    stages, stage_progress = planner.plan_pipeline(job_profile, candidate)
    
    # Verify stages
    assert len(stages) > 0
    assert "resume_screen" in stages
    assert "oa" in stages
    
    # Verify all stages initialized to "created"
    for stage in stages:
        assert stage_progress[stage] == "created"


def test_get_next_stage():
    """Test getting next stage."""
    planner = PipelinePlanner()
    stages = ["resume_screen", "oa", "phone_screen"]
    
    # First stage
    assert planner.get_next_stage(stages, None) == "resume_screen"
    
    # Middle stage
    assert planner.get_next_stage(stages, "resume_screen") == "oa"
    
    # Last stage
    assert planner.get_next_stage(stages, "phone_screen") is None


def test_stage_state_transitions():
    """Test stage state machine."""
    planner = PipelinePlanner()
    stage_progress = {"test_stage": "created"}
    
    # Created can progress
    assert planner.can_progress(stage_progress, "test_stage") is True
    
    # Update to in_progress
    stage_progress = planner.update_stage_state(stage_progress, "test_stage", "in_progress")
    assert stage_progress["test_stage"] == "in_progress"
    
    # In_progress can progress
    assert planner.can_progress(stage_progress, "test_stage") is True
    
    # Update to completed
    stage_progress = planner.update_stage_state(stage_progress, "test_stage", "completed")
    assert stage_progress["test_stage"] == "completed"
    
    # Completed can progress to gated
    assert planner.can_progress(stage_progress, "test_stage") is True
    
    # Update to gated
    stage_progress = planner.update_stage_state(stage_progress, "test_stage", "gated")
    assert stage_progress["test_stage"] == "gated"
    
    # Gated cannot progress further
    assert planner.can_progress(stage_progress, "test_stage") is False
