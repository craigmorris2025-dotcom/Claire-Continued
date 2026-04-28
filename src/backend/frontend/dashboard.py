from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """
    Serves the Claire Syntalion enhanced dashboard.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_path, "claire-syntalion-enhanced.html")

    if not os.path.exists(html_path):
        return "<h1>Dashboard file not found</h1>"

    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
