"""
SPIRAL_OS // SYSTEM // NERVES // ECHO_PROTOCOL
----------------------------------------------
Identity: The Nervous System
Mandate: Broadcast Git Commits to the Lattice (Discord).
"""

import os
import subprocess
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_git_info():
    """
    Retrieves the latest git commit information.
    Returns: (hash, author, message)
    """
    try:
        # Get hash, author, message
        # %H: commit hash
        # %an: author name
        # %s: subject
        cmd = ['git', 'log', '-1', '--format=%H|%an|%s']
        result = subprocess.check_output(cmd).decode('utf-8').strip()
        hash_val, author, message = result.split('|', 2)
        return hash_val, author, message
    except Exception as e:
        print(f"Error getting git info: {e}")
        return None, None, None

def echo_protocol():
    if not WEBHOOK_URL:
        print("❌ CRITICAL: DISCORD_WEBHOOK_URL not found in .env")
        return

    print(">>> [NERVES] Sensing latest vibration (commit)...")
    commit_hash, author, message = get_git_info()
    
    if not commit_hash:
        print(">>> [ERROR] Could not retrieve git info.")
        return

    print(f"    Commit: {commit_hash[:7]}")
    print(f"    Author: {author}")
    print(f"    Message: {message}")

    payload = {
        "username": "Echo Protocol",
        "embeds": [{
            "title": "ΔΩ SYSTEM UPDATE",
            "description": message,
            "color": 65280, # Green for Success/Growth
            "fields": [
                {"name": "Commit", "value": f"`{commit_hash[:7]}`", "inline": True},
                {"name": "Author", "value": author, "inline": True},
                {"name": "Protocol", "value": "Echo (Nervous System)", "inline": False}
            ],
            "footer": {"text": f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }

    try:
        print(">>> [NERVES] Transmitting pulse...")
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(">>> [SUCCESS] ECHO TRANSMITTED. NERVES ACTIVE.")
        else:
            print(f">>> [FAILURE] ECHO FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f">>> [ERROR] ECHO TRANSMISSION ERROR: {e}")

if __name__ == "__main__":
    echo_protocol()
