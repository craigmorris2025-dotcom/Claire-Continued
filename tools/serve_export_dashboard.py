#!/usr/bin/env python
from __future__ import annotations
import argparse, json, mimetypes, sys, traceback, webbrowser, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

def find_project_root(start=None):
    start=(start or Path.cwd()).resolve()
    for c in [start]+list(start.parents):
        if (c/"main.py").exists() and (c/"src"/"claire").exists(): return c
    raise SystemExit("Could not detect Claire project root.")

PROJECT_ROOT=find_project_root(); SRC=PROJECT_ROOT/"src"
for p in (SRC, PROJECT_ROOT):
    if str(p) not in sys.path: sys.path.insert(0,str(p))

from claire.domain.contract import ContractValidator
from claire.orchestrator.pipeline_v4 import PipelineOrchestrator
from claire.runtime.export_browser import ExportBrowser
from claire.runtime.run_history import RunHistory
from claire.runtime.run_events import RUN_EVENTS
from claire.runtime.command_catalog import OpportunityCommandCatalog
from claire.runtime.search_suggestions import OpportunitySearchSuggestions
from claire.runtime.opportunity_seed_generator import OpportunitySeedGenerator

DASHBOARD_DIR=PROJECT_ROOT/"src"/"frontend"/"export_dashboard"
CATALOG=OpportunityCommandCatalog()
SUGGESTIONS=OpportunitySearchSuggestions()
SEEDS=OpportunitySeedGenerator()

