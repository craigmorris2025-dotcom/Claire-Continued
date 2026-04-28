"""
Claire Syntalion Auto-Update Engine — v4.2
"""

import json
import pathlib
import logging
import aiohttp
import zipfile

logger = logging.getLogger("claire.update")

BASE_DIR = pathlib.Path(__file__).resolve().parents[3]
VERSION_FILE = BASE_DIR / "version.json"
UPDATE_URL = BASE_DIR / "updates" / "latest.json"  # Local updates
PACKAGE_DIR = BASE_DIR / "updates"


def load_local_version():
    if not VERSION_FILE.exists():
        return {"version": "0.0.0"}
    return json.loads(VERSION_FILE.read_text())


def save_local_version(data):
    VERSION_FILE.write_text(json.dumps(data, indent=2))


async def fetch_remote_metadata():
    if UPDATE_URL.exists():
        return json.loads(UPDATE_URL.read_text())
    return None


async def download_update(package_name):
    pkg = PACKAGE_DIR / package_name
    if pkg.exists():
        return pkg
    return None


def apply_update(zip_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(BASE_DIR)


async def check_for_updates():
    logger.info("Checking for updates...")

    local = load_local_version()
    remote = await fetch_remote_metadata()

    if not remote:
        logger.warning("No update metadata found.")
        return False

    if remote["version"] == local["version"]:
        logger.info("Already up to date.")
        return False

    logger.info(f"New version available: {remote['version']}")

    pkg = await download_update(remote["package"])
    if not pkg:
        logger.error("Update package not found.")
        return False

    apply_update(pkg)
    save_local_version(remote)

    logger.info(f"Updated to version {remote['version']}")
    return True
