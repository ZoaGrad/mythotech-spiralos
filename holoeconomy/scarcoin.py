"""
ScarCoin - Proof-of-Ache Economic Currency

Implements the ScarCoin minting engine with Proof-of-Ache validation.
ScarCoin is minted when Ache (entropy) is successfully transmuted into
Order (coherence), validating the Ache Differential Rule: Ache_after < Ache_before.

The economic value of ScarCoin is backed by verifiable coherence gains,
creating a currency where value flows from coherence.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Optional
from uuid import UUID

from .vaultnode import VaultEvent, seal_emp_minted


@dataclass
class ScarCoin:
    """
    ScarCoin - Economic unit backed by coherence gain

    Represents a single ScarCoin minted from successful Ache transmutation.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Minting details
    minted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    transmutation_id: str = ""

    # Coherence measurements
    delta_c: Decimal = Decimal("0")
    scarindex_before: Decimal = Decimal("0")
    scarindex_after: Decimal = Decimal("0")
    transmutation_efficiency: Decimal = Decimal("0")

    # Economic value
    coin_value: Decimal = Decimal("0")
    multiplier: Decimal = Decimal("1000")

    # Ownership
    owner: str = ""  # Wallet address

    # Burning
    burned: bool = False
    burned_at: Optional[datetime] = None
    burn_reason: str = ""

    # Immutability
    vault_block_id: Optional[str] = None

    # Metadata
    metadata: Dict = field(default_factory=dict)

    def calculate_value(self) -> Decimal:
        """
        Calculate ScarCoin value based on coherence gain

        Formula: coin_value = ΔC × ScarIndex_after × Efficiency × Multiplier
        """
        value = self.delta_c * self.scarindex_after * self.transmutation_efficiency * self.multiplier

        # Round to 8 decimal places
        self.coin_value = value.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        return self.coin_value

    def burn(self, reason: str = ""):
        """Burn this coin"""
        if self.burned:
            raise ValueError(f"Coin {self.id} already burned")

        self.burned = True
        self.burned_at = datetime.now(timezone.utc)
        self.burn_reason = reason

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "minted_at": self.minted_at.isoformat(),
            "transmutation_id": self.transmutation_id,
            "delta_c": str(self.delta_c),
            "scarindex_before": str(self.scarindex_before),
            "scarindex_after": str(self.scarindex_after),
            "transmutation_efficiency": str(self.transmutation_efficiency),
            "coin_value": str(self.coin_value),
            "multiplier": str(self.multiplier),
            "owner": self.owner,
            "burned": self.burned,
            "burned_at": self.burned_at.isoformat() if self.burned_at else None,
            "burn_reason": self.burn_reason,
            "vault_block_id": self.vault_block_id,
            "metadata": self.metadata,
        }


