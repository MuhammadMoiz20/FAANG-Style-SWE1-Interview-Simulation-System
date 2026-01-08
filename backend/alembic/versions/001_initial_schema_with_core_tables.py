"""Initial schema with core tables

Revision ID: 001
Revises: 
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create candidates table
    op.create_table(
        'candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'], unique=True)
    op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)

    # Create job_profiles table
    op.create_table(
        'job_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('company_style', sa.String(length=100), nullable=True),
        sa.Column('raw_description', sa.Text(), nullable=False),
        sa.Column('must_haves', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('nice_to_haves', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('core_competencies', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('interview_style_bias', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_profiles_id'), 'job_profiles', ['id'], unique=False)

    # Create pipeline_runs table
    op.create_table(
        'pipeline_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('job_profile_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='pipelinestatus'), nullable=False),
        sa.Column('current_stage', sa.String(length=100), nullable=True),
        sa.Column('stages', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('stage_progress', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
        sa.ForeignKeyConstraint(['job_profile_id'], ['job_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_runs_id'), 'pipeline_runs', ['id'], unique=False)

    # Create stage_results table
    op.create_table(
        'stage_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pipeline_run_id', sa.Integer(), nullable=False),
        sa.Column('stage_name', sa.String(length=100), nullable=False),
        sa.Column('stage_type', sa.String(length=50), nullable=False),
        sa.Column('decision', sa.Enum('PROCEED', 'HOLD', 'REJECT', 'BORDERLINE', 'PASS', 'FAIL', name='stagedecision'), nullable=True),
        sa.Column('raw_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('strengths', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('concerns', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('artifacts', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pipeline_run_id'], ['pipeline_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stage_results_id'), 'stage_results', ['id'], unique=False)
    op.create_index(op.f('ix_stage_results_stage_name'), 'stage_results', ['stage_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_stage_results_stage_name'), table_name='stage_results')
    op.drop_index(op.f('ix_stage_results_id'), table_name='stage_results')
    op.drop_table('stage_results')
    op.drop_index(op.f('ix_pipeline_runs_id'), table_name='pipeline_runs')
    op.drop_table('pipeline_runs')
    op.drop_index(op.f('ix_job_profiles_id'), table_name='job_profiles')
    op.drop_table('job_profiles')
    op.drop_index(op.f('ix_candidates_id'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_email'), table_name='candidates')
    op.drop_table('candidates')
    
    # Drop enums
    sa.Enum(name='pipelinestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='stagedecision').drop(op.get_bind(), checkfirst=True)
