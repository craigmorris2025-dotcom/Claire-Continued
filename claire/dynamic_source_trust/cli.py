from __future__ import annotations

import argparse
import json

from .service import DynamicSourceTrustService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire dynamic source trust")
    sub = parser.add_subparsers(dest="command", required=True)

    event = sub.add_parser("event")
    event.add_argument("--domain", required=True)
    event.add_argument("--event-type", required=True)
    event.add_argument("--evidence-id", default=None)
    event.add_argument("--confidence", type=float, default=0.0)
    event.add_argument("--reason", default="")

    quarantine = sub.add_parser("quarantine")
    quarantine.add_argument("--domain", required=True)
    quarantine.add_argument("--reason", default="Manual quarantine")

    release = sub.add_parser("release")
    release.add_argument("--domain", required=True)
    release.add_argument("--reason", default="Manual release")

    sub.add_parser("profiles")

    events = sub.add_parser("events")
    events.add_argument("--domain", default=None)
    events.add_argument("--limit", type=int, default=100)

    args = parser.parse_args()
    service = DynamicSourceTrustService()

    if args.command == "event":
        result = service.record_event(
            domain=args.domain,
            event_type=args.event_type,
            evidence_id=args.evidence_id,
            confidence=args.confidence,
            reason=args.reason,
        )
    elif args.command == "quarantine":
        result = service.quarantine_source(args.domain, reason=args.reason)
    elif args.command == "release":
        result = service.release_source(args.domain, reason=args.reason)
    elif args.command == "profiles":
        result = {"profiles": service.list_profiles()}
    elif args.command == "events":
        result = {"events": service.list_events(domain=args.domain, limit=args.limit)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
