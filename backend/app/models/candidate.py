"""Candidate model."""

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Candidate(Base):
    """
    Candidate entity representing a person going through the interview process.
    """

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    
    # Resume information
    resume_text = Column(Text, nullable=True)
    resume_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    # Relationships
    pipeline_runs = relationship("PipelineRun", back_populates="candidate", passive_deletes=True)
