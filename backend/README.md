# Backend - FAANG Interview Simulation System

FastAPI backend for the interview simulation system.

## Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── app/
│   ├── models/          # SQLAlchemy models
│   │   ├── candidate.py
│   │   ├── job_profile.py
│   │   ├── pipeline_run.py
│   │   └── stage_result.py
│   ├── routers/         # API endpoints
│   │   ├── health.py
│   │   └── pipeline.py
│   ├── schemas/         # Pydantic schemas
│   │   └── pipeline.py
│   ├── services/        # Business logic
│   │   └── pipeline_planner.py
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI app
├── tests/               # Tests (to be added)
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── setup.sh            # Setup script
```

## Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Create database:
   ```bash
   createdb interview_system
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Code Quality

Format code:
```bash
black .
```

Lint:
```bash
ruff check .
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```
