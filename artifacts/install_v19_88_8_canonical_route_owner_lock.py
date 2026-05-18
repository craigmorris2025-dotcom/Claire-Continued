#!/usr/bin/env python3
"""
Claire Syntalion v19.88.8
Canonical Route Owner Lock + Cockpit Connection Proof

Run from Claire project root:
    python install_v19_88_8_canonical_route_owner_lock.py
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
APP = ROOT / "claire" / "app.py"
VERSION = ROOT / "version.json"

START = "# === CLAIRE_V19_88_8_CANONICAL_ROUTE_OWNER_LOCK_START ==="
END = "# === CLAIRE_V19_88_8_CANONICAL_ROUTE_OWNER_LOCK_END ==="

BLOCK = r