from __future__ import annotations

"""
Claire API Server Compatibility Owner.

This module intentionally delegates FastAPI application construction to
runtime_core.app.create_app. It replaces a broken legacy inline-dashboard mutation
file with a clean import-safe ASGI entry point.

No runtime truth mutation, dashboard HTML patching, network activity, or
automatic update behavior is performed here.
"""

from typing import Any

from runtime_core.app import create_app


app = create_app()


def get_app() -> Any:
    """Return the Claire FastAPI ASGI application."""
    return app


def build_server_status() -> dict[str, Any]:
    return {
        "status": "ready",
        "ready": True,
        "app_owner": "runtime_core.app.create_app",
        "compatibility_module": "runtime_core.api.server",
        "runtime_truth_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("runtime_core.api.server:app", host="127.0.0.1", port=8000, reload=True)
