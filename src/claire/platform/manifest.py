"""
Platform Manifest — Claire-Syntalion's self-awareness of completion state.

Three core concepts:
  1. TARGET_STATE  — the complete, fully-working desktop platform spec
  2. current_state() — live scan of what exists and works right now
  3. gap_analysis()  — diff between target and current, with resolution paths
"""
import importlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger("claire.platform.manifest")

TARGET_STATE = {
    "version": "4.2.1",
    "name": "Claire-Syntalion — Sovereign R&D Platform",

    "environment": {
        "python": {"min_version": "3.10", "resolution": "https://www.python.org/downloads/"},
        "venv": {"path": ".venv", "resolution": "python -m venv .venv"},
        "pip_packages": {
            "required": ["fastapi","uvicorn","pydantic","pydantic-settings","python-dotenv","aiohttp"],
            "resolution": "pip install -r requirements.txt",
        },
    },

    "backend": {
        "server":    {"file": "src/backend/server.py", "must_contain": ["4.2","routes_update","routes_proxy","routes_platform"]},
        "api_routes": {"required_files": [
            "src/backend/api/__init__.py","src/backend/api/routes_pipeline.py",
            "src/backend/api/routes_history.py","src/backend/api/routes_acquirers.py",
            "src/backend/api/routes_system.py","src/backend/api/routes_connectors.py",
            "src/backend/api/routes_update.py","src/backend/api/routes_proxy.py",
            "src/backend/api/routes_platform.py","src/backend/api/schemas.py",
        ]},
        "claire_layers": {"required_files": [
            "src/backend/claire/__init__.py","src/backend/claire/contract.py",
            "src/backend/claire/orreadir.py","src/backend/claire/interpreter.py",
        ]},
        "engines": {
            "count": 24,
            "required_files": ["src/backend/engines/__init__.py","src/backend/engines/base.py"],
            "phase_sequence": [
                ["ingestion",  ["ingestion","semantic","company_profiler","product_analyzer"]],
                ["analysis",   ["innovation","market","strategy","risk"]],
                ["valuation",  ["deal_structure","forecast","predictive","portfolio"]],
                ["synthesis",  ["synergy","engineering","customer","competitive"]],
                ["decision",   ["breakthrough","decision","governance","compliance"]],
                ["output",     ["scenario","sensitivity","benchmark","reporting"]],
            ],
        },
        "connectors": {"required_files": [
            "src/backend/connectors/__init__.py","src/backend/connectors/base.py",
            "src/backend/connectors/manager.py","src/backend/connectors/web_fetcher.py",
            "src/backend/connectors/market.py","src/backend/connectors/patent.py",
            "src/backend/connectors/financial.py","src/backend/connectors/news.py",
            "src/backend/connectors/academic.py",
        ]},
        "orchestrator": {"required_files": [
            "src/backend/orchestrator/__init__.py","src/backend/orchestrator/pipeline.py",
            "src/backend/orchestrator/pattern_recognition.py",
            "src/backend/orchestrator/fettio.py","src/backend/orchestrator/desking.py",
        ]},
        "platform_awareness": {"required_files": [
            "src/backend/platform/__init__.py","src/backend/platform/manifest.py",
            "src/backend/platform/resolver.py","src/backend/api/routes_platform.py",
        ]},
        "persistence": {"required_files": [
            "src/backend/persistence/__init__.py","src/backend/persistence/database.py",
        ]},
        "scoring":    {"required_files": ["src/backend/scoring/__init__.py","src/backend/scoring/calibrator.py","src/backend/scoring/scorecard.py"]},
        "bridge":     {"required_files": ["src/backend/bridge/__init__.py","src/backend/bridge/masterpass.py"]},
        "governance": {"required_files": ["src/backend/governance/__init__.py","src/backend/governance/audit.py","src/backend/governance/policy.py"]},
        "mode":       {"required_files": ["src/backend/mode/__init__.py","src/backend/mode/controller.py"]},
        "core":       {"required_files": ["src/backend/core/__init__.py","src/backend/core/data_engine.py","src/backend/core/planner.py","src/backend/core/semantic.py"]},
        "config":     {"required_files": ["src/backend/config/__init__.py","src/backend/config/settings.py","src/backend/config/logging.py"]},
    },

    "frontend": {
        "html": {"file": "src/frontend/index.html", "must_contain": ["v4.2","web_connector.js","updater.js","platform.js"]},
        "css":  {"required_files": ["src/frontend/css/theme.css"]},
        "js":   {"required_files": [
            "src/frontend/js/api.js","src/frontend/js/app.js","src/frontend/js/dashboard.js",
            "src/frontend/js/engines.js","src/frontend/js/history.js","src/frontend/js/modes.js",
            "src/frontend/js/pipeline.js","src/frontend/js/updater.js",
            "src/frontend/js/web_connector.js","src/frontend/js/platform.js",
        ]},
    },

    "data": {
        "required_files": ["data/acquirers.json","data/domains.json"],
        "directories": ["data","data/cache","data/backups","logs","output"],
    },

    "root_files": {"required": [
        "LAUNCH.bat","claire-bootstrap.html","requirements.txt",
        "README.md",".env.example","Dockerfile",
    ]},

    "capabilities": {
        "web_fetch":          {"desc": "Backend can make outbound HTTP requests",         "deps": ["src/backend/connectors/web_fetcher.py"], "test": "/api/proxy/ping"},
        "self_update":        {"desc": "Platform can check for and apply updates",        "deps": ["src/backend/api/routes_update.py","src/frontend/js/updater.js"], "test": "/api/update/status"},
        "self_aware":         {"desc": "Platform knows its own completion state and gap",  "deps": ["src/backend/platform/manifest.py","src/backend/platform/resolver.py","src/backend/api/routes_platform.py"], "test": "/api/platform/status"},
        "pipeline_evaluation":{"desc": "Full 24-engine evaluation pipeline",              "deps": ["src/backend/orchestrator/pipeline.py","src/backend/engines/__init__.py"], "test": "/evaluate"},
        "web_proxy":          {"desc": "Frontend can access web through backend proxy",   "deps": ["src/backend/api/routes_proxy.py","src/frontend/js/web_connector.js"], "test": "/api/proxy/ping"},
        "syntalion_bridge":   {"desc": "MasterPass bridge validates readiness",           "deps": ["src/backend/bridge/masterpass.py"], "test": "/evaluate"},
        "self_healing_launch":{"desc": "LAUNCH.bat finds Python, creates venv, installs", "deps": ["LAUNCH.bat","requirements.txt"]},
        "browser_bootstrap":  {"desc": "claire-bootstrap.html provides browser launcher", "deps": ["claire-bootstrap.html"]},
    },
}


