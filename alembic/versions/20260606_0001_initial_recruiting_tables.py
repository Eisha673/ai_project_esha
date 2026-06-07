"""initial recruiting tables

Revision ID: 20260606_0001
Revises:
Create Date: 2026-06-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260606_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    is_postgres = op.get_context().dialect.name == "postgresql"
    uuid_type = postgresql.UUID(as_uuid=True) if is_postgres else sa.Uuid()
    json_type = postgresql.JSONB() if is_postgres else sa.JSON()
    uuid_default = sa.text("gen_random_uuid()") if is_postgres else None
    errors_default = sa.text("'[]'::jsonb") if is_postgres else sa.text("'[]'")
    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "jobs",
        sa.Column("id", uuid_type, primary_key=True, server_default=uuid_default),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("department", sa.String(100)),
        sa.Column("seniority", sa.String(50)),
        sa.Column("greenhouse_id", sa.String(100)),
        sa.Column("linkedin_job_url", sa.Text()),
        sa.Column("jd_text", sa.Text()),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "candidates",
        sa.Column("id", uuid_type, primary_key=True, server_default=uuid_default),
        sa.Column("job_id", uuid_type, sa.ForeignKey("jobs.id")),
        sa.Column("full_name", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("linkedin_url", sa.Text()),
        sa.Column("greenhouse_application_id", sa.String(100)),
        sa.Column("resume_text", sa.Text()),
        sa.Column("nim_screen_score", sa.Integer()),
        sa.Column("nim_screen_reasoning", sa.Text()),
        sa.Column("nim_screen_strengths", json_type),
        sa.Column("nim_screen_gaps", json_type),
        sa.Column("nim_bias_flagged", sa.Boolean(), server_default=sa.false()),
        sa.Column("assessment_score", sa.Integer()),
        sa.Column("assessment_pass", sa.Boolean()),
        sa.Column("stage", sa.String(50), server_default="applied"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "interviews",
        sa.Column("id", uuid_type, primary_key=True, server_default=uuid_default),
        sa.Column("candidate_id", uuid_type, sa.ForeignKey("candidates.id")),
        sa.Column("calendly_link", sa.Text()),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("question_bank", json_type),
        sa.Column("completed", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "offers",
        sa.Column("id", uuid_type, primary_key=True, server_default=uuid_default),
        sa.Column("candidate_id", uuid_type, sa.ForeignKey("candidates.id")),
        sa.Column("base_salary", sa.Numeric(12, 2)),
        sa.Column("equity_percentage", sa.Numeric(5, 2)),
        sa.Column("bonus_percentage", sa.Numeric(5, 2)),
        sa.Column("offer_letter_text", sa.Text()),
        sa.Column("greenhouse_offer_id", sa.String(100)),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "pipeline_states",
        sa.Column("job_id", uuid_type, sa.ForeignKey("jobs.id"), primary_key=True),
        sa.Column("current_stage", sa.String(50)),
        sa.Column("state_json", json_type),
        sa.Column("human_approved", sa.Boolean(), server_default=sa.false()),
        sa.Column("errors", json_type, server_default=errors_default),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", uuid_type, primary_key=True, server_default=uuid_default),
        sa.Column("job_id", uuid_type, sa.ForeignKey("jobs.id")),
        sa.Column("agent_name", sa.String(100)),
        sa.Column("llm_provider", sa.String(50)),
        sa.Column("nim_model", sa.String(100)),
        sa.Column("status", sa.String(50)),
        sa.Column("input_summary", sa.Text()),
        sa.Column("output_summary", sa.Text()),
        sa.Column("tokens_used", sa.Integer()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("pipeline_states")
    op.drop_table("offers")
    op.drop_table("interviews")
    op.drop_table("candidates")
    op.drop_table("jobs")
