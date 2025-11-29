from fastapi import APIRouter, HTTPException
from core.db import db
from core.governance.executor import enforce_constitution
import uuid

router = APIRouter(prefix="/api/governance", tags=["Governance"])

# --------------------------------------------
# GET — Constitutional Execution Log
# --------------------------------------------
@router.get("/execution")
async def get_execution_log(limit: int = 100):
    try:
        # Use db.client._ensure_client() to get the supabase client
        client = db.client._ensure_client()
        result = client.table("constitutional_execution_log") \
                       .select("*") \
                       .order("timestamp", desc=True) \
                       .limit(limit) \
                       .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------
# POST — Execute an Action (Pass / Veto / Rewrite)
# --------------------------------------------
@router.post("/execute")
async def execute_action(action: dict):
    try:
        # Ensure action has an ID if not provided
        if "id" not in action:
            action["id"] = str(uuid.uuid4())
            
        result = enforce_constitution(action)

        return {
            "submitted_action": action,
            "constitutional_result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
