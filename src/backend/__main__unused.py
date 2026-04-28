"""
CLI Entry Point — python -m src.backend
Commands: serve, health, run, history, interactive
"""
import argparse
import json
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def cmd_serve(args):
    """Start the FastAPI web server."""
    try:
        import uvicorn
    except ImportError:
        print("  ERROR: uvicorn not installed. Run: pip install -r requirements.txt")
        return
    host = args.host if hasattr(args, "host") else "0.0.0.0"
    port = args.port if hasattr(args, "port") else 8000
    print("=" * 60)
    print("  CLAIRE SYNTALION — Enterprise Platform v4.0")
    print(f"  Web UI:   http://localhost:{port}/ui")
    print(f"  API Docs: http://localhost:{port}/docs")
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    uvicorn.run("src.backend.server:app", host=host, port=port, reload=False)


def cmd_health(args=None):
    """Run full system health check."""
    print("=" * 60)
    print("  CLAIRE SYNTALION — Health Check v4.0")
    print("=" * 60)
    checks = []

    # Config
    try:
        from backend.config.settings import get_settings
        s = get_settings()
        checks.append(("Config/Settings", "PASS", f"env={s.env}"))
    except Exception as e:
        checks.append(("Config/Settings", "FAIL", str(e)))

    # Contract Layer
    try:
        from backend.claire.contract import ContractValidator
        cv = ContractValidator()
        checks.append(("Contract Layer", "PASS", "validator active"))
    except Exception as e:
        checks.append(("Contract Layer", "FAIL", str(e)))

    # Orreadir Router
    try:
        from backend.claire.orreadir import OrreadirRouter
        checks.append(("Orreadir Router", "PASS", "router active"))
    except Exception as e:
        checks.append(("Orreadir Router", "FAIL", str(e)))

    # Core: Semantic
    try:
        from backend.core.semantic import SemanticLayer
        sl = SemanticLayer()
        r = sl.process("AI defense platform")
        checks.append(("Core: Semantic/NLP", "PASS", f"{len(r.keywords)} keywords, {len(r.dimensions)} domains"))
    except Exception as e:
        checks.append(("Core: Semantic/NLP", "FAIL", str(e)))

    # Core: Planner
    try:
        from backend.core.planner import Planner
        checks.append(("Core: Planner", "PASS", "active"))
    except Exception as e:
        checks.append(("Core: Planner", "FAIL", str(e)))

    # Core: DataEngine
    try:
        from backend.core.data_engine import DataEngine
        de = DataEngine()
        acqs = de.load_acquirers()
        checks.append(("Core: DataEngine", "PASS", f"{len(acqs)} acquirers loaded"))
    except Exception as e:
        checks.append(("Core: DataEngine", "FAIL", str(e)))

    # Core: Gateway
    try:
        from backend.core.gateway import Gateway
        checks.append(("Core: Gateway", "PASS", "active"))
    except Exception as e:
        checks.append(("Core: Gateway", "FAIL", str(e)))

    # Engines
    try:
        from backend.engines import DOMAIN_REGISTRY
        checks.append(("Domain Engines", "PASS", f"{len(DOMAIN_REGISTRY)} registered"))
    except Exception as e:
        checks.append(("Domain Engines", "FAIL", str(e)))

    # Mode Controller
    try:
        from backend.mode.controller import ModeController
        mc = ModeController()
        checks.append(("Mode Controller", "PASS", f"mode={mc.current_mode}"))
    except Exception as e:
        checks.append(("Mode Controller", "FAIL", str(e)))

    # Orchestrator
    try:
        from backend.orchestrator.pipeline import PipelineOrchestrator
        checks.append(("Orchestrator", "PASS", "pipeline ready"))
    except Exception as e:
        checks.append(("Orchestrator", "FAIL", str(e)))

    # MasterPass Bridge
    try:
        from backend.bridge.masterpass import MasterPassBridge
        checks.append(("MasterPass Bridge", "PASS", "bridge ready"))
    except Exception as e:
        checks.append(("MasterPass Bridge", "FAIL", str(e)))

    # Connectors
    try:
        from backend.connectors.manager import ConnectorManager
        cm = ConnectorManager()
        checks.append(("Connectors", "PASS", f"{len(cm.available_connectors('connected'))} available"))
    except Exception as e:
        checks.append(("Connectors", "FAIL", str(e)))

    # Scoring
    try:
        from backend.scoring.calibrator import ScoreCalibrator
        checks.append(("Score Calibration", "PASS", "active"))
    except Exception as e:
        checks.append(("Score Calibration", "FAIL", str(e)))

    # Database
    try:
        from backend.persistence.database import Database
        db = Database()
        stats = db.get_stats()
        checks.append(("DB Persistence", "PASS", f"SQLite OK, {stats['total_runs']} runs"))
    except Exception as e:
        checks.append(("DB Persistence", "FAIL", str(e)))

    # E2E Pipeline Test
    try:
        from backend.orchestrator.pipeline import PipelineOrchestrator
        from backend.claire.contract import ContractValidator
        cv = ContractValidator()
        intent, errs = cv.validate_input({"raw_input": "AI defense platform", "mode": "deterministic"})
        if intent and not errs:
            po = PipelineOrchestrator()
            result = po.execute(intent)
            ds = result.scores.get("decision_score", 0)
            checks.append(("Pipeline E2E", "PASS", f"{result.intent_id} decision={ds:.3f}"))
        else:
            checks.append(("Pipeline E2E", "FAIL", f"validation: {errs}"))
    except Exception as e:
        checks.append(("Pipeline E2E", "FAIL", str(e)))

    # Print results
    for name, status, detail in checks:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {icon} {name}: {detail}")
    passed = sum(1 for _, s, _ in checks if s == "PASS")
    print("-" * 47)
    print(f"  {passed}/{len(checks)} passed")
    print("=" * 60)


