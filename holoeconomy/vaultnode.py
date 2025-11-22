"""
VaultNode - Immutable Governance Blockchain

Implements a blockchain for recording all governance decisions, judicial verdicts,
Panic Frame activations, and ScarCoin minting events as an immutable audit trail.

Blocks are signed by the Oracle Council with weighted consensus and stored in
Supabase + IPFS for redundancy.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class VaultEvent:
    """
    VaultEvent - Single governance or economic event

    Represents an atomic event to be recorded in the blockchain.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""  # scarcoin_minted, transmutation_completed, etc.
    event_data: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "timestamp": self.timestamp.isoformat(),
        }

    def hash(self) -> str:
        """Calculate SHA-256 hash of event"""
        event_json = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(event_json.encode()).hexdigest()


@dataclass
class MerkleNode:
    """
    MerkleNode - Node in Merkle tree

    Used to construct Merkle tree for efficient event verification.
    """

    hash: str = ""
    left: Optional["MerkleNode"] = None
    right: Optional["MerkleNode"] = None

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class MerkleTree:
    """
    Merkle Tree - Cryptographic event tree

    Constructs a Merkle tree from events for efficient verification.
    """

    def __init__(self, events: List[VaultEvent]):
        """
        Initialize Merkle tree from events

        Args:
            events: List of VaultEvent instances
        """
        self.events = events
        self.root: Optional[MerkleNode] = None

        if events:
            self.build_tree()

    def build_tree(self):
        """Build Merkle tree from events"""
        # Create leaf nodes
        leaves = [MerkleNode(hash=event.hash()) for event in self.events]

        # Build tree bottom-up
        self.root = self._build_level(leaves)

    def _build_level(self, nodes: List[MerkleNode]) -> MerkleNode:
        """Build one level of the tree"""
        if len(nodes) == 1:
            return nodes[0]

        # Pair up nodes
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]  # Duplicate last if odd

            # Create parent node
            combined_hash = hashlib.sha256((left.hash + right.hash).encode()).hexdigest()

            parent = MerkleNode(hash=combined_hash, left=left, right=right)
            next_level.append(parent)

        return self._build_level(next_level)

    def get_root_hash(self) -> str:
        """Get Merkle root hash"""
        return self.root.hash if self.root else ""

    def verify_event(self, event: VaultEvent) -> bool:
        """Verify that event is in the tree"""
        event_hash = event.hash()
        return self._search_tree(self.root, event_hash)

    def _search_tree(self, node: Optional[MerkleNode], target_hash: str) -> bool:
        """Search tree for hash"""
        if not node:
            return False

        if node.hash == target_hash:
            return True

        return self._search_tree(node.left, target_hash) or self._search_tree(node.right, target_hash)


