#!/bin/bash

# Complete project setup script
echo "=========================================="
echo "FAANG Interview Simulation System Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed."
fi

echo ""
echo "=========================================="
echo "Setting up Backend..."
echo "=========================================="
cd backend
chmod +x setup.sh
./setup.sh
cd ..

echo ""
echo "=========================================="
echo "Setting up Frontend..."
echo "=========================================="
cd frontend
chmod +x setup.sh
./setup.sh
cd ..

echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Create PostgreSQL database:"
echo "   createdb interview_system"
echo ""
echo "2. Update backend/.env with your database credentials"
echo ""
echo "3. Run database migrations:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "4. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "5. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "6. Open http://localhost:5173 in your browser"
echo ""
echo "📚 Documentation:"
echo "   - Backend: http://localhost:8000/docs"
echo "   - README: ./README.md"
echo "   - SRS: ./SRS.md"
echo "   - Plan: ./plan.md"
echo ""
