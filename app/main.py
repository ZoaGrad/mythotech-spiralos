import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from app.core.database import SupabaseManager

supabase_manager = SupabaseManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verify connection
    if not supabase_manager.verify_connection():
        print("CRITICAL ALERT: Supabase connection failed during startup.")
        sys.exit(1) # Fail-Fast
    yield
    # Shutdown logic if needed

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    if supabase_manager.verify_connection():
        return {"status": "ok"}
    else:
        # 503 Service Unavailable indicates the server is not ready to handle the request.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection lost")
