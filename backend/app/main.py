"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, pipeline

app = FastAPI(
    title="FAANG Interview Simulation System",
    description="AI-driven interview simulation system with realistic FAANG-style interviews",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(pipeline.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FAANG Interview Simulation System API",
        "version": "0.1.0",
        "docs": "/docs",
    }
