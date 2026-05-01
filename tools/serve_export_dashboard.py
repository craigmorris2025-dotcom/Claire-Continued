#!/usr/bin/env python
r"""Serve Claire's local dashboard with run launcher.

Run from project root:
    python tools\serve_export_dashboard.py
Open:
    http://127.0.0.1:8765
"""

from __future__ import annotations
import argparse, json, mimetypes, sys, traceback, webbrowser
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

from claire.domain.contract import ContractValidator
from claire.orchestrator.pipeline_v4 import PipelineOrchestrator
from claire.runtime.export_browser import ExportBrowser
from claire.runtime.run_history import RunHistory

DASHBOARD_DIR = PROJECT_ROOT / "src" / "frontend" / "export_dashboard"

TEMPLATES = [
    {"id":"defense_control_gated","name":"Defense autonomy / control-gated","raw_input":"A secure mission intelligence platform that ingests authorized mission context, sensor summaries, operator constraints, and simulation results to recommend advisory coordination options for human review. The system does not automate operational decisions. It runs mission simulations, scores coordination risk, routes recommendations through a secure command review console, requires human authorization, records override decisions, and preserves a mission-use audit log. The buyer pain is that defense teams need reviewable autonomy support in contested environments, but deployment must remain control-gated with allowed-use boundaries, operator trust, and auditability."},
    {"id":"climate_insurance","name":"Climate insurance / underwriting","raw_input":"A climate insurance risk intelligence platform for insurers, reinsurers, and underwriting teams that combines historical weather losses, property exposure data, catastrophe scenarios, regional climate concentration, premium adequacy signals, and market withdrawal patterns. The system detects repricing pressure before legacy underwriting workflows react, generates exposure benchmarks, recommends risk-transfer countermeasures, and routes all pricing-impact outputs through underwriter review controls with scenario versioning and audit logs."},
    {"id":"healthcare_operations","name":"Healthcare operations / patient flow","raw_input":"A healthcare operations intelligence platform for hospital command centers that forecasts patient-flow bottlenecks, staffing shortages, emergency department boarding pressure, bed capacity constraints, and discharge delays. The system ingests historical capacity data, staffing patterns, department-level throughput, and operational events to recommend proactive staffing and capacity countermeasures. It must preserve privacy controls, clinical workflow review, human approval before patient-impacting decisions, and measurable throughput or wait-time improvement."}
]

class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "ClaireDashboard/0.2"
    def log_message(self, fmt, *args):
        print("[dashboard]", fmt % args)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path in {"/", "/index.html"}: return self._send_file(DASHBOARD_DIR / "index.html")
            if path in {"/dashboard.css", "/dashboard.js"}: return self._send_file(DASHBOARD_DIR / path.lstrip("/"))
            if path == "/api/health": return self._json({"status":"ok","dashboard_dir":str(DASHBOARD_DIR)})
            if path == "/api/templates": return self._json({"status":"success","templates":TEMPLATES})
            if path == "/api/runs": return self._json(ExportBrowser().list_runs(limit=200, rescan_if_empty=True))
            if path == "/api/summary": return self._json(ExportBrowser().summary())
            if path.startswith("/api/runs/"): return self._handle_run_api(path, parse_qs(parsed.query))
            self.send_error(404, "Not found")
        except Exception as exc:
            self._json({"status":"error","error":str(exc),"traceback":traceback.format_exc()}, status=500)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/rescan": return self._json(RunHistory().rescan_exports("exports"))
            if parsed.path == "/api/evaluate": return self._json(self._run_evaluation())
            self.send_error(404, "Not found")
        except Exception as exc:
            self._json({"status":"error","error":str(exc),"traceback":traceback.format_exc()}, status=500)

    def _run_evaluation(self):
        payload = self._read_json_body()
        raw_input = (payload.get("raw_input") or payload.get("text") or "").strip()
        if not raw_input:
            return {"status":"validation_failed","error":"raw_input is required"}
        intent = ContractValidator().validate_intent({"raw_input": raw_input, "metadata": {"source": "dashboard", "priority": "high"}})
        result = PipelineOrchestrator().execute(intent)
        data = result.to_dict() if hasattr(result, "to_dict") else result
        export_writer = data.get("export_writer", {}) if isinstance(data, dict) else {}
        history_record = export_writer.get("history_record", {}) if isinstance(export_writer, dict) else {}
        run_id = history_record.get("run_id") or export_writer.get("folder_name")
        RunHistory().rescan_exports("exports")
        return {
            "status": data.get("status", "success"),
            "run_id": run_id,
            "folder_name": export_writer.get("folder_name"),
            "decision_classification": data.get("decision_classification"),
            "breakthrough_classification": data.get("breakthrough_classification"),
            "export_level": ((data.get("export_package") or {}).get("export_package_score") or {}).get("level"),
            "export_writer": {
                "status": export_writer.get("status"),
                "output_dir": export_writer.get("output_dir"),
                "folder_name": export_writer.get("folder_name"),
                "written_file_count": export_writer.get("written_file_count"),
                "history_record": history_record,
            },
            "lifecycle_summary": data.get("lifecycle_summary"),
            "scores": data.get("scores"),
        }

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _handle_run_api(self, path, query):
        parts = [unquote(part) for part in path.split("/") if part]
        if len(parts) < 3: return self.send_error(404, "Run id missing")
        run_id = parts[2]
        browser = ExportBrowser()
        if len(parts) == 3: return self._json(browser.get_run(run_id))
        if len(parts) == 4 and parts[3] == "files": return self._json(browser.list_files(run_id))
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
        if not path.exists() or not path.is_file(): return self.send_error(404, f"File not found: {path.name}")
        mime, _ = mimetypes.guess_type(str(path))
        data = path.read_bytes()
        self.send_response(200); self.send_header("Content-Type", mime or "application/octet-stream"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def _json(self, payload, status=200):
        data = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def _text(self, content, filename="artifact.txt"):
        suffix = Path(filename).suffix.lower()
        mime = "application/json" if suffix == ".json" else "text/markdown" if suffix == ".md" else "text/plain"
        data = content.encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", f"{mime}; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

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
    print(f"Claire Dashboard running at {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nStopping dashboard.")
    finally:
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
