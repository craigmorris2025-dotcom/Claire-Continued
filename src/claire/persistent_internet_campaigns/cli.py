from __future__ import annotations

import argparse
import json

from .service import PersistentInternetCampaignService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire persistent internet campaigns")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--query", required=True)
    create.add_argument("--url", action="append", default=[])
    create.add_argument("--cadence", default="manual")
    create.add_argument("--max-results", type=int, default=5)

    refresh = sub.add_parser("refresh")
    refresh.add_argument("--campaign-id", required=True)

    sub.add_parser("list")

    reports = sub.add_parser("reports")
    reports.add_argument("--campaign-id", default=None)

    args = parser.parse_args()
    service = PersistentInternetCampaignService()

    if args.command == "create":
        result = service.create_campaign(
            name=args.name,
            query=args.query,
            urls=args.url,
            cadence=args.cadence,
            max_results=args.max_results,
        )
    elif args.command == "refresh":
        result = service.refresh_campaign_sync(args.campaign_id)
    elif args.command == "list":
        result = {"campaigns": service.list_campaigns()}
    elif args.command == "reports":
        result = {"reports": service.list_reports(args.campaign_id)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
