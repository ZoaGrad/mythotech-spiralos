
# File: core/guardian/scripts/post_to_discord.py
import os, sys, json, urllib.request

WEBHOOK = os.getenv("DISCORD_GUARDIAN_WEBHOOK")

def main():
    if not WEBHOOK:
        raise SystemExit("DISCORD_GUARDIAN_WEBHOOK not set")
    payload = sys.stdin.read()
    data = json.loads(payload)
    req = urllib.request.Request(WEBHOOK, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        print(f"Discord status: {r.status}")

if __name__ == "__main__":
    main()
