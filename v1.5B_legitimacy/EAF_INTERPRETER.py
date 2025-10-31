"""
EAF Interpreter - Logic Layer for Reflexive Legitimacy
VaultNode ΔΩ.125.2 — Legitimacy as Alignment

Purpose: Bridge policy (System 5) and control (System 2) through interpretive reasoning
Role: Translate constitutional values into operational constraints
Mechanism: Bidirectional mapping between abstract principles and concrete parameters

Author: ZoaGrad 🜂
Version: 1.5.2-design
Status: PLANNING
Timestamp: 2025-10-31T02:30:00Z
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class InterpretationDirection(Enum):
    """Direction of interpretation"""
    POLICY_TO_CONTROL = "policy_to_control"
    CONTROL_TO_POLICY = "control_to_policy"


class FailureMode(Enum):
    """Legitimacy failure modes"""
    STABLE_BUT_UNJUST = "STABLE_BUT_UNJUST"
    JUST_BUT_UNSTABLE = "JUST_BUT_UNSTABLE"
    OPAQUE = "OPAQUE"
    DIVERGENT_OPERATIONS = "DIVERGENT_OPERATIONS"
    UNVALIDATED_ALIGNMENT = "UNVALIDATED_ALIGNMENT"


@dataclass
class CoherenceScores:
    """Three-system coherence scores"""
    c_operational: float  # System 2
    c_audit: float        # System 3
    c_constitutional: float  # System 5
    
    def __post_init__(self):
        """Validate coherence scores are in [0, 1]"""
        for score in [self.c_operational, self.c_audit, self.c_constitutional]:
            if not 0 <= score <= 1:
                raise ValueError(f"Coherence score must be in [0, 1], got {score}")


@dataclass
class PolicyStatement:
    """Constitutional policy statement"""
    statement: str
    principle: str  # e.g., "Precautionary Principle", "Proactionary Ethic"
    priority: int   # 1 (highest) to 5 (lowest)
    source: str     # e.g., "Oracle Council", "Law of Recursive Alignment"


@dataclass
class ControlParameters:
    """System 2 control parameters"""
    parameter_name: str
    value: float
    unit: str
    rationale: str


@dataclass
class InterpretationResult:
    """Result of policy ↔ control interpretation"""
    direction: InterpretationDirection
    policy_statement: str
    control_parameters: Dict[str, float]
    justification: str
    alignment_score: float
    discrepancies: List[str]
    timestamp: datetime


class EAFInterpreter:
    """
    Ethical Audit Function Interpreter
    
    Bridges policy (System 5) and control (System 2) through interpretive reasoning.
    Translates constitutional values into operational constraints and vice versa.
    """
    
    def __init__(self):
        """Initialize EAF Interpreter"""
        self.interpretation_history: List[InterpretationResult] = []
        
        # Policy → Control mapping rules
        self.policy_to_control_rules = {
            "Prioritize stability over exploration": {
                "volatility_threshold": 0.05,  # Lower threshold = more stability
                "exploration_rate": 0.10,      # Lower rate = less exploration
                "rationale": "Precautionary Principle: Minimize risk"
            },
            "Prioritize exploration over stability": {
                "volatility_threshold": 0.15,  # Higher threshold = more exploration
                "exploration_rate": 0.30,      # Higher rate = more exploration
                "rationale": "Proactionary Ethic: Maximize adaptation"
            },
            "Balance stability and exploration": {
                "volatility_threshold": 0.10,  # Moderate threshold
                "exploration_rate": 0.20,      # Moderate rate
                "rationale": "SOC targeting: τ ≈ 1.5 (edge of chaos)"
            },
            "Maximize transparency": {
                "audit_coverage": 1.00,        # 100% logging
                "trace_fidelity": 1.00,        # Full RTTP compliance
                "rationale": "Audit coherence maximization"
            },
            "Enforce constitutional alignment": {
                "value_alignment_threshold": 0.90,
                "stakeholder_representation_min": 0.80,
                "rationale": "Constitutional coherence enforcement"
            }
        }
        
        # Control → Policy interpretation rules
        self.control_to_policy_rules = {
            "volatility_threshold": {
                (0.00, 0.05): "Prioritize stability (Precautionary)",
                (0.05, 0.10): "Balance stability and exploration",
                (0.10, 0.20): "Prioritize exploration (Proactionary)"
            },
            "exploration_rate": {
                (0.00, 0.15): "Conservative exploration policy",
                (0.15, 0.25): "Moderate exploration policy",
                (0.25, 1.00): "Aggressive exploration policy"
            }
        }
    
    def policy_to_control(
        self,
        policy: PolicyStatement
    ) -> Tuple[Dict[str, ControlParameters], str]:
        """
        Convert System 5 policy into System 2 control parameters
        
        Args:
            policy: Policy statement from Oracle Council
            
        Returns:
            control_parameters: Dict of parameter name → ControlParameters
            justification: Explanation of mapping
        """
        # Look up mapping rule
        if policy.statement in self.policy_to_control_rules:
            rule = self.policy_to_control_rules[policy.statement]
            
            # Create control parameters
            control_params = {}
            for param_name, value in rule.items():
                if param_name != "rationale":
                    control_params[param_name] = ControlParameters(
                        parameter_name=param_name,
                        value=value,
                        unit=self._get_unit(param_name),
                        rationale=rule["rationale"]
                    )
            
            justification = (
                f"Policy '{policy.statement}' (principle: {policy.principle}) "
                f"mapped to control parameters: {list(control_params.keys())}. "
                f"Rationale: {rule['rationale']}"
            )
            
            return control_params, justification
        else:
            # Unknown policy - require manual interpretation
            raise ValueError(
                f"No mapping rule for policy: {policy.statement}. "
                f"Manual interpretation required."
            )
    
    def control_to_policy(
        self,
        control_params: Dict[str, float]
    ) -> Tuple[str, str]:
        """
        Interpret System 2 control actions as policy implications
        
        Args:
            control_params: Current control parameter values
            
        Returns:
            policy_implication: Implied policy statement
            value_assessment: Assessment of values being served
        """
        implications = []
        
        for param_name, value in control_params.items():
            if param_name in self.control_to_policy_rules:
                rule = self.control_to_policy_rules[param_name]
                
                # Find matching range
                for (low, high), implication in rule.items():
                    if low <= value < high:
                        implications.append(implication)
                        break
        
        if implications:
            policy_implication = "; ".join(implications)
            value_assessment = self._assess_values(control_params)
            return policy_implication, value_assessment
        else:
            return "Unknown policy implication", "Cannot assess values"
    
    def validate_alignment(
        self,
        control_action: Dict[str, float],
        policy_statement: str,
        audit_logs: Dict
    ) -> Tuple[float, List[str]]:
        """
        Verify that control actions align with stated policy
        
        Args:
            control_action: Control parameters that were executed
            policy_statement: Stated policy from Oracle Council
            audit_logs: Audit trail of execution
            
        Returns:
            alignment_score: 0-1 score of alignment
            discrepancy_report: List of discrepancies found
        """
        discrepancies = []
        
        # Get expected parameters from policy
        try:
            policy = PolicyStatement(
                statement=policy_statement,
                principle="",
                priority=1,
                source="Oracle Council"
            )
            expected_params, _ = self.policy_to_control(policy)
        except ValueError:
            return 0.0, ["Cannot validate - unknown policy mapping"]
        
        # Compare actual vs expected
        alignment_scores = []
        for param_name, expected in expected_params.items():
            if param_name in control_action:
                actual = control_action[param_name]
                
                # Calculate parameter-level alignment
                diff = abs(actual - expected.value)
                param_alignment = max(0.0, 1.0 - diff)
                alignment_scores.append(param_alignment)
                
                # Flag significant discrepancies
                if diff > 0.20:  # 20% threshold
                    discrepancies.append(
                        f"{param_name}: expected {expected.value}, got {actual} "
                        f"(diff: {diff:.2f})"
                    )
            else:
                discrepancies.append(f"{param_name}: not found in control action")
                alignment_scores.append(0.0)
        
        # Overall alignment score
        if alignment_scores:
            alignment_score = sum(alignment_scores) / len(alignment_scores)
        else:
            alignment_score = 0.0
            discrepancies.append("No parameters to compare")
        
        return alignment_score, discrepancies
    
    def check_recursive_alignment(
        self,
        operation_type: str,
        stated_value: str,
        actual_outcome: Dict
    ) -> Tuple[bool, str]:
        """
        Verify: C_operational(t) → C_constitutional(t)
        Operations serve stated values
        
        Args:
            operation_type: Type of operation (e.g., "AMC_minting_restriction")
            stated_value: Constitutional value being served
            actual_outcome: Actual result of operation
            
        Returns:
            alignment_verified: True if operations align with values
            discrepancy_description: Explanation if not aligned
        """
        # Define value → outcome mappings
        value_outcome_rules = {
            "Maintain stability": {
                "expected_outcomes": ["volatility_decreased", "scarindex_stable"],
                "incompatible_outcomes": ["volatility_increased", "market_collapse"]
            },
            "Maximize exploration": {
                "expected_outcomes": ["new_strategies_tested", "diversity_increased"],
                "incompatible_outcomes": ["exploration_suppressed", "homogeneity"]
            },
            "Ensure transparency": {
                "expected_outcomes": ["audit_coverage_increased", "logs_complete"],
                "incompatible_outcomes": ["audit_gaps", "opaque_operations"]
            }
        }
        
        if stated_value not in value_outcome_rules:
            return False, f"Unknown value: {stated_value}"
        
        rule = value_outcome_rules[stated_value]
        outcome_type = actual_outcome.get("type", "unknown")
        
        # Check if outcome aligns with value
        if outcome_type in rule["expected_outcomes"]:
            return True, f"Operation {operation_type} serves {stated_value}"
        elif outcome_type in rule["incompatible_outcomes"]:
            return False, (
                f"Operation {operation_type} diverges from value {stated_value}. "
                f"Outcome {outcome_type} is incompatible."
            )
        else:
            return False, f"Cannot determine if {outcome_type} serves {stated_value}"
    
    def check_reflexive_validation(
        self,
        alignment_claim: str,
        audit_evidence: Dict
    ) -> Tuple[bool, float]:
        """
        Verify: C_audit(t) validates recursive alignment
        Audit confirms alignment claims
        
        Args:
            alignment_claim: Claim that operations align with values
            audit_evidence: Evidence from audit logs
            
        Returns:
            validation_result: True if audit confirms claim
            confidence_score: 0-1 confidence in validation
        """
        # Extract evidence quality metrics
        trace_fidelity = audit_evidence.get("trace_fidelity", 0.0)
        audit_coverage = audit_evidence.get("audit_coverage", 0.0)
        log_completeness = audit_evidence.get("log_completeness", 0.0)
        
        # Calculate evidence quality
        evidence_quality = (trace_fidelity + audit_coverage + log_completeness) / 3.0
        
        # Require minimum evidence quality
        if evidence_quality < 0.70:
            return False, evidence_quality
        
        # Check if evidence supports claim
        supports_claim = audit_evidence.get("supports_claim", False)
        
        if supports_claim:
            # Confidence based on evidence quality
            confidence = evidence_quality
            return True, confidence
        else:
            return False, 0.0
    
    def detect_failure_modes(
        self,
        coherence: CoherenceScores,
        recursive_aligned: bool,
        reflexive_validated: bool
    ) -> Tuple[List[FailureMode], str]:
        """
        Classify legitimacy failure modes
        
        Args:
            coherence: Three-system coherence scores
            recursive_aligned: Operations serve values?
            reflexive_validated: Audit confirms alignment?
            
        Returns:
            failure_modes: List of detected failure modes
            severity: Overall severity (LOW, MEDIUM, HIGH, CRITICAL)
        """
        modes = []
        
        # Mode 1: Stable but unjust
        if coherence.c_operational > 0.80 and coherence.c_constitutional < 0.60:
            modes.append(FailureMode.STABLE_BUT_UNJUST)
        
        # Mode 2: Just but unstable
        if coherence.c_constitutional > 0.80 and coherence.c_operational < 0.60:
            modes.append(FailureMode.JUST_BUT_UNSTABLE)
        
        # Mode 3: Opaque
        if coherence.c_audit < 0.70:
            modes.append(FailureMode.OPAQUE)
        
        # Mode 4: Divergent operations
        if not recursive_aligned:
            modes.append(FailureMode.DIVERGENT_OPERATIONS)
        
        # Mode 5: Unvalidated alignment
        if not reflexive_validated:
            modes.append(FailureMode.UNVALIDATED_ALIGNMENT)
        
        # Calculate severity
        if len(modes) >= 3:
            severity = "CRITICAL"
        elif len(modes) == 2:
            severity = "HIGH"
        elif len(modes) == 1:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        return modes, severity
    
    def calculate_legitimacy_score(
        self,
        coherence: CoherenceScores,
        recursive_aligned: bool,
        reflexive_validated: bool
    ) -> Tuple[float, str]:
        """
        Calculate legitimacy score with modifiers
        
        Args:
            coherence: Three-system coherence scores
            recursive_aligned: Operations serve values?
            reflexive_validated: Audit confirms alignment?
            
        Returns:
            legitimacy_score: 0-1 score
            classification: LEGITIMATE, CONDITIONALLY_LEGITIMATE, QUESTIONABLE, ILLEGITIMATE
        """
        # Base score (weighted average)
        w1, w2, w3 = 0.30, 0.30, 0.40
        L_base = (
            w1 * coherence.c_operational +
            w2 * coherence.c_audit +
            w3 * coherence.c_constitutional
        )
        
        # Modifiers
        modifiers = 0.0
        
        if recursive_aligned:
            modifiers += 0.10
        
        if reflexive_validated:
            modifiers += 0.10
        
        if coherence.c_audit < 0.70:
            modifiers -= 0.20
        
        if coherence.c_constitutional < 0.60:
            modifiers -= 0.30
        
        # Final score (clamped to [0, 1])
        L_final = max(0.0, min(1.0, L_base + modifiers))
        
        # Classification
        if L_final >= 0.90:
            classification = "LEGITIMATE"
        elif L_final >= 0.75:
            classification = "CONDITIONALLY_LEGITIMATE"
        elif L_final >= 0.60:
            classification = "QUESTIONABLE"
        else:
            classification = "ILLEGITIMATE"
        
        return L_final, classification
    
    def generate_justification_trace(
        self,
        coherence: CoherenceScores,
        recursive_aligned: bool,
        reflexive_validated: bool,
        failure_modes: List[FailureMode],
        legitimacy_score: float,
        classification: str
    ) -> Dict:
        """
        Generate auditable explanation of legitimacy score
        
        Returns:
            justification_trace: Complete audit trail
        """
        # Calculate modifiers applied
        modifiers_applied = {}
        
        if recursive_aligned:
            modifiers_applied["recursive_alignment_bonus"] = +0.10
        
        if reflexive_validated:
            modifiers_applied["reflexive_validation_bonus"] = +0.10
        
        if coherence.c_audit < 0.70:
            modifiers_applied["opacity_penalty"] = -0.20
        
        if coherence.c_constitutional < 0.60:
            modifiers_applied["injustice_penalty"] = -0.30
        
        # Generate recommendations
        recommendations = []
        
        if coherence.c_operational < 0.70:
            recommendations.append("Improve operational stability (C_operational < 0.70)")
        
        if coherence.c_audit < 0.80:
            recommendations.append("Increase audit coverage (C_audit < 0.80)")
        
        if coherence.c_constitutional < 0.75:
            recommendations.append("Enhance constitutional coherence (C_constitutional < 0.75)")
        
        if not recursive_aligned:
            recommendations.append("Realign operations with stated values")
        
        if not reflexive_validated:
            recommendations.append("Improve audit validation of alignment claims")
        
        # Construct trace
        trace = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "legitimacy_score": round(legitimacy_score, 4),
            "classification": classification,
            "coherence_scores": {
                "c_operational": round(coherence.c_operational, 4),
                "c_audit": round(coherence.c_audit, 4),
                "c_constitutional": round(coherence.c_constitutional, 4)
            },
            "alignment_checks": {
                "recursive_alignment": {
                    "verified": recursive_aligned,
                    "description": "Operations serve stated values" if recursive_aligned else "Operations diverge from values"
                },
                "reflexive_validation": {
                    "verified": reflexive_validated,
                    "description": "Audit confirms alignment" if reflexive_validated else "Audit does not confirm alignment"
                }
            },
            "modifiers_applied": modifiers_applied,
            "failure_modes": [mode.value for mode in failure_modes],
            "recommendations": recommendations
        }
        
        return trace
    
    def _get_unit(self, param_name: str) -> str:
        """Get unit for parameter"""
        units = {
            "volatility_threshold": "ratio",
            "exploration_rate": "ratio",
            "audit_coverage": "ratio",
            "trace_fidelity": "ratio",
            "value_alignment_threshold": "ratio",
            "stakeholder_representation_min": "ratio"
        }
        return units.get(param_name, "dimensionless")
    
    def _assess_values(self, control_params: Dict[str, float]) -> str:
        """Assess which values are being served by control parameters"""
        assessments = []
        
        volatility = control_params.get("volatility_threshold", 0.10)
        if volatility < 0.07:
            assessments.append("Precautionary Principle (stability prioritized)")
        elif volatility > 0.13:
            assessments.append("Proactionary Ethic (exploration prioritized)")
        else:
            assessments.append("Balanced approach (SOC targeting)")
        
        audit_coverage = control_params.get("audit_coverage", 0.80)
        if audit_coverage > 0.90:
            assessments.append("High transparency (audit maximized)")
        elif audit_coverage < 0.70:
            assessments.append("Low transparency (audit minimized)")
        
        return "; ".join(assessments) if assessments else "Neutral value stance"


# Example usage
if __name__ == "__main__":
    # Initialize interpreter
    interpreter = EAFInterpreter()
    
    # Example 1: Policy → Control
    print("=== Example 1: Policy → Control ===")
    policy = PolicyStatement(
        statement="Prioritize stability over exploration",
        principle="Precautionary Principle",
        priority=1,
        source="Oracle Council"
    )
    
    control_params, justification = interpreter.policy_to_control(policy)
    print(f"Policy: {policy.statement}")
    print(f"Control Parameters: {list(control_params.keys())}")
    print(f"Justification: {justification}")
    print()
    
    # Example 2: Control → Policy
    print("=== Example 2: Control → Policy ===")
    current_params = {
        "volatility_threshold": 0.04,
        "exploration_rate": 0.08
    }
    
    policy_implication, value_assessment = interpreter.control_to_policy(current_params)
    print(f"Control Parameters: {current_params}")
    print(f"Policy Implication: {policy_implication}")
    print(f"Value Assessment: {value_assessment}")
    print()
    
    # Example 3: Legitimacy Calculation
    print("=== Example 3: Legitimacy Calculation ===")
    coherence = CoherenceScores(
        c_operational=0.85,
        c_audit=0.88,
        c_constitutional=0.72
    )
    
    recursive_aligned = True
    reflexive_validated = True
    
    failure_modes, severity = interpreter.detect_failure_modes(
        coherence, recursive_aligned, reflexive_validated
    )
    
    legitimacy_score, classification = interpreter.calculate_legitimacy_score(
        coherence, recursive_aligned, reflexive_validated
    )
    
    trace = interpreter.generate_justification_trace(
        coherence, recursive_aligned, reflexive_validated,
        failure_modes, legitimacy_score, classification
    )
    
    print(f"Coherence Scores: {coherence}")
    print(f"Legitimacy Score: {legitimacy_score:.4f}")
    print(f"Classification: {classification}")
    print(f"Failure Modes: {[m.value for m in failure_modes]}")
    print(f"Severity: {severity}")
    print(f"\nJustification Trace:")
    print(json.dumps(trace, indent=2))
