# Claire Safe Version Installer Wrapper

## What this fixes

This wrapper lets you use your existing 28 self-extracting version installers safely.

It prevents the current problems:

- accidental install into the wrong folder
- silent creation of duplicate folder trees
- unsafe overwrites
- unclear dry-run output
- direct extraction into active project root
- version files updating too early
- no rollback on validation failure

## Required use

Do **not** run the version installers directly.

Instead run:

```powershell
python safe_install_claire_version.py `
  --installer "C:\path\to\claire_v5_91_0_installer.py" `
  --project-root "C:\path\to\Claire"
```

That is a dry-run by default.

To actually install:

```powershell
python safe_install_claire_version.py `
  --installer "C:\path\to\claire_v5_91_0_installer.py" `
  --project-root "C:\path\to\Claire" `
  --approve-install
```

To allow replacements:

```powershell
python safe_install_claire_version.py `
  --installer "C:\path\to\claire_v5_91_0_installer.py" `
  --project-root "C:\path\to\Claire" `
  --approve-install `
  --approve-replace
```

## Recommended order

Start with v5.91.0 only.

Do not install v6, v7, v8, v9, or v10 until earlier phases validate.

## Project-root markers required

The wrapper refuses to install unless these exist:

- main.py
- pyproject.toml
- requirements.txt
- pytest.ini
- version.json
- src/claire
- src/frontend
- tests

## What the dry-run shows

For every file it shows:

- source
- destination
- whether destination exists
- action:
  - CREATE
  - BLOCK_OVERWRITE
  - REPLACE_APPROVED
  - FORBIDDEN_PATH

## Validation

After install, it runs:

- Python compile validation for installed Python files
- pytest for newly installed test files unless `--skip-tests` is used

If validation fails, it rolls back created/replaced files.
