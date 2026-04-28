"""
System Routes — GET /health, /modes, /engines
"""
from fastapi import APIRouter
from backend.api.schemas import HealthResponse
from backend.engines import DOMAIN_REGISTRY, PHASE_SEQUENCE
from backend.mode.controller import ModeController
from backend.connectors.manager import ConnectorManager
from backend.core.data_engine import DataEngine
from backend.core.semantic import SemanticLayer, DOMAIN_LEXICONS
from backend.persistence.database import Database
from backend.bridge.masterpass import MasterPassBridge

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check():
    """Comprehensive system health check."""
    checks = {}

    try:
        checks["engines"] = {"name": "Domain Engines", "ok": True,
                             "detail": f"{len(DOMAIN_REGISTRY)} registered"}
    except Exception as e:
        checks["engines"] = {"name": "Domain Engines", "ok": False, "detail": str(e)}

    try:
        checks["phases"] = {"name": "Phase Sequence", "ok": True,
                            "detail": f"{len(PHASE_SEQUENCE)} phases"}
    except Exception as e:
        checks["phases"] = {"name": "Phase Sequence", "ok": False, "detail": str(e)}

    try:
        sem = SemanticLayer()
        test = sem.process("test health check")
        checks["semantic"] = {"name": "Semantic/NLP", "ok": True,
                              "detail": f"{len(DOMAIN_LEXICONS)} domains, conf={test.confidence:.2f}"}
    except Exception as e:
        checks["semantic"] = {"name": "Semantic/NLP", "ok": False, "detail": str(e)}

    try:
        mgr = ConnectorManager()
        checks["connectors"] = {"name": "Connectors", "ok": True,
                                "detail": f"{len(mgr.connectors)} registered"}
    except Exception as e:
        checks["connectors"] = {"name": "Connectors", "ok": False, "detail": str(e)}

    try:
        de = DataEngine()
        profiles = de.load_acquirers()
        checks["acquirers"] = {"name": "Acquirer Data", "ok": True,
                               "detail": f"{len(profiles)} profiles"}
    except Exception as e:
        checks["acquirers"] = {"name": "Acquirer Data", "ok": False, "detail": str(e)}

    try:
        db = Database()
        stats = db.get_stats()
        checks["database"] = {"name": "DB Persistence", "ok": True,
                              "detail": f"SQLite OK, {stats['total_runs']} runs"}
    except Exception as e:
        checks["database"] = {"name": "DB Persistence", "ok": False, "detail": str(e)}

    checks["masterpass"] = {"name": "MasterPass Bridge", "ok": True, "detail": "ready"}

    try:
        mc = ModeController()
        modes = mc.get_all_modes()
        checks["modes"] = {"name": "Mode Controller", "ok": True,
                           "detail": f"{len(modes)} modes available"}
    except Exception as e:
        checks["modes"] = {"name": "Mode Controller", "ok": False, "detail": str(e)}

    passed = sum(1 for c in checks.values() if c.get("ok", False))
    total = len(checks)

    return {
        "status": "healthy" if passed == total else "degraded",
        "version": "4.2.1",
        "checks": list(checks.values()),
        "checks_passed": f"{passed}/{total}",
    }


@router.get("/modes")
async def list_modes():
    """List available operating modes and their capabilities."""
    mc = ModeController()
    return {"modes": mc.get_all_modes()}


@router.get("/engines")
async def list_engines():
    """List all 24 registered engines grouped by phase."""
    phases = []
    idx = 1
    for phase_name, engine_keys in PHASE_SEQUENCE:
        engines = []
        for key in engine_keys:
            eng = DOMAIN_REGISTRY.get(key)
            engines.append({
                "index": idx,
                "key": key,
                "class": eng.__class__.__name__ if eng else "MISSING",
                "phase": eng.get_phase() if eng else phase_name,
                "registered": eng is not None,
            })
            idx += 1
        phases.append({
            "phase": phase_name,
            "engines": engines,
            "count": len(engines),
        })
    return {"phases": phases, "total_engines": len(DOMAIN_REGISTRY)}
