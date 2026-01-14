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

    bind = op.get_bind()
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


def downgrade() -> None:
    bind = op.get_bind()

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
