# Claire Manifest-Driven Updater

This package upgrades the local updater so future update zips can automatically target Claire system folders.

## What changed

The updater now supports two formats:

```text
1. Path-preserving zips
2. Manifest-driven zips
```

The old style still works:

```text
src/claire/engines/example.py
src/claire/orchestrator/pipeline_v4.py
```

The new style uses a manifest:

```text
claire_update_manifest.json
files/
  example_engine.py
  pipeline_v4.py
```

The manifest tells the updater where each file belongs.

## Primary command

```powershell
python tools/claire_update.py .\next_update.zip --run-tests
```

Non-interactive:

```powershell
python tools/claire_update.py .\next_update.zip --run-tests --yes --commit-message "v5.xx apply update"
```

Dry run:

```powershell
python tools/claire_update.py .\next_update.zip --dry-run
```

Inspect manifest:

```powershell
python tools/update_manifest.py .\next_update.zip
python tools/update_manifest.py .\next_update.zip --json
```

## Manifest example

```json
{
  "update_name": "export_writer_package",
  "version": "v5.32",
  "files": [
    {
      "source": "files/export_writer.py",
      "target": "@export/export_writer.py",
      "type": "python",
      "action": "replace"
    },
    {
      "source": "files/pipeline_v4.py",
      "target": "@orchestrator/pipeline_v4.py",
      "type": "python",
      "action": "replace"
    }
  ],
  "post_install": {
    "run_compile_check": true,
    "run_regression_tests": true
  }
}
```

## Target aliases

```text
@engine/name.py        -> src/claire/engines/name.py
@engines/name.py       -> src/claire/engines/name.py
@orchestrator/name.py  -> src/claire/orchestrator/name.py
@domain/name.py        -> src/claire/domain/name.py
@portfolio/name.py     -> src/claire/portfolio/name.py
@export/name.py        -> src/claire/export/name.py
@backend/path          -> backend/path
@frontend/path         -> frontend/path
@tests/path            -> tests/path
@tools/path            -> tools/path
@data/path             -> data/path
@root/path             -> path
```

## Backup and restore

List backups:

```powershell
python tools/claire_update.py --list-backups
```

Restore:

```powershell
python tools/claire_update.py --restore .\data\backups\claire_backup_YYYYMMDD_HHMMSS.zip
```

## Logs

Updater logs are written to:

```text
data/update_logs/
```

Backups are written to:

```text
data/backups/
```

## Recommended commit

```powershell
git add .
git commit -m "v5.32 add manifest driven updater"
```
