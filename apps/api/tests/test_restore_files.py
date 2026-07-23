from __future__ import annotations

import io
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from app import restore_files


def _settings(vault: Path, storage: Path) -> SimpleNamespace:
    return SimpleNamespace(
        brandos_vault_path=str(vault),
        object_storage_path=str(storage),
    )


def test_restore_replaces_only_an_allowed_data_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault = tmp_path / "vault"
    storage = tmp_path / "storage"
    source = tmp_path / "source"
    vault.mkdir()
    storage.mkdir()
    source.mkdir()
    (vault / "old.md").write_text("old", encoding="utf-8")
    (source / "new.md").write_text("new", encoding="utf-8")
    archive_path = tmp_path / "vault.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(source / "new.md", arcname="notes/new.md")

    monkeypatch.setattr(restore_files, "get_settings", lambda: _settings(vault, storage))
    restore_files.restore_archive(vault, archive_path)

    assert not (vault / "old.md").exists()
    assert (vault / "notes" / "new.md").read_text(encoding="utf-8") == "new"


def test_restore_rejects_traversal_before_deleting_existing_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault = tmp_path / "vault"
    storage = tmp_path / "storage"
    vault.mkdir()
    storage.mkdir()
    sentinel = vault / "keep.md"
    sentinel.write_text("keep", encoding="utf-8")
    archive_path = tmp_path / "unsafe.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        member = tarfile.TarInfo("../escape.md")
        payload = b"escape"
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    monkeypatch.setattr(restore_files, "get_settings", lambda: _settings(vault, storage))
    with pytest.raises(ValueError, match="unsafe path"):
        restore_files.restore_archive(vault, archive_path)

    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert not (tmp_path / "escape.md").exists()


def test_restore_rejects_unconfigured_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault = tmp_path / "vault"
    storage = tmp_path / "storage"
    other = tmp_path / "other"
    vault.mkdir()
    storage.mkdir()
    other.mkdir()
    archive_path = tmp_path / "empty.tar.gz"
    with tarfile.open(archive_path, "w:gz"):
        pass

    monkeypatch.setattr(restore_files, "get_settings", lambda: _settings(vault, storage))
    with pytest.raises(ValueError, match="configured BrandOS data root"):
        restore_files.restore_archive(other, archive_path)
