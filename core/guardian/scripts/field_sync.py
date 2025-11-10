
# File: core/guardian/scripts/field_sync.py
import os, json, time
import urllib.request
from datetime import datetime, timezone

EDGE_URL = os.getenv("GUARDIAN_EDGE_URL")  # e.g. https://<project>.functions.supabase.co/guardian_sync?hours=24
DISCORD_WEBHOOK = os.getenv("DISCORD_GUARDIAN_WEBHOOK")
WINDOW_HOURS = int(os.getenv("GUARDIAN_WINDOW_HOURS", "24"))


def fetch_status():
    url = f"{EDGE_URL}&hours={WINDOW_HOURS}" if "?" in EDGE_URL else f"{EDGE_URL}?hours={WINDOW_HOURS}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode("utf-8"))


def format_message(payload: dict) -> dict:
    ts = payload.get("timestamp", datetime.now(timezone.utc).isoformat())
    scar = payload.get("scar_score")
    emoji = payload.get("scar_status", "❔")
    lines = [
        f"**Guardian Heartbeat** {emoji}",
        f"`{ts}`  |  window: {payload.get('window_hours')}h",
        "",
    ]
    for m in payload.get("metrics", []):
        lines.append(f"• **{m['label']}**: {m['value']}")

    if isinstance(scar, (int, float)) and (scar < 0.6 or scar >= 1.4):
        lines.append("\n⚠ **Coherence Alert** — ScarIndex out of band (target: 0.6–1.4).")

    content = "\n".join(lines)
    return {"content": content[:1995]}  # keep under Discord 2k char


def post_discord(msg: dict):
    data = json.dumps(msg).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        return r.status


def main():
    if not EDGE_URL or not DISCORD_WEBHOOK:
        raise SystemExit("Missing GUARDIAN_EDGE_URL or DISCORD_GUARDIAN_WEBHOOK")

    payload = fetch_status()
    msg = format_message(payload)
    code = post_discord(msg)
    print(f"Posted heartbeat to Discord (HTTP {code}).")


if __name__ == "__main__":
    main()