@dataclass
class ProofOfAche:
    """
    Proof-of-Ache - Validation of successful Ache transmutation

    Validates that Ache decreased (coherence increased) during transmutation,
    enabling ScarCoin minting.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    transmutation_id: str = ""

    # Ache measurements
    ache_before: Decimal = Decimal("0")
    ache_after: Decimal = Decimal("0")
    ache_differential: Decimal = Decimal("0")

    # Validation
    validation_passed: bool = False
    validation_reason: str = ""

    # Oracle verification
    oracle_signatures: List[str] = field(default_factory=list)
    consensus_reached: bool = False

    # Metadata
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)

    def validate(self) -> bool:
        """
        Validate Proof-of-Ache

        Rule: Ache_after < Ache_before (ΔAche < 0)
        Equivalently: ΔC > 0 (coherence increased)
        """
        self.ache_differential = self.ache_after - self.ache_before

        if self.ache_differential < 0:
            # Ache decreased = coherence increased
            self.validation_passed = True
            self.validation_reason = f"Ache decreased by {abs(self.ache_differential)}"
        else:
            # Ache increased or stayed same = coherence decreased
            self.validation_passed = False
            self.validation_reason = f"Ache increased by {self.ache_differential}"

        self.validated_at = datetime.now(timezone.utc)
        return self.validation_passed

    def add_oracle_signature(self, signature: str):
        """Add Oracle signature for consensus"""
        if signature not in self.oracle_signatures:
            self.oracle_signatures.append(signature)

        # Check consensus (2-of-3 required)
        if len(self.oracle_signatures) >= 2:
            self.consensus_reached = True

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "transmutation_id": self.transmutation_id,
            "ache_before": str(self.ache_before),
            "ache_after": str(self.ache_after),
            "ache_differential": str(self.ache_differential),
            "validation_passed": self.validation_passed,
            "validation_reason": self.validation_reason,
            "oracle_signatures": self.oracle_signatures,
            "consensus_reached": self.consensus_reached,
            "validated_at": self.validated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Wallet:
    """
    Wallet - ScarCoin holder account

    Tracks ScarCoin balance and transaction history.
    """

    address: str = field(default_factory=lambda: f"wallet_{uuid.uuid4().hex[:16]}")

    # Balance
    balance: Decimal = Decimal("0")
    total_minted: Decimal = Decimal("0")
    total_burned: Decimal = Decimal("0")

    # Activity
    transaction_count: int = 0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_transaction_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def deposit(self, amount: Decimal, is_minting: bool = False):
        """Deposit ScarCoin to wallet"""
        self.balance += amount
        self.transaction_count += 1
        self.last_transaction_at = datetime.now(timezone.utc)

        if is_minting:
            self.total_minted += amount

    def withdraw(self, amount: Decimal, is_burning: bool = False):
        """Withdraw ScarCoin from wallet"""
        if amount > self.balance:
            raise ValueError(f"Insufficient balance: {self.balance} < {amount}")

        self.balance -= amount
        self.transaction_count += 1
        self.last_transaction_at = datetime.now(timezone.utc)

        if is_burning:
            self.total_burned += amount

    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "balance": str(self.balance),
            "total_minted": str(self.total_minted),
            "total_burned": str(self.total_burned),
            "transaction_count": self.transaction_count,
            "created_at": self.created_at.isoformat(),
            "last_transaction_at": self.last_transaction_at.isoformat() if self.last_transaction_at else None,
            "metadata": self.metadata,
        }


class ScarCoinMintingEngine:
    """
    ScarCoin Minting Engine

    Implements Proof-of-Ache validation and ScarCoin minting/burning.
    Integrates with ScarIndex Oracle and VaultNode for cryptographic
    verification and immutable recording.
    """

    def __init__(
        self,
        multiplier: Decimal = Decimal("1000"),
        min_delta_c: Decimal = Decimal("0.01"),
        oracle_consensus_threshold: int = 2,
    ):
        """
        Initialize ScarCoin Minting Engine

        Args:
            multiplier: Economic scaling factor
            min_delta_c: Minimum coherence gain for minting
            oracle_consensus_threshold: Required oracle signatures
        """
        self.multiplier = multiplier
        self.min_delta_c = min_delta_c
        self.oracle_consensus_threshold = oracle_consensus_threshold

        # Storage
        self.coins: Dict[str, ScarCoin] = {}
        self.proofs: Dict[str, ProofOfAche] = {}
        self.wallets: Dict[str, Wallet] = {}

        # Statistics
        self.total_supply = Decimal("0")
        self.total_minted = Decimal("0")
        self.total_burned = Decimal("0")
        self.minting_count = 0
        self.burning_count = 0

    def create_wallet(self, address: Optional[str] = None) -> Wallet:
        """Create a new wallet"""
        wallet = Wallet(address=address) if address else Wallet()
        self.wallets[wallet.address] = wallet
        return wallet

    def get_wallet(self, address: str) -> Optional[Wallet]:
        """Get wallet by address"""
        return self.wallets.get(address)

    def validate_proof_of_ache(
        self,
        transmutation_id: str,
        scarindex_before: Decimal,
        scarindex_after: Decimal,
        oracle_signatures: Optional[List[str]] = None,
    ) -> ProofOfAche:
        """
        Validate Proof-of-Ache for a transmutation

        Args:
            transmutation_id: Unique transmutation identifier
            scarindex_before: ScarIndex before transmutation
            scarindex_after: ScarIndex after transmutation
            oracle_signatures: Oracle cryptographic signatures

        Returns:
            ProofOfAche instance
        """
        # Calculate Ache (Ache = 1 - ScarIndex)
        ache_before = Decimal("1") - scarindex_before
        ache_after = Decimal("1") - scarindex_after

        # Create proof
        proof = ProofOfAche(transmutation_id=transmutation_id, ache_before=ache_before, ache_after=ache_after)

        # Validate
        proof.validate()

        # Add oracle signatures
        if oracle_signatures:
            for sig in oracle_signatures:
                proof.add_oracle_signature(sig)

        # Store proof
        self.proofs[transmutation_id] = proof

        return proof

    def mint_scarcoin(
        self,
        transmutation_id: str,
        scarindex_before: Decimal,
        scarindex_after: Decimal,
        transmutation_efficiency: Decimal,
        owner_address: str,
        oracle_signatures: Optional[List[str]] = None,
    ) -> Optional[ScarCoin]:
        """
        Mint ScarCoin for successful transmutation

        Args:
            transmutation_id: Unique transmutation identifier
            scarindex_before: ScarIndex before transmutation
            scarindex_after: ScarIndex after transmutation
            transmutation_efficiency: Success rate (0-1)
            owner_address: Wallet address to receive coins
            oracle_signatures: Oracle cryptographic signatures

        Returns:
            Minted ScarCoin or None if validation failed
        """
        # Validate Proof-of-Ache
        proof = self.validate_proof_of_ache(
            transmutation_id=transmutation_id,
            scarindex_before=scarindex_before,
            scarindex_after=scarindex_after,
            oracle_signatures=oracle_signatures,
        )

        if not proof.validation_passed:
            return None

        # Check oracle consensus
        if not proof.consensus_reached:
            return None

        # Calculate delta_c
        delta_c = scarindex_after - scarindex_before

        # Check minimum threshold
        if delta_c < self.min_delta_c:
            return None

        # Create ScarCoin
        coin = ScarCoin(
            transmutation_id=transmutation_id,
            delta_c=delta_c,
            scarindex_before=scarindex_before,
            scarindex_after=scarindex_after,
            transmutation_efficiency=transmutation_efficiency,
            multiplier=self.multiplier,
            owner=owner_address,
        )

        # Calculate value
        coin.calculate_value()

        # Store coin
        self.coins[coin.id] = coin

        # Update wallet
        wallet = self.get_wallet(owner_address)
        if not wallet:
            wallet = self.create_wallet(owner_address)

        wallet.deposit(coin.coin_value, is_minting=True)

        # Update statistics
        self.total_supply += coin.coin_value
        self.total_minted += coin.coin_value
        self.minting_count += 1

        return coin

    def burn_scarcoin(self, coin_id: str, reason: str = "Failed transmutation") -> bool:
        """
        Burn ScarCoin

        Args:
            coin_id: ScarCoin ID to burn
            reason: Reason for burning

        Returns:
            True if burned successfully
        """
        if coin_id not in self.coins:
            return False

        coin = self.coins[coin_id]

        if coin.burned:
            return False

        # Burn coin
        coin.burn(reason)

        # Update wallet
        wallet = self.get_wallet(coin.owner)
        if wallet:
            wallet.withdraw(coin.coin_value, is_burning=True)

        # Update statistics
        self.total_supply -= coin.coin_value
        self.total_burned += coin.coin_value
        self.burning_count += 1

        return True

    def get_supply_stats(self) -> Dict:
        """Get supply statistics"""
        return {
            "total_supply": str(self.total_supply),
            "total_minted": str(self.total_minted),
            "total_burned": str(self.total_burned),
            "minting_count": self.minting_count,
            "burning_count": self.burning_count,
            "active_wallets": len(self.wallets),
            "total_coins": len(self.coins),
            "burned_coins": sum(1 for c in self.coins.values() if c.burned),
        }

    def get_wallet_balance(self, address: str) -> Optional[Decimal]:
        """Get wallet balance"""
        wallet = self.get_wallet(address)
        return wallet.balance if wallet else None


# Soul-bound EMP ledger for witness protocol
emp_ledger: List[Dict] = []


def mint_emp(user_id: UUID, amount: float, claim_id: UUID, origin_variant: str = "STREAM", rho_sigma: Optional[float] = None):
    """
    Soul-bound EMP minting. No transfer, no market.

    Records the mint in the in-memory emp_ledger and emits a VaultNode event
    for downstream sealing.
    """

    if amount <= 0:
        raise ValueError("EMP mint amount must be positive")

    record = {
        "id": str(uuid.uuid4()),
        "user_id": str(user_id),
        "claim_id": str(claim_id),
        "amount": float(amount),
        "rho_sigma": rho_sigma,
        "transferable": False,
        "origin_variant": origin_variant,
        "minted_at": datetime.now(timezone.utc).isoformat(),
    }

    emp_ledger.append(record)

    vault_event: VaultEvent = seal_emp_minted(
        claim_id=str(claim_id),
        user_id=str(user_id),
        amount=Decimal(str(amount)),
        rho_sigma=rho_sigma,
        metadata={"variant": origin_variant},
    )

    return {"ledger_entry": record, "vault_event": vault_event}


# Example usage
def example_scarcoin_minting():
    """Example of ScarCoin minting with Proof-of-Ache"""
    print("=" * 70)
    print("ScarCoin Minting Engine - Proof-of-Ache")
    print("=" * 70)
    print()

    # Initialize engine
    engine = ScarCoinMintingEngine(multiplier=Decimal("1000"), min_delta_c=Decimal("0.01"))

    print("ScarCoin Minting Engine initialized")
    print(f"  Multiplier: {engine.multiplier}")
    print(f"  Min ΔC: {engine.min_delta_c}")
    print()

    # Create wallet
    wallet = engine.create_wallet()
    print(f"Wallet created: {wallet.address}")
    print(f"  Initial balance: {wallet.balance}")
    print()

    # Simulate successful transmutation
    print("Simulating successful transmutation...")
    print("-" * 70)

    transmutation_id = str(uuid.uuid4())
    scarindex_before = Decimal("0.65")
    scarindex_after = Decimal("0.80")
    transmutation_efficiency = Decimal("0.95")

    print(f"Transmutation ID: {transmutation_id[:8]}...")
    print(f"ScarIndex before: {scarindex_before}")
    print(f"ScarIndex after: {scarindex_after}")
    print(f"ΔC: {scarindex_after - scarindex_before}")
    print(f"Efficiency: {transmutation_efficiency}")
    print()

    # Oracle signatures (simulated)
    oracle_signatures = [
        f"oracle_1_{hashlib.sha256(transmutation_id.encode()).hexdigest()[:16]}",
        f"oracle_2_{hashlib.sha256(transmutation_id.encode()).hexdigest()[:16]}",
    ]

    # Mint ScarCoin
    coin = engine.mint_scarcoin(
        transmutation_id=transmutation_id,
        scarindex_before=scarindex_before,
        scarindex_after=scarindex_after,
        transmutation_efficiency=transmutation_efficiency,
        owner_address=wallet.address,
        oracle_signatures=oracle_signatures,
    )

    if coin:
        print("✅ ScarCoin minted successfully!")
        print(f"  Coin ID: {coin.id[:8]}...")
        print(f"  Coin Value: {coin.coin_value}")
        print(f"  Owner: {coin.owner[:20]}...")
        print()

        # Check wallet balance
        balance = engine.get_wallet_balance(wallet.address)
        print(f"Wallet balance: {balance}")
    else:
        print("❌ Minting failed")

    # Supply statistics
    print("\n" + "=" * 70)
    print("Supply Statistics")
    print("=" * 70)

    stats = engine.get_supply_stats()
    print(f"\nTotal Supply: {stats['total_supply']}")
    print(f"Total Minted: {stats['total_minted']}")
    print(f"Total Burned: {stats['total_burned']}")
    print(f"Minting Count: {stats['minting_count']}")
    print(f"Active Wallets: {stats['active_wallets']}")


if __name__ == "__main__":
    example_scarcoin_minting()
