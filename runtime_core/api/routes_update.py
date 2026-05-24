from fastapi import APIRouter

from runtime_core.platform.update_manager import UpdateManager

router = APIRouter()
updater = UpdateManager()

@router.get("/update/check")
def check_updates():
    """
    Returns whether update packages are available.
    """
    return updater.check_for_updates()

@router.post("/update/prepare")
def prepare_update(payload: dict):
    """
    Stages an update package for installation.
    """
    package = payload.get("package")
    if not package:
        return {"error": "Missing 'package' field"}

    return updater.prepare_update(package)

@router.post("/update/install")
def install_update(payload: dict):
    """
    Installs a staged update with zero downtime.
    """
    package = payload.get("package")
    if not package:
        return {"error": "Missing 'package' field"}

    return updater.install_update(package)
