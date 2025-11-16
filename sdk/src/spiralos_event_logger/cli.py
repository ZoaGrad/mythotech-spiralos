"""Command line interface for the SpiraLOS event logger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .event_logger import EventLogger
from .storage import JSONStorage


def parse_metadata(pairs: list[str]) -> dict:
    metadata = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError("Metadata must be in key=value format")
        key, value = pair.split("=", 1)
        try:
            metadata[key] = json.loads(value)
        except json.JSONDecodeError:
            metadata[key] = value
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SpiraLOS Event Logger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Log a new event")
    add_parser.add_argument("name", help="Event name")
    add_parser.add_argument("metadata", nargs="*", help="Optional metadata key=value")

    list_parser = subparsers.add_parser("list", help="List recent events")
    list_parser.add_argument("--limit", type=int, default=None, help="Number of events to show")

    export_parser = subparsers.add_parser("export", help="Export events")
    export_parser.add_argument("format", choices=["json", "md", "markdown"], help="Export format")
    export_parser.add_argument("path", help="Destination file path")

    parser.add_argument(
        "--storage-path",
        dest="storage_path",
        default=None,
        help="Optional override for storage file path (defaults to ~/.spiralos/events.json)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    storage = JSONStorage(Path(args.storage_path)) if args.storage_path else JSONStorage()
    logger = EventLogger(storage=storage)

    if args.command == "add":
        metadata = parse_metadata(args.metadata)
        event_id = logger.log_event(args.name, metadata or None)
        print(f"Logged event {event_id}")
        return 0

    if args.command == "list":
        events = logger.retrieve_events(limit=args.limit)
        for event in events:
            print(f"{event['timestamp']} - {event['name']} ({event['id']})")
            if event.get("metadata"):
                print(f"  metadata: {json.dumps(event['metadata'], ensure_ascii=False)}")
        return 0

    if args.command == "export":
        if args.format in {"md", "markdown"}:
            logger.export_to_markdown(args.path)
        else:
            logger.export_to_json(args.path)
        print(f"Exported events to {args.path}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
