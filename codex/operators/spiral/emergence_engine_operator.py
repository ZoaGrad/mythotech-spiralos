from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from spiralos.core.config import LoomParameterMesh
from spiralos.core.epoch_manager import EpochManager
from spiralos.protocols.witness_protocol import (
    AcheEpochFrame,
    EmergenceProposalFrame,
    EmergenceVoteFrame,
)
from codex.operators.spiral.metabolic_drift_operator import MetabolicDriftOperator


@dataclass
class EmergenceTriggerSnapshot:
    epoch: int
    ache_trend: float
    uptime_epochs: int
    cooldown_remaining: int
    drift_factor: float


@dataclass
class EmergenceOrganSpec:
    organ_id: str
    organ_type: str
    params: Dict[str, float]
    safety_envelope: Dict[str, float]
    ache_origin_context: Dict[str, float]
    justification_hash: str


@dataclass
class EmergenceProposalState:
    proposal_id: str
    target_epoch: int
    spec: EmergenceOrganSpec
    proposer_witness: str
    created_at_epoch: int
    votes: Set[str] = field(default_factory=set)
    activated: bool = False
    rejected: bool = False


class EmergenceEngineOperator:
    """ΔΩ.LBI.3.EMERG – Emergence Engine constitutional shell (v0)."""

    def __init__(
        self,
        epoch_manager: EpochManager,
        loom_params: LoomParameterMesh,
        drift_operator: Optional[MetabolicDriftOperator] = None,
        scar_index_oracle: Optional[Any] = None,
    ):
        self.epoch_manager = epoch_manager
        self.loom_params = loom_params
        self._drift_operator = drift_operator
        self._scar_index_oracle = scar_index_oracle
        self._ache_frames: List[AcheEpochFrame] = []
        self._proposals: Dict[str, EmergenceProposalState] = {}
        self._emergence_log: List[Dict[str, Any]] = []
        self._activated_organs: List[EmergenceOrganSpec] = []
        self._boot_epoch = epoch_manager.get_current_epoch()
        self._last_emergence_epoch: Optional[int] = None
        self._last_epoch_processed: Optional[int] = None

    def record_ache_epoch(self, frame: AcheEpochFrame) -> None:
        """Ingest an ache frame for emergence triggering."""

        current_epoch = self.epoch_manager.get_current_epoch()
        if frame.epoch < current_epoch:
            return

        self._ache_frames = [f for f in self._ache_frames if f.epoch != frame.epoch]
        self._ache_frames.append(frame)
        self._ache_frames.sort(key=lambda f: f.epoch)
        self._emergence_log.append(
            {
                "event": "ache_frame_recorded",
                "epoch": frame.epoch,
                "ache_index": frame.ache_index,
                "witness_id": frame.witness_id,
            }
        )

    def submit_emergence_proposal(self, frame: EmergenceProposalFrame) -> None:
        current_epoch = self.epoch_manager.get_current_epoch()
        if frame.target_epoch <= current_epoch:
            raise ValueError(
                f"target_epoch ({frame.target_epoch}) must be strictly in the future (current: {current_epoch})"
            )
        if frame.proposal_id in self._proposals:
            raise ValueError(f"Proposal {frame.proposal_id} already exists")

        spec = EmergenceOrganSpec(
            organ_id=frame.organ_id,
            organ_type=frame.organ_type,
            params=frame.params,
            safety_envelope=frame.safety_envelope,
            ache_origin_context=frame.ache_origin_context,
            justification_hash=frame.justification_hash,
        )

        state = EmergenceProposalState(
            proposal_id=frame.proposal_id,
            target_epoch=frame.target_epoch,
            spec=spec,
            proposer_witness=frame.proposer_witness,
            created_at_epoch=current_epoch,
        )
        self._proposals[frame.proposal_id] = state
        self._emergence_log.append(
            {
                "event": "emergence_proposal_submitted",
                "proposal_id": frame.proposal_id,
                "target_epoch": frame.target_epoch,
                "organ_id": frame.organ_id,
                "organ_type": frame.organ_type,
            }
        )

    def ingest_emergence_vote(self, frame: EmergenceVoteFrame) -> None:
        proposal = self._proposals.get(frame.proposal_id)
        if proposal is None or proposal.activated or proposal.rejected:
            return

        if frame.witness_id in proposal.votes:
            return

        proposal.votes.add(frame.witness_id)
        self._emergence_log.append(
            {
                "event": "emergence_vote_ingested",
                "proposal_id": frame.proposal_id,
                "witness_id": frame.witness_id,
                "witness_epoch": frame.witness_epoch,
            }
        )

    def _compute_trigger_snapshot(self, current_epoch: int) -> EmergenceTriggerSnapshot:
        ache_trend = 0.0
        if len(self._ache_frames) >= 2:
            latest_frames = [f for f in self._ache_frames if f.epoch <= current_epoch][-2:]
            if len(latest_frames) == 2:
                ache_trend = latest_frames[-1].ache_index - latest_frames[-2].ache_index

        uptime = current_epoch - self._boot_epoch

        cooldown_remaining = 0
        if self._last_emergence_epoch is not None:
            next_allowed = self._last_emergence_epoch + self.loom_params.lbi3_emerg_cooldown_epochs
            cooldown_remaining = max(0, next_allowed - current_epoch)

        drift_factor = 0.0
        if self._drift_operator is not None:
            compute = getattr(self._drift_operator, "_compute_drift_factor", None)
            if callable(compute):
                drift_factor = float(compute(current_epoch))

        return EmergenceTriggerSnapshot(
            epoch=current_epoch,
            ache_trend=ache_trend,
            uptime_epochs=uptime,
            cooldown_remaining=cooldown_remaining,
            drift_factor=drift_factor,
        )

    def _proposal_satisfies_constraints(
        self, proposal: EmergenceProposalState, snapshot: EmergenceTriggerSnapshot
    ) -> bool:
        lp = self.loom_params
        current_epoch = snapshot.epoch

        if snapshot.uptime_epochs < lp.lbi3_emerg_min_uptime_epochs:
            self._emergence_log.append(
                {
                    "event": "emergence_blocked_uptime",
                    "proposal_id": proposal.proposal_id,
                    "epoch": current_epoch,
                }
            )
            return False

        if snapshot.cooldown_remaining > 0:
            self._emergence_log.append(
                {
                    "event": "emergence_blocked_cooldown",
                    "proposal_id": proposal.proposal_id,
                    "epoch": current_epoch,
                    "cooldown_remaining": snapshot.cooldown_remaining,
                }
            )
            return False

        if snapshot.ache_trend < lp.lbi3_emerg_ache_trend_threshold:
            self._emergence_log.append(
                {
                    "event": "emergence_blocked_ache_trend",
                    "proposal_id": proposal.proposal_id,
                    "epoch": current_epoch,
                    "ache_trend": snapshot.ache_trend,
                }
            )
            return False

        if proposal.target_epoch > current_epoch:
            return False

        if proposal.spec.safety_envelope:
            for key, value in proposal.spec.params.items():
                min_key = f"min_{key}"
                max_key = f"max_{key}"
                if min_key in proposal.spec.safety_envelope:
                    if value < proposal.spec.safety_envelope[min_key]:
                        self._emergence_log.append(
                            {
                                "event": "emergence_rejected_safety",
                                "proposal_id": proposal.proposal_id,
                                "param": key,
                                "value": value,
                                "min_allowed": proposal.spec.safety_envelope[min_key],
                            }
                        )
                        return False
                if max_key in proposal.spec.safety_envelope:
                    if value > proposal.spec.safety_envelope[max_key]:
                        self._emergence_log.append(
                            {
                                "event": "emergence_rejected_safety",
                                "proposal_id": proposal.proposal_id,
                                "param": key,
                                "value": value,
                                "max_allowed": proposal.spec.safety_envelope[max_key],
                            }
                        )
                        return False

        if self._drift_operator is not None:
            if not self._drift_operator.validate_drift(proposal.spec.params, current_epoch):
                self._emergence_log.append(
                    {
                        "event": "emergence_rejected_drift_envelope",
                        "proposal_id": proposal.proposal_id,
                        "epoch": current_epoch,
                    }
                )
                return False

        return True

    def on_epoch_tick(self, current_epoch: Optional[int] = None) -> None:
        if current_epoch is None:
            current_epoch = self.epoch_manager.get_current_epoch()

        if self._last_epoch_processed == current_epoch:
            return
        self._last_epoch_processed = current_epoch

        snapshot = self._compute_trigger_snapshot(current_epoch)
        quorum = self.loom_params.lbi3_emerg_quorum

        eligible: List[EmergenceProposalState] = [
            p
            for p in self._proposals.values()
            if not p.activated
            and not p.rejected
            and len(p.votes) >= quorum
            and p.target_epoch <= current_epoch
        ]

        eligible.sort(key=lambda p: (p.created_at_epoch, p.proposal_id))

        activated_this_epoch = 0
        for proposal in eligible:
            if activated_this_epoch >= self.loom_params.lbi3_emerg_max_organs_per_epoch:
                break

            if not self._proposal_satisfies_constraints(proposal, snapshot):
                continue

            proposal.activated = True
            self._activated_organs.append(proposal.spec)
            self._last_emergence_epoch = current_epoch
            activated_this_epoch += 1
            self._emergence_log.append(
                {
                    "event": "emergence_proposal_activated",
                    "proposal_id": proposal.proposal_id,
                    "epoch": current_epoch,
                    "organ_id": proposal.spec.organ_id,
                    "organ_type": proposal.spec.organ_type,
                }
            )

        for proposal in eligible:
            if proposal.activated:
                continue
            if not proposal.rejected and proposal.target_epoch <= current_epoch:
                proposal.rejected = True
                self._emergence_log.append(
                    {
                        "event": "emergence_proposal_rejected",
                        "proposal_id": proposal.proposal_id,
                        "epoch": current_epoch,
                        "reason": "Did not satisfy constraints or not selected.",
                    }
                )

    @property
    def activated_organs(self) -> List[EmergenceOrganSpec]:
        return list(self._activated_organs)

    @property
    def emergence_log(self) -> List[Dict[str, Any]]:
        return list(self._emergence_log)