TEMPLATES=[
 {"id":"defense_control_gated","name":"Defense autonomy / control-gated","raw_input":"A secure mission intelligence platform that ingests authorized mission context, sensor summaries, operator constraints, and simulation results to recommend advisory coordination options for human review. The system does not automate operational decisions. It runs mission simulations, scores coordination risk, routes recommendations through a secure command review console, requires human authorization, records override decisions, and preserves a mission-use audit log. The buyer pain is that defense teams need reviewable autonomy support in contested environments, but deployment must remain control-gated with allowed-use boundaries, operator trust, and auditability."},
 {"id":"climate_insurance","name":"Climate insurance / underwriting","raw_input":"A climate insurance risk intelligence platform for insurers, reinsurers, and underwriting teams that combines historical weather losses, property exposure data, catastrophe scenarios, regional climate concentration, premium adequacy signals, and market withdrawal patterns. The system detects repricing pressure before legacy underwriting workflows react, generates exposure benchmarks, recommends risk-transfer countermeasures, and routes all pricing-impact outputs through underwriter review controls with scenario versioning and audit logs."}
]

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print("[dashboard]", fmt % args)
    def do_GET(self):
        parsed=urlparse(self.path); path=parsed.path
        try:
            if path in {"/","/index.html"}: return self.file(DASHBOARD_DIR/"index.html")
            if path in {"/dashboard.css","/dashboard.js"}: return self.file(DASHBOARD_DIR/path.lstrip("/"))
            if path=="/api/templates": return self.json({"status":"success","templates":TEMPLATES})
            if path=="/api/commands": return self.json(CATALOG.catalog())
            if path=="/api/runs": return self.json(ExportBrowser().list_runs(limit=200,rescan_if_empty=True))
            if path=="/api/summary": return self.json(ExportBrowser().summary())
            if path=="/api/events": return self.json(RUN_EVENTS.list())
            if path.startswith("/api/events/"): return self.events(path,parse_qs(parsed.query))
            if path.startswith("/api/runs/"): return self.run_api(path,parse_qs(parsed.query))
            self.send_error(404,"Not found")
        except Exception as e:
            self.json({"status":"error","error":str(e),"traceback":traceback.format_exc()},500)
    def do_POST(self):
        parsed=urlparse(self.path)
        try:
            if parsed.path=="/api/rescan": return self.json(RunHistory().rescan_exports("exports"))
            if parsed.path=="/api/evaluate": return self.json(self.eval_sync(self.body()))
            if parsed.path=="/api/evaluate/async": return self.json(self.eval_async(self.body()))
            if parsed.path=="/api/commands/suggest": return self.json(self.suggest(self.body()))
            if parsed.path=="/api/opportunities/generate": return self.json(self.generate(self.body()))
            self.send_error(404,"Not found")
        except Exception as e:
            self.json({"status":"error","error":str(e),"traceback":traceback.format_exc()},500)
    def suggest(self,payload):
        return SUGGESTIONS.suggest(sector=payload.get("sector","cross_sector"),workflow=payload.get("workflow","discover"),signal=payload.get("signal",""),count=int(payload.get("count",10) or 10))
    def generate(self,payload):
        return SEEDS.generate(workflow=payload.get("workflow","discover"),execution_mode=payload.get("execution_mode","deterministic"),sector=payload.get("sector","cross_sector"),command_id=payload.get("command_id","discover_non_obvious"),signal=payload.get("signal",""),count=int(payload.get("count",5) or 5))
    def events(self,path,query):
        parts=[unquote(p) for p in path.split("/") if p]
        since=query.get("since",[None])[0]
        since=int(since) if since is not None and str(since).isdigit() else None
        return self.json(RUN_EVENTS.get(parts[2],since))
    def eval_async(self,payload):
        raw=(payload.get("raw_input") or payload.get("text") or "").strip()
        if not raw: return {"status":"validation_failed","error":"raw_input is required"}
        run_id=RUN_EVENTS.create_run(raw[:80]+("..." if len(raw)>80 else ""),{"source":"dashboard","workflow":payload.get("workflow"),"execution_mode":payload.get("execution_mode")})
        threading.Thread(target=self.worker,args=(run_id,raw,payload),daemon=True).start()
        RUN_EVENTS.add(run_id,"started","Background Claire evaluation started.","launcher",3)
        return {"status":"started","event_run_id":run_id}
    def worker(self,run_id,raw,payload):
        try:
            RUN_EVENTS.add(run_id,"stage_started","Validating request.","contract",6)
            mode=payload.get("execution_mode") or "deterministic"
            if mode == "connected_intelligence": mode = "connected"
            if mode not in {"deterministic","connected","hybrid"}: mode="deterministic"
            intent=ContractValidator().validate_intent({"raw_input":raw,"mode":mode,"metadata":{"source":"dashboard","priority":"high","workflow":payload.get("workflow")}})
            RUN_EVENTS.add(run_id,"stage_complete",f"Contract validation complete. Execution mode: {mode}.","contract",10)
            RUN_EVENTS.add(run_id,"stage_started","Running Claire pipeline.","pipeline",15)
            result=PipelineOrchestrator().execute(intent)
            data=result.to_dict() if hasattr(result,"to_dict") else result
            RUN_EVENTS.add(run_id,"stage_complete","Core pipeline complete.","pipeline",70)
            summary=data.get("lifecycle_summary") or {}
            if summary: RUN_EVENTS.add(run_id,"stage_complete",f"Lifecycle: {summary.get('active_stage_count')}/{summary.get('implemented_stage_count')} active.","lifecycle",80,summary)
            ew=data.get("export_writer") or {}
            if ew: RUN_EVENTS.add(run_id,"stage_complete",f"Export writer: {ew.get('status')}","export_writer",88,{"output_dir":ew.get("output_dir")})
            RunHistory().rescan_exports("exports")
            compact=self.compact(data)
            RUN_EVENTS.set_result(run_id,compact)
            RUN_EVENTS.add(run_id,"complete","Claire run complete. Export artifacts are ready.","complete",100,compact)
        except Exception as e:
            RUN_EVENTS.add(run_id,"error",str(e),"error",100,{"traceback":traceback.format_exc()},"error")
    def eval_sync(self,payload):
        raw=(payload.get("raw_input") or payload.get("text") or "").strip()
        if not raw: return {"status":"validation_failed","error":"raw_input is required"}
        mode=payload.get("execution_mode") or "deterministic"
        if mode=="connected_intelligence": mode="connected"
        if mode not in {"deterministic","connected","hybrid"}: mode="deterministic"
        intent=ContractValidator().validate_intent({"raw_input":raw,"mode":mode,"metadata":{"source":"dashboard","priority":"high","workflow":payload.get("workflow")}})
        result=PipelineOrchestrator().execute(intent)
        data=result.to_dict() if hasattr(result,"to_dict") else result
        RunHistory().rescan_exports("exports")
        return self.compact(data)
    def compact(self,data):
        ew=data.get("export_writer") or {}; hr=ew.get("history_record") or {}; ep=data.get("export_package") or {}
        return {"status":data.get("status","success"),"run_id":hr.get("run_id") or ew.get("folder_name"),"folder_name":ew.get("folder_name"),"decision_classification":data.get("decision_classification"),"breakthrough_classification":data.get("breakthrough_classification"),"export_level":(ep.get("export_package_score") or {}).get("level"),"export_writer":{"status":ew.get("status"),"output_dir":ew.get("output_dir"),"folder_name":ew.get("folder_name"),"written_file_count":ew.get("written_file_count"),"history_record":hr},"lifecycle_summary":data.get("lifecycle_summary"),"scores":data.get("scores")}
    def body(self):
        n=int(self.headers.get("Content-Length","0") or 0); raw=self.rfile.read(n).decode("utf-8") if n else "{}"; return json.loads(raw or "{}")
    def run_api(self,path,query):
        parts=[unquote(p) for p in path.split("/") if p]; run_id=parts[2]; browser=ExportBrowser()
        if len(parts)==3: return self.json(browser.get_run(run_id))
        if len(parts)==4 and parts[3]=="files": return self.json(browser.list_files(run_id))
        if len(parts)==5 and parts[3]=="files":
            filename=parts[4]; raw=query.get("raw",["0"])[0]=="1"; maxc=int(query.get("max_chars",["0"])[0] or 0); res=browser.read_file(run_id,filename,max_chars=maxc or None)
            if raw and res.get("status")=="success": return self.text(res.get("content",""),filename)
            return self.json(res)
        self.send_error(404,"Unsupported run API path")
    def file(self,path):
        if not path.exists() or not path.is_file(): return self.send_error(404,f"File not found: {path.name}")
        data=path.read_bytes(); mime,_=mimetypes.guess_type(str(path)); self.send_response(200); self.send_header("Content-Type",mime or "application/octet-stream"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def json(self,payload,status=200):
        data=json.dumps(payload,indent=2,default=str).encode("utf-8"); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def text(self,content,filename="artifact.txt"):
        suf=Path(filename).suffix.lower(); mime="application/json" if suf==".json" else "text/markdown" if suf==".md" else "text/plain"; data=content.encode("utf-8"); self.send_response(200); self.send_header("Content-Type",f"{mime}; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--host",default="127.0.0.1"); ap.add_argument("--port",type=int,default=8765); ap.add_argument("--no-open",action="store_true"); args=ap.parse_args()
    if not (DASHBOARD_DIR/"index.html").exists(): raise SystemExit(f"Dashboard files not found at {DASHBOARD_DIR}")
    srv=ThreadingHTTPServer((args.host,args.port),Handler); url=f"http://{args.host}:{args.port}"; print(f"Claire Dashboard running at {url}"); print("Press Ctrl+C to stop.")
    if not args.no_open: webbrowser.open(url)
    try: srv.serve_forever()
    except KeyboardInterrupt: print("\\nStopping dashboard.")
    finally: srv.server_close()
if __name__=="__main__": main()