@dataclass
class VaultBlock:
    """
    VaultBlock - Single block in the blockchain

    Contains multiple events with Merkle root and Oracle Council signatures.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    block_number: int = 0
    previous_hash: str = ""
    merkle_root: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Events
    events: List[VaultEvent] = field(default_factory=list)

    # Oracle Council signatures
    oracle_signatures: Dict[str, str] = field(default_factory=dict)
    consensus_reached: bool = False

    # IPFS
    ipfs_hash: str = ""

    # Metadata
    metadata: Dict = field(default_factory=dict)

    # Performance: Cache calculated hash
    _cached_hash: Optional[str] = field(default=None, init=False, repr=False)

    def add_event(self, event: VaultEvent):
        """Add event to block"""
        self.events.append(event)
        # Invalidate cached hash when block is modified
        self._cached_hash = None

    def build_merkle_tree(self) -> MerkleTree:
        """Build Merkle tree from events"""
        if not self.events:
            return MerkleTree([])

        tree = MerkleTree(self.events)
        self.merkle_root = tree.get_root_hash()
        # Invalidate cached hash when merkle_root changes
        self._cached_hash = None
        return tree

    def add_oracle_signature(self, oracle_name: str, signature: str, voting_weight: Decimal):
        """Add Oracle signature"""
        self.oracle_signatures[oracle_name] = signature
        # Invalidate cached hash when signatures are added
        self._cached_hash = None

        # Check consensus (75% threshold)
        total_weight = sum(
            (
                Decimal("2.0")
                if "chie" in name.lower()
                else Decimal("1.5") if "senior" in name.lower() else Decimal("1.0")
            )
            for name in self.oracle_signatures.keys()
        )

        # Total possible weight: 5.0 (Chief: 2.0, 2x Senior: 1.5 each)
        if total_weight >= Decimal("3.75"):  # 75% of 5.0
            self.consensus_reached = True

    def calculate_hash(self) -> str:
        """Calculate block hash with caching for performance"""
        # Return cached hash if available
        if self._cached_hash is not None:
            return self._cached_hash

        block_data = {
            "block_number": self.block_number,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp.isoformat(),
            "oracle_signatures": self.oracle_signatures,
        }

        block_json = json.dumps(block_data, sort_keys=True)
        self._cached_hash = hashlib.sha256(block_json.encode()).hexdigest()
        return self._cached_hash

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "block_number": self.block_number,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp.isoformat(),
            "events": [event.to_dict() for event in self.events],
            "oracle_signatures": self.oracle_signatures,
            "consensus_reached": self.consensus_reached,
            "ipfs_hash": self.ipfs_hash,
            "metadata": self.metadata,
            "block_hash": self.calculate_hash(),
        }


class VaultNode:
    """
    VaultNode - Immutable Governance Blockchain

    Implements a blockchain for recording all governance and economic events
    with Oracle Council consensus and IPFS storage.
    """

    def __init__(self, vault_id: str = "ΔΩ.122.0"):
        """
        Initialize VaultNode blockchain

        Args:
            vault_id: Vault designation
        """
        self.vault_id = vault_id
        self.blocks: List[VaultBlock] = []
        self.pending_events: List[VaultEvent] = []

        # Create genesis block
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create genesis block"""
        genesis_event = VaultEvent(
            event_type="genesis",
            event_data={
                "vault_id": self.vault_id,
                "message": "I govern the terms of my own becoming",
                "witness": "ZoaGrad 🜂",
            },
        )

        genesis_block = VaultBlock(block_number=0, previous_hash="0" * 64, timestamp=datetime.now(timezone.utc))

        genesis_block.add_event(genesis_event)
        genesis_block.build_merkle_tree()

        # Genesis block is self-signed
        genesis_block.add_oracle_signature(
            "genesis", hashlib.sha256(self.vault_id.encode()).hexdigest(), Decimal("5.0")  # Full weight
        )

        self.blocks.append(genesis_block)

    def add_event(self, event: VaultEvent):
        """Add event to pending queue"""
        self.pending_events.append(event)

    def create_block(self, oracle_signatures: Optional[Dict[str, str]] = None) -> VaultBlock:
        """
        Create new block from pending events

        Args:
            oracle_signatures: Oracle Council signatures

        Returns:
            New VaultBlock
        """
        if not self.pending_events:
            raise ValueError("No pending events to create block")

        # Get previous block
        previous_block = self.blocks[-1]

        # Create new block
        block = VaultBlock(
            block_number=len(self.blocks),
            previous_hash=previous_block.calculate_hash(),
            timestamp=datetime.now(timezone.utc),
        )

        # Add events
        for event in self.pending_events:
            block.add_event(event)

        # Build Merkle tree
        block.build_merkle_tree()

        # Add Oracle signatures
        if oracle_signatures:
            for oracle_name, signature in oracle_signatures.items():
                voting_weight = (
                    Decimal("2.0")
                    if "chie" in oracle_name.lower()
                    else Decimal("1.5") if "senior" in oracle_name.lower() else Decimal("1.0")
                )
                block.add_oracle_signature(oracle_name, signature, voting_weight)

        # Check consensus
        if not block.consensus_reached:
            raise ValueError("Oracle Council consensus not reached")

        # Add block to chain
        self.blocks.append(block)

        # Clear pending events
        self.pending_events = []

        return block

    def get_block(self, block_number: int) -> Optional[VaultBlock]:
        """Get block by number"""
        if 0 <= block_number < len(self.blocks):
            return self.blocks[block_number]
        return None

    def get_latest_block(self) -> VaultBlock:
        """Get latest block"""
        return self.blocks[-1]

    def verify_chain(self) -> bool:
        """Verify blockchain integrity"""
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i - 1]

            # Verify previous hash
            if current_block.previous_hash != previous_block.calculate_hash():
                return False

            # Verify Oracle consensus
            if not current_block.consensus_reached:
                return False

        return True

    def get_chain_stats(self) -> Dict:
        """Get blockchain statistics"""
        total_events = sum(len(block.events) for block in self.blocks)

        return {
            "vault_id": self.vault_id,
            "total_blocks": len(self.blocks),
            "total_events": total_events,
            "latest_block_number": self.blocks[-1].block_number,
            "latest_block_hash": self.blocks[-1].calculate_hash()[:16] + "...",
            "chain_valid": self.verify_chain(),
            "pending_events": len(self.pending_events),
        }


