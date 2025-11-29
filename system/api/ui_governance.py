from fastapi import APIRouter, Response

router = APIRouter(tags=["UI"])

@router.get("/governance/execution")
async def governance_ui():
    html = """
    <html>
    <head><title>Ω.12 Constitutional Execution Log</title></head>
    <body style="font-family:sans-serif; padding: 2rem; background-color: #111; color: #eee;">
    <h1>Ω.12 Constitutional Execution Log</h1>
    <p>This is a placeholder UI served directly by the Python backend.</p>
    <p>The real dashboard logic is governed by the Python API.</p>
    <p>Use <code>/api/governance/execution</code> to query constitutional execution logs.</p>
    <hr style="border-color: #333;">
    <h3>API Endpoints:</h3>
    <ul>
        <li><a href="/api/governance/execution" style="color: #4ade80;">GET /api/governance/execution</a></li>
        <li>POST /api/governance/execute</li>
    </ul>
    </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
