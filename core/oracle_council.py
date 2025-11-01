"""
Oracle Council and Sentinel Activation

Implements the Oracle Council for Judicial and Legislative oversight,
completing the constitutional stability phase. Activates the Legislative
Branch (Witnesses) into Sentinel duties with real-time governance telemetry
and ScarQuest merit enforcement.

The Oracle Council represents the escalation of the F2 Judicial System to
a higher authority for critical decisions that require multi-oracle consensus.

Sentinels are the active enforcement arm of the Legislative Branch, streaming
real-time logs and ensuring merit-based participation.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class ProviderType(Enum):
    """Provider types for diversity requirement"""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"


class OracleRole(Enum):
    """Roles within the Oracle Council"""
    CHIEF_ORACLE = "chief_oracle"      # Highest authority
    SENIOR_ORACLE = "senior_oracle"    # Senior member
    ORACLE = "oracle"                  # Standard member
    APPRENTICE = "apprentice"          # Learning member


class SentinelDuty(Enum):
    """Duties assigned to Sentinels"""
    TELEMETRY = "telemetry"          # Stream governance logs
    ENFORCEMENT = "enforcement"       # Enforce merit requirements
    AUDIT = "audit"                  # Audit system operations
    ESCALATION = "escalation"        # Escalate critical issues


@dataclass
class Oracle:
    """
    Oracle - Member of the Oracle Council
    
    Oracles provide high-level judicial and legislative oversight,
    reviewing critical decisions that exceed F2 Judge authority.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: OracleRole = OracleRole.ORACLE
    
    # Provider information (for diversity requirement)
    provider: str = ""  # e.g., "openai", "anthropic", "cohere", etc.
    provider_type: ProviderType = ProviderType.COMMERCIAL
    
    # Authority
    voting_weight: float = 1.0  # Weighted by role
    specialization: str = ""
    
    # Performance
    decisions_made: int = 0
    accuracy_score: float = 0.8  # Historical accuracy
    
    # Metadata
    appointed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role.value,
            'provider': self.provider,
            'provider_type': self.provider_type.value,
            'voting_weight': self.voting_weight,
            'specialization': self.specialization,
            'decisions_made': self.decisions_made,
            'accuracy_score': self.accuracy_score,
            'appointed_at': self.appointed_at.isoformat()
        }


