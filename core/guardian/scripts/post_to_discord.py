# File: core/guardian/scripts/post_to_discord.py
import json
import os
import sys
import urllib.request
from urllib.parse import urlparse

WEBHOOK = os.getenv("DISCORD_GUARDIAN_WEBHOOK")


def _require_https(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise SystemExit("DISCORD_GUARDIAN_WEBHOOK must use https://")
    return url


def main():
    if not WEBHOOK:
        raise SystemExit("DISCORD_GUARDIAN_WEBHOOK not set")
    payload = sys.stdin.read()
    data = json.loads(payload)
    req = urllib.request.Request(
        _require_https(WEBHOOK), data=json.dumps(data).encode(), headers={"Content-Type": "application/json"}
    )
    # Discord webhook is validated via _require_https before network I/O
    with urllib.request.urlopen(req) as r:  # nosec B310
        print(f"Discord status: {r.status}")


if __name__ == "__main__":
    main()
