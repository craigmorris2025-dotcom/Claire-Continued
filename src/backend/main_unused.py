from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from .api.routes_update import router as update_router
from .api.routes_command import router as command_router

app = FastAPI()

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

app.include_router(update_router, prefix="/api")
app.include_router(command_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = frontend_dir / "index.html"
    return index_path.read_text(encoding="utf-8")
from .api.routes_dashboard import router as dashboard_router
app.include_router(dashboard_router, prefix='/api')