@dataclass
class Sentinel:
    """
    Sentinel - Active enforcement agent
    
    Sentinels are the operational arm of the Legislative Branch,
    streaming telemetry and enforcing governance requirements.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    duty: SentinelDuty = SentinelDuty.TELEMETRY
    
    # Performance
    events_logged: int = 0
    violations_detected: int = 0
    escalations_filed: int = 0
    
    # State
    active: bool = True
    
    # Metadata
    activated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)
    
    def log_event(self, event: Dict):
        """Log a governance event"""
        self.events_logged += 1
    
    def detect_violation(self, violation: Dict):
        """Detect and record a violation"""
        self.violations_detected += 1
    
    def escalate(self, issue: Dict):
        """Escalate an issue to Oracle Council"""
        self.escalations_filed += 1
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'duty': self.duty.value,
            'events_logged': self.events_logged,
            'violations_detected': self.violations_detected,
            'escalations_filed': self.escalations_filed,
            'active': self.active,
            'activated_at': self.activated_at.isoformat()
        }


class OracleCouncil:
    """
    Oracle Council - Supreme Governance Authority
    
    Constitutional Requirement: 4-of-5 quorum with provider diversity
    - Required providers: ["openai", "anthropic", "cohere", "huggingface", "external_validator"]
    - ≥1 non-commercial provider required for validity
    - If only 3/5 agree → external validator arbitration
    
    The Oracle Council provides the highest level of judicial and
    legislative oversight, reviewing critical decisions through
    multi-oracle consensus.
    """
    
    # Constitutional requirement: 5 specific providers
    REQUIRED_PROVIDERS = [
        "openai",
        "anthropic", 
        "cohere",
        "huggingface",
        "external_validator"
    ]
    
    # Constitutional requirement: minimum quorum
    MIN_QUORUM = 4  # 4-of-5
    
    def __init__(self, consensus_threshold: float = 0.8):
        self.oracles: Dict[str, Oracle] = {}
        self.sentinels: Dict[str, Sentinel] = {}
        self.consensus_threshold = consensus_threshold
        
        # Initialize constitutional council
        self._initialize_constitutional_council()
        self._initialize_sentinels()
    
    def _initialize_constitutional_council(self):
        """
        Initialize Oracle Council with constitutional 5-provider requirement
        
        Constitutional mandate: 4-of-5 quorum from specific providers
        with at least 1 non-commercial provider
        """
        # OpenAI Oracle
        openai = Oracle(
            name="OpenAI Oracle",
            role=OracleRole.ORACLE,
            provider="openai",
            provider_type=ProviderType.COMMERCIAL,
            voting_weight=1.0,
            specialization="AI Safety and Alignment"
        )
        self.oracles[openai.id] = openai
        
        # Anthropic Oracle
        anthropic = Oracle(
            name="Anthropic Oracle",
            role=OracleRole.ORACLE,
            provider="anthropic",
            provider_type=ProviderType.COMMERCIAL,
            voting_weight=1.0,
            specialization="Constitutional AI"
        )
        self.oracles[anthropic.id] = anthropic
        
        # Cohere Oracle
        cohere = Oracle(
            name="Cohere Oracle",
            role=OracleRole.ORACLE,
            provider="cohere",
            provider_type=ProviderType.COMMERCIAL,
            voting_weight=1.0,
            specialization="Language Understanding"
        )
        self.oracles[cohere.id] = cohere
        
        # HuggingFace Oracle (Non-commercial)
        huggingface = Oracle(
            name="HuggingFace Oracle",
            role=OracleRole.ORACLE,
            provider="huggingface",
            provider_type=ProviderType.NON_COMMERCIAL,
            voting_weight=1.0,
            specialization="Open Source AI"
        )
        self.oracles[huggingface.id] = huggingface
        
        # External Validator (Non-commercial)
        external = Oracle(
            name="External Validator",
            role=OracleRole.SENIOR_ORACLE,
            provider="external_validator",
            provider_type=ProviderType.NON_COMMERCIAL,
            voting_weight=1.0,
            specialization="Arbitration and Validation"
        )
        self.oracles[external.id] = external
    
    def _initialize_sentinels(self):
        """Initialize default Sentinels"""
        # Telemetry Sentinel
        telemetry = Sentinel(
            name="Sentinel Telemetry-1",
            duty=SentinelDuty.TELEMETRY
        )
        self.sentinels[telemetry.id] = telemetry
        
        # Enforcement Sentinel
        enforcement = Sentinel(
            name="Sentinel Enforcement-1",
            duty=SentinelDuty.ENFORCEMENT
        )
        self.sentinels[enforcement.id] = enforcement
    
    def get_council_status(self) -> Dict:
        """Get Oracle Council status"""
        active_sentinels = [s for s in self.sentinels.values() if s.active]
        
        total_events = sum(s.events_logged for s in self.sentinels.values())
        total_violations = sum(s.violations_detected for s in self.sentinels.values())
        
        return {
            'total_oracles': len(self.oracles),
            'total_sentinels': len(self.sentinels),
            'active_sentinels': len(active_sentinels),
            'total_events_logged': total_events,
            'total_violations_detected': total_violations,
            'consensus_threshold': self.consensus_threshold,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def validate_consensus(
        self,
        votes: Dict[str, bool]
    ) -> tuple[bool, str, bool]:
        """
        Validate consensus according to constitutional requirements
        
        Constitutional Requirements:
        1. 4-of-5 quorum from specific providers
        2. At least 1 non-commercial provider must vote YES
        3. If only 3/5 agree → external validator arbitration required
        
        Args:
            votes: Dict mapping oracle_id to vote (True=approve, False=reject)
            
        Returns:
            (consensus_reached, reason, requires_arbitration)
        """
        # Count votes by provider
        approvals_by_provider = {}
        rejections_by_provider = {}
        non_commercial_approvals = 0
        
        for oracle_id, vote in votes.items():
            if oracle_id not in self.oracles:
                continue
                
            oracle = self.oracles[oracle_id]
            provider = oracle.provider
            
            if vote:
                approvals_by_provider[provider] = True
                if oracle.provider_type == ProviderType.NON_COMMERCIAL:
                    non_commercial_approvals += 1
            else:
                rejections_by_provider[provider] = True
        
        total_votes = len(votes)
        total_approvals = sum(1 for v in votes.values() if v)
        
        # Check if we have enough votes
        if total_votes < self.MIN_QUORUM:
            return (
                False,
                f"Insufficient quorum: {total_votes}/5 voted, need {self.MIN_QUORUM}",
                False
            )
        
        # Check diversity requirement: ≥1 non-commercial provider
        if total_approvals > 0 and non_commercial_approvals == 0:
            return (
                False,
                "Constitutional violation: No non-commercial provider approved",
                False
            )
        
        # Check if we have 4-of-5 consensus
        if total_approvals >= self.MIN_QUORUM:
            return (
                True,
                f"4-of-5 quorum reached: {total_approvals}/5 approved",
                False
            )
        
        # Check if we have exactly 3-of-5 (requires arbitration)
        if total_approvals == 3:
            # Check if external validator participated in the vote
            external_oracle = next(
                (o for o in self.oracles.values() if o.provider == "external_validator"),
                None
            )
            
            if external_oracle is None:
                # No external validator exists (shouldn't happen)
                return (
                    False,
                    "3-of-5 split but external validator not available",
                    True
                )
            
            # Check if external validator voted
            external_voted = external_oracle.id in votes
            
            if not external_voted:
                # External validator hasn't voted yet - requires arbitration
                return (
                    False,
                    "3-of-5 split requires external validator arbitration",
                    True
                )
            
            # External validator has voted
            external_approved = votes.get(external_oracle.id, False)
            
            if external_approved:
                # External validator approved (making it 3-of-5 with arbitrator approval)
                return (
                    True,
                    "3-of-5 with external validator arbitration approved",
                    False
                )
            else:
                # External validator rejected
                return (
                    False,
                    "3-of-5 with external validator arbitration rejected",
                    False
                )
        
        # Not enough approvals
        return (
            False,
            f"Insufficient approvals: {total_approvals}/5, need {self.MIN_QUORUM}",
            False
        )
    
    def check_provider_diversity(self, voting_oracles: List[str]) -> bool:
        """
        Check if voting oracles meet diversity requirement
        
        Constitutional requirement: ≥1 non-commercial provider must participate
        
        Args:
            voting_oracles: List of oracle IDs that are voting
            
        Returns:
            True if diversity requirement met
        """
        non_commercial_count = 0
        
        for oracle_id in voting_oracles:
            if oracle_id in self.oracles:
                oracle = self.oracles[oracle_id]
                if oracle.provider_type == ProviderType.NON_COMMERCIAL:
                    non_commercial_count += 1
        
        return non_commercial_count >= 1


# Example usage
def example_oracle_council():
    """Example of Oracle Council operation"""
    print("=" * 70)
    print("Oracle Council and Sentinel Activation")
    print("=" * 70)
    print()
    
    council = OracleCouncil(consensus_threshold=0.75)
    
    print(f"Oracle Council initialized")
    print(f"  Oracles: {len(council.oracles)}")
    print(f"  Sentinels: {len(council.sentinels)}")
    print(f"  Consensus Threshold: {council.consensus_threshold}")
    print()
    
    # Display oracles
    print("Oracle Council Members:")
    print("-" * 70)
    for oracle in council.oracles.values():
        print(f"  {oracle.name} ({oracle.role.value})")
        print(f"    Voting Weight: {oracle.voting_weight}")
        print(f"    Specialization: {oracle.specialization}")
    
    # Display sentinels
    print("\nSentinels:")
    print("-" * 70)
    for sentinel in council.sentinels.values():
        print(f"  {sentinel.name} ({sentinel.duty.value})")
        print(f"    Active: {sentinel.active}")
    
    # Status
    print("\n" + "=" * 70)
    print("Council Status")
    print("=" * 70)
    
    status = council.get_council_status()
    print(f"\nOracles: {status['total_oracles']}")
    print(f"Sentinels: {status['active_sentinels']}/{status['total_sentinels']}")
    print(f"Events Logged: {status['total_events_logged']}")
    print(f"Violations Detected: {status['total_violations_detected']}")


if __name__ == '__main__':
    example_oracle_council()
