import sys
import os
import uuid
import logging
from datetime import datetime, timezone

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from core.db import get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_telemetry_pipeline")

def test_telemetry_ingestion():
    logger.info("Testing Telemetry Pipeline...")
    
    supabase = get_supabase()
    
    # 1. Test Valid Insertion
    logger.info("Testing valid insertion...")
    event_id = str(uuid.uuid4())
    payload = {
        "event_type": "test_event",
        "source_id": "test_runner",
        "payload": {"metric": 42},
        "processed_status": "pending",
        "event_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        res = supabase.table("telemetry_events").insert(payload).execute()
        if not res.data:
            logger.error("Failed to insert valid event")
            return False
        logger.info(f"✅ Inserted event: {res.data[0]['id']}")
        inserted_id = res.data[0]['id']
    except Exception as e:
        logger.error(f"Insertion failed: {e}")
        return False

    # 2. Verify Schema (Check new columns)
    logger.info("Verifying schema fields...")
    event = res.data[0]
    if 'processed_status' not in event:
        logger.error("Missing 'processed_status' column")
        return False
    if 'source_id' not in event:
        logger.error("Missing 'source_id' column")
        return False
        
    logger.info("✅ Schema verification successful")

    # 3. Clean up
    logger.info("Cleaning up...")
    supabase.table("telemetry_events").delete().eq("id", inserted_id).execute()
    
    return True

if __name__ == "__main__":
    try:
        success = test_telemetry_ingestion()
        if success:
            logger.info("Test PASSED")
            sys.exit(0)
        else:
            logger.error("Test FAILED")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")
        sys.exit(1)
