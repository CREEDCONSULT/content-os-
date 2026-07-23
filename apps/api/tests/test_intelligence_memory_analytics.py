from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Settings, get_settings
from app.main import app


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    return Settings(
        app_env="test",
        database_url="sqlite+pysqlite://",
        brandos_vault_path=str(tmp_path / "vault"),
        object_storage_path=str(tmp_path / "storage"),
        **overrides,
    )


def test_vault_sync_exports_imports_and_preserves_canonical_conflict(
    authenticated_client: TestClient,
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        initial = authenticated_client.post("/api/v1/memory/vault/sync")
        assert initial.status_code == 200
        assert initial.json()["exported"] >= 52
        root = Path(initial.json()["root"])
        assert (root / "01_Brand_Core").is_dir()
        assert (root / "13_Templates").is_dir()

        inbox_note = root / "03_Ideas/Inbox/Vault capture test.md"
        inbox_note.write_text(
            "# Vault capture test\n\nA founder-created note imported from the dedicated vault.",
            encoding="utf-8",
        )
        imported = authenticated_client.post("/api/v1/memory/vault/sync")
        assert imported.status_code == 200
        assert imported.json()["imported"] >= 1
        ideas = authenticated_client.get(
            "/api/v1/ideas",
            params={"search": "Vault capture test"},
        ).json()
        assert ideas["total"] == 1
        assert ideas["items"][0]["source_type"] == "vault"

        records = authenticated_client.get("/api/v1/memory/records").json()
        canonical = next(item for item in records if item["canonical_status"] == "canonical")
        canonical_path = root / canonical["vault_path"]
        changed = canonical_path.read_text(encoding="utf-8") + "\nManual conflicting edit.\n"
        canonical_path.write_text(changed, encoding="utf-8")
        conflicted = authenticated_client.post("/api/v1/memory/vault/sync")
        assert conflicted.status_code == 200
        assert conflicted.json()["conflicts"] >= 1
        assert canonical_path.read_text(encoding="utf-8") == changed
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_benchmark_url_creates_original_mezie_teardown(
    authenticated_client: TestClient,
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        creator = authenticated_client.post(
            "/api/v1/intelligence/creators",
            json={
                "name": "Reference Builder",
                "username": "reference-builder",
                "platform": "YouTube",
                "url": "https://youtube.com/@reference-builder",
                "why_tracked": "Clear systems explanations for builder audiences.",
                "tier": 2,
                "relevance_score": 8.2,
            },
        )
        assert creator.status_code == 201
        benchmark = authenticated_client.post(
            "/api/v1/intelligence/benchmarks",
            json={
                "creator_id": creator.json()["id"],
                "source_url": "https://youtube.com/watch?v=local-fixture",
                "title": "How builders make systems visible",
                "transcript_excerpt": (
                    "This exact creator sentence contains enough words to trigger the "
                    "copying safeguard if repeated verbatim in an adaptation."
                ),
                "observed_hook": "Start with the cost of the invisible system.",
                "observed_structure": "Problem, mechanism, evidence, next action.",
                "transferable_mechanics": [
                    "Reveal the operational cost before explaining the mechanism"
                ],
                "pattern_tags": ["systems", "evidence"],
            },
        )
        assert benchmark.status_code == 201
        teardown = benchmark.json()
        assert teardown["evidence_level"] == "operator_excerpt"
        assert teardown["protected_identity"]
        assert teardown["mezie_adaptations"]
        assert "exact creator sentence" not in teardown["mezie_adaptations"][0].lower()
        assert any("Apify is disabled" in item for item in teardown["limitations"])
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_telegram_webhook_verifies_secret_sender_and_idempotency(
    authenticated_client: TestClient,
    tmp_path: Path,
) -> None:
    settings = _settings(
        tmp_path,
        telegram_enabled=True,
        telegram_webhook_secret=SecretStr("telegram-test-secret"),
        telegram_allowed_user_ids=[42],
    )
    app.dependency_overrides[get_settings] = lambda: settings
    update = {
        "update_id": 9001,
        "message": {
            "message_id": 17,
            "from": {"id": 42},
            "text": "/idea Voice-first capture should preserve the source reference",
        },
    }
    try:
        missing_secret = authenticated_client.post("/api/v1/telegram/webhook", json=update)
        assert missing_secret.status_code == 401

        blocked_sender = authenticated_client.post(
            "/api/v1/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "telegram-test-secret"},
            json={
                **update,
                "update_id": 9002,
                "message": {**update["message"], "from": {"id": 99}},
            },
        )
        assert blocked_sender.status_code == 403

        captured = authenticated_client.post(
            "/api/v1/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "telegram-test-secret"},
            json=update,
        )
        assert captured.status_code == 200
        assert captured.json()["created_record_type"] == "idea"

        duplicate = authenticated_client.post(
            "/api/v1/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "telegram-test-secret"},
            json=update,
        )
        assert duplicate.status_code == 200
        assert duplicate.json()["id"] == captured.json()["id"]
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_voice_fixture_to_idea_and_duplicate_heartbeat_prevention(
    authenticated_client: TestClient,
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        voice = authenticated_client.post(
            "/api/v1/telegram/capture-test",
            json={
                "sender_id": 42,
                "message_type": "voice",
                "transcript": ("A voice note idea about making the next builder action visible."),
            },
        )
        assert voice.status_code == 200
        assert voice.json()["is_demo"] is True
        assert voice.json()["created_record_type"] == "idea"

        first = authenticated_client.post(
            "/api/v1/heartbeat/run",
            json={"run_date": "2026-09-15", "idempotency_key": "heartbeat-test-2026-09-15"},
        )
        assert first.status_code == 200
        assert first.json()["brief"]["content_opportunities"]
        assert first.json()["model_cost"] == 0
        second = authenticated_client.post(
            "/api/v1/heartbeat/run",
            json={"run_date": "2026-09-15", "idempotency_key": "different-key-same-date"},
        )
        assert second.status_code == 200
        assert second.json()["id"] == first.json()["id"]
        assert (
            tmp_path / "vault" / "05_Research" / "Daily Intelligence" / "2026-09-15.md"
        ).is_file()
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_analytics_csv_import_and_controlled_experiment(
    authenticated_client: TestClient,
) -> None:
    csv_body = "\n".join(
        [
            "platform,views,impressions,engagement,saves,shares,watch_time_seconds",
            "LinkedIn,1000,1400,90,30,12,0",
            "Instagram,2200,3000,180,75,31,9200",
            "YouTube,invalid,100,2,1,0,30",
        ]
    )
    imported = authenticated_client.post(
        "/api/v1/analytics/import",
        files={"file": ("metrics.csv", csv_body.encode(), "text/csv")},
    )
    assert imported.status_code == 200
    assert imported.json()["imported"] == 2
    assert imported.json()["rejected"] == 1
    assert imported.json()["insight_ids"]

    overview = authenticated_client.get("/api/v1/analytics/overview")
    assert overview.status_code == 200
    assert overview.json()["totals"]["views"] >= 3200
    assert any(
        "does not establish causation" in item["hypothesis"] for item in overview.json()["insights"]
    )

    experiment = authenticated_client.post(
        "/api/v1/analytics/experiments",
        json={
            "title": "Identity hook versus educational hook",
            "question": "Do identity hooks improve saves on Builder Walks?",
            "hypothesis": "Identity hooks may increase qualified saves.",
            "variable": "hook type",
            "control_conditions": [
                "Same topic",
                "Same duration",
                "Same production quality",
            ],
            "platform": "Instagram",
            "content_type": "Builder Walk",
            "expected_outcome": "Higher save rate for the identity-hook variant.",
            "success_metric": "Save rate",
            "measurement_start": "2026-09-20",
            "measurement_end": "2026-10-04",
        },
    )
    assert experiment.status_code == 201
    assert experiment.json()["status"] == "planned"
    assert experiment.json()["variable"] == "hook type"
