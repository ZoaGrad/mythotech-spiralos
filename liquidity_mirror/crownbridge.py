"""
CrownBridge - Cross-Chain Asset Bridge with MPC Custody

Implements Multi-Party Computation (MPC) key shares for distributed custody
and 2-of-3 cryptographic verification for secure cross-chain asset transfers.

This is a proof-of-concept demonstrating constitutional liquidity principles
with distributed governance control over bridge assets.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid
import hashlib
import json
import secrets


class BridgeStatus(Enum):
    """Bridge transaction status"""
    INITIATED = "initiated"
    PENDING_SIGNATURES = "pending_signatures"
    SIGNED = "signed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GovernanceBranch(Enum):
    """Three-Branch Governance"""
    LEGISLATIVE = "legislative"  # F1 Witnesses/Sentinels
    JUDICIAL = "judicial"        # F2 Judges
    EXECUTIVE = "executive"      # F4 Panic Frames


@dataclass
class MPCKeyShare:
    """
    Multi-Party Computation Key Share
    
    Distributed across governance branches for constitutional custody.
    """
    share_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Governance assignment
    branch: GovernanceBranch = GovernanceBranch.LEGISLATIVE
    branch_member_id: str = ""
    
    # Key material (simplified - production would use threshold cryptography)
    share_data: str = field(default_factory=lambda: secrets.token_hex(32))
    public_key: str = field(default_factory=lambda: secrets.token_hex(64))
    
    # Metadata
    active: bool = True
    last_used_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'share_id': self.share_id,
            'created_at': self.created_at.isoformat(),
            'branch': self.branch.value,
            'branch_member_id': self.branch_member_id,
            'public_key': self.public_key,
            'active': self.active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }


@dataclass
class CryptographicSignature:
    """
    Cryptographic signature for bridge transaction
    
    Part of 2-of-3 verification protocol.
    """
    signature_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Signer
    share_id: str = ""
    branch: GovernanceBranch = GovernanceBranch.LEGISLATIVE
    signer_id: str = ""
    
    # Signature data (simplified)
    signature: str = ""
    message_hash: str = ""
    
    # Validation
    valid: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'signature_id': self.signature_id,
            'timestamp': self.timestamp.isoformat(),
            'share_id': self.share_id,
            'branch': self.branch.value,
            'signer_id': self.signer_id,
            'signature': self.signature,
            'message_hash': self.message_hash,
            'valid': self.valid
        }


@dataclass
class BridgeTransaction:
    """
    Cross-chain bridge transaction
    
    Requires 2-of-3 governance signatures for execution.
    """
    tx_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initiated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Chain details
    source_chain: str = ""
    dest_chain: str = ""
    
    # Asset details
    asset_id: str = ""
    asset_symbol: str = ""
    amount: Decimal = Decimal('0')
    
    # Addresses
    sender_address: str = ""
    receiver_address: str = ""
    
    # Status
    status: BridgeStatus = BridgeStatus.INITIATED
    
    # Signatures (2-of-3 required)
    signatures: List[CryptographicSignature] = field(default_factory=list)
    required_signatures: int = 2
    
    # Execution
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # VaultNode linkage
    vault_block_id: Optional[str] = None
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    def get_message_hash(self) -> str:
        """Generate message hash for signing"""
        message = f"{self.tx_id}:{self.source_chain}:{self.dest_chain}:{self.asset_id}:{self.amount}:{self.sender_address}:{self.receiver_address}"
        return hashlib.sha256(message.encode()).hexdigest()
    
    def has_sufficient_signatures(self) -> bool:
        """Check if transaction has sufficient valid signatures"""
        valid_signatures = [sig for sig in self.signatures if sig.valid]
        return len(valid_signatures) >= self.required_signatures
    
    def get_signature_branches(self) -> List[GovernanceBranch]:
        """Get branches that have signed"""
        return [sig.branch for sig in self.signatures if sig.valid]
    
    def to_dict(self) -> Dict:
        return {
            'tx_id': self.tx_id,
            'initiated_at': self.initiated_at.isoformat(),
            'source_chain': self.source_chain,
            'dest_chain': self.dest_chain,
            'asset_id': self.asset_id,
            'asset_symbol': self.asset_symbol,
            'amount': str(self.amount),
            'sender_address': self.sender_address,
            'receiver_address': self.receiver_address,
            'status': self.status.value,
            'signatures': [sig.to_dict() for sig in self.signatures],
            'required_signatures': self.required_signatures,
            'has_sufficient_signatures': self.has_sufficient_signatures(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'vault_block_id': self.vault_block_id
        }


class CrownBridge:
    """
    CrownBridge - Cross-Chain Asset Bridge
    
    Implements distributed MPC custody with 2-of-3 governance signature
    verification for constitutional liquidity across chains.
    """
    
    def __init__(self):
        """Initialize CrownBridge"""
        # MPC key shares
        self.key_shares: Dict[str, MPCKeyShare] = {}
        self.branch_shares: Dict[GovernanceBranch, List[str]] = {
            GovernanceBranch.LEGISLATIVE: [],
            GovernanceBranch.JUDICIAL: [],
            GovernanceBranch.EXECUTIVE: []
        }
        
        # Bridge transactions
        self.transactions: Dict[str, BridgeTransaction] = {}
        
        # Statistics
        self.total_transactions = 0
        self.total_volume = Decimal('0')
        self.successful_transactions = 0
        self.failed_transactions = 0
        
        # Initialize default key shares
        self._initialize_default_shares()
    
    def _initialize_default_shares(self):
        """Initialize default MPC key shares for each governance branch"""
        branches = [
            (GovernanceBranch.LEGISLATIVE, "sentinel_alpha"),
            (GovernanceBranch.JUDICIAL, "judge_beta"),
            (GovernanceBranch.EXECUTIVE, "panic_gamma")
        ]
        
        for branch, member_id in branches:
            share = self.create_key_share(branch, member_id)
            print(f"✅ Initialized {branch.value} key share: {share.share_id[:8]}...")
    
    def create_key_share(
        self,
        branch: GovernanceBranch,
        branch_member_id: str
    ) -> MPCKeyShare:
        """Create new MPC key share"""
        share = MPCKeyShare(
            branch=branch,
            branch_member_id=branch_member_id
        )
        
        self.key_shares[share.share_id] = share
        self.branch_shares[branch].append(share.share_id)
        
        return share
    
    def get_key_share(self, share_id: str) -> Optional[MPCKeyShare]:
        """Get key share by ID"""
        return self.key_shares.get(share_id)
    
    def get_branch_shares(self, branch: GovernanceBranch) -> List[MPCKeyShare]:
        """Get all key shares for a governance branch"""
        share_ids = self.branch_shares.get(branch, [])
        return [self.key_shares[sid] for sid in share_ids if sid in self.key_shares]
    
    def initiate_bridge_transaction(
        self,
        source_chain: str,
        dest_chain: str,
        asset_id: str,
        asset_symbol: str,
        amount: Decimal,
        sender_address: str,
        receiver_address: str
    ) -> BridgeTransaction:
        """Initiate cross-chain bridge transaction"""
        tx = BridgeTransaction(
            source_chain=source_chain,
            dest_chain=dest_chain,
            asset_id=asset_id,
            asset_symbol=asset_symbol,
            amount=amount,
            sender_address=sender_address,
            receiver_address=receiver_address,
            status=BridgeStatus.INITIATED
        )
        
        self.transactions[tx.tx_id] = tx
        self.total_transactions += 1
        
        return tx
    
    def sign_transaction(
        self,
        tx_id: str,
        share_id: str
    ) -> Optional[CryptographicSignature]:
        """
        Sign bridge transaction with MPC key share
        
        Args:
            tx_id: Transaction ID
            share_id: Key share ID
            
        Returns:
            CryptographicSignature if successful
        """
        tx = self.transactions.get(tx_id)
        share = self.key_shares.get(share_id)
        
        if not tx or not share:
            return None
        
        if not share.active:
            return None
        
        # Check if already signed by this branch
        existing_branches = tx.get_signature_branches()
        if share.branch in existing_branches:
            return None
        
        # Generate message hash
        message_hash = tx.get_message_hash()
        
        # Create signature (simplified - production would use actual cryptography)
        signature_data = hashlib.sha256(
            f"{message_hash}:{share.share_data}".encode()
        ).hexdigest()
        
        signature = CryptographicSignature(
            share_id=share_id,
            branch=share.branch,
            signer_id=share.branch_member_id,
            signature=signature_data,
            message_hash=message_hash,
            valid=True  # Simplified validation
        )
        
        # Add signature to transaction
        tx.signatures.append(signature)
        
        # Update key share usage
        share.last_used_at = datetime.utcnow()
        
        # Update transaction status
        if tx.has_sufficient_signatures():
            tx.status = BridgeStatus.SIGNED
        else:
            tx.status = BridgeStatus.PENDING_SIGNATURES
        
        return signature
    
    def execute_bridge_transaction(
        self,
        tx_id: str
    ) -> bool:
        """
        Execute bridge transaction after signature verification
        
        Requires 2-of-3 governance signatures.
        """
        tx = self.transactions.get(tx_id)
        if not tx:
            return False
        
        # Check sufficient signatures
        if not tx.has_sufficient_signatures():
            return False
        
        # Verify signatures are from different branches
        signature_branches = tx.get_signature_branches()
        if len(set(signature_branches)) < tx.required_signatures:
            return False
        
        # Execute transaction
        tx.status = BridgeStatus.EXECUTING
        tx.executed_at = datetime.utcnow()
        
        # Simulate execution (production would interact with actual chains)
        # ...
        
        # Complete transaction
        tx.status = BridgeStatus.COMPLETED
        tx.completed_at = datetime.utcnow()
        
        # Update statistics
        self.successful_transactions += 1
        self.total_volume += tx.amount
        
        return True
    
    def get_transaction(self, tx_id: str) -> Optional[BridgeTransaction]:
        """Get transaction by ID"""
        return self.transactions.get(tx_id)
    
    def get_bridge_stats(self) -> Dict:
        """Get bridge statistics"""
        return {
            'total_transactions': self.total_transactions,
            'successful_transactions': self.successful_transactions,
            'failed_transactions': self.failed_transactions,
            'success_rate': (
                self.successful_transactions / self.total_transactions * 100
                if self.total_transactions > 0 else 0
            ),
            'total_volume': str(self.total_volume),
            'total_key_shares': len(self.key_shares),
            'active_key_shares': sum(1 for share in self.key_shares.values() if share.active)
        }


# Example usage
def example_crownbridge():
    """Example of CrownBridge"""
    print("=" * 70)
    print("CrownBridge - Cross-Chain Asset Bridge with MPC Custody")
    print("=" * 70)
    print()
    
    # Initialize bridge
    print("Initializing CrownBridge...")
    print("-" * 70)
    bridge = CrownBridge()
    print()
    
    # Initiate bridge transaction
    print("Initiating bridge transaction...")
    print("-" * 70)
    
    tx = bridge.initiate_bridge_transaction(
        source_chain="SpiralOS",
        dest_chain="Hedera",
        asset_id="scar_001",
        asset_symbol="SCAR",
        amount=Decimal('1000'),
        sender_address="spiralos_alice",
        receiver_address="hedera_alice"
    )
    
    print(f"✅ Transaction initiated: {tx.tx_id[:8]}...")
    print(f"  Source: {tx.source_chain}")
    print(f"  Destination: {tx.dest_chain}")
    print(f"  Asset: {tx.amount} {tx.asset_symbol}")
    print(f"  Status: {tx.status.value}")
    print()
    
    # Get key shares for signing
    legislative_shares = bridge.get_branch_shares(GovernanceBranch.LEGISLATIVE)
    judicial_shares = bridge.get_branch_shares(GovernanceBranch.JUDICIAL)
    executive_shares = bridge.get_branch_shares(GovernanceBranch.EXECUTIVE)
    
    # Sign with Legislative branch
    print("Signing with Legislative branch (Sentinel)...")
    print("-" * 70)
    
    sig1 = bridge.sign_transaction(tx.tx_id, legislative_shares[0].share_id)
    if sig1:
        print(f"✅ Signature 1: {sig1.signature_id[:8]}...")
        print(f"  Branch: {sig1.branch.value}")
        print(f"  Signer: {sig1.signer_id}")
        print(f"  Valid: {sig1.valid}")
        print(f"  Transaction Status: {tx.status.value}")
        print()
    
    # Sign with Judicial branch
    print("Signing with Judicial branch (Judge)...")
    print("-" * 70)
    
    sig2 = bridge.sign_transaction(tx.tx_id, judicial_shares[0].share_id)
    if sig2:
        print(f"✅ Signature 2: {sig2.signature_id[:8]}...")
        print(f"  Branch: {sig2.branch.value}")
        print(f"  Signer: {sig2.signer_id}")
        print(f"  Valid: {sig2.valid}")
        print(f"  Transaction Status: {tx.status.value}")
        print(f"  Sufficient Signatures: {tx.has_sufficient_signatures()}")
        print()
    
    # Execute transaction
    print("Executing bridge transaction...")
    print("-" * 70)
    
    success = bridge.execute_bridge_transaction(tx.tx_id)
    if success:
        print(f"✅ Transaction executed successfully!")
        print(f"  Status: {tx.status.value}")
        print(f"  Executed At: {tx.executed_at.isoformat() if tx.executed_at else 'N/A'}")
        print(f"  Completed At: {tx.completed_at.isoformat() if tx.completed_at else 'N/A'}")
        print()
    
    # Bridge statistics
    print("=" * 70)
    print("Bridge Statistics")
    print("=" * 70)
    
    stats = bridge.get_bridge_stats()
    print(f"\nTotal Transactions: {stats['total_transactions']}")
    print(f"Successful Transactions: {stats['successful_transactions']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    print(f"Total Volume: {stats['total_volume']} SCAR")
    print(f"Total Key Shares: {stats['total_key_shares']}")
    print(f"Active Key Shares: {stats['active_key_shares']}")


if __name__ == '__main__':
    example_crownbridge()
