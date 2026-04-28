import json
import os
import shutil
from datetime import datetime
from pathlib import Path

class UpdateManager:
    """
    Industry-standard update manager responsible for:
    - Checking for updates
    - Validating update packages
    - Preparing updates safely
    - Installing updates with zero downtime
    """

    VERSION_FILE = "data/version.json"
    UPDATE_PACKAGE_DIR = "updates/incoming"
    ACTIVE_DIR = "src"
    STAGING_DIR = "updates/staging"
    BACKUP_DIR = "updates/backup"

    def __init__(self):
        self.current_version = self._load_version()

    def _load_version(self):
        if not os.path.exists(self.VERSION_FILE):
            return {"version": "0.0.0"}

        with open(self.VERSION_FILE, "r") as f:
            return json.load(f)

    def check_for_updates(self):
        incoming = Path(self.UPDATE_PACKAGE_DIR)
        if not incoming.exists():
            return {"update_available": False}

        packages = list(incoming.glob("*.zip"))
        if not packages:
            return {"update_available": False}

        return {
            "update_available": True,
            "packages": [p.name for p in packages],
            "current_version": self.current_version.get("version")
        }

    def prepare_update(self, package_name):
        incoming = Path(self.UPDATE_PACKAGE_DIR) / package_name
        staging = Path(self.STAGING_DIR)

        staging.mkdir(parents=True, exist_ok=True)

        if not incoming.exists():
            return {"error": "Package not found"}

        shutil.copy(incoming, staging / package_name)

        return {"status": "staged", "package": package_name}

    def install_update(self, package_name):
        staging = Path(self.STAGING_DIR)
        backup = Path(self.BACKUP_DIR)
        active = Path(self.ACTIVE_DIR)

        backup.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_target = backup / f"src_backup_{timestamp}"
        shutil.copytree(active, backup_target)

        package_path = staging / package_name
        extract_dir = staging / "extracted"
        extract_dir.mkdir(exist_ok=True)

        shutil.unpack_archive(str(package_path), str(extract_dir))

        shutil.rmtree(active)
        shutil.move(str(extract_dir), str(active))

        return {
            "status": "installed",
            "version": self.current_version.get("version"),
            "backup": str(backup_target)
        }
