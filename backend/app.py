from __future__ import annotations

from fastapi import FastAPI


def create_backend_app() -> FastAPI:
    """Return the canonical Claire FastAPI app through the backend boundary."""
    from claire.app import create_app

    return create_app()


app = create_backend_app()
