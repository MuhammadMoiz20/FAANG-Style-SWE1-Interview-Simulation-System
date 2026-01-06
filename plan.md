# Implementation Plan: FAANG-Style SWE1 Interview Simulation System

This plan turns the SRS into an executable roadmap, with an efficient architecture that starts as a modular monolith and can evolve into services without rework.

---

## 1. Architecture Overview (Efficient by Default)

### 1.1 Recommended Approach
- **Modular monolith** with clear service boundaries and interfaces.
- **Single API surface** for the UI/clients, internal modules organized by domain.
- **LLM gateway** as a single integration layer for AI calls (prompts, personas, grading).
- **Evented pipeline** inside the monolith using a job queue abstraction (can remain in-process initially).

This avoids early microservice overhead while keeping the path open to extraction later.

### 1.2 Core Modules (Logical Services)
- **Job Ingest**
- **Resume Screening**
- **Pipeline Planner**
- **OA Engine**
- **Interview Orchestrator** (state machine + scheduling)
- **Interviewer Agent Runtime** (prompting + persona control)
- **Grading Engine**
- **Debrief + Decision Engine**
- **Candidate Output Generator**
- **Admin/Calibration Tools**

### 1.3 Data Stores
- **Relational DB (Postgres)**: structured entities, sessions, scorecards, decisions.
- **Object Storage**: transcripts, audio, artifacts (optional voice).
- **Vector Store** (optional MVP+): archetype retrieval, rubric examples.
- **Cache (Redis)**: session state, active interviews, token budgeting.

### 1.4 High-Level Flow (Execution)
1. Job Ingest -> JobProfile
2. Resume Screening -> ResumeScreenResult
3. Pipeline Planner builds pipeline stages
4. OA Engine runs -> OA Result
5. Interview Orchestrator runs sessions -> Scorecards
6. Debrief Engine -> EvidenceScore
7. Decision Generator -> Decision Packet

---

## 2. Domain Model (Core Tables / Schemas)

### 2.1 Entities
- **JobProfile** (role, must_haves, interview_style_bias, etc.)
- **Candidate** (basic info, resume, metadata)
- **PipelineRun** (candidate_id, job_profile_id, status, stage_progress)
- **StageResult** (stage, decision, raw_scores, artifacts)
- **InterviewSession** (stage, persona, time_remaining, hints_used)
- **Scorecard** (ratings, confidence, strengths, concerns)
- **Evidence** (rubric evidence, hint penalties, time impacts)
- **DecisionPacket** (final decision, strengths, improvements)

### 2.2 Event/State Model
Use explicit stage states:
- `created -> in_progress -> completed -> gated`
This drives the pipeline planner and avoids hidden coupling.

---

## 3. LLM + Persona Design

### 3.1 LLM Gateway
Central wrapper for:
- prompt templates
- role-based system messages
- log/tracing of all LLM calls
- response validation (schema checks)

### 3.2 Prompt Groups
- **Interviewer prompts** (per persona + per phase)
- **Grader prompts** (rubric-based scoring)
- **Decision prompts** (hiring debrief synthesis)
- **OA generation prompts** (archetype-based)

### 3.3 Guardrails
- content filter for proprietary question leakage
- strict JSON schema parsing for grading
- token budgeting per session

---

## 4. Detailed Implementation Phases

### Phase 0: Foundations (Week 0)
- Choose framework and stack (suggested: Node + Fastify/Next API or Python + FastAPI).
- Establish repo structure: `apps/`, `packages/`, `services/`, `prompts/`, `schemas/`.
- Add linting, formatting, basic CI.
- Create DB migration tooling and initial schema.

Deliverables:
- Running API with health endpoint.
- Schema migrations applied locally.

### Phase 1: Data Models + Pipeline Skeleton
- Implement core tables (JobProfile, Candidate, PipelineRun, StageResult).
- Build pipeline planner skeleton:
  - takes JobProfile + candidate metadata
  - outputs stages in order
- Implement stage state machine (created, in_progress, completed, gated).

Deliverables:
- `POST /pipeline/start` creates a PipelineRun.
- Basic stage progression stored in DB.

