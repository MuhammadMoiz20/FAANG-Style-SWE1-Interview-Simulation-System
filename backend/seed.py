"""Seed database with sample data for testing."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Candidate, JobProfile, PipelineRun


def seed_database():
    """Seed the database with sample data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Candidate).count() > 0:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create sample candidates
        candidates = [
            Candidate(
                email="alice@example.com",
                name="Alice Johnson",
                resume_text="BS Computer Science, 3 years Python, React experience...",
            ),
            Candidate(
                email="bob@example.com",
                name="Bob Smith",
                resume_text="MS Software Engineering, 2 years Java, AWS experience...",
            ),
            Candidate(
                email="charlie@example.com",
                name="Charlie Brown",
                resume_text="Self-taught developer, 5 years JavaScript, Node.js...",
            ),
        ]
        
        for candidate in candidates:
            db.add(candidate)
        
        db.commit()
        print(f"✓ Created {len(candidates)} candidates")
        
        # Create sample job profiles
        job_profiles = [
            JobProfile(
                role="Software Engineer I",
                company="Meta",
                company_style="Meta-like",
                raw_description="We are looking for a Software Engineer to join our team...",
                must_haves=["Python or Java", "Data Structures & Algorithms", "BS in CS"],
                nice_to_haves=["React", "AWS", "System Design"],
                core_competencies=["Algorithms", "Coding", "Communication", "Problem Solving"],
                interview_style_bias={
                    "speed": 0.7,
                    "communication": 0.6,
                    "system_design": 0.2,
                },
                source_url="https://example.com/jobs/swe1",
            ),
            JobProfile(
                role="Software Engineer I",
                company="Google",
                company_style="Google-like",
                raw_description="Join Google as a Software Engineer...",
                must_haves=["CS Fundamentals", "Algorithms", "Coding"],
                nice_to_haves=["Python", "C++", "Distributed Systems"],
                core_competencies=["Algorithms", "Data Structures", "System Design", "Coding"],
                interview_style_bias={
                    "speed": 0.5,
                    "communication": 0.7,
                    "system_design": 0.3,
                },
                source_url="https://example.com/jobs/google-swe",
            ),
        ]
        
        for job_profile in job_profiles:
            db.add(job_profile)
        
        db.commit()
        print(f"✓ Created {len(job_profiles)} job profiles")
        
        print("\n✅ Database seeded successfully!")
        print("\nSample Data:")
        print(f"  Candidates: {db.query(Candidate).count()}")
        print(f"  Job Profiles: {db.query(JobProfile).count()}")
        print("\nYou can now create pipeline runs using:")
        print("  POST /pipeline/start")
        print('  Body: {"candidate_id": 1, "job_profile_id": 1}')
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
