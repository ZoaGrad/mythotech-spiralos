# holoeconomy/poc/mint_guard.py

import os
import sys

from dotenv import load_dotenv

from supabase import Client, create_client

# --- Constants ---
WI_THRESHOLD = 0.60

# --- Environment Setup ---
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Guardrail Function ---


def wi_ok() -> bool:
    """
    Checks if the latest Witness Diversity Index (Wᵢ) meets the minimum threshold.

    Returns:
        bool: True if Wᵢ ≥ threshold, False otherwise.
    """
    print(f"Checking Wᵢ against threshold of {WI_THRESHOLD}...")

    try:
        # Fetch the most recent Wᵢ value from the database
        response = (
            supabase.table("wi_metrics").select("wi_value").order("calculation_timestamp", desc=True).limit(1).execute()
        )

        if not response.data:
            print("🚨 Guardrail Veto: No Wᵢ metrics found in the database.")
            return False

        latest_wi = response.data[0]["wi_value"]
        print(f"Latest Wᵢ value found: {latest_wi:.4f}")

        if latest_wi >= WI_THRESHOLD:
            print(f"✅ Guardrail Pass: Wᵢ ({latest_wi:.4f}) is >= {WI_THRESHOLD}.")
            return True
        else:
            print(f"🚨 Guardrail Veto: Wᵢ ({latest_wi:.4f}) is < {WI_THRESHOLD}.")
            return False

    except Exception as e:
        print(f"🚨 Guardrail Error: An exception occurred while checking Wᵢ: {e}")
        return False


def update_guard_flag(status: bool):
    """
    Updates the 'wi_ok' flag in the guard_flags table.
    """
    print(f"Updating 'wi_ok' guard flag to: {status}")
    try:
        supabase.table("guard_flags").update({"is_active": status, "last_checked": "now()"}).eq(
            "flag_name", "wi_ok"
        ).execute()
        print("Successfully updated guard flag.")
    except Exception as e:
        print(f"Error updating guard flag: {e}")


# --- Main Execution ---

if __name__ == "__main__":
    print("🔬 Running Proof-of-Concept Mint Guard...")

    is_compliant = wi_ok()

    # Update the database flag to reflect the current status
    update_guard_flag(is_compliant)

    if not is_compliant:
        # Exit with a non-zero status code to indicate failure in a CI/CD pipeline
        print("\nConstitutionality check failed. Aborting process.")
        sys.exit(1)

    print("\nConstitutional compliance verified. Process can continue.")
    sys.exit(0)
