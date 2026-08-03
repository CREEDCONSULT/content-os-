from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from sqlalchemy import select


REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.db.models import Base  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def camel_case(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def to_convex_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): to_convex_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_convex_value(item) for item in value]
    return value


def row_to_document(row: Any) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for column in row.__table__.columns:
        value = to_convex_value(getattr(row, column.name))
        if column.name == "id":
            document["sqlId"] = str(value)
            continue
        if value is None:
            continue
        document[camel_case(column.name)] = value
    return document


def mapped_models() -> list[type[Any]]:
    models = [mapper.class_ for mapper in Base.registry.mappers]
    return sorted(models, key=lambda model: model.__tablename__)


def export_table(model: type[Any], output_dir: Path) -> dict[str, Any]:
    table_name = model.__tablename__
    output_path = output_dir / f"{table_name}.jsonl"
    count = 0
    order_column = getattr(model, "created_at", None)
    if order_column is None:
        order_column = getattr(model, "id")

    with SessionLocal() as session, output_path.open("w", encoding="utf-8", newline="\n") as file:
        rows = session.scalars(select(model).order_by(order_column)).all()
        for row in rows:
            file.write(json.dumps(row_to_document(row), ensure_ascii=False, sort_keys=True))
            file.write("\n")
            count += 1

    return {
        "table": table_name,
        "count": count,
        "path": str(output_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export SQL tables as Convex JSONLines imports.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory. Defaults to data/convex-export/<timestamp>.",
    )
    args = parser.parse_args()

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(args.output) if args.output else REPO_ROOT / "data" / "convex-export" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = [export_table(model, output_dir) for model in mapped_models()]
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "table_count": len(tables),
        "row_count": sum(table["count"] for table in tables),
        "tables": tables,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({"manifest": str(manifest_path), **manifest}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
