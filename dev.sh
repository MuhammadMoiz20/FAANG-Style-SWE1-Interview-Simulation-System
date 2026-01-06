#!/bin/bash

# Development runner - starts both backend and frontend

echo "=========================================="
echo "Starting FAANG Interview System"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if setup has been run
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend not set up. Run ./setup.sh first"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Run ./setup.sh first"
    exit 1
fi

# Start backend
echo "Starting backend on http://localhost:8000"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:5173"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "✓ Services Started!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
