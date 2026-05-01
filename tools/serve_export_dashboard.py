#!/usr/bin/env python
r"""Serve Claire's local export dashboard.

Run from project root:
    python tools\serve_export_dashboard.py
Open:
    http://127.0.0.1:8765
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


def find_project_root(start=None):
    start = (start or Path.cwd()).resolve()
    for candidate in [start] + list(start.parents):
        if (candidate / "main.py").exists() and (candidate / "src" / "claire").exists():
            return candidate
    raise SystemExit("Could not detect Claire project root. Run from the folder containing main.py and src/claire.")


PROJECT_ROOT = find_project_root()
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from claire.runtime.export_browser import ExportBrowser
from claire.runtime.run_history import RunHistory


DASHBOARD_DIR = PROJECT_ROOT / "src" / "frontend" / "export_dashboard"


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "ClaireExportDashboard/0.1"

    def log_message(self, fmt, *args):
        print("[dashboard]", fmt % args)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path in {"/", "/index.html"}:
                return self._send_file(DASHBOARD_DIR / "index.html")
            if path in {"/dashboard.css", "/dashboard.js"}:
                return self._send_file(DASHBOARD_DIR / path.lstrip("/"))
            if path == "/api/runs":
                return self._json(ExportBrowser().list_runs(limit=200, rescan_if_empty=True))
            if path == "/api/summary":
                return self._json(ExportBrowser().summary())
            if path.startswith("/api/runs/"):
                return self._handle_run_api(path, parse_qs(parsed.query))
            self.send_error(404, "Not found")
        except Exception as exc:
            self._json({"status": "error", "error": str(exc)}, status=500)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/rescan":
                return self._json(RunHistory().rescan_exports("exports"))
            self.send_error(404, "Not found")
        except Exception as exc:
            self._json({"status": "error", "error": str(exc)}, status=500)

    def _handle_run_api(self, path, query):
        parts = [unquote(part) for part in path.split("/") if part]
        if len(parts) < 3:
            return self.send_error(404, "Run id missing")
        run_id = parts[2]
        browser = ExportBrowser()
        if len(parts) == 3:
            return self._json(browser.get_run(run_id))
        if len(parts) == 4 and parts[3] == "files":
            return self._json(browser.list_files(run_id))
        if len(parts) == 5 and parts[3] == "files":
            filename = parts[4]
            raw = query.get("raw", ["0"])[0] == "1"
            max_chars = int(query.get("max_chars", ["0"])[0] or 0)
            result = browser.read_file(run_id, filename, max_chars=max_chars or None)
            if raw and result.get("status") == "success":
                return self._text(result.get("content", ""), filename=filename)
            return self._json(result)
        self.send_error(404, "Unsupported run API path")

    def _send_file(self, path):
        if not path.exists() or not path.is_file():
            return self.send_error(404, f"File not found: {path.name}")
        mime, _ = mimetypes.guess_type(str(path))
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload, status=200):
        data = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _text(self, content, filename="artifact.txt"):
        suffix = Path(filename).suffix.lower()
        mime = "application/json" if suffix == ".json" else "text/markdown" if suffix == ".md" else "text/plain"
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser(description="Serve Claire's local export dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    if not (DASHBOARD_DIR / "index.html").exists():
        raise SystemExit(f"Dashboard files not found at {DASHBOARD_DIR}")

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Claire Export Dashboard running at {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_open:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
