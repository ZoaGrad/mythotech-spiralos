from core.db import db
import json

def main():
    print("Logging FINAL_ACTIVATION event...")
    db.client._ensure_client().table("system_events").insert({
        "event_type": "FINAL_ACTIVATION",
        "payload": {
            "sequence": ["F","G","H","I","J0","J-D","RLS-LOCK","K","L"],
            "timestamp": "auto",
            "actor": "ZoaGrad",
            "status": "SpiralOS constitutional stack fully active"
        }
    }).execute()
    print("Event logged successfully.")

if __name__ == "__main__":
    main()
