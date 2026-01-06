# FAANG-Style SWE1 Interview Simulation System

**Specification v1.0**

## 1. Purpose & Goals

### Objective

Build an AI-driven system that **fully simulates a FAANG entry-level SWE (SWE1) hiring pipeline**, end-to-end, with **realistic decision-making**, **human-like interviewers**, and **bar-based hiring outcomes**.

The system must:

* Behave like real FAANG recruiters/interviewers
* Use realistic interview structures and evaluation criteria
* Produce decisions consistent with actual hiring debriefs
* Provide immersive, real-time interviews via AI agents (voice or text)
* Avoid proprietary question leakage while remaining authentic

### Non-Goals

* Video interviews (explicitly excluded)
* Coaching during interviews (except limited hints like real interviewers)
* Copying proprietary or leaked FAANG OA questions verbatim

---

## 2. End-to-End Candidate Flow

```
Job Ingest
   ↓
Resume Screen
   ↓
Online Assessment (OA)
   ↓
Phone Screen (Behavioral + Coding)
   ↓
Virtual Onsite Loop (4–5 interviews)
   ↓
Hiring Debrief
   ↓
Final Decision (Hire / No Hire / Hold*)
```

* Hold is optional/configurable

---

## 3. System Architecture (High Level)

```
┌─────────────────────┐
│ Job Ingest Service  │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Resume Parser       │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Pipeline Planner    │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Interview Engine    │◄───────┐
│  (AI Agents)        │        │
└─────────┬───────────┘        │
          ↓                    │
┌─────────────────────┐        │
│ Grading Engine      │────────┘
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Hiring Debrief      │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Decision Generator  │
└─────────────────────┘
```

---

## 4. Job Ingest Service

### Input

* Job URL (preferred)
* OR pasted job description text

### Responsibilities

* Scrape job description (fallback to user-provided text)
* Extract:

  * Must-have requirements
  * Nice-to-have requirements
  * Keywords (languages, frameworks, domains)
  * Seniority signals (new grad vs industry)
  * Company style profile (speed vs rigor vs values)

### Output: `JobProfile`

```json
{
  "role": "Software Engineer I",
  "company_style": "Meta-like",
  "must_haves": ["Python or Java", "DSA", "BS CS"],
  "nice_to_haves": ["React", "AWS"],
  "core_competencies": ["Algorithms", "Coding", "Communication"],
  "interview_style_bias": {
    "speed": 0.7,
    "communication": 0.6,
    "system_design": 0.2
  }
}
```

---

## 5. Resume Screening Module

### Behavior

Simulates a FAANG recruiter screen.

### Evaluation Dimensions

* Education baseline (CS or equivalent)
* Evidence of coding
* Impact (metrics, ownership)
* Resume clarity
* Match vs JD must-haves

### Output

* `Proceed`
* `Hold`
* `Reject`

### Output: `ResumeScreenResult`

```json
{
  "decision": "Proceed",
  "strengths": ["Strong internships", "Clear impact metrics"],
  "concerns": ["Limited low-level systems experience"]
}
```

---

## 6. Online Assessment (OA) Engine

### OA Selection Logic

Based on:

* Job profile
* Company style
* Candidate seniority

### OA Formats

* 2 coding problems (70–90 min)
* 3 coding problems (90 min)
* Coding + light MCQ (optional)

### Question Generation

Use **problem archetypes**, not copied questions.

#### Archetype Examples

* Sliding window
* Hash map counting
* BFS/DFS
* Tree recursion
* Greedy + sorting
* Binary search on answer

Each problem includes:

* Difficulty target
* Expected complexity
* Hidden edge cases
* Time pressure

### OA Scoring

* Correctness (hidden tests)
* Time/space complexity
* Completion speed

### OA Gate

* Pass
* Borderline
* Fail

---

## 7. Interview Engine (AI Interviewers)

### Core Principle

**Interviewer ≠ Grader**

Two separate agents:

* Interviewer Agent (talks)
* Grading Agent (evaluates)

---

## 8. Interviewer Agent Specification

### Modalities

