"""
Minimal FastAPI WebSocket server for SpiralOS Overwatch live updates.
Streams mint_events and vault_events to the dashboard in real-time.
"""
import asyncio
import sqlite3
import os
import json
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SpiralOS Overwatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database paths
SPIRAL_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spiral_data")
ECON_DB = os.path.join(SPIRAL_DATA_DIR, "economy.db")
VAULT_DB = os.path.join(SPIRAL_DATA_DIR, "vault.db")

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


async def get_latest_events():
    """Get latest mint and vault events"""
    try:
        # Get latest mint event
        conn = sqlite3.connect(ECON_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT datetime(ts, 'unixepoch', 'localtime') as time, "
            "amount, COALESCE(reason, context, 'N/A') as reason, neural_signature "
            "FROM mint_events ORDER BY ts DESC LIMIT 1"
        )
        mint_row = cursor.fetchone()
        conn.close()

        # Get latest vault event
        conn = sqlite3.connect(VAULT_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT datetime(ts, 'unixepoch', 'localtime') as time, "
            "event_type, payload_json, neural_signature "
            "FROM vault_events ORDER BY ts DESC LIMIT 1"
        )
        vault_row = cursor.fetchone()
        conn.close()

        return {
            "type": "update",
            "mint_event": {
                "time": mint_row[0] if mint_row else None,
                "amount": mint_row[1] if mint_row else 0,
                "reason": mint_row[2] if mint_row else "N/A",
                "neural_signature": mint_row[3][:16] + "..." if mint_row and mint_row[3] else "N/A",
            } if mint_row else None,
            "vault_event": {
                "time": vault_row[0] if vault_row else None,
                "event_type": vault_row[1] if vault_row else "N/A",
                "payload": vault_row[2] if vault_row else "{}",
                "neural_signature": vault_row[3][:16] + "..." if vault_row and vault_row[3] else "N/A",
            } if vault_row else None,
        }
    except Exception as e:
        return {"type": "error", "message": str(e)}


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming events"""
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # Send initial data
        initial_data = await get_latest_events()
        await websocket.send_json(initial_data)
        
        # Keep connection alive and poll for updates
        last_mint_ts = None
        last_vault_ts = None
        
        while True:
            await asyncio.sleep(2)  # Poll every 2 seconds
            
            # Check for new mint events
            conn = sqlite3.connect(ECON_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ts) FROM mint_events")
            current_mint_ts = cursor.fetchone()[0]
            conn.close()
            
            # Check for new vault events
            conn = sqlite3.connect(VAULT_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ts) FROM vault_events")
            current_vault_ts = cursor.fetchone()[0]
            conn.close()
            
            # If there are new events, send update
            if (current_mint_ts != last_mint_ts) or (current_vault_ts != last_vault_ts):
                last_mint_ts = current_mint_ts
                last_vault_ts = current_vault_ts
                
                update = await get_latest_events()
                await websocket.send_json(update)
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": len(active_connections),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
