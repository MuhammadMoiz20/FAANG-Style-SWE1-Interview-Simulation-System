"""Normalize enum values to lowercase.

Revision ID: 002
Revises: 001
Create Date: 2026-01-14
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        _upgrade_postgresql(op, bind)
    else:
        # SQLite: enums are stored as TEXT, just normalize case
        _upgrade_sqlite(op)


def _upgrade_postgresql(op, bind):
    """PostgreSQL-specific enum migration."""
    pipelinestatus_new = sa.Enum(
        "created",
        "in_progress",
        "completed",
        "failed",
        "cancelled",
        name="pipelinestatus_new",
    )
    stagedecision_new = sa.Enum(
        "proceed",
        "hold",
        "reject",
        "borderline",
        "pass",
        "fail",
        name="stagedecision_new",
    )

    pipelinestatus_new.create(bind, checkfirst=False)
    stagedecision_new.create(bind, checkfirst=False)

    op.execute("ALTER TABLE pipeline_runs ALTER COLUMN status DROP DEFAULT")
    op.execute(
        "ALTER TABLE pipeline_runs "
        "ALTER COLUMN status TYPE pipelinestatus_new "
        "USING lower(status::text)::pipelinestatus_new"
    )
    op.execute("ALTER TABLE pipeline_runs ALTER COLUMN status SET DEFAULT 'created'")

    op.execute(
        "ALTER TABLE stage_results "
        "ALTER COLUMN decision TYPE stagedecision_new "
        "USING lower(decision::text)::stagedecision_new"
    )

    sa.Enum(name="pipelinestatus").drop(bind, checkfirst=False)
    sa.Enum(name="stagedecision").drop(bind, checkfirst=False)

    op.execute("ALTER TYPE pipelinestatus_new RENAME TO pipelinestatus")
    op.execute("ALTER TYPE stagedecision_new RENAME TO stagedecision")


def _upgrade_sqlite(op):
    """SQLite enum normalization - just lowercase existing values."""
    op.execute(
        "UPDATE pipeline_runs SET status = LOWER(status) WHERE status != LOWER(status)"
    )
    op.execute(
        "UPDATE stage_results SET decision = LOWER(decision) WHERE decision IS NOT NULL AND decision != LOWER(decision)"
    )


def downgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        _downgrade_postgresql(op, bind)
    else:
        # SQLite: convert back to uppercase
        _downgrade_sqlite(op)


def _downgrade_postgresql(op, bind):
    """PostgreSQL-specific enum downgrade."""
    op.execute("ALTER TABLE pipeline_runs ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE pipeline_runs ALTER COLUMN status TYPE TEXT")
    op.execute("ALTER TABLE stage_results ALTER COLUMN decision TYPE TEXT")

    pipelinestatus_old = sa.Enum(
        "CREATED",
        "IN_PROGRESS",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        name="pipelinestatus_old",
    )
    stagedecision_old = sa.Enum(
        "PROCEED",
        "HOLD",
        "REJECT",
        "BORDERLINE",
        "PASS",
        "FAIL",
        name="stagedecision_old",
    )
    pipelinestatus_old.create(bind, checkfirst=False)
    stagedecision_old.create(bind, checkfirst=False)

    op.execute(
        "ALTER TABLE pipeline_runs "
        "ALTER COLUMN status TYPE pipelinestatus_old "
        "USING upper(status)::pipelinestatus_old"
    )
    op.execute("ALTER TABLE pipeline_runs ALTER COLUMN status SET DEFAULT 'CREATED'")

    op.execute(
        "ALTER TABLE stage_results "
        "ALTER COLUMN decision TYPE stagedecision_old "
        "USING CASE "
        "WHEN decision IS NULL THEN NULL "
        "ELSE upper(decision)::stagedecision_old END"
    )

    sa.Enum(name="pipelinestatus").drop(bind, checkfirst=False)
    sa.Enum(name="stagedecision").drop(bind, checkfirst=False)

    op.execute("ALTER TYPE pipelinestatus_old RENAME TO pipelinestatus")
    op.execute("ALTER TYPE stagedecision_old RENAME TO stagedecision")


def _downgrade_sqlite(op):
    """SQLite enum downgrade - convert back to uppercase."""
    op.execute("UPDATE pipeline_runs SET status = UPPER(status)")
    op.execute(
        "UPDATE stage_results SET decision = UPPER(decision) WHERE decision IS NOT NULL"
    )
