"""add agent runtime and skill registry

Revision ID: dd607cc884a2
Revises: c06caa04f0c9
Create Date: 2026-07-23 16:10:25.264284
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "dd607cc884a2"
down_revision: str | None = "c06caa04f0c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "skill_definitions",
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("trigger_summary", sa.Text(), nullable=False),
        sa.Column("input_schema", sa.JSON(), nullable=False),
        sa.Column("required_context", sa.JSON(), nullable=False),
        sa.Column("allowed_tools", sa.JSON(), nullable=False),
        sa.Column("workflow", sa.JSON(), nullable=False),
        sa.Column("output_schema", sa.JSON(), nullable=False),
        sa.Column("memory_policy", sa.Text(), nullable=False),
        sa.Column("approval_policy", sa.Text(), nullable=False),
        sa.Column("failure_behavior", sa.Text(), nullable=False),
        sa.Column("model_profile", sa.String(length=80), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("cost_class", sa.String(length=30), nullable=False),
        sa.Column("source_path", sa.String(length=800), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skill_definitions")),
    )
    op.create_index(
        op.f("ix_skill_definitions_enabled"),
        "skill_definitions",
        ["enabled"],
        unique=False,
    )
    op.create_index(
        op.f("ix_skill_definitions_slug"),
        "skill_definitions",
        ["slug"],
        unique=True,
    )
    op.create_table(
        "context_packs",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("intent", sa.String(length=500), nullable=False),
        sa.Column("source_records", sa.JSON(), nullable=False),
        sa.Column("context_markdown", sa.Text(), nullable=False),
        sa.Column("token_estimate", sa.Integer(), nullable=False),
        sa.Column("freshness_notes", sa.JSON(), nullable=False),
        sa.Column("exclusions", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_context_packs_brand_id_brands"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_context_packs")),
    )
    op.create_index(
        op.f("ix_context_packs_brand_id"),
        "context_packs",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_context_packs_status"),
        "context_packs",
        ["status"],
        unique=False,
    )
    with op.batch_alter_table("agent_runs") as batch_op:
        batch_op.add_column(
            sa.Column(
                "request_id",
                sa.String(length=80),
                nullable=False,
                server_default="migration:legacy",
            )
        )
        batch_op.add_column(sa.Column("idempotency_key", sa.String(length=160), nullable=True))
        batch_op.add_column(
            sa.Column(
                "provider",
                sa.String(length=40),
                nullable=False,
                server_default="mock",
            )
        )
        batch_op.add_column(
            sa.Column("context_pack_id", sa.Uuid(as_uuid=False), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "input_envelope",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'{}'"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "output_envelope",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'{}'"),
            )
        )
        for column_name in (
            "proposed_writes",
            "completed_writes",
            "approvals_required",
            "next_actions",
        ):
            batch_op.add_column(
                sa.Column(
                    column_name,
                    sa.JSON(),
                    nullable=False,
                    server_default=sa.text("'[]'"),
                )
            )
        batch_op.add_column(
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_index(
            op.f("ix_agent_runs_context_pack_id"),
            ["context_pack_id"],
            unique=False,
        )
        batch_op.create_index(
            op.f("ix_agent_runs_idempotency_key"),
            ["idempotency_key"],
            unique=True,
        )
        batch_op.create_index(
            op.f("ix_agent_runs_request_id"),
            ["request_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            op.f("fk_agent_runs_context_pack_id_context_packs"),
            "context_packs",
            ["context_pack_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("agent_runs") as batch_op:
        batch_op.drop_constraint(
            op.f("fk_agent_runs_context_pack_id_context_packs"),
            type_="foreignkey",
        )
        batch_op.drop_index(op.f("ix_agent_runs_request_id"))
        batch_op.drop_index(op.f("ix_agent_runs_idempotency_key"))
        batch_op.drop_index(op.f("ix_agent_runs_context_pack_id"))
        batch_op.drop_column("completed_at")
        batch_op.drop_column("next_actions")
        batch_op.drop_column("approvals_required")
        batch_op.drop_column("completed_writes")
        batch_op.drop_column("proposed_writes")
        batch_op.drop_column("output_envelope")
        batch_op.drop_column("input_envelope")
        batch_op.drop_column("context_pack_id")
        batch_op.drop_column("provider")
        batch_op.drop_column("idempotency_key")
        batch_op.drop_column("request_id")
    op.drop_index(op.f("ix_context_packs_status"), table_name="context_packs")
    op.drop_index(op.f("ix_context_packs_brand_id"), table_name="context_packs")
    op.drop_table("context_packs")
    op.drop_index(op.f("ix_skill_definitions_slug"), table_name="skill_definitions")
    op.drop_index(op.f("ix_skill_definitions_enabled"), table_name="skill_definitions")
    op.drop_table("skill_definitions")
