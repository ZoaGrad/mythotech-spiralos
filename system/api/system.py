from fastapi import APIRouter, HTTPException

from system.core.database import SupabaseManager


system_router = APIRouter(prefix="/system", tags=["system"])


@system_router.get("/health")
async def healthcheck():
    """Report liveness and dependency status for the spinal cord."""

    try:
        SupabaseManager.verify_connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"supabase_unhealthy: {exc}")

    return {"status": "ok", "dependencies": {"supabase": "connected"}}
