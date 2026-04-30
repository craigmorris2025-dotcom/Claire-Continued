# Claire Local Updater Package

This package adds a local update installer so future Claire update zips can be applied faster and more safely.

## Files included

```text
tools/claire_update.py
tools/update_manifest.py
data/backups/.gitkeep
data/update_logs/.gitkeep
tools/README_UPDATER.md
```

## Install location

Extract this zip into the project root, the same folder that contains:

```text
main.py
src/
backend/
frontend/
data/
```

## Basic usage

From the Claire project root:

```powershell
python tools/claire_update.py .\claire_export_package_engine_update.zip --run-tests
```

This will:

```text
1. detect the project root
2. inspect the update zip
3. show files to be created/replaced
4. create a timestamped backup
5. install the files
6. run Python compile checks
7. optionally run regression tests
8. write an update log
```

## Faster non-interactive usage

```powershell
python tools/claire_update.py .\some_update.zip --run-tests --yes --commit-message "v5.xx apply update"
```

## Dry run

```powershell
python tools/claire_update.py .\some_update.zip --dry-run
```

## Inspect a zip manifest

```powershell
python tools/update_manifest.py .\some_update.zip
```

Full JSON manifest:

```powershell
python tools/update_manifest.py .\some_update.zip --json
```

## Restore from backup

List backups:

```powershell
python tools/claire_update.py --list-backups
```

Restore one:

```powershell
python tools/claire_update.py --restore .\data\backups\claire_backup_YYYYMMDD_HHMMSS.zip
```

## Recommended commit

After this package is installed:

```powershell
git add .
git commit -m "v5.31 add local updater package"
```