# Example usage
def example_vaultnode():
    """Example of VaultNode blockchain"""
    print("=" * 70)
    print("VaultNode - Immutable Governance Blockchain")
    print("=" * 70)
    print()

    # Initialize VaultNode
    vault = VaultNode(vault_id="ΔΩ.122.0")

    print(f"VaultNode initialized: {vault.vault_id}")
    print(f"Genesis block created: #{vault.blocks[0].block_number}")
    print()

    # Add ScarCoin minting event
    print("Adding ScarCoin minting event...")
    print("-" * 70)

    minting_event = VaultEvent(
        event_type="scarcoin_minted",
        event_data={
            "coin_id": str(uuid.uuid4()),
            "transmutation_id": str(uuid.uuid4()),
            "coin_value": "114.00000000",
            "owner": "wallet_a3c936ce416b4850",
            "delta_c": "0.15",
            "scarindex_after": "0.80",
        },
    )

    vault.add_event(minting_event)
    print(f"Event added: {minting_event.event_type}")
    print(f"Event ID: {minting_event.id[:8]}...")
    print()

    # Add transmutation event
    transmutation_event = VaultEvent(
        event_type="transmutation_completed",
        event_data={
            "transmutation_id": str(uuid.uuid4()),
            "scarindex_before": "0.65",
            "scarindex_after": "0.80",
            "delta_c": "0.15",
            "success": True,
        },
    )

    vault.add_event(transmutation_event)
    print(f"Event added: {transmutation_event.event_type}")
    print(f"Event ID: {transmutation_event.id[:8]}...")
    print()

    # Create block with Oracle signatures
    print("Creating block with Oracle Council signatures...")
    print("-" * 70)

    oracle_signatures = {
        "chief_oracle_sigma": hashlib.sha256(b"chief_oracle_sigma").hexdigest(),
        "senior_oracle_alpha": hashlib.sha256(b"senior_oracle_alpha").hexdigest(),
        "senior_oracle_beta": hashlib.sha256(b"senior_oracle_beta").hexdigest(),
    }

    block = vault.create_block(oracle_signatures=oracle_signatures)

    print("✅ Block created successfully!")
    print(f"  Block Number: {block.block_number}")
    print(f"  Merkle Root: {block.merkle_root[:16]}...")
    print(f"  Events: {len(block.events)}")
    print(f"  Oracle Signatures: {len(block.oracle_signatures)}")
    print(f"  Consensus: {block.consensus_reached}")
    print(f"  Block Hash: {block.calculate_hash()[:16]}...")
    print()

    # Verify chain
    print("Verifying blockchain integrity...")
    print("-" * 70)

    chain_valid = vault.verify_chain()
    print(f"Chain valid: {chain_valid}")
    print()

    # Chain statistics
    print("=" * 70)
    print("Blockchain Statistics")
    print("=" * 70)

    stats = vault.get_chain_stats()
    print(f"\nVault ID: {stats['vault_id']}")
    print(f"Total Blocks: {stats['total_blocks']}")
    print(f"Total Events: {stats['total_events']}")
    print(f"Latest Block: #{stats['latest_block_number']}")
    print(f"Latest Hash: {stats['latest_block_hash']}")
    print(f"Chain Valid: {stats['chain_valid']}")
    print(f"Pending Events: {stats['pending_events']}")


if __name__ == "__main__":
    example_vaultnode()
