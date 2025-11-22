import sys
import os

# Ensure python can find the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, List, Any
from src.core.database import create_wallet, get_wallet_balance, execute_transfer, get_vault_client

class LedgerManager:
    """
    The Manager of the Ledger of Souls.
    Handles high-level economic interactions, ensuring wallet existence and transaction safety.
    """
    
    def __init__(self):
        self.client = get_vault_client()

    def ensure_wallet(self, user_id: str):
        """Ensures a wallet exists for the user."""
        # We check balance first? Or just try create.
        # create_wallet uses upsert/ignore, so it's safe.
        create_wallet(user_id)

    def get_balance(self, user_id: str) -> float:
        """Returns the SCAR balance for a user."""
        return get_wallet_balance(user_id)

    def transfer(self, sender: str, receiver: str, amount: float) -> Dict[str, Any]:
        """
        Executes a P2P transfer.
        
        Args:
            sender: User ID of sender.
            receiver: User ID of receiver.
            amount: Amount of SCAR to transfer.
            
        Returns:
            dict: {'success': bool, 'message': str, 'new_balance': float}
        """
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive.", "new_balance": self.get_balance(sender)}

        # 1. Ensure Receiver has a wallet (The Pocket must exist to catch the coin)
        self.ensure_wallet(receiver)
        
        # 2. Execute Transfer via Database RPC (The Hand)
        success = execute_transfer(sender, receiver, amount)
        
        if success:
            new_bal = self.get_balance(sender)
            return {"success": True, "message": "Transfer successful.", "new_balance": new_bal}
        else:
            # Could be insufficient funds or system error.
            # We check balance to hint why.
            current_bal = self.get_balance(sender)
            if current_bal < amount:
                return {"success": False, "message": "Insufficient funds.", "new_balance": current_bal}
            else:
                return {"success": False, "message": "System error during transfer.", "new_balance": current_bal}

    def get_transaction_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Retrieves recent transactions for a user."""
        try:
            # Robust Fallback: Fetch Sent and Received separately and merge
            # This avoids the .or_ syntax ambiguity in different client versions
            
            # 1. Fetch Sent
            sent = self.client.table("transactions")\
                .select("*")\
                .eq("sender_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            sent_txs = sent.data if sent.data else []
            
            # 2. Fetch Received
            received = self.client.table("transactions")\
                .select("*")\
                .eq("receiver_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            recv_txs = received.data if received.data else []
            
            # 3. Merge and Sort
            all_txs = sent_txs + recv_txs
            # Sort by created_at desc
            all_txs.sort(key=lambda x: x['created_at'], reverse=True)
            
            return all_txs[:limit]
        except Exception as e:
            print(f"ERROR: Failed to fetch history for {user_id}: {e}")
            return []

# --- VERIFICATION VECTOR ---
if __name__ == "__main__":
    # Force UTF-8 for Windows Console compatibility or just use ASCII
    print(">>> DO.SW-PRIME // LEDGER VERIFICATION SEQUENCE <<<")
    
    ledger = LedgerManager()
    
    # Test Identities
    ARCHITECT = "sovereign_architect"
    GUARDIAN = "guardian_test_unit"
    
    # 1. Check Initial State
    arch_bal = ledger.get_balance(ARCHITECT)
    guard_bal = ledger.get_balance(GUARDIAN)
    print(f"Initial State | Architect: {arch_bal} SCAR | Guardian: {guard_bal} SCAR")
    
    # 2. Execute Transfer
    TRANSFER_AMOUNT = 10.0
    print(f"\nAttempting Transfer: {TRANSFER_AMOUNT} SCAR from {ARCHITECT} to {GUARDIAN}...")
    
    result = ledger.transfer(ARCHITECT, GUARDIAN, TRANSFER_AMOUNT)
    
    if result["success"]:
        print("Transfer: SUCCESS")
    else:
        print(f"Transfer: FAILED ({result['message']})")
        
    # 3. Verify Final State
    arch_bal_final = ledger.get_balance(ARCHITECT)
    guard_bal_final = ledger.get_balance(GUARDIAN)
    
    print(f"Sender Balance: {arch_bal_final:.4f}")
    print(f"Receiver Balance: {guard_bal_final:.4f}")
    
    # 4. Verify Transaction Log
    print("\nVerifying Transaction Log...")
    history = ledger.get_transaction_history(ARCHITECT, limit=1)
    if history:
        last_tx = history[0]
        print(f"Last Tx: {last_tx['sender_id']} -> {last_tx['receiver_id']} : {last_tx['amount']} SCAR")
    else:
        print("WARNING: No transaction log found.")

    print("\n>>> LEDGER VERIFICATION COMPLETE <<<")
