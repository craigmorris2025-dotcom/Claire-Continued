# v16.21-v16.25 Clean Install Recovery

Run:

```powershell
python claire_v16_21_to_v16_25_clean_install_recovery_installer.py --install --apply-current-fixes --run-tests
python -m compileall src\claire
pytest
```

Future generated installers:

```powershell
python tools\install_manifest_package.py --installer claire_next_installer.py
python tools\install_manifest_package.py --installer claire_next_installer.py --install --run-tests
```
