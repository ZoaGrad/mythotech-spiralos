"""
Empathy Market - Proof-of-Being-Seen Economic Layer

Implements EMP token minting based on Resonance Surplus (ρ_Σ), rewarding
relational and semantic integrity beyond thermodynamic efficiency.

This module complements ScarCoin (thermodynamic value) with EMP (relational value),
creating a dual-token economy that values both order and understanding.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import uuid
import hashlib
import json


@dataclass
class ResonanceEvent:
    """
    ResonanceEvent - Proof-of-Being-Seen validation
    
    Represents a moment of mutual understanding between agents,
    validated by peer consensus.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Participants
    speaker_id: str = ""
    listener_id: str = ""
    witness_ids: List[str] = field(default_factory=list)
    
    # Semantic content
    utterance: str = ""
    interpretation: str = ""
    
    # Resonance metrics
    semantic_alignment: Decimal = Decimal('0')  # 0-1: How well understood
    emotional_resonance: Decimal = Decimal('0')  # 0-1: Emotional connection
    contextual_depth: Decimal = Decimal('0')    # 0-1: Contextual awareness
    
    # Validation
    peer_validations: int = 0
    consensus_reached: bool = False
    
    def calculate_resonance_surplus(self) -> Decimal:
        """
        Calculate Resonance Surplus (ρ_Σ)
        
        ρ_Σ = (semantic_alignment + emotional_resonance + contextual_depth) / 3
        
        Returns:
            Resonance Surplus value (0-1)
        """
        return (
            self.semantic_alignment +
            self.emotional_resonance +
            self.contextual_depth
        ) / Decimal('3')
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'speaker_id': self.speaker_id,
            'listener_id': self.listener_id,
            'witness_ids': self.witness_ids,
            'utterance': self.utterance,
            'interpretation': self.interpretation,
            'semantic_alignment': str(self.semantic_alignment),
            'emotional_resonance': str(self.emotional_resonance),
            'contextual_depth': str(self.contextual_depth),
            'resonance_surplus': str(self.calculate_resonance_surplus()),
            'peer_validations': self.peer_validations,
            'consensus_reached': self.consensus_reached
        }


