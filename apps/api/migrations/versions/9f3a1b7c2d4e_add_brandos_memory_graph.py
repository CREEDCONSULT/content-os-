"""add brandos memory graph

Revision ID: 9f3a1b7c2d4e
Revises: 4ca6a901f2f5
Create Date: 2026-08-03 13:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9f3a1b7c2d4e"
down_revision: str | None = "4ca6a901f2f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_entities",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("slug", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column(
            "canonical_status",
            sa.Enum(
                "CANONICAL",
                "WORKING",
                "ARCHIVED",
                "RESTRICTED",
                name="canonicalstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("sensitivity", sa.String(length=60), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_knowledge_entities_brand_id_brands"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_entities")),
        sa.UniqueConstraint(
            "brand_id",
            "entity_type",
            "slug",
            name=op.f("uq_knowledge_entities_brand_id"),
        ),
    )
    op.create_index(
        op.f("ix_knowledge_entities_brand_id"),
        "knowledge_entities",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_entities_canonical_status"),
        "knowledge_entities",
        ["canonical_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_entities_entity_type"),
        "knowledge_entities",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_entities_is_demo"),
        "knowledge_entities",
        ["is_demo"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_entities_sensitivity"),
        "knowledge_entities",
        ["sensitivity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_entities_slug"),
        "knowledge_entities",
        ["slug"],
        unique=False,
    )

    op.create_table(
        "knowledge_edges",
        sa.Column("brand_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.String(length=120), nullable=False),
        sa.Column("relationship_type", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=240), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "canonical_status",
            sa.Enum(
                "CANONICAL",
                "WORKING",
                "ARCHIVED",
                "RESTRICTED",
                name="canonicalstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("sensitivity", sa.String(length=60), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("approved_by", sa.String(length=120), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
            name=op.f("fk_knowledge_edges_brand_id_brands"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_edges")),
        sa.UniqueConstraint(
            "brand_id",
            "source_type",
            "source_id",
            "relationship_type",
            "target_type",
            "target_id",
            name=op.f("uq_knowledge_edges_brand_id"),
        ),
    )
    op.create_index(
        op.f("ix_knowledge_edges_brand_id"),
        "knowledge_edges",
        ["brand_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_canonical_status"),
        "knowledge_edges",
        ["canonical_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_is_demo"),
        "knowledge_edges",
        ["is_demo"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_relationship_type"),
        "knowledge_edges",
        ["relationship_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_sensitivity"),
        "knowledge_edges",
        ["sensitivity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_source_id"),
        "knowledge_edges",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_source_type"),
        "knowledge_edges",
        ["source_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_target_id"),
        "knowledge_edges",
        ["target_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_edges_target_type"),
        "knowledge_edges",
        ["target_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_edges_target_type"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_target_id"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_source_type"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_source_id"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_sensitivity"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_relationship_type"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_is_demo"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_canonical_status"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_brand_id"), table_name="knowledge_edges")
    op.drop_table("knowledge_edges")

    op.drop_index(op.f("ix_knowledge_entities_slug"), table_name="knowledge_entities")
    op.drop_index(op.f("ix_knowledge_entities_sensitivity"), table_name="knowledge_entities")
    op.drop_index(op.f("ix_knowledge_entities_is_demo"), table_name="knowledge_entities")
    op.drop_index(op.f("ix_knowledge_entities_entity_type"), table_name="knowledge_entities")
    op.drop_index(op.f("ix_knowledge_entities_canonical_status"), table_name="knowledge_entities")
    op.drop_index(op.f("ix_knowledge_entities_brand_id"), table_name="knowledge_entities")
    op.drop_table("knowledge_entities")
