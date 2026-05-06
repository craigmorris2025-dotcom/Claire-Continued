# Claire Desktop Launcher Version Connector

Installed files:

- `START_CLAIRE_DESKTOP.bat`
- `tools/desktop_version_sync.py`
- `data/version_sync/.gitkeep`
- `data/dashboard/state_snapshots/.gitkeep`

Purpose:

This connects the desktop launcher to the current Claire version state while preserving the known working launch route:

```bat
tools\portable_launcher.py --live --app
```

It writes launcher/version proof snapshots to:

- `data/version_sync/desktop_launcher_version_state.json`
- `data/dashboard/state_snapshots/desktop_launcher_state.json`

It does not modify runtime engines, lifecycle routing, scoring, or `core_run_output.json`.
