from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import structlog

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.intelligence import get_or_create_heartbeat_setting, run_heartbeat

logger = structlog.get_logger()
READY_FILE = Path("/run/brandos-heartbeat-worker-ready")


def run_due_heartbeat() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        heartbeat_setting = get_or_create_heartbeat_setting(db)
        if not heartbeat_setting.enabled:
            return
        try:
            timezone = ZoneInfo(heartbeat_setting.timezone)
        except ZoneInfoNotFoundError:
            logger.error(
                "heartbeat_timezone_invalid",
                timezone=heartbeat_setting.timezone,
            )
            return
        local_now = datetime.now(timezone)
        if local_now.hour != heartbeat_setting.schedule_hour:
            return
        run, _, duplicate = run_heartbeat(
            db,
            settings,
            run_date=local_now.date(),
            trigger="scheduled",
            idempotency_key=f"scheduled-heartbeat:{local_now.date().isoformat()}",
        )
        logger.info(
            "heartbeat_schedule_checked",
            run_id=run.id,
            duplicate=duplicate,
            status=run.status,
        )


def main() -> None:
    READY_FILE.touch()
    logger.info("heartbeat_worker_started")
    while True:
        try:
            run_due_heartbeat()
        except Exception:
            logger.exception("heartbeat_worker_iteration_failed")
        time.sleep(60)


if __name__ == "__main__":
    main()
