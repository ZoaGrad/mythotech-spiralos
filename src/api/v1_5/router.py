from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel

from src.core.governance.amc import AutonomousMarketController
from src.economy.dynamic_mint_burn import DynamicMintBurnEngine
from src.holoeconomy.holonic_agents import HolonicLiquidityAgent
from src.core.bridge.fmi1 import FMI1Bridge
from src.core.paradox.stress_loop import ParadoxStressLoop

router = APIRouter(prefix="/api/v1.5", tags=["v1.5"])

# Initialize components (Singleton-ish for now)
amc = AutonomousMarketController()
mint_burn_engine = DynamicMintBurnEngine()
fmi1_bridge = FMI1Bridge()
stress_loop = ParadoxStressLoop()

# --- AMC Endpoints ---

class AMCTuneRequest(BaseModel):
    kp: float
    ki: float
    kd: float
    authorization: str

@router.get("/amc/status")
async def get_amc_status():
    return amc.get_status()

@router.post("/amc/tune")
async def tune_amc(request: AMCTuneRequest):
    # Verify authorization (Placeholder)
    if request.authorization != "F2_SECRET_KEY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    amc.tune(request.kp, request.ki, request.kd)
    return {"success": True, "controller_id": amc.controller_id, "new_gains": {"kp": amc.kp, "ki": amc.ki, "kd": amc.kd}}

# --- Mint/Burn Endpoints ---

class MintBurnRequest(BaseModel):
    event_type: str
    amount: float
    reason: str

@router.post("/mint-burn/execute")
async def execute_mint_burn(request: MintBurnRequest):
    # Internal use only / Admin
    # In reality, this should be protected
    event_id = mint_burn_engine.execute_event(
        request.event_type, request.amount, 
        mint_burn_engine.oracle.get_current_index(), 
        0.0, # Deviation unknown if manual
        request.reason
    )
    return {"event_id": event_id, "success": True}

# --- Holonic Agents Endpoints ---

@router.get("/holonic-agents/list")
async def list_holonic_agents(active: bool = True, limit: int = 20):
    # Placeholder: Fetch from DB view
    # For now, return a dummy list or implement DB fetch
    return {"agents": [], "total": 0}

# --- FMI-1 Endpoints ---

class FMI1TransformRequest(BaseModel):
    source_space: str
    target_space: str
    value: float

@router.get("/fmi1/coherence")
async def get_fmi1_coherence():
    return fmi1_bridge.get_coherence_metrics()

@router.post("/fmi1/transform")
async def transform_fmi1(request: FMI1TransformRequest):
    result = fmi1_bridge.transform(request.source_space, request.target_space, request.value)
    if not result:
        raise HTTPException(status_code=400, detail="Transformation failed")
    return result

# --- Paradox Endpoints ---

class StressTestRequest(BaseModel):
    stress_type: str
    intensity: float
    duration_seconds: int
    authorization: str

@router.post("/paradox/stress-test")
async def trigger_stress_test(request: StressTestRequest):
    if request.authorization != "F2_SECRET_KEY":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    result = stress_loop.trigger_stress_test(request.stress_type, request.intensity, request.duration_seconds)
    return result

@router.get("/equilibrium/status")
async def get_equilibrium_status():
    # Placeholder
    return {
        "tau": 1.5,
        "target_tau": 1.5,
        "deviation": 0.0,
        "equilibrium_score": 1.0,
        "total_liquidity": 1000000.0
    }
