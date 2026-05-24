"""Dashboard-facing updater workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from runtime_core.updater.package_downloader import PackageDownloader
from runtime_core.updater.package_installer import PackageInstaller
from runtime_core.updater.package_verifier import PackageVerifier
from runtime_core.updater.rollback_manager import RollbackManager
from runtime_core.updater.update_audit_log import UpdateAuditLog
from runtime_core.updater.update_health import UpdaterHealth


class DashboardUpdateWorkflow:
    """Preview and install approved update zips from the dashboard."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def status(self) -> Dict[str, Any]:
        health = UpdaterHealth(self.project_root).status()
        health["dashboard_workflow"] = "v5.68"
        health["dashboard_install_enabled"] = True
        return health

    def preview(self, url: str, expected_sha256: str = "") -> Dict[str, Any]:
        download, verification, plan = self._prepare(url, expected_sha256)
        log_path = UpdateAuditLog(self.project_root).write(
            "dashboard_update_preview",
            {"download": download, "verification": verification, "plan": plan},
        )
        return {
            "status": "success",
            "mode": "preview",
            "download": download,
            "verification": verification,
            "plan": plan,
            "audit_log": str(log_path),
        }

    def install(
        self,
        url: str,
        expected_sha256: str = "",
        confirm: bool = False,
        run_baseline: bool = False,
    ) -> Dict[str, Any]:
        if not confirm:
            return {
                "status": "confirmation_required",
                "message": "Set confirm=true to install an approved update package.",
            }
        download, verification, _ = self._prepare(url, expected_sha256)
        install = PackageInstaller(self.project_root).install(Path(download["package_path"]), dry_run=False)
        baseline = None
        if run_baseline:
            from tools.run_claire_baseline import BaselineRunner

            code = BaselineRunner().run()
            baseline = {"status": "success" if code == 0 else "failed", "exit_code": code}
        log_path = UpdateAuditLog(self.project_root).write(
            "dashboard_update_installed",
            {"download": download, "verification": verification, "install": install, "baseline": baseline},
        )
        return {
            "status": "success",
            "mode": "install",
            "download": download,
            "verification": verification,
            "install": install,
            "baseline": baseline,
            "audit_log": str(log_path),
        }

    def rollbacks(self) -> Dict[str, Any]:
        return RollbackManager(self.project_root).list_backups()

    def _prepare(self, url: str, expected_sha256: str) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        if not url:
            raise ValueError("Update URL is required.")
        download = PackageDownloader(self.project_root).download(url)
        verification = PackageVerifier().verify(Path(download["package_path"]), expected_sha256=expected_sha256)
        plan = PackageInstaller(self.project_root).install(Path(download["package_path"]), dry_run=True)
        return download, verification, plan
