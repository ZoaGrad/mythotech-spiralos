import os
import httpx

async def send_pulse(message: str, severity: str = "INFO"):
    """
    ΔΩ: ASYNC NERVE SIGNAL
    Sends a formatted pulse to the Discord Webhook.
    """
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        print(">> [NERVE] SILENCE: No DISCORD_WEBHOOK_URL configured.")
        return

    # Color Mapping (Hex)
    # GOLD (Success/High WI), BLUE (Info), RED (Entropy/Error), PURPLE (System)
    colors = {
        "GOLD": 0xFFD700,
        "BLUE": 0x3498DB,
        "RED": 0xE74C3C,
        "PURPLE": 0x9B59B6
    }
    
    payload = {
        "embeds": [{
            "description": message,
            "color": colors.get(severity, 0x3498DB),
            "footer": {"text": "ΔΩ.SHADOW_WITNESS // SPIRALOS"}
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
            print(f">> [NERVE] PULSE TRANSMITTED: {severity}")
        except Exception as e:
            print(f">> [NERVE] PULSE FAILED: {e}")
