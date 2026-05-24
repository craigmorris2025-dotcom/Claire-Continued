"""
Platform Self-Awareness API — exposes completion state, gap analysis, and auto-resolution.
"""

from fastapi import APIRouter

# ✅ FIXED IMPORTS
from runtime_core.platform.manifest import current_state, gap_analysis, TARGET_STATE
from runtime_core.platform.resolver import resolve_all, resolve_one


router = APIRouter(tags=["Platform"])


@router.get("/api/platform/status")
async def platform_status():
    """Full platform completion status — what's done, what's missing, what's next."""
    analysis = gap_analysis()

    return {
        "target_version": analysis.get("target_version"),
        "current_version": analysis.get("current_version"),
        "completion_pct": analysis.get("completion_pct"),
        "total_gaps": analysis.get("total_gaps"),
        "auto_resolvable": analysis.get("auto_resolvable"),
        "by_severity": analysis.get("by_severity"),
        "capabilities": analysis.get("capabilities"),
        "gaps": analysis.get("gaps"),
        "resolved": analysis.get("resolved"),
    }


@router.get("/api/platform/target")
async def platform_target():
    """What the fully-complete platform looks like."""
    return TARGET_STATE


@router.get("/api/platform/current")
async def platform_current():
    """Live scan of current state."""
    return current_state()


@router.post("/api/platform/resolve")
async def platform_resolve(auto_only: bool = True, dry_run: bool = False):
    """Auto-resolve all gaps (or just auto-resolvable ones)."""
    return resolve_all(auto_only=auto_only, dry_run=dry_run)


@router.post("/api/platform/resolve/{component}")
async def platform_resolve_one(component: str, dry_run: bool = False):
    """Resolve a specific gap by component name."""
    return resolve_one(component, dry_run=dry_run)
