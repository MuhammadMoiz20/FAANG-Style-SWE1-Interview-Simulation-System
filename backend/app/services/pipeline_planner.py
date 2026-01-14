"""Pipeline planning service."""

from typing import Dict, List

from app.models.job_profile import JobProfile
from app.models.candidate import Candidate


class PipelinePlanner:
    """
    Pipeline Planner service.
    
    Determines the stages a candidate should go through based on
    job profile and candidate metadata.
    """

    # Standard SWE1 pipeline stages
    STANDARD_STAGES = [
        "resume_screen",
        "oa",
        "phone_screen",
        "onsite_coding_1",
        "onsite_coding_2",
        "onsite_behavioral",
        "onsite_design_lite",
        "debrief",
    ]

    STATE_TRANSITIONS = {
        "created": ["in_progress"],
        "in_progress": ["completed"],
        "completed": ["gated"],
        "gated": [],
    }
    VALID_TARGET_STATES = {
        state for transitions in STATE_TRANSITIONS.values() for state in transitions
    }

    def plan_pipeline(
        self, job_profile: JobProfile, candidate: Candidate
    ) -> tuple[List[str], Dict[str, str]]:
        """
        Generate ordered stages and initial state for a pipeline run.
        
        Args:
            job_profile: The job profile for the role
            candidate: The candidate metadata
            
        Returns:
            Tuple of (stages_list, stage_progress_dict)
            - stages_list: ordered list of stage names
            - stage_progress_dict: initial state mapping {stage: "created"}
        """
        # For now, use standard pipeline
        # Future: customize based on job_profile.interview_style_bias
        stages = self.STANDARD_STAGES.copy()
        
        # Initialize all stages to "created" state
        stage_progress = {stage: "created" for stage in stages}
        
        return stages, stage_progress

    def get_next_stage(self, stages: List[str], current_stage: str | None) -> str | None:
        """
        Get the next stage in the pipeline.
        
        Args:
            stages: List of all stages
            current_stage: Current stage name (or None if at start)
            
        Returns:
            Next stage name, or None if at end
        """
        if current_stage is None:
            return stages[0] if stages else None
        
        try:
            current_idx = stages.index(current_stage)
            if current_idx + 1 < len(stages):
                return stages[current_idx + 1]
        except ValueError:
            pass
        
        return None

    def can_progress(
        self, stage_progress: Dict[str, str], stage: str, new_state: str | None = None
    ) -> bool:
        """
        Check if a stage can progress (state machine validation).
        
        Args:
            stage_progress: Current stage progress mapping
            stage: Stage to check
            
        Returns:
            True if stage can progress to next state or to new_state if provided
        """
        current_state = stage_progress.get(stage, "created")
        transitions = self.STATE_TRANSITIONS.get(current_state, [])

        if new_state is None:
            return bool(transitions)

        return new_state in transitions

    def update_stage_state(
        self, stage_progress: Dict[str, str], stage: str, new_state: str
    ) -> Dict[str, str]:
        """
        Update a stage's state.
        
        Args:
            stage_progress: Current stage progress mapping
            stage: Stage to update
            new_state: New state value
            
        Returns:
            Updated stage_progress dict
        """
        current_state = stage_progress.get(stage, "created")
        if new_state == current_state:
            return stage_progress

        if new_state not in self.VALID_TARGET_STATES:
            raise ValueError(f"Unknown stage state: {new_state}")

        if not self.can_progress(stage_progress, stage, new_state=new_state):
            raise ValueError(
                f"Invalid transition for stage '{stage}': {current_state} -> {new_state}"
            )

        stage_progress[stage] = new_state
        return stage_progress
