# Backup and Restore

The recovery unit contains:

- `database.dump`: PostgreSQL custom-format dump.
- `vault.tar.gz`: dedicated BrandOS Markdown vault.
- `storage.tar.gz`: uploaded object originals.
- `manifest.json`: format version, UTC creation time, migration, and SHA-256 hashes.

Backups are written to ignored `backups/` by default. Copy trusted backups to an
encrypted location outside the workstation; local-only copies do not protect
against disk loss.

## Create

With `postgres` and `api` healthy:

```powershell
.\scripts\backup.ps1
```

An optional `-OutputDirectory` can target a different existing/local directory.
The script never includes `.env` or provider credentials.

## Test recovery safely

```powershell
.\scripts\test-backup-restore.ps1
```

This creates a fresh backup, verifies every checksum, restores the database dump
into a uniquely named temporary PostgreSQL database, verifies the brand record,
and drops that temporary database. It does not mutate live tables or volumes.

## Restore live state

1. Confirm the selected archive and preserve any external copy.
2. Run:

```powershell
.\scripts\restore.ps1 -BackupPath .\backups\mezie-brandos-YYYYMMDD-HHMMSS.zip -ConfirmRestore
```

The restore script:

1. validates the manifest and all hashes;
2. creates a new pre-restore safety backup;
3. stops API, heartbeat, and web services;
4. restores PostgreSQL with `--clean --if-exists`;
5. restores only the configured vault and storage roots through a traversal-safe helper;
6. restarts services and waits for `/ready`;
7. restarts stopped services even if restoration fails.

Do not rename files inside the ZIP or extract and modify a backup before restore.

## Recovery objective

The local target is a same-workstation recovery point equal to the last completed
backup. No automatic off-device retention or point-in-time PostgreSQL archive is
claimed. Establish those controls before remote deployment.
