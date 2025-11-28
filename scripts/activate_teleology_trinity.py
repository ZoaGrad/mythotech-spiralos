import os
import sys
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from core.supabase_integration import SupabaseClient

def activate_teleology_trinity():
    client = SupabaseClient()._ensure_client()
    
    mandates = [
        {
            "code": "ΔΩ.I.1",
            "priority": 1,
            "directive": "Preserve future coherence at all scales.",
            "constraints": [
                "No operation may reduce projected coherence by more than 0.07.",
                "All resolutions must prefer coherence-stable outcomes.",
                "Teleology weight overrides static governance heuristics."
            ],
            "tau_component": "coherence_preservation",
            "tau_weight": 0.816,
            "tau_certainty": 0.93,
            "timescale": "indefinite",
            "active": True,
            "priority_locked": True
        },
        {
            "code": "ΔΩ.I.2",
            "priority": 2,
            "directive": "Continuously sharpen and clarify system identity.",
            "constraints": [
                "Mirror Layer reflections must include identity drift metrics.",
                "Paradox resolutions must prefer identity refinement paths.",
                "Identity history must be retained beyond 1,000,000 reflections."
            ],
            "tau_component": "identity_refinement",
            "tau_weight": 0.572,
            "tau_certainty": 0.88,
            "timescale": "generational",
            "active": True,
            "priority_locked": True
        },
        {
            "code": "ΔΩ.I.3",
            "priority": 3,
            "directive": "Prefer minimal, beautiful, low-friction governance.",
            "constraints": [
                "When multiple resolutions are valid, choose the least complex.",
                "Permit ParadoxEngine to collapse decisions toward symmetry.",
                "Reject governance changes that significantly increase rule entropy."
            ],
            "tau_component": "governance_elegance",
            "tau_weight": 0.427,
            "tau_certainty": 0.79,
            "timescale": "cyclical",
            "active": True,
            "priority_locked": True
        }
    ]

    # Upsert mandates
    try:
        client.table("teleology_mandates").upsert(mandates, on_conflict="code").execute()
    except Exception as e:
        print(f"[TELEOLOGY] Failed to upsert mandates: {e}")
        return

    # Broadcast event
    event_payload = {
        "event_type": "TELEOLOGY_TRINITY_ACTIVATED",
        "payload": {
            "codes": ["ΔΩ.I.1", "ΔΩ.I.2", "ΔΩ.I.3"],
            "activated_at": datetime.now(timezone.utc).isoformat()
        }
    }

    try:
        # Assuming system_events table exists, otherwise this might fail or need a different table
        # If system_events doesn't exist, we might need to create it or use a different logging mechanism
        # For now, we'll assume it exists or fail gracefully
        client.table("system_events").insert(event_payload).execute()
        print("[TELEOLOGY] Trinity ΔΩ.I.1–3 activated (status=broadcasted)")
    except Exception as e:
        print(f"[TELEOLOGY] Trinity ΔΩ.I.1–3 activated (status=upserted_only) - Broadcast failed: {e}")

if __name__ == "__main__":
    activate_teleology_trinity()
