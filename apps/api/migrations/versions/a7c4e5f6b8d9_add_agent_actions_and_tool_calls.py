"""add agent actions and tool calls

Revision ID: a7c4e5f6b8d9
Revises: f6b2c9d8e1a0
Create Date: 2026-08-03 15:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a7c4e5f6b8d9"
down_revision: str | None = "f6b2c9d8e1a0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_tool_calls",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("session_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("agent_run_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("tool_type", sa.String(length=60), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("cost_estimate", sa.Float(), nullable=False),
        sa.Column("approval_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_run_id"],
            ["agent_runs.id"],
            name=op.f("fk_agent_tool_calls_agent_run_id_agent_runs"),
        ),
        sa.ForeignKeyConstraint(
            ["approval_id"],
            ["approvals.id"],
            name=op.f("fk_agent_tool_calls_approval_id_approvals"),
        ),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_agent_tool_calls_brand_id_brands"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["conversation_sessions.id"],
            name=op.f("fk_agent_tool_calls_session_id_conversation_sessions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_tool_calls")),
    )
    op.create_index(
        op.f("ix_agent_tool_calls_agent_run_id"),
        "agent_tool_calls",
        ["agent_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_approval_id"),
        "agent_tool_calls",
        ["approval_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_brand_id"),
        "agent_tool_calls",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_is_demo"),
        "agent_tool_calls",
        ["is_demo"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_session_id"),
        "agent_tool_calls",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_status"),
        "agent_tool_calls",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_tool_name"),
        "agent_tool_calls",
        ["tool_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_tool_calls_tool_type"),
        "agent_tool_calls",
        ["tool_type"],
        unique=False,
    )

    op.create_table(
        "proposed_dashboard_actions",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("session_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("agent_run_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("target_id", sa.String(length=120), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column(
            "risk_level",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="risklevel", native_enum=False),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("approval_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_run_id"],
            ["agent_runs.id"],
            name=op.f("fk_proposed_dashboard_actions_agent_run_id_agent_runs"),
        ),
        sa.ForeignKeyConstraint(
            ["approval_id"],
            ["approvals.id"],
            name=op.f("fk_proposed_dashboard_actions_approval_id_approvals"),
        ),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_proposed_dashboard_actions_brand_id_brands"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["conversation_sessions.id"],
            name=op.f("fk_proposed_dashboard_actions_session_id_conversation_sessions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_proposed_dashboard_actions")),
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_action_type"),
        "proposed_dashboard_actions",
        ["action_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_agent_run_id"),
        "proposed_dashboard_actions",
        ["agent_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_approval_id"),
        "proposed_dashboard_actions",
        ["approval_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_brand_id"),
        "proposed_dashboard_actions",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_is_demo"),
        "proposed_dashboard_actions",
        ["is_demo"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_risk_level"),
        "proposed_dashboard_actions",
        ["risk_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_session_id"),
        "proposed_dashboard_actions",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_status"),
        "proposed_dashboard_actions",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_target_id"),
        "proposed_dashboard_actions",
        ["target_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_proposed_dashboard_actions_target_type"),
        "proposed_dashboard_actions",
        ["target_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_target_type"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_target_id"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_status"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_session_id"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_risk_level"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_is_demo"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_brand_id"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_approval_id"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_agent_run_id"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_index(
        op.f("ix_proposed_dashboard_actions_action_type"),
        table_name="proposed_dashboard_actions",
    )
    op.drop_table("proposed_dashboard_actions")

    op.drop_index(op.f("ix_agent_tool_calls_tool_type"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_tool_name"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_status"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_session_id"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_is_demo"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_brand_id"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_approval_id"), table_name="agent_tool_calls")
    op.drop_index(op.f("ix_agent_tool_calls_agent_run_id"), table_name="agent_tool_calls")
    op.drop_table("agent_tool_calls")