* Text (required)
* Voice (optional; STT/TTS)

### State Machine

```
Intro → Resume Probe → Question → Clarifications
→ Solutioning → Coding → Testing → Complexity
→ Wrap-up → Internal Evaluation
```

### Interviewer Constraints

* Strict time awareness
* Hint budget enforced
* Interruptions allowed
* No coaching
* No revealing scores/tests

---

## 9. Interview Personas

### Coding Interviewer A (Efficiency-biased)

* Pushes for optimal complexity
* Low hint tolerance

### Coding Interviewer B (Communication-biased)

* Values clarity, structure, test cases

### Behavioral Interviewer

* STAR enforcement
* Conflict probing
* Ownership detection

### Design-Lite Interviewer (SWE1)

* Decomposition
* Tradeoffs
* APIs / data modeling
* No distributed systems depth

Each persona has configurable:

* Interruptiveness
* Hint strictness
* Silence tolerance

---

## 10. Hint System

### Hint Levels

* Level 0: Open-ended nudge
* Level 1: Directional hint
* Level 2: Explicit guidance (rare)

### Policy

* Max 2 Level-0 hints
* Max 1 Level-1 hint
* Level-2 severely impacts score

Hints are logged and penalize autonomy.

---

## 11. Grading Engine

### Coding Rubric (0–1 normalized)

* correctness
* complexity
* autonomy
* communication
* testing

### Behavioral Rubric

* Situation clarity
* Ownership
* Action quality
* Results
* Reflection

### Rating Mapping (1–4)

| Rating | Meaning     |
| ------ | ----------- |
| 4      | Strong Hire |
| 3      | Hire        |
| 2      | Lean No     |
| 1      | No Hire     |

Each score includes confidence ∈ [0,1].

---

## 12. Phone Screen

### Structure

* 5 min intro
* 10 min resume + behavioral
* 35 min coding
* 5 min Q&A

### Gate

* Advance
* No

---

## 13. Onsite Loop

Typical SWE1 Loop:

* Coding Interview 1
* Coding Interview 2
* Behavioral / Values
* Design-Lite
* (Optional) Hiring Manager

Each interview produces a scorecard.

---

## 14. Hiring Debrief Engine

### Killer Signals (Auto No-Hire)

* Integrity issues
* Toxic behavior
* Cannot code baseline problems
* Massive leveling mismatch

### Bar Rules

* ≥2 coding interviews rated ≥3
* No coding interview rated 1
* Behavioral ≥2

### Evidence Score

```
EvidenceScore = Σ(weight × rating × confidence) − ConsistencyPenalty
```

### Decision Thresholds

* Hire: ≥ 2.85 + bar met
* No Hire: < 2.6 or bar fail
* Hold: optional 2.6–2.85

---

## 15. Final Output to Candidate

### Decision Packet

* Final decision
* Strengths
* Areas for improvement
* Leveling note
* Suggested prep focus

No raw scores unless explicitly enabled.

---

## 16. Data Models (Core)

### InterviewSession

```json
{
  "stage": "onsite_coding_1",
  "persona": "coding_efficiency",
  "time_remaining": 12,
  "hints_used": [0, 1],
  "rubric_evidence": {}
}
```

### Scorecard

```json
{
  "overall_rating": 3,
  "confidence": 0.7,
  "strengths": ["Good decomposition"],
  "concerns": ["Missed edge case"],
  "leveling": "At SWE1"
}
```

---

## 17. Realism Controls (Critical)

* Time cutoffs enforced
* Interviewers may end early
* Slight interviewer variance
* Candidate questions affect behavioral score
* Communication silence penalized

---

## 18. Security & Ethics

* No proprietary question replication
* No deceptive hiring claims
* Clear disclosure: “simulation tool”

---

## 19. Extensibility

* Company-specific calibration profiles
* SWE2/Senior variants
* Mock recruiter feedback mode
* Confidence tracking over multiple runs

---

## 20. Success Criteria

* Interview outcomes correlate with real FAANG performance
* Candidates report realism
* Decisions explainable via evidence
* No “gaming” through memorization

---
