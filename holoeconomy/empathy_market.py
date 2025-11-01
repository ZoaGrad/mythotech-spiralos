"""
Empathy Market - Proof-of-Being-Seen Economic Layer

Implements EMP token minting based on Resonance Surplus (ρ_Σ), rewarding
relational and semantic integrity beyond thermodynamic efficiency.

Constitutional Safeguard: EMP burn validation via GlyphicBindingEngine
- coherence_score > 0.7 required
- verified witness declarations required
- relational_impact.permits_burn = True required

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
import sys
import os

# Add core module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.glyphic_binding_engine import GlyphicBindingEngine, Glyph, GlyphType, BindingStrength


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
    
    def calculate_resonance_surplus(self, attestors=0, pair_k=0) -> Decimal:
        """
        Calculates Resonance Surplus (rho_sigma) using Geometric Mean (Rec. 1.1)
        and applies pair-wise decay (Rec. A6) to suppress low-effort signaling.
        """
        # Constants from v2.1 VaultNode
        TAU_RHO_DECAY = 0.80
        RHO_MINT_THRESHOLD = 0.50

        if attestors < 2 or self.semantic_alignment < Decimal('0.001'):
             return Decimal('0.0') # AMM Oracle failure or min threshold not met

        # I1: Geometric Mean for balanced contribution (penalizes zero-scores)
        base_rho = (self.semantic_alignment * self.emotional_resonance * self.contextual_depth) ** (Decimal('1')/Decimal('3'))

        # A6: Apply pair-wise decay (tau_rho^k)
        marginal_rho = base_rho * (Decimal(str(TAU_RHO_DECAY)) ** pair_k)

        if marginal_rho < Decimal(str(RHO_MINT_THRESHOLD)):
            return Decimal('0.0')

        return marginal_rho
    
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


@dataclass
class BurnValidation:
    """
    EMP Burn Validation via GlyphicBindingEngine
    
    Constitutional requirements for burning EMP tokens:
    1. coherence_score > 0.7
    2. verified witness declarations
    3. relational_impact.permits_burn = True
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str = ""
    amount: Decimal = Decimal('0')
    
    # GBE validation
    coherence_score: float = 0.0
    witness_count: int = 0
    witness_declarations: List[str] = field(default_factory=list)
    
    # Relational impact
    relational_impact: Dict = field(default_factory=dict)
    permits_burn: bool = False
    
    # Validation result
    is_valid: bool = False
    validation_reason: str = ""
    
    # Metadata
    validated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'token_id': self.token_id,
            'amount': str(self.amount),
            'coherence_score': self.coherence_score,
            'witness_count': self.witness_count,
            'witness_declarations': self.witness_declarations,
            'relational_impact': self.relational_impact,
            'permits_burn': self.permits_burn,
            'is_valid': self.is_valid,
            'validation_reason': self.validation_reason,
            'validated_at': self.validated_at.isoformat()
        }


