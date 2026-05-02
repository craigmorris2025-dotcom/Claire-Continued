#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any, Dict, List


def find_project_root(start: Path | None = None) -> Path:
    start = (start or Path(__file__).resolve()).resolve()
    for candidate in [start] + list(start.parents):
        if (candidate / "main.py").exists() and (candidate / "src" / "claire").exists():
            return candidate
    raise SystemExit("Could not detect Claire project root.")


class PortableLauncher:
    """Launch Claire from any folder/drive without hardcoded paths."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def status(self, live: bool = False, app: bool = False) -> Dict[str, Any]:
        python = self.select_python()
        checks = {
            "project_root": self.root.exists(),
            "dashboard_server": (self.root / "tools" / "serve_export_dashboard.py").exists(),
            "dashboard_html": (self.root / "src" / "frontend" / "export_dashboard" / "index.html").exists(),
            "baseline_runner": (self.root / "tools" / "run_claire_baseline.py").exists(),
            "local_venv_python": (self.root / ".venv" / "Scripts" / "python.exe").exists(),
            "selected_python_available": bool(python),
        }
        return {
            "status": "success" if all(checks.values()) else "partial",
            "portable_launcher": "v5.64_desktop_live",
            "root": str(self.root),
            "selected_python": python,
            "live_requested": live,
            "app_shell_requested": app,
            "live_env": "CLAIRE_ENABLE_LIVE_FEEDS=1" if live else "disabled",
            "checks": checks,
            "recommended_command": "START_CLAIRE_LIVE.bat" if live else "START_CLAIRE_PORTABLE.bat",
        }

    def select_python(self) -> str:
        candidates = [
            self.root / ".venv" / "Scripts" / "python.exe",
            self.root / ".venv" / "Scripts" / "pythonw.exe",
        ]
        for candidate in candidates:
            if candidate.exists() and self._python_works(str(candidate)):
                return str(candidate)

        for command in (["py", "-3"], ["python"], ["python3"]):
            if self._python_works(command):
                return " ".join(command)
        return ""

    def launch(self, host: str, port: int, no_open: bool = False, run_baseline: bool = False, live: bool = False, app: bool = False) -> int:
        python = self.select_python()
        if not python:
            print("No usable Python was found. Keep the .venv folder with Claire or install Python 3.10+ on this machine.")
            return 1

        if run_baseline:
            baseline_code = self._run_python(python, [str(self.root / "tools" / "run_claire_baseline.py")])
            if baseline_code != 0:
                print("Baseline failed. Dashboard launch stopped so the portable copy can be inspected.")
                return baseline_code

        selected_port = self.find_open_port(host, port)
        url = f"http://{host}:{selected_port}"
        args = self._python_command(python) + [
            str(self.root / "tools" / "serve_export_dashboard.py"),
            "--host",
            host,
            "--port",
            str(selected_port),
            "--no-open",
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.root / "src") + os.pathsep + str(self.root) + os.pathsep + env.get("PYTHONPATH", "")
        if live:
            env["CLAIRE_ENABLE_LIVE_FEEDS"] = "1"
            env["CLAIRE_DESKTOP_LIVE"] = "1"
        if app:
            env["CLAIRE_APP_SHELL"] = "1"
        print("Claire Portable Launcher")
        print("=======================")
        print(f"Root:   {self.root}")
        print(f"Python: {python}")
        print(f"URL:    {url}")
        print(f"Live:   {'enabled' if live else 'disabled'}")
        print(f"Shell:  {'app-like' if app else 'browser'}")
        print("")
        process = subprocess.Popen(args, cwd=str(self.root), env=env)
        if self.wait_for_health(url):
            print("Claire dashboard is ready.")
            if not no_open:
                webbrowser.open(url)
        else:
            print("Dashboard process started, but health check did not respond yet.")
            if not no_open:
                webbrowser.open(url)

        try:
            return process.wait()
        except KeyboardInterrupt:
            print("\nStopping Claire dashboard.")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            return 0

    def find_open_port(self, host: str, preferred: int) -> int:
        for port in [preferred] + list(range(preferred + 1, preferred + 50)):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.2)
                if sock.connect_ex((host, port)) != 0:
                    return port
        raise RuntimeError("No open local port found for Claire dashboard.")

    def wait_for_health(self, url: str, timeout: float = 12.0) -> bool:
        deadline = time.time() + timeout
        health_url = url.rstrip("/") + "/api/health"
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(health_url, timeout=1.5) as response:
                    return response.status == 200
            except Exception:
                time.sleep(0.4)
        return False

    def _run_python(self, python: str, args: List[str]) -> int:
        command = self._python_command(python) + args
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.root / "src") + os.pathsep + str(self.root) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.call(command, cwd=str(self.root), env=env)

    def _python_command(self, python: str) -> List[str]:
        if python == "py -3":
            return ["py", "-3"]
        return [python]

    def _python_works(self, python: str | List[str]) -> bool:
        try:
            command = self._python_command(python) if isinstance(python, str) else python
            result = subprocess.run(command + ["-c", "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            return result.returncode == 0
        except Exception:
            return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable Claire dashboard launcher.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--status", action="store_true", help="Print portable launcher readiness and exit.")
    parser.add_argument("--run-baseline", action="store_true", help="Run baseline validation before launching.")
    parser.add_argument("--live", action="store_true", help="Enable desktop live connected metadata mode.")
    parser.add_argument("--app", action="store_true", help="Enable app-like desktop shell mode.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = find_project_root()
    launcher = PortableLauncher(root)
    if args.status:
        print(json.dumps(launcher.status(live=args.live, app=args.app), indent=2))
        return 0
    return launcher.launch(args.host, args.port, no_open=args.no_open, run_baseline=args.run_baseline, live=args.live, app=args.app)


if __name__ == "__main__":
    raise SystemExit(main())
