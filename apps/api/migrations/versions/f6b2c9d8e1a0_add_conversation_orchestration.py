"""add conversation orchestration

Revision ID: f6b2c9d8e1a0
Revises: 9f3a1b7c2d4e
Create Date: 2026-08-03 15:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f6b2c9d8e1a0"
down_revision: str | None = "9f3a1b7c2d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversation_sessions",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("channel", sa.String(length=40), nullable=False),
        sa.Column("external_thread_id", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_intent", sa.String(length=240), nullable=True),
        sa.Column("active_agent", sa.String(length=80), nullable=False),
        sa.Column("memory_scope", sa.String(length=40), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("open_questions", sa.JSON(), nullable=False),
        sa.Column("proposed_action_count", sa.Integer(), nullable=False),
        sa.Column("approval_count", sa.Integer(), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_conversation_sessions_brand_id_brands"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversation_sessions")),
        sa.UniqueConstraint(
            "brand_id",
            "channel",
            "external_thread_id",
            name=op.f("uq_conversation_sessions_brand_id"),
        ),
    )
    op.create_index(
        op.f("ix_conversation_sessions_active_agent"),
        "conversation_sessions",
        ["active_agent"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_brand_id"),
        "conversation_sessions",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_channel"),
        "conversation_sessions",
        ["channel"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_external_thread_id"),
        "conversation_sessions",
        ["external_thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_is_demo"),
        "conversation_sessions",
        ["is_demo"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_last_message_at"),
        "conversation_sessions",
        ["last_message_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_memory_scope"),
        "conversation_sessions",
        ["memory_scope"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_sessions_status"),
        "conversation_sessions",
        ["status"],
        unique=False,
    )

    op.create_table(
        "conversation_messages",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("session_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("channel", sa.String(length=40), nullable=False),
        sa.Column("sender_type", sa.String(length=40), nullable=False),
        sa.Column("sender_id", sa.String(length=160), nullable=False),
        sa.Column("message_type", sa.String(length=60), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("source_reference", sa.String(length=800), nullable=True),
        sa.Column("telegram_update_id", sa.String(length=120), nullable=True),
        sa.Column("telegram_message_id", sa.String(length=120), nullable=True),
        sa.Column("attachment_ids", sa.JSON(), nullable=False),
        sa.Column("agent_run_id", sa.Uuid(as_uuid=False), nullable=True),
        sa.Column("sensitivity", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_run_id"],
            ["agent_runs.id"],
            name=op.f("fk_conversation_messages_agent_run_id_agent_runs"),
        ),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_conversation_messages_brand_id_brands"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["conversation_sessions.id"],
            name=op.f("fk_conversation_messages_session_id_conversation_sessions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversation_messages")),
    )
    op.create_index(
        op.f("ix_conversation_messages_agent_run_id"),
        "conversation_messages",
        ["agent_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_brand_id"),
        "conversation_messages",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_channel"),
        "conversation_messages",
        ["channel"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_is_demo"),
        "conversation_messages",
        ["is_demo"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_message_type"),
        "conversation_messages",
        ["message_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_sender_id"),
        "conversation_messages",
        ["sender_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_sender_type"),
        "conversation_messages",
        ["sender_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_sensitivity"),
        "conversation_messages",
        ["sensitivity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_session_id"),
        "conversation_messages",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_status"),
        "conversation_messages",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_messages_telegram_update_id"),
        "conversation_messages",
        ["telegram_update_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_conversation_messages_telegram_update_id"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_status"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_session_id"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_sensitivity"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_sender_type"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_sender_id"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_message_type"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_is_demo"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_channel"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_brand_id"), table_name="conversation_messages")
    op.drop_index(op.f("ix_conversation_messages_agent_run_id"), table_name="conversation_messages")
    op.drop_table("conversation_messages")

    op.drop_index(op.f("ix_conversation_sessions_status"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_memory_scope"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_last_message_at"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_is_demo"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_external_thread_id"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_channel"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_brand_id"), table_name="conversation_sessions")
    op.drop_index(op.f("ix_conversation_sessions_active_agent"), table_name="conversation_sessions")
    op.drop_table("conversation_sessions")