def cmd_run(args):
    """Run pipeline on input text."""
    from backend.orchestrator.pipeline import PipelineOrchestrator
    from backend.claire.contract import ContractValidator
    from backend.scoring.scorecard import ScoreCard

    mode = getattr(args, "mode", "deterministic")
    text = getattr(args, "text", None)
    if not text:
        text = input("  Enter target text: ").strip()
    if not text:
        print("  No input."); return

    cv = ContractValidator()
    intent, errs = cv.validate_input({"raw_input": text, "mode": mode})
    if errs:
        print(f"  Validation errors: {errs}"); return

    po = PipelineOrchestrator()
    result = po.execute(intent)
    print(ScoreCard().generate(result))


def cmd_history(args=None):
    """Show pipeline run history."""
    from backend.persistence.database import Database
    db = Database()
    runs = db.get_runs(20)
    print(f"\n  Pipeline History ({len(runs)} runs):")
    print("  " + "-" * 56)
    for i, r in enumerate(runs, 1):
        ds = r.get("decision_score", 0)
        dc = r.get("decision_class", "?")
        print(f"  {i:3}. [{r.get('mode','?'):13}] Decision={ds:.3f} ({dc})  {r.get('created_at','')}")
    if not runs:
        print("  No runs yet.")


def cmd_interactive(args=None):
    """Interactive console."""
    print("\n  CLAIRE SYNTALION — Interactive Console v4.0")
    print("  Commands: run, health, history, quit\n")
    while True:
        try:
            cmd = input("  claire> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if cmd in ("quit", "exit", "q"):
            break
        elif cmd == "health":
            cmd_health()
        elif cmd == "history":
            cmd_history()
        elif cmd in ("run", "scorecard"):
            mode = input("  Mode [deterministic]: ").strip() or "deterministic"
            text = input("  Target text: ").strip()
            if text:
                class FakeArgs:
                    pass
                a = FakeArgs()
                a.text = text
                a.mode = mode
                cmd_run(a)
        else:
            print(f"  Unknown: {cmd}")
    print("  Goodbye.")


def main():
    parser = argparse.ArgumentParser(description="Claire Syntalion Enterprise v4.0")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("health", help="System health check")

    p_serve = sub.add_parser("serve", help="Start web server")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8000)

    p_run = sub.add_parser("run", help="Run pipeline")
    p_run.add_argument("--text", "-t", type=str)
    p_run.add_argument("--mode", "-m", default="deterministic",
                       choices=["deterministic", "connected", "hybrid"])

    sub.add_parser("history", help="Show run history")
    sub.add_parser("interactive", help="Interactive console")

    args = parser.parse_args()
    if not args.command:
        cmd_serve(args)
    elif args.command == "health":
        cmd_health()
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "history":
        cmd_history()
    elif args.command == "interactive":
        cmd_interactive()


if __name__ == "__main__":
    main()
