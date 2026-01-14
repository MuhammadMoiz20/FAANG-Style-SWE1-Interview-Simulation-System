"""Add constraints and updated_at triggers.

Revision ID: 003
Revises: 002
Create Date: 2026-01-14
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


POSTGRESQL_UPDATED_AT_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Deduplicate stage_results before enforcing uniqueness.
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DELETE FROM stage_results a
            USING stage_results b
            WHERE a.pipeline_run_id = b.pipeline_run_id
              AND a.stage_name = b.stage_name
              AND a.id < b.id;
            """
        )
    else:
        # SQLite-compatible deduplication
        op.execute(
            """
            DELETE FROM stage_results
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM stage_results
                GROUP BY pipeline_run_id, stage_name
            );
            """
        )

    existing_stage_indexes = {
        index["name"] for index in inspector.get_indexes("stage_results")
    }
    existing_stage_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("stage_results")
        if constraint.get("name")
    }
    if "ix_stage_results_pipeline_stage" in existing_stage_indexes:
        op.drop_index("ix_stage_results_pipeline_stage", table_name="stage_results")
    if "uq_stage_results_pipeline_stage" not in existing_stage_constraints:
        op.create_unique_constraint(
            "uq_stage_results_pipeline_stage",
            "stage_results",
            ["pipeline_run_id", "stage_name"],
        )

    # Ensure only one active pipeline run per candidate/job profile.
    op.execute(
        """
        WITH ranked AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY candidate_id, job_profile_id
                       ORDER BY id DESC
                   ) AS rn
            FROM pipeline_runs
            WHERE status IN ('created', 'in_progress')
        )
        UPDATE pipeline_runs
        SET status = 'cancelled'
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
        """
    )

    existing_pipeline_indexes = {
        index["name"] for index in inspector.get_indexes("pipeline_runs")
    }
    if "uq_pipeline_runs_candidate_job_active" not in existing_pipeline_indexes:
        op.create_index(
            "uq_pipeline_runs_candidate_job_active",
            "pipeline_runs",
            ["candidate_id", "job_profile_id"],
            unique=True,
            postgresql_where=sa.text("status IN ('created', 'in_progress')"),
            sqlite_where=sa.text("status IN ('created', 'in_progress')"),
        )

    # Create updated_at triggers (PostgreSQL only)
    # SQLite relies on SQLAlchemy's onupdate=func.now() in the ORM models
    if bind.dialect.name == "postgresql":
        _create_postgresql_updated_at_triggers(op)


def _create_postgresql_updated_at_triggers(op):
    """Create PostgreSQL triggers for auto-updating updated_at."""
    op.execute(POSTGRESQL_UPDATED_AT_TRIGGER_SQL)
    for table in ("candidates", "job_profiles", "pipeline_runs", "stage_results"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_set_updated_at_{table} ON {table}")
        op.execute(
            "CREATE TRIGGER "
            f"trg_set_updated_at_{table} "
            f"BEFORE UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION set_updated_at_timestamp()"
        )


def downgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        _drop_postgresql_updated_at_triggers(op)


def _drop_postgresql_updated_at_triggers(op):
    """Drop PostgreSQL triggers."""
    for table in ("candidates", "job_profiles", "pipeline_runs", "stage_results"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_set_updated_at_{table} ON {table}")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at_timestamp()")
