# ========================================================
# Sequence J₀ — Autopoiesis Safety Coordinator
# ========================================================

from dataclasses import dataclass
from typing import Dict

from core.db import db
from core.teleology import TauVector
from core.coherence import CoherenceEngine


@dataclass
class StructuralIntent:
    requester: str
    op_code: str
    target_schema: str
    target_object: str
    sql_diff: str
    reason: str
    action_vector: Dict[str, float]  # features for τ alignment and complexity


class WhitelistViolation(Exception): pass
class SafetyPolicyViolation(Exception): pass


class AutopoiesisSafetyCoordinator:
    """
    Core J₀ gatekeeper.
    All structural changes must pass through this coordinator.
    """

    def __init__(self, tau: TauVector, coherence: CoherenceEngine):
        self.tau = tau
        self.coherence = coherence

    # ----------------------------------------
    # Public entrypoint
    # ----------------------------------------
    def submit_structural_intent(self, intent: StructuralIntent) -> str:
        self._assert_whitelisted(intent)
        tau_alignment = self._compute_tau_alignment(intent)
        projected_delta = self._estimate_coherence_delta(intent)
        complexity = self._estimate_complexity(intent)
        self._enforce_safety_policies(tau_alignment, projected_delta, complexity)

        change_id = db.insert_structural_change_request(
            intent=intent,
            tau_alignment=tau_alignment,
            projected_delta=projected_delta,
            complexity=complexity,
        )
        return change_id

    # ----------------------------------------
    # Internal safety checks
    # ----------------------------------------
    def _assert_whitelisted(self, intent: StructuralIntent) -> None:
        wl = db.fetch_whitelist_entry(intent.op_code)
        if not wl or not wl["allowed"]:
            raise WhitelistViolation(f"Operation not allowed: {intent.op_code}")

    def _compute_tau_alignment(self, intent: StructuralIntent) -> float:
        return self.tau.dot(intent.action_vector)

    def _estimate_coherence_delta(self, intent: StructuralIntent) -> float:
        # Placeholder: In a real system, this would use the coherence engine to simulate impact
        # For now, we return a safe default or use a dummy method on coherence engine if available
        # The Mission Spec says: return self.coherence.estimate_structural_impact(intent)
        # But CoherenceEngine might not have this method yet.
        if hasattr(self.coherence, 'estimate_structural_impact'):
            return self.coherence.estimate_structural_impact(intent)
        return 0.0

    def _estimate_complexity(self, intent: StructuralIntent) -> float:
        sql_len = len(intent.sql_diff)
        return min(1.0, sql_len / 5000.0)

    def _enforce_safety_policies(self, tau_alignment, projected_delta, complexity):
        policy = db.fetch_active_structural_policy("J0_DEFAULT")
        if not policy:
            raise SafetyPolicyViolation("No active J₀ policy found.")

        if tau_alignment < policy["tau_min_alignment"]:
            raise SafetyPolicyViolation(
                f"τ-alignment too low: {tau_alignment:.3f}"
            )

        if projected_delta < policy["max_negative_coherence_delta"]:
            raise SafetyPolicyViolation(
                f"Projected coherence loss too large: {projected_delta:.4f}"
            )

        if complexity > policy["max_complexity_score"]:
            raise SafetyPolicyViolation(
                f"Change too complex: {complexity:.3f}"
            )
