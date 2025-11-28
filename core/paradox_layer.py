from dataclasses import dataclass
from typing import List, Dict, Optional, Literal
from datetime import datetime

from core.mirror_layer import MirrorLayer, QuantumTag
from core.coherence import CoherenceEngine
from core.db import db


ParadoxStrategy = Literal["reconcile", "prioritize", "purge"]
ParadoxStatus = Literal["open", "resolved", "ignored"]


@dataclass
class ParadoxCandidate:
    entity_a_type: str
    entity_a_id: str
    entity_b_type: str
    entity_b_id: str
    paradox_kind: str
    severity: float  # 0.0–1.0


@dataclass
class ParadoxRecord:
    id: str
    candidate: ParadoxCandidate
    strategy: Optional[ParadoxStrategy] = None
    status: ParadoxStatus = "open"


class ParadoxDetector:
    """
    Scans council, governance, reflections, and identity tags
    to surface internal contradictions as ParadoxCandidate objects.
    """

    def __init__(self, coherence: CoherenceEngine):
        self.coherence = coherence

    def scan_all(self) -> List[ParadoxCandidate]:
        candidates: List[ParadoxCandidate] = []
        candidates += self._scan_council_conflicts()
        candidates += self._scan_reflection_conflicts()
        candidates += self._scan_governance_conflicts()
        candidates += self._scan_identity_conflicts()
        return candidates

    def _scan_council_conflicts(self) -> List[ParadoxCandidate]:
        """
        Example: same claim_id with conflicting council_judgments
        (e.g., approve vs deny within a short time window).
        """
        rows = db.fetch_council_conflicts()
        return [
            ParadoxCandidate(
                entity_a_type="council_judgment",
                entity_a_id=row["judgment_id_a"],
                entity_b_type="council_judgment",
                entity_b_id=row["judgment_id_b"],
                paradox_kind="council_conflict",
                severity=float(row.get("severity", 0.7)),
            )
            for row in rows
        ]

    def _scan_reflection_conflicts(self) -> List[ParadoxCandidate]:
        """
        Example: system_reflections that propose mutually incompatible
        governance directions on the same scope.
        """
        rows = db.fetch_reflection_conflicts()
        return [
            ParadoxCandidate(
                entity_a_type="system_reflection",
                entity_a_id=row["reflection_id_a"],
                entity_b_type="system_reflection",
                entity_b_id=row["reflection_id_b"],
                paradox_kind="reflection_conflict",
                severity=float(row.get("severity", 0.6)),
            )
            for row in rows
        ]

    def _scan_governance_conflicts(self) -> List[ParadoxCandidate]:
        """
        Example: governance_proposals that would overwrite each other
        or set incompatible parameters.
        """
        rows = db.fetch_governance_conflicts()
        return [
            ParadoxCandidate(
                entity_a_type="governance_proposal",
                entity_a_id=row["proposal_id_a"],
                entity_b_type="governance_proposal",
                entity_b_id=row["proposal_id_b"],
                paradox_kind="governance_conflict",
                severity=float(row.get("severity", 0.8)),
            )
            for row in rows
        ]

    def _scan_identity_conflicts(self) -> List[ParadoxCandidate]:
        """
        Example: the same origin/intent pair tagged with systematically
        opposing outcomes (identity drift / role contradiction).
        """
        rows = db.fetch_identity_conflicts()
        return [
            ParadoxCandidate(
                entity_a_type=row["entity_type_a"],
                entity_a_id=row["entity_id_a"],
                entity_b_type=row["entity_type_b"],
                entity_b_id=row["entity_id_b"],
                paradox_kind="identity_conflict",
                severity=float(row.get("severity", 0.5)),
            )
            for row in rows
        ]


