"""
Structured Logging Configuration.
Sets up file + console handlers with ISO timestamps.
"""
import logging
import os
import sys
from datetime import datetime
from backend.config.settings import get_settings


def setup_logging() -> logging.Logger:
    """Configure application-wide logging."""
    settings = get_settings()

    # Ensure log directory
    os.makedirs(settings.log_dir, exist_ok=True)

    # Root logger
    root = logging.getLogger("claire")
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Clear existing handlers
    root.handlers.clear()

    # Format
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    console.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    root.addHandler(console)

    # File handler
    log_file = os.path.join(
        settings.log_dir,
        f"claire_{datetime.utcnow().strftime('%Y%m%d')}.log"
    )
    try:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        root.addHandler(fh)
    except (OSError, PermissionError):
        root.warning(f"Could not open log file: {log_file}")

    # Quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    root.info(f"Logging initialized: level={settings.log_level}, env={settings.env}")
    return root
