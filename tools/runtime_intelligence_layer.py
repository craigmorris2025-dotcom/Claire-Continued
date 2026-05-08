#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def load(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return {"error": repr(exc)}

def main() -> int:
    runtime = ROOT / "data" / "runtime"
    manifest = load(runtime / "runtime_manifest.json") or {}
    modules = load(runtime / "active_module_registry.json") or {}
    files = manifest.get("files", [])
    category_counts = manifest.get("category_counts", {})
    dormant_candidates = [
        f["path"] for f in files
        if f.get("category") == "active_runtime"
        and any(x in f["path"] for x in ["proof", "demo", "maturity", "placeholder"])
    ][:100]
    payload = {
        "layer": "runtime_intelligence_layer",
        "version": "v16.35",
        "created_at": datetime.now().isoformat(),
        "status": "available",
        "category_counts": category_counts,
        "active_module_count": modules.get("module_count"),
        "failed_module_count": modules.get("failed_count"),
        "dormant_or_review_candidates": dormant_candidates,
        "recommendations": [
            "keep protected runtime spine locked",
            "validate installers before execution",
            "review dormant candidates before archiving",
            "keep generated exports outside runtime decisions",
        ],
    }
    out = runtime / "runtime_intelligence.json"
    runtime.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"layer": payload["layer"], "status": payload["status"], "candidate_count": len(dormant_candidates)}, indent=2))
    print(f"\nRuntime intelligence written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
