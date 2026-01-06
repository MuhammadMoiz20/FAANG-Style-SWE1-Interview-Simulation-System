# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites Check

Ensure you have:
- Python 3.11+ (`python3 --version`)
- Node.js 18+ (`node --version`)
- PostgreSQL 14+ (`psql --version`)

### 2. Run Setup

From the project root:

```bash
./setup.sh
```

This will install all dependencies for both backend and frontend.

### 3. Create Database

```bash
createdb interview_system
```

### 4. Configure Backend

Update `backend/.env` with your database credentials:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/interview_system
```

### 5. Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 6. Seed Database (Optional)

Add sample data for testing:

```bash
python seed.py
```

This creates:
- 3 sample candidates
- 2 job profiles (Meta-like and Google-like)

### 7. Start Backend

In one terminal:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 8. Start Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:5173

### 9. Test the System

1. Open http://localhost:5173 in your browser
2. You should see "Backend Connected" status
3. Try the API at http://localhost:8000/docs

#### Test Pipeline Creation

Using the API docs (http://localhost:8000/docs):

1. Go to `POST /pipeline/start`
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "candidate_id": 1,
     "job_profile_id": 1
   }
   ```
4. Click "Execute"
5. You should get a pipeline run with stages!

#### Using curl

```bash
# Create a pipeline run
curl -X POST "http://localhost:8000/pipeline/start" \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": 1, "job_profile_id": 1}'

# Get pipeline status
curl "http://localhost:8000/pipeline/1"

# Advance pipeline to next stage
curl -X POST "http://localhost:8000/pipeline/1/advance"
```

## 🎯 What's Next?

Now that you have Phase 0 & 1 running:

1. **Explore the API** - Check out all endpoints at http://localhost:8000/docs
2. **Review the Code** - Look at the models, services, and routers
3. **Read the Plan** - See [plan.md](./plan.md) for upcoming phases
4. **Start Phase 2** - Begin implementing Job Ingest and Resume Screening

## 🐛 Troubleshooting

### Database Connection Error

If you see database connection errors:

1. Verify PostgreSQL is running:
   ```bash
   pg_isready
   ```

2. Check your credentials in `backend/.env`

3. Ensure database exists:
   ```bash
   psql -l | grep interview_system
   ```

### Backend Won't Start

1. Activate virtual environment:
   ```bash
   cd backend
   source venv/bin/activate
   ```

2. Check dependencies are installed:
   ```bash
   pip list
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

### Frontend Issues

1. Clear node_modules and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check Node version:
   ```bash
   node --version  # Should be 18+
   ```

### Port Already in Use

If port 8000 or 5173 is in use:

**Backend:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
Update `vite.config.ts` to use different port.

## 📚 Additional Resources

- **Full Documentation**: [README.md](./README.md)
- **Requirements**: [SRS.md](./SRS.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Backend README**: [backend/README.md](./backend/README.md)
- **Frontend README**: [frontend/README.md](./frontend/README.md)

## ✅ Phase 0 & 1 Checklist

- [x] Backend API running
- [x] Frontend running
- [x] Database migrations applied
- [x] Health endpoint working
- [x] Pipeline start endpoint working
- [x] Can create pipeline runs
- [x] Stage state machine functioning

**You're ready to build Phase 2!** 🚀
