#!/usr/bin/env python
r"""
Claire web-download updater bootstrap.

Usage:
    python tools\claire_update_from_url.py --url "file:///C:/path/claire_update.zip" --dry-run
    python tools\claire_update_from_url.py --url "https://approved.example.com/claire_update.zip" --yes
    python tools\claire_update_from_url.py --rollback data\backups\claire_web_update_backup_YYYYMMDD_HHMMSS_update.zip
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def find_project_root(start: Optional[Path] = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in [start] + list(start.parents):
        if (candidate / "main.py").exists() and (candidate / "src" / "claire").exists():
            return candidate
    raise SystemExit("Could not detect Claire project root.")


def ensure_import_path(root: Path) -> None:
    for path in (root / "src", root):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download, verify, install, and audit a Claire update package.")
    parser.add_argument("--url", help="Approved update package URL or local file path.")
    parser.add_argument("--expected-sha256", default="", help="Optional expected SHA256 for the package zip.")
    parser.add_argument("--root", default="", help="Claire project root. Defaults to auto-detect.")
    parser.add_argument("--dry-run", action="store_true", help="Download and verify, but do not install.")
    parser.add_argument("--yes", "-y", action="store_true", help="Install without interactive confirmation.")
    parser.add_argument("--no-backup", action="store_true", help="Install without creating a rollback backup.")
    parser.add_argument("--rollback", default="", help="Restore from a rollback backup zip.")
    parser.add_argument("--status", action="store_true", help="Show updater health and rollback readiness.")
    parser.add_argument("--list-rollbacks", action="store_true", help="List available rollback backups.")
    parser.add_argument("--validate-rollback", default="", help="Validate a rollback backup zip without restoring it.")
    parser.add_argument("--run-baseline", action="store_true", help="Run Claire baseline validation after install.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve() if args.root else find_project_root()
    ensure_import_path(root)

    from runtime_core.updater.package_downloader import PackageDownloader
    from runtime_core.updater.package_installer import PackageInstaller
    from runtime_core.updater.package_verifier import PackageVerifier
    from runtime_core.updater.rollback_manager import RollbackManager
    from runtime_core.updater.update_audit_log import UpdateAuditLog
    from runtime_core.updater.update_health import UpdaterHealth

    audit = UpdateAuditLog(root)
    rollback_manager = RollbackManager(root)

    if args.status:
        result = UpdaterHealth(root).status()
        print(json.dumps(result, indent=2))
        return 0 if result.get("status") in {"success", "partial"} else 1

    if args.list_rollbacks:
        print(json.dumps(rollback_manager.list_backups(), indent=2))
        return 0

    if args.validate_rollback:
        result = rollback_manager.validate_backup(Path(args.validate_rollback).resolve())
        print(json.dumps(result, indent=2))
        return 0 if result.get("valid") else 1

    if args.rollback:
        result = rollback_manager.restore(Path(args.rollback).resolve())
        log_path = audit.write("rollback_restore", result)
        print(json.dumps(result, indent=2))
        print(f"Rollback audit log: {log_path}")
        return 0

    if not args.url:
        raise SystemExit("--url is required unless --rollback is used.")

    downloader = PackageDownloader(root)
    verifier = PackageVerifier()
    installer = PackageInstaller(root)

    download = downloader.download(args.url)
    verification = verifier.verify(Path(download["package_path"]), expected_sha256=args.expected_sha256)
    plan = installer.install(Path(download["package_path"]), dry_run=True)

    print("Claire Web Download Updater")
    print("===========================")
    print(f"Source URL:   {args.url}")
    print(f"Package:      {download['package_path']}")
    print(f"SHA256:       {download['sha256']}")
    print(f"Update:       {verification['manifest']['update_name']} {verification['manifest']['version']}")
    print(f"Files:        {verification['file_count']}")
    print("")
    for item in plan["plan"]:
        print(f"- {item['action']}: {item['target']}")

    if args.dry_run:
        log_path = audit.write("web_update_dry_run", {"download": download, "verification": verification, "plan": plan})
        print("")
        print(f"Dry run complete. Audit log: {log_path}")
        return 0

    if not args.yes:
        response = input("Install this Claire update? Type YES to continue: ").strip()
        if response != "YES":
            audit.write("web_update_cancelled", {"download": download, "verification": verification})
            raise SystemExit("Update cancelled.")

    install = installer.install(Path(download["package_path"]), dry_run=False, no_backup=args.no_backup)
    baseline = None
    if args.run_baseline:
        from tools.run_claire_baseline import BaselineRunner
        baseline_code = BaselineRunner().run()
        baseline = {"status": "success" if baseline_code == 0 else "failed", "exit_code": baseline_code}
    log_path = audit.write("web_update_installed", {
        "download": download,
        "verification": verification,
        "install": install,
        "baseline": baseline,
    })

    print("")
    print("Claire update installed.")
    print(f"Installed files: {len(install['installed_files'])}")
    if install.get("backup_path"):
        print(f"Rollback backup: {install['backup_path']}")
    if baseline:
        print(f"Baseline: {baseline['status']}")
    print(f"Audit log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
