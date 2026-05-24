from __future__ import annotations

import argparse
import json

from .service import InternetRuntimeStabilityService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire internet runtime stability")
    sub = parser.add_subparsers(dest="command", required=True)

    refresh = sub.add_parser("refresh-campaign")
    refresh.add_argument("--campaign-id", required=True)

    due = sub.add_parser("run-due")
    due.add_argument("--limit", type=int, default=None)

    sub.add_parser("health")

    failures = sub.add_parser("failures")
    failures.add_argument("--limit", type=int, default=50)

    reports = sub.add_parser("reports")
    reports.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    service = InternetRuntimeStabilityService()

    if args.command == "refresh-campaign":
        result = service.refresh_campaign_with_recovery_sync(args.campaign_id) if hasattr(service, "refresh_campaign_with_recovery_sync") else _run(service.refresh_campaign_with_recovery(args.campaign_id))
    elif args.command == "run-due":
        result = _run(service.run_scheduler_due_with_recovery(limit=args.limit))
    elif args.command == "health":
        result = service.health()
    elif args.command == "failures":
        result = {"failures": service.list_failures(limit=args.limit)}
    elif args.command == "reports":
        result = {"reports": service.list_reports(limit=args.limit)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


def _run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    main()