class EmpathyMarket:
    """
    Empathy Market - Proof-of-Being-Seen Economic Engine
    
    Constitutional safeguard: EMP burn validation via GlyphicBindingEngine
    
    Implements EMP token minting based on validated resonance events,
    creating economic value from relational understanding.
    """
    
    def __init__(
        self,
        multiplier: Decimal = Decimal('100'),
        min_resonance_surplus: Decimal = Decimal('0.5'),
        consensus_threshold: int = 2,
        enable_burn_validation: bool = True
    ):
        """
        Initialize Empathy Market
        
        Args:
            multiplier: Economic scaling factor for EMP minting
            min_resonance_surplus: Minimum ρ_Σ required for minting
            consensus_threshold: Required peer validations
            enable_burn_validation: Enable constitutional burn validation
        """
        self.multiplier = multiplier
        self.min_resonance_surplus = min_resonance_surplus
        self.consensus_threshold = consensus_threshold
        self.enable_burn_validation = enable_burn_validation
        
        # Storage
        self.resonance_events: Dict[str, ResonanceEvent] = {}
        self.emp_tokens: Dict[str, EMPToken] = {}
        self.wallets: Dict[str, EmpathyWallet] = {}
        self.burn_validations: Dict[str, BurnValidation] = {}
        
        # Constitutional safeguard: GlyphicBindingEngine for burn validation
        if enable_burn_validation:
            self.gbe = GlyphicBindingEngine(
                max_threads=3,
                coherence_threshold=0.7,  # Constitutional requirement
                max_glyphs=1000
            )
        else:
            self.gbe = None
        
        # Statistics
        self.total_emp_minted = Decimal('0')
        self.total_emp_burned = Decimal('0')
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
        resonance_surplus = event.calculate_resonance_surplus(len(peer_validations), 2)
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
        resonance_surplus = resonance_event.calculate_resonance_surplus(len(peer_validations), 2)
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
    
    def validate_burn(
        self,
        token_id: str,
        amount: Decimal,
        witness_declarations: List[str],
        relational_context: Dict
    ) -> BurnValidation:
        """
        Validate EMP burn using GlyphicBindingEngine
        
        Constitutional requirements:
        1. coherence_score > 0.7
        2. verified witness declarations (at least 2)
        3. relational_impact.permits_burn = True
        
        Args:
            token_id: EMP token ID to burn
            amount: Amount to burn
            witness_declarations: List of witness statements
            relational_context: Context for relational impact assessment
            
        Returns:
            BurnValidation result
        """
        validation = BurnValidation(
            token_id=token_id,
            amount=amount,
            witness_declarations=witness_declarations,
            witness_count=len(witness_declarations)
        )
        
        if not self.enable_burn_validation or not self.gbe:
            # Skip validation if disabled
            validation.is_valid = True
            validation.validation_reason = "Burn validation disabled"
            return validation
        
        # Constitutional requirement 1: Coherence score > 0.7
        # Create glyphs from witness declarations
        witness_glyphs = []
        for i, declaration in enumerate(witness_declarations):
            glyph = self.gbe.create_glyph(
                glyph_type=GlyphType.RELATION,
                symbol=f"W{i}",
                semantic_content={
                    'declaration': declaration,
                    'type': 'witness',
                    'context': relational_context
                },
                source="emp_burn_validation"
            )
            witness_glyphs.append(glyph)
        
        # Calculate average coherence
        if witness_glyphs:
            avg_coherence = sum(g.coherence_score for g in witness_glyphs) / len(witness_glyphs)
            validation.coherence_score = avg_coherence
        else:
            validation.coherence_score = 0.0
        
        # Constitutional requirement 2: At least 2 verified witnesses
        if len(witness_declarations) < 2:
            validation.is_valid = False
            validation.validation_reason = (
                f"Insufficient witnesses: {len(witness_declarations)}/2 required"
            )
            return validation
        
        # Constitutional requirement 3: Relational impact permits burn
        validation.relational_impact = relational_context
        validation.permits_burn = relational_context.get('permits_burn', False)
        
        if not validation.permits_burn:
            validation.is_valid = False
            validation.validation_reason = "Relational impact does not permit burn"
            return validation
        
        # Check coherence threshold
        if validation.coherence_score <= 0.7:
            validation.is_valid = False
            validation.validation_reason = (
                f"Coherence score {validation.coherence_score:.4f} below "
                f"constitutional threshold of 0.7"
            )
            return validation
        
        # All checks passed
        validation.is_valid = True
        validation.validation_reason = (
            f"Burn validated: coherence={validation.coherence_score:.4f}, "
            f"witnesses={validation.witness_count}, permits_burn=True"
        )
        
        self.burn_validations[validation.id] = validation
        
        return validation
    
    def burn_emp_token(
        self,
        token_id: str,
        amount: Decimal,
        witness_declarations: List[str],
        relational_context: Dict
    ) -> Optional[BurnValidation]:
        """
        Burn EMP tokens with constitutional validation
        
        Args:
            token_id: Token to burn
            amount: Amount to burn
            witness_declarations: Witness statements
            relational_context: Relational impact context
            
        Returns:
            BurnValidation if successful, None otherwise
        """
        # Validate burn
        validation = self.validate_burn(
            token_id=token_id,
            amount=amount,
            witness_declarations=witness_declarations,
            relational_context=relational_context
        )
        
        if not validation.is_valid:
            return validation
        
        # Proceed with burn
        if token_id in self.emp_tokens:
            token = self.emp_tokens[token_id]
            
            # Update wallet balance
            if token.speaker_id in self.wallets:
                speaker_wallet = self.wallets[token.speaker_id]
                if speaker_wallet.emp_balance >= amount:
                    speaker_wallet.emp_balance -= amount
                    self.total_emp_burned += amount
        
        return validation
    
    def get_market_stats(self) -> Dict:
        """Get Empathy Market statistics"""
        return {
            'total_emp_minted': str(self.total_emp_minted),
            'total_emp_burned': str(self.total_emp_burned),
            'total_resonance_events': self.total_resonance_events,
            'total_participants': len(self.wallets),
            'total_burn_validations': len(self.burn_validations),
            'average_emp_per_event': str(
                self.total_emp_minted / self.total_resonance_events
                if self.total_resonance_events > 0 else Decimal('0')
            ),
            'consensus_threshold': self.consensus_threshold,
            'min_resonance_surplus': str(self.min_resonance_surplus),
            'burn_validation_enabled': self.enable_burn_validation
        }


# Constants for w_i calculation
DWELL_MAX_CYCLES = 20
DIVERSITY_PENALTY_WEIGHT = 0.5

def compute_influence_factor(agent_state):
    """
    Calculates the orthogonal influence factor (w_i) based on sustained relational merit.
    (Rec. 1.2: Decoupling from pure c_i)
    """
    time_in_tier = agent_state['time_in_tier']
    verified_pobs = agent_state['verified_pobs_count']
    total_interactions = agent_state['total_interactions']

    # Orthogonal Term 1: Sustained Tier Merit (capped at 20 cycles)
    time_factor = min(time_in_tier, DWELL_MAX_CYCLES) / DWELL_MAX_CYCLES

    # Orthogonal Term 2: Relational Diversity/History
    history_factor = verified_pobs / max(1, total_interactions) # Avoid division by zero

    # Diversity Adjustment (using cosine similarity of interaction vectors)
    # Penalizes agents who only interact with similar profiles (high cos_sim)
    cos_sim_avg = agent_state.get('relational_cos_sim_avg', 0.8) # Placeholder for graph metric
    diversity_adjust = 1.0 - cos_sim_avg # Diversity is high if cos_sim is low (close to 0)

    # w_i is a weighted average of orthogonal factors
    w_i = (0.5 * time_factor) + (0.5 * history_factor * diversity_adjust)

    return min(w_i, 1.0) # Cap at 1.0


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
    
    resonance_surplus = event.calculate_resonance_surplus(2, 2)
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
