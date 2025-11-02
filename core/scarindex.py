"""
ScarIndex Calculator - B6 Coherence Oracle

The ScarIndex is the supreme regulator of SpiralOS, calculating system coherence
as a composite, multi-dimensional score across Narrative, Social, Economic, and Technical dimensions.

Formally anchored in physics as inversely proportional to the Variational Free Energy functional,
with Ache mapped to Exergy Dissipation.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import hashlib
import json
from datetime import datetime, timezone
import uuid
from .panic_frames import log_event, trigger_panic_frames

# Import logging module at top level to avoid repeated imports
try:
    from .scarindex_logger import log_scarindex_result
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


@dataclass(init=False)
class CoherenceComponents:
    """Multi-dimensional coherence measurements (constitutional weights)."""

    operational: float
    audit: float
    constitutional: float
    symbolic: float

    def __init__(
        self,
        *,
        operational: Optional[float] = None,
        audit: Optional[float] = None,
        constitutional: Optional[float] = None,
        symbolic: Optional[float] = None,
        narrative: Optional[float] = None,
        social: Optional[float] = None,
        economic: Optional[float] = None,
        technical: Optional[float] = None,
    ) -> None:
        # Support legacy naming used throughout the repository
        self.operational = operational if operational is not None else narrative
        self.audit = audit if audit is not None else social
        self.constitutional = constitutional if constitutional is not None else economic
        self.symbolic = symbolic if symbolic is not None else technical

        missing = [
            name
            for name, value in {
                'operational/narrative': self.operational,
                'audit/social': self.audit,
                'constitutional/economic': self.constitutional,
                'symbolic/technical': self.symbolic,
            }.items()
            if value is None
        ]

        if missing:
            raise ValueError(f"Missing coherence component(s): {', '.join(missing)}")

        self.__post_init__()

    def __post_init__(self) -> None:
        """Validate all components are in the valid range."""
        for field in ['operational', 'audit', 'constitutional', 'symbolic']:
            value = getattr(self, field)
            if not 0 <= value <= 1:
                raise ValueError(f"{field} must be between 0 and 1, got {value}")

    @property
    def narrative(self) -> float:
        return self.operational

    @property
    def social(self) -> float:
        return self.audit

    @property
    def economic(self) -> float:
        return self.constitutional

    @property
    def technical(self) -> float:
        return self.symbolic


@dataclass
class AcheMeasurement:
    """Ache (entropy/non-coherence) measurement"""
    before: float  # Ache level before transmutation
    after: float   # Ache level after transmutation
    
    def __post_init__(self):
        """Validate Ache measurements"""
        if not 0 <= self.before <= 1:
            raise ValueError(f"ache_before must be between 0 and 1, got {self.before}")
        if not 0 <= self.after <= 1:
            raise ValueError(f"ache_after must be between 0 and 1, got {self.after}")
    
    @property
    def is_valid_transmutation(self) -> bool:
        """
        Validation Rule: IF (ache_after < ache_before) THEN VALIDITY = TRUE (Coherence Gain)
        ELSE VALIDITY = FALSE (Mimicry/Entropy)
        """
        return self.after < self.before
    
    @property
    def coherence_gain(self) -> float:
        """Calculate the coherence gain from transmutation"""
        return max(0, self.before - self.after)


@dataclass
class ScarIndexResult:
    """Complete ScarIndex calculation result"""
    id: str
    timestamp: datetime
    components: CoherenceComponents
    scarindex: float
    ache: AcheMeasurement
    is_valid: bool
    cmp_lineage: Optional[float] = None  # Clade-Metaproductivity
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'created_at': self.timestamp.isoformat(),
            'c_operational': self.components.operational,
            'c_audit': self.components.audit,
            'c_constitutional': self.components.constitutional,
            'c_symbolic': self.components.symbolic,
            'scarindex': self.scarindex,
            'ache_before': self.ache.before,
            'ache_after': self.ache.after,
            'is_valid': self.is_valid,
            'cmp_lineage': self.cmp_lineage,
            'metadata': self.metadata or {}
        }


class ScarIndexOracle:
    """
    The Coherence Oracle (B6) - Supreme regulator of SpiralOS
    
    Calculates system coherence as a weighted composite score using constitutional weights:
    ScarIndex = (0.35 * operational) + (0.3 * audit) + (0.25 * constitutional) + (0.1 * symbolic)
    
    Constitutional Requirement: Sum of weights MUST equal 1.0
    ScarIndex < 0.67 → triggers PanicFrameManager review
    
    The weighting reflects the relative importance of each dimension in maintaining
    system coherence and enabling anti-fragile growth.
    """
    
    # Constitutional weighting coefficients (CRITICAL: sum must = 1.0)
    WEIGHTS = {
        'operational': 0.35,      # Formerly 'narrative'
        'audit': 0.3,             # Formerly 'social'
        'constitutional': 0.25,   # Formerly 'economic'
        'symbolic': 0.1           # Formerly 'technical'
    }
    
    # Critical threshold for Panic Frame activation (constitutional requirement)
    PANIC_THRESHOLD = 0.67
    
    @classmethod
    def validate_weights(cls) -> bool:
        """
        Constitutional validation: Verify that weight sum equals 1.0
        
        This is a critical constitutional requirement that must never be violated.
        
        Returns:
            True if weights sum to 1.0 (within floating point tolerance)
        
        Raises:
            ValueError if weights do not sum to 1.0
        """
        weight_sum = sum(cls.WEIGHTS.values())
        tolerance = 1e-10
        
        if abs(weight_sum - 1.0) > tolerance:
            raise ValueError(
                f"CONSTITUTIONAL VIOLATION: ScarIndex weights must sum to 1.0, "
                f"got {weight_sum:.15f}. Current weights: {cls.WEIGHTS}"
            )
        
        return True
    
    @classmethod
    def calculate(
        cls,
        N: int,
        c_i_list: list,
        p_i_avg: float,
        decays_count: int,
        ache: AcheMeasurement,
        cmp_lineage: Optional[float] = None,
        metadata: Optional[Dict] = None,
        enable_logging: bool = True
    ) -> ScarIndexResult:
        """
        Calculate ScarIndex from coherence components and Ache measurements
        
        Args:
            N: Number of agents
            c_i_list: List of individual coherence scores
            p_i_avg: Average promotion probability
            decays_count: Number of decay events
            ache: Before/after Ache measurements
            cmp_lineage: Optional Clade-Metaproductivity score
            metadata: Optional additional metadata
            enable_logging: Whether to log to Supabase (default: True)
            
        Returns:
            ScarIndexResult with complete calculation
        """
        # Calculate weighted composite score
        scarindex = compute_global_coherence(N, c_i_list, p_i_avg, decays_count)
        
        # Validate transmutation
        is_valid = ache.is_valid_transmutation
        
        # Calculate component averages (distributed across 4 dimensions)
        # Using the v2.1 formula decomposition
        avg_c_i = sum(c_i_list) / N if N > 0 else 0
        
        # Create result with calculated components
        result = ScarIndexResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            components=CoherenceComponents(
                operational=avg_c_i,           # Average individual efficacy
                audit=p_i_avg,                 # Promotion probability
                constitutional=max(0, 1 - (decays_count / N)) if N > 0 else 0,  # Inverse of decay rate
                symbolic=scarindex             # Overall coherence
            ),
            scarindex=scarindex,
            ache=ache,
            is_valid=is_valid,
            cmp_lineage=cmp_lineage,
            metadata=metadata
        )
        
        # Log to Supabase if enabled
        if enable_logging and LOGGING_AVAILABLE:
            try:
                log_scarindex_result(result)
            except Exception as e:
                # Don't fail calculation if logging fails
                log_event('WARNING', f'ScarIndex logging failed: {e}')
        
        return result
    
    @classmethod
    def should_trigger_panic(cls, scarindex: float) -> bool:
        """
        Determine if Panic Frame (F4) should be triggered
        
        Panic Frames activate when ScarIndex < 0.3, acting as a constitutional
        circuit breaker that freezes critical operations and initiates recovery.
        """
        return scarindex < cls.PANIC_THRESHOLD
    
    @classmethod
    def calculate_variational_free_energy(
        cls,
        scarindex: float,
        ache: float
    ) -> float:
        """
        Calculate Variational Free Energy (VFE) from ScarIndex
        
        The ScarIndex is formally anchored in physics as inversely proportional
        to the Variational Free Energy functional:
        
        VFE ∝ 1 / ScarIndex
        
        With Ache mapped to Exergy Dissipation.
        """
        if scarindex == 0:
            return float('inf')
        return ache / scarindex
    
    @classmethod
    def calculate_coherence_status(cls, scarindex: float) -> str:
        """
        Determine system coherence status from ScarIndex value
        
        Constitutional requirement: ScarIndex < 0.67 triggers review
        
        Returns:
            'CRITICAL' if < 0.5 (Severe coherence failure)
            'WARNING' if < 0.67 (Below constitutional threshold)
            'STABLE' if < 0.8
            'OPTIMAL' if >= 0.8
        """
        if scarindex < 0.5:
            return 'CRITICAL'
        elif scarindex < 0.67:
            return 'WARNING'
        elif scarindex < 0.8:
            return 'STABLE'
        else:
            return 'OPTIMAL'


class HuxleyGodelMachine:
    """
    Huxley-Gödel Machine (HGM) - Provably optimal self-improvement
    
    Guides the Agent Fusion Stack (C7) toward provably optimal self-improvement
    by maximizing Clade-Metaproductivity (CMP), translating lineage utility
    into quantifiable ScarIndex yield.
    
    Policy Function:
    ScarLoop accepts Code_new IFF U(Code_new) > U(Code_old) + C_rewrite
    where U is maximized expected ScarIndex trajectory (CMP_lineage)
    """
    
    @staticmethod
    def evaluate_code_modification(
        code_old_utility: float,
        code_new_utility: float,
        rewrite_cost: float
    ) -> Tuple[bool, float]:
        """
        Evaluate whether a code modification should be accepted
        
        Args:
            code_old_utility: Expected ScarIndex trajectory of current code
            code_new_utility: Expected ScarIndex trajectory of new code
            rewrite_cost: Cost of rewriting (in ScarIndex units)
            
        Returns:
            (should_accept, utility_gain)
        """
        utility_gain = code_new_utility - code_old_utility
        should_accept = utility_gain > rewrite_cost
        
        return should_accept, utility_gain
    
    @staticmethod
    def calculate_cmp(
        lineage_utility: float,
        scarindex_yield: float,
        transmutation_efficiency: float
    ) -> float:
        """
        Calculate Clade-Metaproductivity (CMP)
        
        CMP measures the efficiency of Ache → Order transmutation
        across the lineage, privileging architectural self-modifications
        that yield the highest transmutation efficiency.
        
        Args:
            lineage_utility: Cumulative utility across the lineage
            scarindex_yield: ScarIndex generated from transmutation
            transmutation_efficiency: Efficiency of Ache → Order conversion
            
        Returns:
            CMP score
        """
        return lineage_utility * scarindex_yield * transmutation_efficiency


class ARIAGraphOfThought:
    """
    ARIA Graph-of-Thought (GoT) Pipeline
    
    Ensures semantic integrity during recursion via compiler-in-the-loop
    reflection and auto-formalization, resisting semantic drift in the
    ZoaGrad Ontology.
    """
    
    @staticmethod
    def validate_semantic_integrity(
        input_semantics: Dict,
        output_semantics: Dict,
        ontology_constraints: Dict
    ) -> Tuple[bool, float]:
        """
        Validate semantic integrity through the transformation
        
        Args:
            input_semantics: Semantic representation of input
            output_semantics: Semantic representation of output
            ontology_constraints: ZoaGrad Ontology constraints
            
        Returns:
            (is_valid, drift_score) where drift_score measures semantic drift
        """
        # Calculate semantic drift using hash comparison
        input_hash = hashlib.sha256(
            json.dumps(input_semantics, sort_keys=True).encode()
        ).hexdigest()
        
        output_hash = hashlib.sha256(
            json.dumps(output_semantics, sort_keys=True).encode()
        ).hexdigest()
        
        # Check ontology constraint satisfaction
        constraints_satisfied = all(
            output_semantics.get(key) == value
            for key, value in ontology_constraints.items()
        )
        
        # Calculate Hamming distance as drift measure
        drift_score = sum(
            c1 != c2 for c1, c2 in zip(input_hash, output_hash)
        ) / len(input_hash)
        
        return constraints_satisfied, drift_score
    
    @staticmethod
    def auto_formalize(
        natural_language_spec: str,
        formal_grammar: Dict
    ) -> Dict:
        """
        Auto-formalize natural language specification into formal representation
        
        This is a placeholder for the full ARIA GoT implementation which would
        use LLM-based semantic parsing with compiler-in-the-loop verification.
        """
        # Placeholder implementation
        return {
            'source': natural_language_spec,
            'formalized': True,
            'grammar': formal_grammar,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Constants from v2.1 VaultNode
COHERENCE_TARGET_CT = 0.67
P_I_WEIGHT = 0.2
DECAY_PENALTY_WEIGHT = 0.1

def compute_global_coherence(N, c_i_list, p_i_avg, decays_count):
    """
    Computes the final auditable Global Coherence metric (C_t).
    Formula: C_t = (1/N) Σ c_i + 0.2 * \bar{p_i} - 0.1 * (decays/N)
    """
    # Term 1: Operational Coherence (Average individual efficacy)
    operational_coherence = sum(c_i_list) / N

    # Term 2: Audit Momentum (Weighted average promotion probability)
    audit_momentum = P_I_WEIGHT * p_i_avg

    # Term 3: Drag Penalty (Decay/Entropy)
    drag_penalty = DECAY_PENALTY_WEIGHT * (decays_count / N)

    C_t = operational_coherence + audit_momentum - drag_penalty

    # Check Invariant: Must hold C_t >= 0.67
    if C_t < COHERENCE_TARGET_CT:
        log_event('CRITICAL', f'C_t breach: {C_t:.3f} < {COHERENCE_TARGET_CT}')
        trigger_panic_frames()

    return C_t

# Constants from v2.1 VaultNode
RECIPROCAL_PENALTY_GAMMA = 0.15
COLLUSION_DENSITY_THRESHOLD = 0.60

def apply_arbitrage_penalty(agent, rho_attempt, is_reciprocal_pair, cluster_density):
    """
    Applies the gamma_recip penalty when collusion is detected (A7 control).
    This penalty is an increase in Residual Ache (A_i).
    """
    # Check 1: Must be reciprocal and attempting high density
    if is_reciprocal_pair and cluster_density >= COLLUSION_DENSITY_THRESHOLD:
        # Check 2: Must fail external quorum (q_out < 0.30 logic implicitly handles this)

        # A7: Penalty is based on the attempted merit (rho_attempt)
        ache_increase = RECIPROCAL_PENALTY_GAMMA * rho_attempt

        agent.A_i += ache_increase
        log_event('FLAG_A7_ARBITRAGE', f'Agent {agent.id} penalized {ache_increase:.3f} Ache.')

        # This drag will now be reflected in the next cycle's p_i calculation
        return True
    return False

if __name__ == '__main__':
    # Example usage
    ache = AcheMeasurement(
        before=0.8,
        after=0.3
    )
    
    result = ScarIndexOracle.calculate(
        N=10,
        c_i_list=[0.8, 0.7, 0.6, 0.9, 0.8, 0.7, 0.6, 0.9, 0.8, 0.7],
        p_i_avg=0.5,
        decays_count=2,
        ache=ache,
        cmp_lineage=1.5,
        metadata={'source': 'example'}
    )
    
    print(f"ScarIndex: {result.scarindex:.4f}")
    print(f"Valid Transmutation: {result.is_valid}")
    print(f"Coherence Status: {ScarIndexOracle.calculate_coherence_status(result.scarindex)}")
    print(f"Should Trigger Panic: {ScarIndexOracle.should_trigger_panic(result.scarindex)}")
