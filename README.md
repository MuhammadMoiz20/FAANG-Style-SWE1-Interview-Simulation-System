# FAANG Interview Simulation System

An AI-driven system that fully simulates a FAANG-style SWE1 (entry-level Software Engineer) hiring pipeline with realistic decision-making, human-like interviewers, and bar-based hiring outcomes.

## 🎯 Project Vision

This system simulates the complete interview experience including:
- Resume screening
- Online assessments (OA)
- Phone screens
- Virtual onsite loops (4-5 interviews)
- Hiring debrief and final decisions

Built with **realistic AI interviewers** that behave like actual FAANG hiring teams, providing authentic practice for candidates preparing for technical interviews.

## 📋 Current Status: Phase 0 & 1 Complete ✅

### Completed Features

#### Phase 0: Foundations
- ✅ FastAPI backend with health endpoint
- ✅ React + Vite frontend
- ✅ PostgreSQL database with Alembic migrations
- ✅ Linting and formatting (Black, Ruff, ESLint)
- ✅ Basic CI/CD structure

#### Phase 1: Data Models + Pipeline Skeleton
- ✅ Core tables implemented:
  - `JobProfile` - Role requirements and interview biases
  - `Candidate` - Candidate information and resume
  - `PipelineRun` - Complete candidate journey tracking
  - `StageResult` - Individual stage outcomes
- ✅ Pipeline planner skeleton with stage state machine
- ✅ `POST /pipeline/start` endpoint
- ✅ Stage progression logic (`created → in_progress → completed → gated`)

## 🏗️ Architecture

### Repository Structure

```
Interview-Simulation-System/
├── backend/                 # FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── setup.sh
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── services/       # API client
│   │   ├── App.tsx         # Main component
│   │   └── main.tsx        # Entry point
│   ├── package.json
│   └── setup.sh
├── plan.md                 # Implementation roadmap
├── SRS.md                  # Software Requirements Specification
└── README.md              # This file
```

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- PostgreSQL
- Alembic (migrations)
- Pydantic (validation)

**Frontend:**
- React 18
- TypeScript
- Vite
- Axios

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Run setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Create PostgreSQL database:**
   ```bash
   createdb interview_system
   ```

4. **Update environment variables:**
   Edit `.env` with your database credentials:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/interview_system
   ```

5. **Run migrations:**
   ```bash
   source venv/bin/activate
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will be available at http://localhost:8000
   API documentation at http://localhost:8000/docs

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Run setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at http://localhost:5173

### Quick Start (Both Services)

From the project root:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 📡 API Endpoints

### Health Check
- `GET /health` - System health status

### Pipeline Management
- `POST /pipeline/start` - Start a new pipeline run
  ```json
  {
    "candidate_id": 1,
    "job_profile_id": 1
  }
  ```
- `GET /pipeline/{pipeline_id}` - Get pipeline run details
- `POST /pipeline/{pipeline_id}/advance` - Advance to next stage (test helper)

## 🗄️ Database Schema

### Core Tables

**candidates**
- Stores candidate information and resume

**job_profiles**
- Role requirements, company style, interview biases

**pipeline_runs**
- Tracks candidate journey through stages
- State machine for stage progression

**stage_results**
- Individual stage outcomes (resume screen, OA, interviews)
- Scores, strengths, concerns, artifacts

### Stage State Machine

Each stage progresses through states:
```
created → in_progress → completed → gated
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Linting
```bash
# Backend
cd backend
black .
ruff check .

# Frontend
cd frontend
npm run lint
```

## 📚 Documentation

- [Software Requirements Specification](./SRS.md) - Complete system requirements
- [Implementation Plan](./plan.md) - Detailed development roadmap
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when backend is running)

## 🛣️ Roadmap

### ✅ Phase 0: Foundations (Complete)
- Repository structure
- API with health endpoint
- Database migrations

### ✅ Phase 1: Data Models + Pipeline Skeleton (Complete)
- Core tables
- Pipeline planner
- POST /pipeline/start endpoint

### 🔄 Phase 2: Job Ingest + Resume Screening (Next)
- Job description parsing
- LLM-based resume screening
- Proceed/Hold/Reject logic

### 📋 Phase 3: Online Assessment Engine
- OA question generation (archetype-based)
- Code execution and evaluation
- Scoring and gating logic

### 📋 Phase 4: Interview Orchestrator + AI Agents
- Interview state machine
- AI interviewer personas
- Real-time interview sessions

### 📋 Phase 5: Grading Engine + Debrief
- Rubric-based grading
- Hiring debrief simulation
- Final hire/no-hire decisions

### 📋 Phase 6: Candidate Output + Admin Tools
- Decision packets
- Admin dashboard
- Transcript review

### 📋 Phase 7: Realism Controls + Hardening
- Time enforcement
- Variance injection
- Safety filtering

## 🤝 Contributing

This is a learning/interview prep project. Contributions welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This is a **simulation tool** for interview preparation. It does not:
- Copy proprietary FAANG interview questions
- Guarantee hiring outcomes
- Replace actual interview practice

Use this tool ethically and as a supplement to your interview preparation.

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## 📞 Support

For issues or questions:
1. Check existing [issues](../../issues)
2. Create a new issue with detailed description
3. Join discussions in [discussions](../../discussions)

---

**Built with ❤️ for better interview preparation**
