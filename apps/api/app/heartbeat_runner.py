from __future__ import annotations

from datetime import UTC, datetime

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.intelligence import get_or_create_heartbeat_setting, run_heartbeat


def main() -> None:
    settings = get_settings()
    run_date = datetime.now(UTC).date()
    with SessionLocal() as db:
        heartbeat_setting = get_or_create_heartbeat_setting(db)
        if not heartbeat_setting.enabled:
            print("Heartbeat schedule is disabled; no run created.")
            return
        run, _, duplicate = run_heartbeat(
            db,
            settings,
            run_date=run_date,
            trigger="scheduled",
            idempotency_key=f"scheduled-heartbeat:{run_date.isoformat()}",
        )
        state = "existing" if duplicate else "created"
        print(f"Heartbeat {state}: {run.id} ({run.status}).")


if __name__ == "__main__":
    main()