def _file_exists(path: str) -> bool:
    return Path(path).exists()

def _file_contains(path: str, markers: List[str]) -> Tuple[bool, List[str]]:
    missing = []
    try:
        content = Path(path).read_text(encoding="utf-8", errors="replace")
        for m in markers:
            if m not in content:
                missing.append(m)
        return len(missing) == 0, missing
    except Exception:
        return False, markers

def _check_python() -> Dict[str, Any]:
    v = sys.version_info
    return {"installed": True, "version": f"{v.major}.{v.minor}.{v.micro}",
            "meets_minimum": v >= (3, 10), "executable": sys.executable}

def _check_packages(required: List[str]) -> Dict[str, Any]:
    installed, missing = [], []
    for pkg in required:
        try:
            importlib.import_module(pkg.replace("-", "_").split("[")[0])
            installed.append(pkg)
        except ImportError:
            missing.append(pkg)
    return {"installed": installed, "missing": missing, "all_present": len(missing) == 0}

def _check_venv() -> Dict[str, Any]:
    vp = Path(".venv")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    return {"exists": vp.exists(), "active": in_venv}

def _check_server() -> Dict[str, Any]:
    try:
        import urllib.request
        resp = urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=3)
        data = json.loads(resp.read().decode())
        return {"running": True, "healthy": data.get("status") == "healthy", "data": data}
    except Exception:
        return {"running": False, "healthy": False}

def _check_web() -> Dict[str, Any]:
    try:
        import urllib.request
        urllib.request.urlopen("https://httpbin.org/get", timeout=5)
        return {"online": True}
    except Exception as e:
        return {"online": False, "error": str(e)}


def current_state(root: str = ".") -> Dict[str, Any]:
    """Live scan — what exists, what works, what's broken."""
    rp = Path(root)
    state = {"scanned_at": datetime.now().isoformat(), "root": str(rp.resolve()), "version": "unknown"}

    vf = rp / "data" / "version.json"
    if vf.exists():
        try: state["version"] = json.loads(vf.read_text()).get("version", "unknown")
        except Exception: pass

    state["environment"] = {
        "python": _check_python(), "venv": _check_venv(),
        "packages": _check_packages(TARGET_STATE["environment"]["pip_packages"]["required"]),
    }

    def scan_files(file_list):
        present = [f for f in file_list if (rp / f).exists()]
        missing = [f for f in file_list if not (rp / f).exists()]
        return {"present": present, "missing": missing, "complete": len(missing) == 0,
                "pct": round(len(present) / max(len(file_list), 1) * 100, 1)}

    backend_state = {}
    for section, spec in TARGET_STATE["backend"].items():
        if "required_files" in spec:
            backend_state[section] = scan_files(spec["required_files"])
        elif "file" in spec:
            exists = _file_exists(str(rp / spec["file"]))
            ok, mm = (True, []) if not exists else _file_contains(str(rp / spec["file"]), spec.get("must_contain", []))
            backend_state[section] = {"exists": exists, "content_valid": ok, "missing_markers": mm}
    state["backend"] = backend_state

    frontend_state = {}
    for section, spec in TARGET_STATE["frontend"].items():
        if "required_files" in spec:
            frontend_state[section] = scan_files(spec["required_files"])
        elif "file" in spec:
            exists = _file_exists(str(rp / spec["file"]))
            ok, mm = (True, []) if not exists else _file_contains(str(rp / spec["file"]), spec.get("must_contain", []))
            frontend_state[section] = {"exists": exists, "content_valid": ok, "missing_markers": mm}
    state["frontend"] = frontend_state

    state["data"] = {
        "files": scan_files(TARGET_STATE["data"]["required_files"]),
        "directories": {d: (rp / d).is_dir() for d in TARGET_STATE["data"]["directories"]},
    }
    state["root_files"] = scan_files(TARGET_STATE["root_files"]["required"])
    state["runtime"] = {"server": _check_server(), "web": _check_web()}
    return state


