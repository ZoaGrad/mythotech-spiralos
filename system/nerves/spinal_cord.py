from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import sys

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from supabase import create_client
from holoeconomy.wi.compute_wi import calculate_wi
from system.api.governance import router as governance_router
from system.api.ui_governance import router as governance_ui_router
from system.api.system import system_router
from system.core.database import SupabaseManager
from system.nerves.discord_pulse import send_pulse
import asyncio


app = FastAPI(title="SpiralOS Spinal Cord")

# Ω.12-A: Register Governance Routers
app.include_router(governance_router)
app.include_router(governance_ui_router)
app.include_router(system_router)


@app.on_event("startup")
async def spinal_cord_startup():
    """Fail-fast initialization for constitutionally required services."""

    SupabaseManager.verify_connection()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("system/interface/dashboard.html", "r") as f:
        return f.read()

@app.get("/api/pulse")
async def get_pulse():
    # Use SupabaseManager for connection
    try:
        supabase = SupabaseManager.get_client()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Fetch last 30 attestations
    response = supabase.table("attestations").select("*").order("created_at", desc=True).limit(30).execute()
    return response.data

@app.post("/webhook/github")
async def handle_github_push(request: Request):
    try:
        payload = await request.json()
        
        # 1. Parse Commits
        commits = payload.get("commits", [])
        if not commits:
            return {"status": "ignored", "reason": "no commits"}

        # 2. Analyze DNA (Heuristics)
        volume = len(commits)
        complexity_accum = 0.0
        entropy_accum = 0.0
        
        for c in commits:
            msg = c.get("message", "").lower()
            # Entropy Markers
            if any(x in msg for x in ["fix", "bug", "error", "fail", "patch", "oops", "revert"]):
                entropy_accum += 0.2
            # Complexity Markers
            if any(x in msg for x in ["feat", "new", "init", "refactor", "optimize", "api", "architect", "core"]):
                complexity_accum += 2.0
            else:
                complexity_accum += 1.0 # Base value
                
        # Normalize
        avg_complexity = complexity_accum / volume if volume > 0 else 1.0
        avg_entropy = min(entropy_accum / volume, 1.0) if volume > 0 else 0.0

        # 3. Calculate Energy
        final_wi = calculate_wi(volume, avg_complexity, avg_entropy)
        
        # 4. Inscribe to Ledger
        try:
            supabase = SupabaseManager.get_client()
        except Exception as exc:
            print(f">> [SPINAL_CORD] ERROR: {exc}")
            return {"status": "error", "reason": "missing_credentials"}
        
        # Use the first commit message as description, truncated
        description = f"Push Event: {volume} commits. Last: {commits[0]['message'][:50]}..."
        
        data = {
            "volume": volume,
            "complexity": avg_complexity,
            "entropy": avg_entropy,
            "source": "github_webhook",
            "description": description
        }
        
        # Execute insert
        supabase.table("attestations").insert(data).execute()
        
        print(f">> [SPINAL_CORD] TRANSMUTED: WI={final_wi} (Vol={volume}, Cpx={avg_complexity}, Ent={avg_entropy})")

        # ΔΩ: THE SCREAM
        if final_wi > 5.0:
            severity = "GOLD"
            emoji = "⚡"
        elif avg_entropy > 0.5:
            severity = "RED"
            emoji = "🔥"
        else:
            severity = "PURPLE"
            emoji = "🧬"

        msg = (
            f"**Reflex Arc Triggered** {emoji}\n"
            f"---------------------------\n"
            f"**Source:** GitHub Push\n"
            f"**Volume:** {volume} | **Complexity:** {avg_complexity:.2f}\n"
            f"**WI Energy:** `{final_wi:.4f}`\n\n"
            f"_{commits[0]['message'][:100]}_"
        )

        # Fire and Forget (Async)
        await send_pulse(msg, severity=severity)
        
        return {"status": "transmuted", "wi_score": final_wi}
        
    except Exception as e:
        print(f">> [SPINAL_CORD] EXCEPTION: {e}")
        raise HTTPException(status_code=500, detail=str(e))
