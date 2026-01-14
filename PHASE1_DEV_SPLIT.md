# Phase 1 (Data Models + Pipeline Skeleton) - 3-Dev Async PR Plan

## Goal
Deliver Phase 1 from `plan.md`:
- Core tables: JobProfile, Candidate, PipelineRun, StageResult.
- Pipeline planner skeleton: inputs JobProfile + Candidate, outputs ordered stages.
- Stage state machine: created -> in_progress -> completed -> gated.
- `POST /pipeline/start` creates a PipelineRun with stored stage progression.

## Non-goals (Phase 1)
- LLM calls, resume screening, OA, interview orchestration.
- UI work.

## Shared Decisions (agree once, then build)
- Stage states: `created`, `in_progress`, `completed`, `gated`.
- Stage names for SWE1 pipeline (draft): `resume_screen`, `oa`, `phone_screen`, `onsite_coding_1`, `onsite_coding_2`, `onsite_behavioral`, `onsite_design_lite`, `debrief`.
- `POST /pipeline/start` expects existing `candidate_id` and `job_profile_id`.

## PR Breakdown (Async, minimal file overlap)

### Dev A - Data Models + Migrations
Scope:
- SQLAlchemy models and Alembic migrations for core tables.
- Constraints, indexes, and relationships.

Deliverables:
- Models: Candidate, JobProfile, PipelineRun, StageResult.
- Alembic migration with tables, enums, indexes.
- Ensure timestamps and JSON columns align with defaults.

Files likely touched:
- `backend/app/models/*.py`
- `backend/alembic/versions/*.py`
- `backend/app/models/__init__.py`

Acceptance criteria:
- `alembic upgrade head` creates all tables with expected columns.
- Relationships and enums resolve without runtime errors.

Tests/validation:
- Simple model import check or minimal DB create (existing test harness ok).

### Dev B - Pipeline Planner + State Machine
Scope:
- Pipeline planner service outputs stage list and initial stage_progress.
- State machine validation and transitions.

Deliverables:
- Planner exposes `plan_pipeline`, `get_next_stage`, `can_progress`, `update_stage_state`.
- Unit tests for stage order and valid transitions.

Files likely touched:
- `backend/app/services/pipeline_planner.py`
- `backend/tests/test_pipeline_planner.py`

Acceptance criteria:
- Stage list returned in correct order.
- Invalid transitions are blocked in tests.
- Stage progress initialized to `created` for all stages.

Tests/validation:
- `pytest backend/tests/test_pipeline_planner.py`

### Dev C - Pipeline API + Schemas + Integration Tests
Scope:
- API routes for starting a pipeline run and reading it back.
- Pydantic schemas for request/response.
- Integration tests for `POST /pipeline/start`.

Deliverables:
- `POST /pipeline/start` creates a PipelineRun with stages and progress.
- `GET /pipeline/{id}` returns pipeline data.
- Error handling for missing candidate/job_profile.

Files likely touched:
- `backend/app/routers/pipeline.py`
- `backend/app/schemas/pipeline.py`
- `backend/tests/test_pipeline_api.py`

Acceptance criteria:
- Response includes `id`, `status`, `current_stage`, `stages`, `stage_progress`.
- 404 for invalid candidate/job profile.

Tests/validation:
- `pytest backend/tests/test_pipeline_api.py`

## Integration Notes
- Keep enum/string values consistent across models, planner, and API.
- Favor JSON `stage_progress` as `{stage_name: state}` for easy updates.
- If conflict arises around stage naming, defer to `plan.md` defaults.

## Definition of Done (Phase 1)
- DB schema migrated with core tables.
- Pipeline planner skeleton returns ordered stages and initial state.
- `POST /pipeline/start` works end-to-end with persisted stage_progress.