### Phase 2: Job Ingest + Resume Screening
- Job Ingest:
  - URL parsing (stub if no scraping yet).
  - JD text ingestion.
  - Extract requirements and style bias using LLM.
- Resume Screening:
  - LLM rubric scoring with structured output.
  - Configurable thresholds for Proceed/Hold/Reject.

Deliverables:
- `POST /job/ingest`
- `POST /resume/screen`
- ResumeScreenResult persisted in StageResult.

### Phase 3: OA Engine
- OA archetype library (local JSON with archetypes).
- OA generator uses archetypes + difficulty targets.
- OA evaluation:
  - sample input/output sets
  - hidden tests
  - scoring rubric (correctness, complexity, speed)
- OA gate logic (pass, borderline, fail).

Deliverables:
- `POST /oa/generate`
- `POST /oa/submit`
- OA StageResult with gate.

### Phase 4: Interview Orchestrator + Interviewer Agent
- Implement interview session state machine:
  - intro, probe, question, clarifications, solutioning, coding, testing, complexity, wrap-up.
- Persona config registry (efficiency, communication, behavioral, design-lite).
- Hint budget logic with penalties recorded.
- Transcript capture + timing enforcement.

Deliverables:
- `POST /interview/start`
- `POST /interview/next` (returns interviewer turn)
- Session persistence with timestamps.

### Phase 5: Grading Engine + Debrief
- Implement grading rubric per interview type.
- LLM grader returns normalized rubric scores.
- Convert to 1-4 ratings with confidence.
- Debrief engine aggregates evidence and applies bar rules.

Deliverables:
- `POST /interview/grade`
- `POST /debrief/run`
- Decision produced (Hire/No/Hold).

### Phase 6: Candidate Output + Admin Tools
- Generate DecisionPacket with strengths/areas.
- Admin UI endpoints for reviewing transcripts and scorecards.
- Calibration profiles (company-style biases).

Deliverables:
- `GET /candidate/decision`
- `GET /admin/pipeline/:id`

### Phase 7: Realism Controls + Hardening
- Time cutoff enforcement with warnings and forced wrap-up.
- Variance injection (minor randomness in persona strictness).
- Safety filtering for question leakage.
- Security and ethics disclosures in UI and responses.

Deliverables:
- Realism toggles in config.
- Automated QA suite for rubric consistency.

---

## 5. Prompt + Rubric Assets

Organize assets for reuse and versioning:
- `prompts/interviewers/*.md`
- `prompts/graders/*.md`
- `prompts/decision/*.md`
- `rubrics/*.json`
- `archetypes/*.json`

Each prompt should be paired with:
- input schema
- output schema
- example input/output (minimal)

---

## 6. API Surface (Draft)

- `POST /job/ingest`
- `POST /resume/screen`
- `POST /pipeline/start`
- `POST /oa/generate`
- `POST /oa/submit`
- `POST /interview/start`
- `POST /interview/next`
- `POST /interview/grade`
- `POST /debrief/run`
- `GET /candidate/decision`

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Stage state transitions.
- Bar rule logic.
- Hint budget enforcement.
- EvidenceScore calculation.

### 7.2 Integration Tests
- End-to-end pipeline run with mocked LLM.
- Resume -> OA -> interview -> debrief.

### 7.3 Prompt/LLM Tests
- Schema validation for all LLM responses.
- Golden transcript comparisons for regressions.

---

## 8. Risks + Mitigations

- **LLM variability**: enforce schema, add retries with strict parsing.
- **Prompt leakage**: add content filters and archetype pool.
- **Overfitting to rubrics**: add randomization + calibration profiles.
- **Latency**: pre-generate OA, cache persona prompts.

---

## 9. Milestone Checklist

- M1: Pipeline skeleton + storage
- M2: Resume + Job ingest live
- M3: OA engine passing tests
- M4: Interview engine + personas
- M5: Grading + debrief + decision
- M6: UI outputs + admin tools
- M7: Realism tuning + QA suite

---

## 10. Suggested Next Steps

1. Choose implementation stack and repo structure.
2. Finalize schema for JobProfile, PipelineRun, InterviewSession, Scorecard.
3. Start Phase 1 with pipeline skeleton and state machine.
