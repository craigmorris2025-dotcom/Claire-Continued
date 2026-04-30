from fastapi import FastAPI
from .router import router

app = FastAPI(title="Claire API")
app.include_router(router)


from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

app.mount("/static", StaticFiles(directory="src/frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    with open("src/frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()
