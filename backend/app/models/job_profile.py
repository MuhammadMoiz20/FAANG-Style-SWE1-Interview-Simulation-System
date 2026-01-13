"""JobProfile model."""

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class JobProfile(Base):
    """
    Job Profile entity representing a specific role and its requirements.
    
    This captures the extracted job requirements, company style, and
    interview biases for a specific position.
    """

    __tablename__ = "job_profiles"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True, index=True)
    company_style = Column(String(100), nullable=True)  # e.g., "Meta-like", "Google-like"
    
    # Job description
    raw_description = Column(Text, nullable=False)
    
    # Requirements
    must_haves = Column(JSON, nullable=False, default=list, server_default="[]")  # List[str]
    nice_to_haves = Column(JSON, nullable=False, default=list, server_default="[]")  # List[str]
    core_competencies = Column(JSON, nullable=False, default=list, server_default="[]")  # List[str]
    
    # Interview style bias (0-1 scale)
    interview_style_bias = Column(JSON, nullable=False, default=dict, server_default="{}")  # Dict[str, float]
    # e.g., {"speed": 0.7, "communication": 0.6, "system_design": 0.2}
    
    # Metadata
    source_url = Column(String(500), nullable=True)
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
    pipeline_runs = relationship("PipelineRun", back_populates="job_profile", passive_deletes=True)
