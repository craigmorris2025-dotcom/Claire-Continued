from __future__ import annotations

import argparse
import json

from .service import GovernedCampaignSchedulerService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire governed campaign scheduler")
    sub = parser.add_subparsers(dest="command", required=True)

    schedule = sub.add_parser("schedule")
    schedule.add_argument("--campaign-id", required=True)
    schedule.add_argument("--cadence-minutes", type=int, default=1440)
    schedule.add_argument("--disabled", action="store_true")

    run = sub.add_parser("run-due")
    run.add_argument("--limit", type=int, default=None)

    sub.add_parser("list")
    sub.add_parser("lock-status")

    reports = sub.add_parser("reports")
    reports.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    service = GovernedCampaignSchedulerService()

    if args.command == "schedule":
        result = service.set_schedule(
            campaign_id=args.campaign_id,
            cadence_minutes=args.cadence_minutes,
            enabled=not args.disabled,
        )
    elif args.command == "run-due":
        result = service.run_due_once_sync(limit=args.limit)
    elif args.command == "list":
        result = {"schedules": service.list_schedules()}
    elif args.command == "lock-status":
        result = service.lock_status()
    elif args.command == "reports":
        result = {"reports": service.list_reports(limit=args.limit)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
