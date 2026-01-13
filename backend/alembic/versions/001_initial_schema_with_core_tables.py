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
    # Create enums first
    pipelinestatus_enum = sa.Enum('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='pipelinestatus')
    pipelinestatus_enum.create(op.get_bind(), checkfirst=True)
    
    stagedecision_enum = sa.Enum('PROCEED', 'HOLD', 'REJECT', 'BORDERLINE', 'PASS', 'FAIL', name='stagedecision')
    stagedecision_enum.create(op.get_bind(), checkfirst=True)
    
    # Create candidates table
    op.create_table(
        'candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
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
        sa.Column('must_haves', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('nice_to_haves', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('core_competencies', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('interview_style_bias', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_profiles_id'), 'job_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_job_profiles_role'), 'job_profiles', ['role'], unique=False)
    op.create_index(op.f('ix_job_profiles_company'), 'job_profiles', ['company'], unique=False)

    # Create pipeline_runs table
    op.create_table(
        'pipeline_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('job_profile_id', sa.Integer(), nullable=False),
        sa.Column('status', pipelinestatus_enum, nullable=False, server_default='CREATED'),
        sa.Column('current_stage', sa.String(length=100), nullable=True),
        sa.Column('stages', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('stage_progress', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_profile_id'], ['job_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pipeline_runs_id'), 'pipeline_runs', ['id'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_candidate_id'), 'pipeline_runs', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_job_profile_id'), 'pipeline_runs', ['job_profile_id'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_status'), 'pipeline_runs', ['status'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_current_stage'), 'pipeline_runs', ['current_stage'], unique=False)
    op.create_index('ix_pipeline_runs_candidate_status', 'pipeline_runs', ['candidate_id', 'status'], unique=False)
    op.create_index('ix_pipeline_runs_job_profile_status', 'pipeline_runs', ['job_profile_id', 'status'], unique=False)

    # Create stage_results table
    op.create_table(
        'stage_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pipeline_run_id', sa.Integer(), nullable=False),
        sa.Column('stage_name', sa.String(length=100), nullable=False),
        sa.Column('stage_type', sa.String(length=50), nullable=False),
        sa.Column('decision', stagedecision_enum, nullable=True),
        sa.Column('raw_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('strengths', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('concerns', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('artifacts', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_run_id'], ['pipeline_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stage_results_id'), 'stage_results', ['id'], unique=False)
    op.create_index(op.f('ix_stage_results_pipeline_run_id'), 'stage_results', ['pipeline_run_id'], unique=False)
    op.create_index(op.f('ix_stage_results_stage_name'), 'stage_results', ['stage_name'], unique=False)
    op.create_index(op.f('ix_stage_results_stage_type'), 'stage_results', ['stage_type'], unique=False)
    op.create_index(op.f('ix_stage_results_decision'), 'stage_results', ['decision'], unique=False)
    op.create_index('ix_stage_results_pipeline_stage', 'stage_results', ['pipeline_run_id', 'stage_name'], unique=False)
    op.create_index('ix_stage_results_pipeline_type', 'stage_results', ['pipeline_run_id', 'stage_type'], unique=False)
    op.create_index('ix_stage_results_pipeline_decision', 'stage_results', ['pipeline_run_id', 'decision'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_stage_results_pipeline_decision', table_name='stage_results')
    op.drop_index('ix_stage_results_pipeline_type', table_name='stage_results')
    op.drop_index('ix_stage_results_pipeline_stage', table_name='stage_results')
    op.drop_index(op.f('ix_stage_results_decision'), table_name='stage_results')
    op.drop_index(op.f('ix_stage_results_stage_type'), table_name='stage_results')
    op.drop_index(op.f('ix_stage_results_stage_name'), table_name='stage_results')
    op.drop_index(op.f('ix_stage_results_pipeline_run_id'), table_name='stage_results')
    op.drop_index(op.f('ix_stage_results_id'), table_name='stage_results')
    op.drop_table('stage_results')
    
    op.drop_index('ix_pipeline_runs_job_profile_status', table_name='pipeline_runs')
    op.drop_index('ix_pipeline_runs_candidate_status', table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_current_stage'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_status'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_job_profile_id'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_candidate_id'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_id'), table_name='pipeline_runs')
    op.drop_table('pipeline_runs')
    
    op.drop_index(op.f('ix_job_profiles_company'), table_name='job_profiles')
    op.drop_index(op.f('ix_job_profiles_role'), table_name='job_profiles')
    op.drop_index(op.f('ix_job_profiles_id'), table_name='job_profiles')
    op.drop_table('job_profiles')
    
    op.drop_index(op.f('ix_candidates_id'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_email'), table_name='candidates')
    op.drop_table('candidates')
    
    # Drop enums
    sa.Enum(name='stagedecision').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='pipelinestatus').drop(op.get_bind(), checkfirst=True)
