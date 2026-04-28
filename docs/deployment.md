# Claire Syntalion — Deployment Guide

## Quick Start

1. **Double-click `LAUNCH.bat`** — creates venv, installs deps, runs health checks, starts server
2. Open http://localhost:8000/ui in your browser

## Manual Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run health checks
python -m src.backend health

# Start the server
python -m src.backend serve
```

## CLI Commands

```bash
python -m src.backend serve       # Start web server
python -m src.backend health      # Run all health checks
python -m src.backend run "text"  # Quick pipeline evaluation
python -m src.backend history     # View run history
python -m src.backend interactive # REPL mode
```

## Environment Variables

All variables use the `CLAIRE_` prefix. See `.env.example` for defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| CLAIRE_ENV | development | Environment name |
| CLAIRE_HOST | 0.0.0.0 | Server bind address |
| CLAIRE_PORT | 8000 | Server port |
| CLAIRE_DB_PATH | data/claire.db | SQLite database path |
| CLAIRE_DATA_DIR | data | Data directory |
| CLAIRE_LOG_DIR | logs | Log directory |
| CLAIRE_OUTPUT_DIR | output | Output directory |
| CLAIRE_DEFAULT_MODE | deterministic | Default operating mode |
| CLAIRE_CORS_ORIGINS | * | CORS allowed origins |

## Docker

```bash
docker build -t claire-syntalion .
docker run -p 8000:8000 claire-syntalion
```

## Project Structure

```
claire-syntalion/
├── src/backend/       # Python backend (FastAPI + CLAIRE engine)
├── src/frontend/      # HTML/CSS/JS SPA
├── data/              # JSON data files + SQLite DB
├── tests/             # pytest test suite
├── docs/              # Documentation
├── output/            # Pipeline output files
├── logs/              # Application logs
├── LAUNCH.bat         # Double-click launcher (Windows)
└── requirements.txt   # Python dependencies
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Set CLAIRE_PORT in .env |
| Module not found | Ensure you activated the venv |
| Database locked | Stop other instances |
| 404 on /ui | Verify src/frontend/index.html exists |
