import sys
import os
import uuid
from decimal import Decimal
import logging

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
print(f"Added {project_root} to sys.path")

from holoeconomy.scarcoin import ScarCoinMintingEngine, ScarCoin
from core.db import get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_holoeconomy_mints")

def test_minting_flow():
    logger.info("Testing ScarCoin Minting Flow...")
    
    # Initialize Engine
    engine = ScarCoinMintingEngine()
    
    # Create Wallet
    wallet = engine.create_wallet()
    logger.info(f"Created wallet: {wallet.address}")
    
    # Simulate Transmutation
    transmutation_id = str(uuid.uuid4())
    scarindex_before = Decimal("0.60")
    scarindex_after = Decimal("0.75")
    efficiency = Decimal("0.90")
    
    # Mint Coin
    logger.info("Minting ScarCoin...")
    coin = engine.mint_scarcoin(
        transmutation_id=transmutation_id,
        scarindex_before=scarindex_before,
        scarindex_after=scarindex_after,
        transmutation_efficiency=efficiency,
        owner_address=wallet.address,
        oracle_signatures=["sig1", "sig2"] # Mock signatures
    )
    
    if not coin:
        logger.error("Minting failed!")
        return False
        
    logger.info(f"Minted Coin ID: {coin.id}")
    logger.info(f"Value: {coin.coin_value}")
    
    # Verify in Supabase
    logger.info("Verifying in Supabase...")
    supabase = get_supabase()
    res = supabase.table("scarcoin_mints").select("*").eq("id", coin.id).execute()
    
    if not res.data:
        logger.error("Coin not found in Supabase!")
        return False
        
    stored_coin = res.data[0]
    if float(stored_coin['amount']) != float(coin.coin_value):
        logger.error(f"Amount mismatch: {stored_coin['amount']} != {coin.coin_value}")
        return False
        
    logger.info("✅ Supabase verification successful!")
    
    # Clean up (optional, but good practice for tests)
    logger.info("Cleaning up test data...")
    supabase.table("scarcoin_mints").delete().eq("id", coin.id).execute()
    
    return True

if __name__ == "__main__":
    try:
        success = test_minting_flow()
        if success:
            logger.info("Test PASSED")
            sys.exit(0)
        else:
            logger.error("Test FAILED")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")
        sys.exit(1)
