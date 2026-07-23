from __future__ import annotations

import argparse
import shutil
import tarfile
from pathlib import Path

from app.core.config import get_settings


def _assert_allowed_target(target: Path) -> Path:
    settings = get_settings()
    resolved = target.resolve()
    allowed = {
        Path(settings.brandos_vault_path).resolve(),
        Path(settings.object_storage_path).resolve(),
    }
    if resolved not in allowed:
        raise ValueError("Restore target is not a configured BrandOS data root.")
    return resolved


def _validate_archive(archive: tarfile.TarFile) -> None:
    for member in archive.getmembers():
        path = Path(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Archive contains an unsafe path.")
        if member.issym() or member.islnk():
            raise ValueError("Archive links are not accepted.")


def restore_archive(target: Path, archive_path: Path) -> None:
    resolved_target = _assert_allowed_target(target)
    resolved_archive = archive_path.resolve(strict=True)
    resolved_target.mkdir(parents=True, exist_ok=True)

    with tarfile.open(resolved_archive, mode="r:gz") as archive:
        _validate_archive(archive)
        for child in resolved_target.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        archive.extractall(resolved_target, filter="data")


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore a validated BrandOS file archive.")
    parser.add_argument("target", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    restore_archive(args.target, args.archive)


if __name__ == "__main__":
    main()
