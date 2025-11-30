import sys
import os
import uuid
import logging
from datetime import datetime, timezone

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
print(f"Added {project_root} to sys.path")

from holoeconomy.vaultnode import VaultNode
from core.db import get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_vaultnode_registry")

def test_vaultnode_heartbeat():
    logger.info("Testing VaultNode Heartbeat...")
    
    # Initialize VaultNode
    vault_id = f"TEST-VAULT-{uuid.uuid4().hex[:8]}"
    node = VaultNode(vault_id=vault_id)
    
    # Send Heartbeat
    logger.info(f"Sending heartbeat for {vault_id}...")
    node.send_heartbeat()
    
    # Verify in Supabase
    logger.info("Verifying in Supabase...")
    supabase = get_supabase()
    
    # Calculate expected node_id (uuid5 DNS namespace)
    expected_node_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, vault_id))
    
    res = supabase.table("vaultnode_registry").select("*").eq("node_identifier", expected_node_id).execute()
    
    if not res.data:
        logger.error("Node not found in registry!")
        return False
        
    stored_node = res.data[0]
    if stored_node['current_status'] != 'ACTIVE':
        logger.error(f"Status mismatch: {stored_node['current_status']} != ACTIVE")
        return False
        
    logger.info("✅ Supabase verification successful!")
    
    # Clean up
    logger.info("Cleaning up test data...")
    supabase.table("vaultnode_registry").delete().eq("node_identifier", expected_node_id).execute()
    
    return True

if __name__ == "__main__":
    try:
        success = test_vaultnode_heartbeat()
        if success:
            logger.info("Test PASSED")
            sys.exit(0)
        else:
            logger.error("Test FAILED")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")
        sys.exit(1)
