import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def is_reality_engine_enabled() -> bool:
    """
    Check if the Reality Engine is enabled.
    Defaults to False if not explicitly set to 'true'.
    """
    return os.getenv("REALITY_ENGINE_ENABLED", "false").lower() == "true"

def get_reality_config() -> dict:
    """
    Get the Reality Engine configuration.
    """
    return {
        "enabled": is_reality_engine_enabled(),
        "mode": "ACTIVE" if is_reality_engine_enabled() else "DORMANT",
        "version": "ΔΩ.F"
    }
