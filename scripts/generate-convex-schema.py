from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from sqlalchemy import Boolean, Float, Integer, JSON  # noqa: E402

from app.db.models import Base  # noqa: E402


INDEXED_COLUMNS = {
    "status",
    "canonical_status",
    "source_reference",
    "is_active",
    "is_demo",
    "update_id",
    "sender_id",
    "message_type",
    "sync_status",
    "embedding_status",
    "platform",
    "event_type",
    "week_start",
    "captured_at",
    "slug",
    "checksum_sha256",
    "storage_key",
    "request_id",
    "idempotency_key",
}


def camel_case(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def convex_validator(column: object) -> str:
    column_type = column.type
    if isinstance(column_type, Boolean):
        base = "v.boolean()"
    elif isinstance(column_type, (Integer, Float)):
        base = "v.number()"
    elif isinstance(column_type, JSON):
        base = "v.any()"
    else:
        base = "v.string()"
    return f"v.optional({base})"


def table_indexes(table: object) -> list[tuple[str, list[str]]]:
    indexes: list[tuple[str, list[str]]] = [("by_sql_id", ["sqlId"])]
    field_names = {camel_case(column.name): column.name for column in table.columns if column.name != "id"}

    for column in table.columns:
        if column.name == "id":
            continue
        field = camel_case(column.name)
        if column.name.endswith("_id") or column.name in INDEXED_COLUMNS:
            indexes.append((f"by_{column.name}", [field]))

    if "brandId" in field_names:
        for field, column_name in [
            ("status", "status"),
            ("canonicalStatus", "canonical_status"),
            ("isDemo", "is_demo"),
            ("platform", "platform"),
            ("pillar", "pillar"),
        ]:
            if field in field_names:
                indexes.append((f"by_brand_id_and_{column_name}", ["brandId", field]))

    deduped: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for name, fields in indexes:
        if name in seen:
            continue
        deduped.append((name, fields))
        seen.add(name)
    return deduped


def render_schema() -> str:
    lines = [
        'import { defineSchema, defineTable } from "convex/server";',
        'import { v } from "convex/values";',
        "",
        "// SQL migration mirror schema.",
        "// `sqlId` preserves the original SQL primary key so we can backfill safely",
        "// before any later Convex-native ID remap.",
        "",
        "export default defineSchema({",
    ]

    for table in sorted(Base.metadata.tables.values(), key=lambda item: item.name):
        lines.append(f"  {table.name}: defineTable({{")
        lines.append("    sqlId: v.string(),")
        for column in table.columns:
            if column.name == "id":
                continue
            lines.append(f"    {camel_case(column.name)}: {convex_validator(column)},")
        lines.append("  })")

        indexes = table_indexes(table)
        for index_name, fields in indexes:
            quoted_fields = ", ".join(f'"{field}"' for field in fields)
            lines.append(f'    .index("{index_name}", [{quoted_fields}])')
        lines[-1] = f"{lines[-1]},"

    lines.append("});")
    return "\n".join(lines) + "\n"


def main() -> None:
    target = REPO_ROOT / "convex" / "schema.ts"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_schema(), encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
