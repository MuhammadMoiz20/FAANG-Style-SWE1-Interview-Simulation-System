#!/bin/bash

# Backend setup script
echo "Setting up FAANG Interview Simulation System Backend..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your database credentials"
fi

echo "✓ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your PostgreSQL database credentials"
echo "2. Create the database: createdb interview_system"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start the server: uvicorn app.main:app --reload"