class ParadoxResolver:
    """
    Applies a resolution strategy to each ParadoxCandidate and records
    the result in paradox_events + paradox_resolutions.
    """

    def __init__(self, mirror_layer: MirrorLayer, coherence: CoherenceEngine):
        self.mirror_layer = mirror_layer
        self.coherence = coherence

    def resolve(self, candidate: ParadoxCandidate) -> ParadoxRecord:
        strategy = self._choose_strategy(candidate)
        event_id = db.insert_paradox_event(candidate, strategy)

        if strategy == "reconcile":
            self._reconcile(candidate, event_id)
        elif strategy == "prioritize":
            self._prioritize(candidate, event_id)
        elif strategy == "purge":
            self._purge(candidate, event_id)

        return ParadoxRecord(
            id=event_id,
            candidate=candidate,
            strategy=strategy,
            status="resolved",
        )

    def _choose_strategy(self, candidate: ParadoxCandidate) -> ParadoxStrategy:
        """
        Simple decision heuristic (can be upgraded to ML or rule engine later):
        - Severe governance conflicts → prioritize or purge.
        - Mild reflection conflicts → reconcile.
        - Identity conflicts → reconcile or purge.
        """
        k = candidate.paradox_kind
        s = candidate.severity

        if k == "governance_conflict" and s >= 0.8:
            return "prioritize"
        if k == "council_conflict" and s >= 0.75:
            return "reconcile"
        if k == "identity_conflict" and s < 0.6:
            return "reconcile"
        if k == "reflection_conflict" and s < 0.7:
            return "reconcile"
        # fallback
        return "purge" if s >= 0.85 else "prioritize"

    def _reconcile(self, candidate: ParadoxCandidate, event_id: str) -> None:
        """
        Merge states into a harmonic configuration:
        - compute a blended configuration based on certainty / ScarIndex.
        - update underlying rows.
        """
        before_state = db.fetch_entities_state(candidate)
        merged_state = self.coherence.blend_states(before_state)
        db.apply_state_update(candidate, merged_state)
        db.insert_paradox_resolution(
            event_id=event_id,
            strategy="reconcile",
            before_state=before_state,
            after_state=merged_state,
        )

    def _prioritize(self, candidate: ParadoxCandidate, event_id: str) -> None:
        """
        Selects the more coherent / higher-authority option based on:
        - origin priority (e.g., ZoaGrad > System > Pantheon, etc.)
        - coherence contribution (delta ScarIndex)
        """
        before_state = db.fetch_entities_state(candidate)
        chosen_state = self.coherence.select_preferred(before_state)
        db.apply_state_update(candidate, chosen_state)
        db.insert_paradox_resolution(
            event_id=event_id,
            strategy="prioritize",
            before_state=before_state,
            after_state=chosen_state,
        )

    def _purge(self, candidate: ParadoxCandidate, event_id: str) -> None:
        """
        Soft-delete or deactivate the less coherent or spurious element.
        """
        before_state = db.fetch_entities_state(candidate)
        purged_state = self.coherence.mark_incoherent(before_state)
        db.apply_state_update(candidate, purged_state)
        db.insert_paradox_resolution(
            event_id=event_id,
            strategy="purge",
            before_state=before_state,
            after_state=purged_state,
        )


class ParadoxEngine:
    """
    Periodically runs paradox detection + resolution, and logs
    coherence changes to ensure bounded oscillation.
    """

    def __init__(self, mirror_layer: MirrorLayer, coherence: CoherenceEngine):
        self.detector = ParadoxDetector(coherence)
        self.resolver = ParadoxResolver(mirror_layer, coherence)
        self.coherence = coherence

    def run_cycle(self) -> Dict[str, any]:
        """
        One paradox resolution cycle:
        - detect candidates
        - resolve them
        - measure coherence delta
        """
        start_c = self.coherence.current_score()
        candidates = self.detector.scan_all()
        resolved_records: List[ParadoxRecord] = []

        for c in candidates:
            record = self.resolver.resolve(c)
            resolved_records.append(record)

        end_c = self.coherence.current_score()
        delta_c = end_c - start_c

        db.log_paradox_cycle(
            started_at=datetime.utcnow(),
            num_candidates=len(candidates),
            num_resolved=len(resolved_records),
            coherence_delta=delta_c,
        )

        return {
            "candidates": len(candidates),
            "resolved": len(resolved_records),
            "coherence_delta": delta_c,
        }
