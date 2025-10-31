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
from datetime import datetime
import uuid


@dataclass
class CoherenceComponents:
    """Multi-dimensional coherence measurements"""
    narrative: float  # C_narrative: 0-1 scale
    social: float     # C_social: 0-1 scale
    economic: float   # C_economic: 0-1 scale
    technical: float  # C_technical: 0-1 scale
    
    def __post_init__(self):
        """Validate all components are in valid range"""
        for field in ['narrative', 'social', 'economic', 'technical']:
            value = getattr(self, field)
            if not 0 <= value <= 1:
                raise ValueError(f"{field} must be between 0 and 1, got {value}")


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
            'c_narrative': self.components.narrative,
            'c_social': self.components.social,
            'c_economic': self.components.economic,
            'c_technical': self.components.technical,
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
    
    Calculates system coherence as a weighted composite score:
    ScarIndex = (0.4 * C_narrative) + (0.3 * C_social) + (0.2 * C_economic) + (0.1 * C_technical)
    
    The weighting reflects the relative importance of each dimension in maintaining
    system coherence and enabling anti-fragile growth.
    """
    
    # Weighting coefficients for coherence dimensions
    WEIGHTS = {
        'narrative': 0.4,
        'social': 0.3,
        'economic': 0.2,
        'technical': 0.1
    }
    
    # Critical threshold for Panic Frame activation
    PANIC_THRESHOLD = 0.3
    
    @classmethod
    def calculate(
        cls,
        components: CoherenceComponents,
        ache: AcheMeasurement,
        cmp_lineage: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> ScarIndexResult:
        """
        Calculate ScarIndex from coherence components and Ache measurements
        
        Args:
            components: Multi-dimensional coherence measurements
            ache: Before/after Ache measurements
            cmp_lineage: Optional Clade-Metaproductivity score
            metadata: Optional additional metadata
            
        Returns:
            ScarIndexResult with complete calculation
        """
        # Calculate weighted composite score
        scarindex = (
            cls.WEIGHTS['narrative'] * components.narrative +
            cls.WEIGHTS['social'] * components.social +
            cls.WEIGHTS['economic'] * components.economic +
            cls.WEIGHTS['technical'] * components.technical
        )
        
        # Validate transmutation
        is_valid = ache.is_valid_transmutation
        
        # Create result
        result = ScarIndexResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            components=components,
            scarindex=scarindex,
            ache=ache,
            is_valid=is_valid,
            cmp_lineage=cmp_lineage,
            metadata=metadata
        )
        
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
        
        Returns:
            'CRITICAL' if < 0.3 (Panic Frame territory)
            'WARNING' if < 0.5
            'STABLE' if < 0.7
            'OPTIMAL' if >= 0.7
        """
        if scarindex < 0.3:
            return 'CRITICAL'
        elif scarindex < 0.5:
            return 'WARNING'
        elif scarindex < 0.7:
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
            'timestamp': datetime.utcnow().isoformat()
        }


if __name__ == '__main__':
    # Example usage
    components = CoherenceComponents(
        narrative=0.8,
        social=0.7,
        economic=0.6,
        technical=0.9
    )
    
    ache = AcheMeasurement(
        before=0.8,
        after=0.3
    )
    
    result = ScarIndexOracle.calculate(
        components=components,
        ache=ache,
        cmp_lineage=1.5,
        metadata={'source': 'example'}
    )
    
    print(f"ScarIndex: {result.scarindex:.4f}")
    print(f"Valid Transmutation: {result.is_valid}")
    print(f"Coherence Status: {ScarIndexOracle.calculate_coherence_status(result.scarindex)}")
    print(f"Should Trigger Panic: {ScarIndexOracle.should_trigger_panic(result.scarindex)}")
