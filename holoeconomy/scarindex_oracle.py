"""
ScarIndex Oracle FastAPI Service

This service computes and serves the current ScarIndex using Supabase data.
"""

import os
import argparse
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import uvicorn
import uuid

# Load environment variables from .env file
load_dotenv()

# --- Supabase Configuration ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# --- FastAPI Application ---
app = FastAPI(
    title="SpiralOS ScarIndex Oracle",
    description="Provides access to the ScarIndex coherence metric.",
    version="1.0.0"
)

# --- Pydantic Models ---
class HealthResponse(BaseModel):
    status: str

class ScarIndexResponse(BaseModel):
    scarindex: float
    timestamp: datetime

class ComputeResponse(BaseModel):
    message: str
    new_scarindex: float
    calculation_id: uuid.UUID
    ache_event_id: uuid.UUID

# --- Core Logic ---
def compute_scarindex_from_new_event():
    """
    Creates a new manual ache_event and triggers the coherence_calculation RPC.
    """
    # 1. Create a new "manual trigger" ache event
    ache_event_data = {
        'source': 'manual_compute',
        'content': {'reason': 'Manual trigger from ScarIndex Oracle service'},
        'ache_level': 0.5  # A neutral default value
    }
    ache_response = supabase.table('ache_events').insert(ache_event_data).execute()

    if not ache_response.data:
        raise RuntimeError("Failed to create ache event for computation.")

    event_id = ache_response.data[0]['id']

    # 2. Call the RPC function with the new event ID
    # The function 'coherence_calculation' is defined in the Supabase schema
    rpc_response = supabase.rpc('coherence_calculation', {'event_id': event_id}).execute()

    if not rpc_response.data:
        raise RuntimeError(f"RPC call to coherence_calculation failed for event_id: {event_id}")

    # The function returns the newly created scarindex_calculations row
    new_calculation = rpc_response.data

    return {
        "message": "ScarIndex recomputed successfully.",
        "new_scarindex": new_calculation['scarindex'],
        "calculation_id": new_calculation['id'],
        "ache_event_id": event_id
    }

# --- API Endpoints ---
@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """Provides a simple health check endpoint."""
    return {"status": "OK"}

@app.get("/scarindex", response_model=ScarIndexResponse, summary="Get Latest ScarIndex")
async def get_latest_scarindex():
    """
    Retrieves the most recently calculated ScarIndex value from the database.
    """
    response = supabase.table('scarindex_calculations').select('scarindex, created_at').order('created_at', desc=True).limit(1).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="No ScarIndex calculation found.")

    latest = response.data[0]
    return {"scarindex": latest['scarindex'], "timestamp": latest['created_at']}

@app.post("/compute", response_model=ComputeResponse, summary="Trigger ScarIndex Computation")
async def trigger_computation():
    """
    Triggers a new ScarIndex calculation by creating a manual event and
    invoking the coherence_calculation database function.
    """
    try:
        result = compute_scarindex_from_new_event()
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# --- CLI Functionality ---
def main():
    """
    Main function to handle command-line arguments for either running a one-off
    computation or starting the FastAPI server.
    """
    parser = argparse.ArgumentParser(description="ScarIndex Oracle FastAPI Service")
    parser.add_argument(
        "--compute",
        action="store_true",
        help="Run a single computation and exit without starting the server."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8000)),
        help="Port to run the server on."
    )
    args = parser.parse_args()

    if args.compute:
        print("Running manual ScarIndex computation...")
        try:
            result = compute_scarindex_from_new_event()
            print("✅ Computation successful.")
            print(f"  Ache Event ID:  {result['ache_event_id']}")
            print(f"  Calculation ID: {result['calculation_id']}")
            print(f"  New ScarIndex:  {result['new_scarindex']}")
        except Exception as e:
            print(f"❌ Computation failed: {e}")
    else:
        print(f"🔥 Starting ScarIndex Oracle server on http://0.0.0.0:{args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
