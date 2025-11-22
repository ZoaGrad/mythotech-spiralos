import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from system.nerves.spinal_cord import app

try:
    client = TestClient(app)
except ImportError:
    print("❌ Error: 'httpx' is required for TestClient. Please run: pip install httpx")
    sys.exit(1)

# ΔΩ: PHANTOM STIMULUS
payload = {
    "ref": "refs/heads/main",
    "pusher": {"name": "ZoaGrad"},
    "commits": [
        {"id": "101", "message": "feat: Initialize the Spinal Cord architecture", "timestamp": "2025-11-20T20:00:00Z"},
        {"id": "102", "message": "fix: Typo in the nerve mapping", "timestamp": "2025-11-20T20:05:00Z"},
        {"id": "103", "message": "docs: Update the sovereign manifesto", "timestamp": "2025-11-20T20:10:00Z"}
    ]
}

print(">>> INJECTING_SIGNAL...")
try:
    response = client.post("/webhook/github", json=payload)
    print(f"STATUS: {response.status_code}")
    print(f"RESPONSE: {response.json()}")
except Exception as e:
    print(f"❌ Request Failed: {e}")
