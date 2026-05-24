from __future__ import annotations

from fastapi import FastAPI


def create_backend_app() -> FastAPI:
    """Return the canonical FastAPI app through the backend boundary."""
    from runtime_core.app import create_app

    return create_app()


app = create_backend_app()