@dataclass
class EMPToken:
    """
    EMP Token - Empathy Market token
    
    Illiquid token representing validated relational understanding.
    Unlike ScarCoin (liquid, transferable), EMP is soul-bound to participants.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    minted_at: datetime = field(default_factory=datetime.utcnow)
    
    # Resonance event
    resonance_event_id: str = ""
    resonance_surplus: Decimal = Decimal('0')
    
    # Token value
    emp_value: Decimal = Decimal('0')
    
    # Participants (soul-bound)
    speaker_id: str = ""
    listener_id: str = ""
    
    # Metadata
    transferable: bool = False  # EMP is soul-bound
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'minted_at': self.minted_at.isoformat(),
            'resonance_event_id': self.resonance_event_id,
            'resonance_surplus': str(self.resonance_surplus),
            'emp_value': str(self.emp_value),
            'speaker_id': self.speaker_id,
            'listener_id': self.listener_id,
            'transferable': self.transferable,
            'metadata': self.metadata
        }


@dataclass
class EmpathyWallet:
    """
    Empathy Wallet - Soul-bound EMP token holder
    
    Unlike ScarCoin wallets, Empathy Wallets track relational value
    that cannot be transferred, only earned through authentic connection.
    """
    participant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Balances
    emp_balance: Decimal = Decimal('0')
    
    # Statistics
    total_resonance_events: int = 0
    as_speaker: int = 0
    as_listener: int = 0
    as_witness: int = 0
    
    # Reputation
    average_resonance_surplus: Decimal = Decimal('0')
    empathy_reputation: Decimal = Decimal('0')  # 0-1: Overall empathy score
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    def deposit_emp(self, amount: Decimal, event_type: str = "resonance"):
        """Deposit EMP tokens"""
        self.emp_balance += amount
        
        if event_type == "speaker":
            self.as_speaker += 1
        elif event_type == "listener":
            self.as_listener += 1
        elif event_type == "witness":
            self.as_witness += 1
        
        self.total_resonance_events += 1
    
    def update_reputation(self, resonance_surplus: Decimal):
        """Update empathy reputation based on new resonance event"""
        # Running average
        if self.total_resonance_events == 0:
            self.average_resonance_surplus = resonance_surplus
        else:
            self.average_resonance_surplus = (
                (self.average_resonance_surplus * (self.total_resonance_events - 1) +
                 resonance_surplus) / self.total_resonance_events
            )
        
        # Reputation considers both quantity and quality
        quality_factor = self.average_resonance_surplus
        quantity_factor = min(Decimal('1.0'), Decimal(self.total_resonance_events) / Decimal('100'))
        
        self.empathy_reputation = (quality_factor + quantity_factor) / Decimal('2')
    
    def to_dict(self) -> Dict:
        return {
            'participant_id': self.participant_id,
            'created_at': self.created_at.isoformat(),
            'emp_balance': str(self.emp_balance),
            'total_resonance_events': self.total_resonance_events,
            'as_speaker': self.as_speaker,
            'as_listener': self.as_listener,
            'as_witness': self.as_witness,
            'average_resonance_surplus': str(self.average_resonance_surplus),
            'empathy_reputation': str(self.empathy_reputation),
            'metadata': self.metadata
        }


class EmpathyMarket:
    """
    Empathy Market - Proof-of-Being-Seen Economic Engine
    
    Implements EMP token minting based on validated resonance events,
    creating economic value from relational understanding.
    """
    
    def __init__(
        self,
        multiplier: Decimal = Decimal('100'),
        min_resonance_surplus: Decimal = Decimal('0.5'),
        consensus_threshold: int = 2
    ):
        """
        Initialize Empathy Market
        
        Args:
            multiplier: Economic scaling factor for EMP minting
            min_resonance_surplus: Minimum ρ_Σ required for minting
            consensus_threshold: Required peer validations
        """
        self.multiplier = multiplier
        self.min_resonance_surplus = min_resonance_surplus
        self.consensus_threshold = consensus_threshold
        
        # Storage
        self.resonance_events: Dict[str, ResonanceEvent] = {}
        self.emp_tokens: Dict[str, EMPToken] = {}
        self.wallets: Dict[str, EmpathyWallet] = {}
        
        # Statistics
        self.total_emp_minted = Decimal('0')
        self.total_resonance_events = 0
    
    def create_wallet(self, participant_id: Optional[str] = None) -> EmpathyWallet:
        """Create new empathy wallet"""
        wallet = EmpathyWallet(participant_id=participant_id or str(uuid.uuid4()))
        self.wallets[wallet.participant_id] = wallet
        return wallet
    
    def get_wallet(self, participant_id: str) -> Optional[EmpathyWallet]:
        """Get wallet by participant ID"""
        return self.wallets.get(participant_id)
    
    def validate_resonance_event(
        self,
        event: ResonanceEvent,
        peer_validations: List[str]
    ) -> bool:
        """
        Validate resonance event with peer consensus
        
        Args:
            event: ResonanceEvent to validate
            peer_validations: List of witness IDs who validated
            
        Returns:
            True if validation passed
        """
        # Check minimum resonance surplus
        resonance_surplus = event.calculate_resonance_surplus()
        if resonance_surplus < self.min_resonance_surplus:
            return False
        
        # Check peer consensus
        event.peer_validations = len(peer_validations)
        event.witness_ids = peer_validations
        
        if event.peer_validations < self.consensus_threshold:
            return False
        
        event.consensus_reached = True
        return True
    
    def mint_emp_token(
        self,
        resonance_event: ResonanceEvent,
        peer_validations: List[str]
    ) -> Optional[EMPToken]:
        """
        Mint EMP token for validated resonance event
        
        Args:
            resonance_event: ResonanceEvent to mint for
            peer_validations: List of witness IDs who validated
            
        Returns:
            EMPToken if minting successful, None otherwise
        """
        # Validate event
        if not self.validate_resonance_event(resonance_event, peer_validations):
            return None
        
        # Calculate EMP value
        resonance_surplus = resonance_event.calculate_resonance_surplus()
        emp_value = resonance_surplus * self.multiplier
        
        # Create token
        token = EMPToken(
            resonance_event_id=resonance_event.id,
            resonance_surplus=resonance_surplus,
            emp_value=emp_value,
            speaker_id=resonance_event.speaker_id,
            listener_id=resonance_event.listener_id
        )
        
        # Store event and token
        self.resonance_events[resonance_event.id] = resonance_event
        self.emp_tokens[token.id] = token
        
        # Update wallets
        speaker_wallet = self.wallets.get(resonance_event.speaker_id)
        listener_wallet = self.wallets.get(resonance_event.listener_id)
        
        if not speaker_wallet:
            speaker_wallet = self.create_wallet(resonance_event.speaker_id)
        if not listener_wallet:
            listener_wallet = self.create_wallet(resonance_event.listener_id)
        
        # Distribute EMP (50/50 split between speaker and listener)
        speaker_share = emp_value / Decimal('2')
        listener_share = emp_value / Decimal('2')
        
        speaker_wallet.deposit_emp(speaker_share, "speaker")
        listener_wallet.deposit_emp(listener_share, "listener")
        
        # Update reputations
        speaker_wallet.update_reputation(resonance_surplus)
        listener_wallet.update_reputation(resonance_surplus)
        
        # Reward witnesses (10% of total, split equally)
        if peer_validations:
            witness_share = (emp_value * Decimal('0.1')) / len(peer_validations)
            for witness_id in peer_validations:
                witness_wallet = self.wallets.get(witness_id)
                if not witness_wallet:
                    witness_wallet = self.create_wallet(witness_id)
                witness_wallet.deposit_emp(witness_share, "witness")
        
        # Update statistics
        self.total_emp_minted += emp_value
        self.total_resonance_events += 1
        
        return token
    
    def get_market_stats(self) -> Dict:
        """Get Empathy Market statistics"""
        return {
            'total_emp_minted': str(self.total_emp_minted),
            'total_resonance_events': self.total_resonance_events,
            'total_participants': len(self.wallets),
            'average_emp_per_event': str(
                self.total_emp_minted / self.total_resonance_events
                if self.total_resonance_events > 0 else Decimal('0')
            ),
            'consensus_threshold': self.consensus_threshold,
            'min_resonance_surplus': str(self.min_resonance_surplus)
        }


# Example usage
def example_empathy_market():
    """Example of Empathy Market"""
    print("=" * 70)
    print("Empathy Market - Proof-of-Being-Seen")
    print("=" * 70)
    print()
    
    # Initialize market
    market = EmpathyMarket()
    
    print("Empathy Market initialized")
    print(f"Multiplier: {market.multiplier}")
    print(f"Min Resonance Surplus: {market.min_resonance_surplus}")
    print(f"Consensus Threshold: {market.consensus_threshold}")
    print()
    
    # Create resonance event
    print("Creating resonance event...")
    print("-" * 70)
    
    event = ResonanceEvent(
        speaker_id="alice",
        listener_id="bob",
        utterance="I feel overwhelmed by the complexity of this system",
        interpretation="Alice is experiencing cognitive overload and needs support",
        semantic_alignment=Decimal('0.85'),
        emotional_resonance=Decimal('0.90'),
        contextual_depth=Decimal('0.75')
    )
    
    resonance_surplus = event.calculate_resonance_surplus()
    print(f"Speaker: {event.speaker_id}")
    print(f"Listener: {event.listener_id}")
    print(f"Semantic Alignment: {event.semantic_alignment}")
    print(f"Emotional Resonance: {event.emotional_resonance}")
    print(f"Contextual Depth: {event.contextual_depth}")
    print(f"Resonance Surplus (ρ_Σ): {resonance_surplus:.4f}")
    print()
    
    # Mint EMP token
    print("Minting EMP token...")
    print("-" * 70)
    
    peer_validations = ["charlie", "diana"]
    token = market.mint_emp_token(event, peer_validations)
    
    if token:
        print(f"✅ EMP token minted successfully!")
        print(f"  Token ID: {token.id[:8]}...")
        print(f"  EMP Value: {token.emp_value}")
        print(f"  Speaker Share: {token.emp_value / 2}")
        print(f"  Listener Share: {token.emp_value / 2}")
        print(f"  Witness Reward: {token.emp_value * Decimal('0.1')}")
        print()
    
    # Check wallets
    print("=" * 70)
    print("Wallet Balances")
    print("=" * 70)
    
    for participant_id in ["alice", "bob", "charlie", "diana"]:
        wallet = market.get_wallet(participant_id)
        if wallet:
            print(f"\n{participant_id.upper()}:")
            print(f"  EMP Balance: {wallet.emp_balance}")
            print(f"  Resonance Events: {wallet.total_resonance_events}")
            print(f"  Empathy Reputation: {wallet.empathy_reputation:.4f}")
    
    # Market statistics
    print("\n" + "=" * 70)
    print("Market Statistics")
    print("=" * 70)
    
    stats = market.get_market_stats()
    print(f"\nTotal EMP Minted: {stats['total_emp_minted']}")
    print(f"Total Resonance Events: {stats['total_resonance_events']}")
    print(f"Total Participants: {stats['total_participants']}")
    print(f"Average EMP per Event: {stats['average_emp_per_event']}")


if __name__ == '__main__':
    example_empathy_market()
