# Claire Portable Launch

Use this project folder from a flash drive by opening:

```text
START_CLAIRE_PORTABLE.bat
```

For a safer start that runs the baseline first:

```text
START_CLAIRE_PORTABLE_SAFE.bat
```

The launcher detects its own folder, uses `.venv\Scripts\python.exe` when present, finds an open local port starting at `8765`, starts the dashboard, and opens the browser.

For desktop live connected mode:

```text
START_CLAIRE_LIVE.bat
START_CLAIRE_LIVE_SAFE.bat
```

Live mode sets:

```text
CLAIRE_ENABLE_LIVE_FEEDS=1
CLAIRE_DESKTOP_LIVE=1
```

It opens the same current dashboard, defaults the UI toward hybrid/public-company mode, and keeps governance plus deterministic fallback active. Live scans are metadata-only and require public URLs pasted into the Public Company Live Scan panel.

Useful checks:

```powershell
.\.venv\Scripts\python.exe tools\portable_launcher.py --status
.\.venv\Scripts\python.exe tools\run_claire_baseline.py
.\.venv\Scripts\python.exe tools\claire_update_from_url.py --status
```

Keep these folders with the portable copy:

```text
.venv
src
tools
data
exports
tests
```

Live feed fetching remains opt-in. The local dashboard and deterministic/hybrid workflow should run offline from the portable copy.