def gap_analysis(root: str = ".") -> Dict[str, Any]:
    """Diff target vs current. Returns gaps + resolution paths."""
    cur = current_state(root)
    rp = Path(root)
    gaps, resolved = [], []

    # Environment
    py = cur["environment"]["python"]
    if not py.get("meets_minimum"):
        gaps.append({"cat": "env", "comp": "python", "sev": "critical",
                     "desc": f"Python {py.get('version','missing')} < 3.10",
                     "fix": {"type": "manual", "url": TARGET_STATE["environment"]["python"]["resolution"]}})
    else:
        resolved.append({"comp": "python", "status": f"v{py['version']}"})

    for pkg in cur["environment"]["packages"].get("missing", []):
        gaps.append({"cat": "env", "comp": f"pip:{pkg}", "sev": "high",
                     "desc": f"Package '{pkg}' missing", "fix": {"type": "auto", "cmd": f"pip install {pkg}"}})

    # Files
    def check_files(section_state, category):
        for name, info in section_state.items():
            if isinstance(info, dict) and "missing" in info and info["missing"]:
                for f in info["missing"]:
                    gaps.append({"cat": category, "comp": name, "sev": "high",
                                 "desc": f"Missing: {f}", "file": f,
                                 "fix": {"type": "auto", "method": "generate_file"}})
            elif isinstance(info, dict) and (info.get("complete") or info.get("exists")):
                if not info.get("content_valid", True):
                    gaps.append({"cat": category, "comp": name, "sev": "medium",
                                 "desc": f"Needs update: markers {info.get('missing_markers',[])}",
                                 "fix": {"type": "auto", "method": "update_file"}})
                else:
                    resolved.append({"comp": f"{category}/{name}", "status": "complete"})

    check_files(cur.get("backend", {}), "backend")
    check_files(cur.get("frontend", {}), "frontend")

    for f in cur.get("root_files", {}).get("missing", []):
        gaps.append({"cat": "root", "comp": f, "sev": "medium",
                     "desc": f"Missing root file: {f}", "fix": {"type": "auto", "method": "generate_file"}})

    for d, exists in cur.get("data", {}).get("directories", {}).items():
        if not exists:
            gaps.append({"cat": "data", "comp": d, "sev": "low",
                         "desc": f"Missing dir: {d}", "fix": {"type": "auto", "method": "create_dir"}})

    # Capabilities
    cap_status = {}
    for cname, cspec in TARGET_STATE["capabilities"].items():
        deps_met = all(_file_exists(str(rp / d)) for d in cspec.get("deps", []))
        cap_status[cname] = {"desc": cspec["desc"], "satisfied": deps_met, "deps": cspec.get("deps", [])}
        if not deps_met:
            md = [d for d in cspec.get("deps", []) if not _file_exists(str(rp / d))]
            gaps.append({"cat": "capability", "comp": cname, "sev": "high",
                         "desc": f"'{cname}' unsatisfied — missing: {md}",
                         "fix": {"type": "auto", "method": "generate_capability_deps", "files": md}})

    total = len(gaps) + len(resolved)
    pct = round(len(resolved) / max(total, 1) * 100, 1)
    auto = [g for g in gaps if g.get("fix", {}).get("type") == "auto"]

    return {
        "target_version": TARGET_STATE["version"],
        "current_version": cur.get("version", "unknown"),
        "scanned_at": cur["scanned_at"],
        "completion_pct": pct,
        "total_gaps": len(gaps), "total_resolved": len(resolved),
        "auto_resolvable": len(auto),
        "by_severity": {s: len([g for g in gaps if g["sev"] == s]) for s in ["critical","high","medium","low"]},
        "gaps": gaps, "resolved": resolved, "capabilities": cap_status,
        "current_state": cur,
    }
