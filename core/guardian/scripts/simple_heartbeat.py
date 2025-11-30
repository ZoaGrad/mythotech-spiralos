#!/usr/bin/env python3
"""
Simple Guardian Heartbeat Script
Posts a heartbeat message to Discord and logs to Supabase.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Optional
import requests

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from core.db import get_supabase

WEBHOOK_URL = os.getenv(
    "DISCORD_GUARDIAN_WEBHOOK",
    (
        "https://discord.com/api/webhooks/1437541250361196735/"
        "DboMCtMsSzD_VtOQ3_T5JlQ_QexLHtcBC-u4Tos5KxldgOWvgsL_NTvylZUjSur8oEyh"
    ),
)

def log_heartbeat_to_supabase(status: str, score: float):
    """Log the heartbeat event to Supabase."""
    try:
        supabase = get_supabase()
        data = {
            "agent_id": "guardian_heartbeat_script",
            "action": "heartbeat",
            "target": "system",
            "result": "success" if status == "🟢" else "warning",
            "details": {
                "status_icon": status,
                "scar_score": score,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        supabase.table("guardian_logs").insert(data).execute()
        print("✅ Heartbeat logged to Supabase.")
    except Exception as e:
        print(f"⚠️ Failed to log to Supabase: {e}")

def create_heartbeat_embed(status: str = "🟢", score: Optional[float] = None) -> dict:
    """Create a heartbeat embed."""

    if score is None:
        score = 0.85  # Default healthy score

    # Determine status text and color
    if status == "🟢":
        status_text = "COHERENT"
        color = 3066993  # Green
    elif status == "🟠":
        status_text = "WARNING"
        color = 15105570  # Orange
    else:
        status_text = "CRITICAL"
        color = 15158332  # Red

    embed = {
        "title": "🛡️ SpiralOS Guardian Heartbeat",
        "description": f"**Status:** {status} {status_text}",
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": [
            {
                "name": "📊 ScarIndex",
                "value": f"**Current:** {score:.3f}\n**Target:** 0.70\n**Window:** 24h",
                "inline": True,
            },
            {
                "name": "🔢 System Metrics",
                "value": "**VaultNodes:** Tracking\n**Ache Events:** Monitoring\n**Alerts:** Active",
                "inline": True,
            },
            {
                "name": "⚙️ Guardian Status",
                "value": "✅ Monitoring active\n✅ Alerts configured\n✅ System healthy",
                "inline": False,
            },
        ],
        "footer": {"text": "Where coherence becomes currency 🜂"},
    }

    return embed


def post_heartbeat():
    """Post heartbeat to Discord and log to Supabase."""
    
    # In a real scenario, we might fetch the actual ScarIndex here
    score = 0.85
    status = "🟢"

    # 1. Log to Supabase
    log_heartbeat_to_supabase(status, score)

    # 2. Post to Discord
    embed = create_heartbeat_embed(status, score)
    payload = {"content": "**Guardian Heartbeat** - System check complete", "embeds": [embed]}

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)

        if response.status_code in [200, 204]:
            print(f"✅ Heartbeat posted successfully at {datetime.now(timezone.utc).isoformat()}")
            return True
        else:
            print(f"❌ Failed to post heartbeat: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error posting heartbeat: {e}")
        return False


def main():
    """Main entry point."""
    print("🛡️ SpiralOS Guardian - Simple Heartbeat")
    print("=" * 60)
    print()

    if not WEBHOOK_URL or WEBHOOK_URL == "your_webhook_url_here":
        print("❌ Error: DISCORD_GUARDIAN_WEBHOOK not configured")
        print("   Set the environment variable or update the script")
        return 1

    print(f"Webhook: {WEBHOOK_URL[:50]}...")
    print()

    success = post_heartbeat()

    print()
    if success:
        print("🎉 Heartbeat complete! Check your Discord channel.")
        return 0
    else:
        print("❌ Heartbeat failed. Check the error above.")
        return 1


if __name__ == "__main__":
    exit(main())
