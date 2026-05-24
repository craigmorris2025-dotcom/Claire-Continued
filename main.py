import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(ROOT, ".env"))
except Exception:
    pass

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if os.path.exists(SRC) and SRC not in sys.path:
    sys.path.append(SRC)

from runtime_core.app import create_app

app = create_app()


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("PLATFORM_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("PLATFORM_PORT", "8000"))
    except ValueError:
        port = 8000
    uvicorn.run("main:app", host=host, port=port, reload=True)
