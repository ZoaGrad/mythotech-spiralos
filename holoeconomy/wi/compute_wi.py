# holoeconomy/wi/compute_wi.py

import os

import numpy as np
from dotenv import load_dotenv

from supabase import Client, create_client

load_dotenv()

# --- Environment Setup ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Helper Functions ---


def gini(arr):
    """Calculates the Gini coefficient of a numpy array."""
    if arr.size == 0:
        return 0.0
    # All values are identical
    if np.all(arr == arr[0]):
        return 0.0

    sorted_arr = np.sort(arr)
    n = arr.size
    cumx = np.cumsum(sorted_arr, dtype=float)
    # The area between the Lorenz curve and the line of perfect equality
    B = np.sum(cumx) / (n * np.sum(sorted_arr))
    return 1 + (1 / n) - 2 * B


# --- Vitality Components ---


def calculate_tv(witnesses: list, attestations: list) -> float:
    """
    Calculates Topological Vitality (Tν).
    Measures the diversity of witness participation via attestation distribution.
    Uses the Gini coefficient: 0 = perfect equality, 1 = max inequality.
    We want a low Gini score, so we use 1 - gini.
    """
    if not witnesses or not attestations:
        return 0.0

    attestation_counts = {w["witness_id"]: 0 for w in witnesses}
    for attestation in attestations:
        if attestation["witness_id"] in attestation_counts:
            attestation_counts[attestation["witness_id"]] += 1

    counts_array = np.array(list(attestation_counts.values()))

    # High diversity = low Gini coefficient
    return 1.0 - gini(counts_array)


def calculate_cv(attestations: list) -> float:
    """
    Calculates Content Vitality (Cν).
    Measures the diversity of attested content.
    Metric: Ratio of unique data hashes to total attestations.
    """
    if not attestations:
        return 0.0

    total_attestations = len(attestations)
    unique_hashes = len(set(a["data_hash"] for a in attestations))

    return unique_hashes / total_attestations


def calculate_rv(witnesses: list) -> float:
    """
    Calculates Reputation Vitality (Rν).
    Placeholder: In a real scenario, this would fetch reputation scores
    (e.g., from a social graph or on-chain history) and measure their diversity.
    Using 1 - Gini coefficient of reputation scores.
    """
    # TODO: Replace with actual reputation data integration.
    # For now, assume a moderately diverse reputation distribution.
    if len(witnesses) < 2:
        return 1.0  # Perfect diversity if only one witness

    # Placeholder: dummy reputation scores with some variance
    np.random.seed(42)
    dummy_reputations = np.random.normal(loc=100, scale=20, size=len(witnesses))

    return 1.0 - gini(dummy_reputations)


def calculate_ev(witnesses: list) -> float:
    """
    Calculates Economic Vitality (Eν).
    Placeholder: In a real scenario, this would fetch economic stakes
    (e.g., token holdings) and measure their diversity.
    Using 1 - Gini coefficient of stakes.
    """
    # TODO: Replace with actual economic data integration.
    # For now, assume a moderately diverse economic distribution.
    if len(witnesses) < 2:
        return 1.0

    # Placeholder: dummy economic stakes
    np.random.seed(42)
    dummy_stakes = np.random.lognormal(mean=10, sigma=2, size=len(witnesses))

    return 1.0 - gini(dummy_stakes)


# --- Main Wᵢ Calculation ---


def wi() -> dict:
    """
    Calculates the Witness Diversity Index (Wᵢ).
    Fetches required data and computes the four vitality metrics,
    then combines them into a single index.
    """
    print("Fetching active witnesses...")
    witness_res = supabase.table("witnesses").select("witness_id").eq("is_active", True).execute()
    witnesses = witness_res.data

    print("Fetching all attestations...")
    attestation_res = supabase.table("attestations").select("witness_id, data_hash").execute()
    attestations = attestation_res.data

    if not witnesses:
        print("No active witnesses found.")
        return {"wi_value": 0, "tv": 0, "cv": 0, "rv": 0, "ev": 0}

    print("Calculating vitality metrics...")
    tv = calculate_tv(witnesses, attestations)
    cv = calculate_cv(attestations)
    rv = calculate_rv(witnesses)
    ev = calculate_ev(witnesses)

    # Wᵢ is the geometric mean of the four components
    wi_value = (tv * cv * rv * ev) ** 0.25

    metrics = {"wi_value": wi_value, "tv": tv, "cv": cv, "rv": rv, "ev": ev}

    return metrics


def store_metrics(metrics: dict):
    """Stores the calculated metrics in the Supabase database."""
    print(f"Storing metrics in database: {metrics}")
    try:
        data, count = supabase.table("wi_metrics").insert(metrics).execute()
        print("Successfully stored Wᵢ metrics.")
        return data
    except Exception as e:
        print(f"Error storing metrics: {e}")
        return None


if __name__ == "__main__":
    print("🌀 Starting Witness Diversity Index (Wᵢ) Calculation...")

    calculated_metrics = wi()

    print("\n--- Calculated Metrics ---")
    for key, value in calculated_metrics.items():
        print(f"{key.upper()}: {value:.4f}")
    print("--------------------------")

    if calculated_metrics:
        store_metrics(calculated_metrics)

    print("\n✅ Wᵢ Calculation complete.")
