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
from claire.runtime.market_universe_taxonomy import MarketUniverseTaxonomy
from claire.runtime.search_suggestions import OpportunitySearchSuggestions
from claire.runtime.opportunity_seed_generator import OpportunitySeedGenerator
from claire.runtime.opportunity_candidate_store import OPPORTUNITY_CANDIDATES
from claire.feeds.feed_registry import FeedRegistry
from claire.governance.redline_classifier import RedlineClassifier
from claire.governance.legal_audit_log import LegalAuditLog

DASHBOARD_DIR=PROJECT_ROOT/"src"/"frontend"/"export_dashboard"
CATALOG=OpportunityCommandCatalog()
TAXONOMY=MarketUniverseTaxonomy()
SUGGESTIONS=OpportunitySearchSuggestions()
SEEDS=OpportunitySeedGenerator()
FEEDS=FeedRegistry()
GOVERNANCE=RedlineClassifier()
LEGAL_AUDIT=LegalAuditLog()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print("[dashboard]", fmt % args)
    def do_GET(self):
        parsed=urlparse(self.path); path=parsed.path
        try:
            if path in {"/","/index.html"}: return self.file(DASHBOARD_DIR/"index.html")
            if path in {"/dashboard.css","/dashboard.js"}: return self.file(DASHBOARD_DIR/path.lstrip("/"))
            if path=="/api/commands": return self.json(CATALOG.catalog())
            if path=="/api/market-universe": return self.json(TAXONOMY.catalog())
            if path=="/api/feeds/status": return self.json(FEEDS.status())
            if path=="/api/governance/audit": return self.json(LEGAL_AUDIT.recent())
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
            if parsed.path=="/api/governance/evaluate": return self.json(self.governance_evaluate(self.body()))
            if parsed.path=="/api/feeds/scan": return self.json(self.scan_feed(self.body()))
            if parsed.path=="/api/rescan": return self.json(RunHistory().rescan_exports("exports"))
            if parsed.path=="/api/evaluate": return self.json(self.eval_sync(self.body()))
            if parsed.path=="/api/evaluate/async": return self.json(self.eval_async(self.body()))
            if parsed.path=="/api/opportunities/search-needed-solutions": return self.json(self.search_needed_solutions(self.body()))
            if parsed.path=="/api/opportunities/generate": return self.json(self.generate_public_opportunities(self.body()))
            if parsed.path=="/api/opportunities/run-candidate": return self.json(self.run_candidate(self.body()))
            self.send_error(404,"Not found")
        except Exception as e:
            self.json({"status":"error","error":str(e),"traceback":traceback.format_exc()},500)
    def governance_evaluate(self,payload):
        text=(payload.get("raw_input") or payload.get("signal") or payload.get("text") or "")
        context={
            "workflow":payload.get("workflow"),
            "execution_mode":payload.get("execution_mode"),
            "market_universe":payload.get("market_universe"),
            "industry_domain":payload.get("industry_domain"),
            "buyer_segment":payload.get("buyer_segment"),
            "objective":payload.get("objective"),
        }
        decision=GOVERNANCE.classify(text,context)
        audit=LEGAL_AUDIT.log("governance_evaluation",decision,context)
        return {"status":"success","decision":decision,"audit_event":audit}
    def scan_feed(self,payload):
        decision=GOVERNANCE.classify(payload.get("signal",""),payload)
        LEGAL_AUDIT.log("feed_scan_precheck",decision,payload)
        if decision.get("decision")=="block":
            return {"status":"blocked","decision":decision}
        result=FEEDS.scan(
            market_universe=payload.get("market_universe","custom_universe"),
            mode=payload.get("execution_mode","deterministic"),
            filters=payload,
        )
        result["governance_decision"]=decision
        return result
    def search_needed_solutions(self,payload):
        return SUGGESTIONS.suggest(
            market_universe=payload.get("market_universe","custom_universe"),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
            workflow=payload.get("workflow","discover"),
            signal=payload.get("signal",""),
            count=int(payload.get("count",10) or 10),
        )
    def generate_public_opportunities(self,payload):
        generated = SEEDS.generate(
            workflow=payload.get("workflow","discover"),
            execution_mode=payload.get("execution_mode","deterministic"),
            market_universe=payload.get("market_universe","custom_universe"),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
            command_id=payload.get("command_id","discover_market_gaps"),
            signal=payload.get("signal",""),
            count=int(payload.get("count",5) or 5),
        )
        public_cards=[]
        for candidate in generated.get("candidates", []):
            candidate_id=OPPORTUNITY_CANDIDATES.put(candidate)
            stored=OPPORTUNITY_CANDIDATES.get(candidate_id) or {}
            public_cards.append(OPPORTUNITY_CANDIDATES.public_card(stored))
        return {
            "status":"success",
            "candidate_count":len(public_cards),
            "candidates":public_cards,
            "workflow":generated.get("workflow"),
            "execution_mode":generated.get("execution_mode"),
            "market_universe":generated.get("market_universe"),
            "industry_domain":generated.get("industry_domain"),
            "buyer_segment":generated.get("buyer_segment"),
            "objective":generated.get("objective"),
        }
    def run_candidate(self,payload):
        candidate_id=payload.get("candidate_id")
        candidate=OPPORTUNITY_CANDIDATES.get(candidate_id or "")
        if not candidate: return {"status":"not_found","error":"candidate not found or expired"}
        launch_payload={
            "raw_input":candidate.get("raw_input",""),
            "workflow":candidate.get("workflow"),
            "execution_mode":candidate.get("execution_mode"),
            "market_universe":candidate.get("market_universe"),
            "industry_domain":candidate.get("industry_domain"),
            "buyer_segment":candidate.get("buyer_segment"),
            "objective":candidate.get("objective"),
        }
        return self.eval_async(launch_payload)
    def events(self,path,query):
        parts=[unquote(p) for p in path.split("/") if p]
        since=query.get("since",[None])[0]
        since=int(since) if since is not None and str(since).isdigit() else None
        return self.json(RUN_EVENTS.get(parts[2],since))
    def eval_async(self,payload):
        raw=(payload.get("raw_input") or payload.get("text") or "").strip()
        if not raw: return {"status":"validation_failed","error":"raw_input is required"}
        metadata={
            "source":"dashboard",
            "workflow":payload.get("workflow"),
            "market_universe":payload.get("market_universe"),
            "industry_domain":payload.get("industry_domain"),
            "buyer_segment":payload.get("buyer_segment"),
            "objective":payload.get("objective"),
            "execution_mode":payload.get("execution_mode"),
        }
        governance_decision=GOVERNANCE.classify(raw,metadata)
        LEGAL_AUDIT.log("dashboard_launch_precheck",governance_decision,metadata)
        if governance_decision.get("decision")=="block":
            return {"status":"blocked","decision":governance_decision}
        run_id=RUN_EVENTS.create_run(raw[:80]+("..." if len(raw)>80 else ""),metadata)
        RUN_EVENTS.add(run_id,"stage_complete","Governance precheck: "+governance_decision.get("decision","allow"),"governance",4,governance_decision)
        threading.Thread(target=self.worker,args=(run_id,raw,payload),daemon=True).start()
        RUN_EVENTS.add(run_id,"started","Background Claire evaluation started.","launcher",3)
        return {"status":"started","event_run_id":run_id}
    def worker(self,run_id,raw,payload):
        try:
            RUN_EVENTS.add(run_id,"stage_started","Validating request.","contract",6)
            mode=self.normalize_mode(payload.get("execution_mode"))
            intent=ContractValidator().validate_intent({"raw_input":raw,"mode":mode,"metadata":{"source":"dashboard","priority":"high","workflow":payload.get("workflow"),"market_universe":payload.get("market_universe"),"industry_domain":payload.get("industry_domain"),"buyer_segment":payload.get("buyer_segment"),"objective":payload.get("objective")}})
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
        mode=self.normalize_mode(payload.get("execution_mode"))
        intent=ContractValidator().validate_intent({"raw_input":raw,"mode":mode,"metadata":{"source":"dashboard","priority":"high","workflow":payload.get("workflow")}})
        result=PipelineOrchestrator().execute(intent)
        data=result.to_dict() if hasattr(result,"to_dict") else result
        RunHistory().rescan_exports("exports")
        return self.compact(data)
    def normalize_mode(self, mode):
        mode=mode or "deterministic"
        if mode=="connected_intelligence": mode="connected"
        return mode if mode in {"deterministic","connected","hybrid"} else "deterministic"
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
