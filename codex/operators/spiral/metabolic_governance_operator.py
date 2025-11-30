from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from spiralos.core.config import LoomParameterMesh
from spiralos.core.epoch_manager import EpochManager
from spiralos.protocols.witness_protocol import MetabolicVoteFrame


@dataclass
class MetabolicGovernanceProposal:
    proposal_id: str
    target_epoch: int
    params: Dict[str, float]
    proposer_witness: str
    created_at_epoch: int
    rationale_hash: str
    votes: Set[str] = field(default_factory=set)
    activated: bool = False
    superseded: bool = False


class MetabolicGovernanceOperator:
    """ΔΩ.LBI.3.GOV – Witness-voted governance over metabolic parameters."""

    def __init__(self, epoch_manager: EpochManager, loom_params: LoomParameterMesh):
        self.epoch_manager = epoch_manager
        self.loom_params = loom_params
        self._proposals: Dict[str, MetabolicGovernanceProposal] = {}
        self._governance_log: List[Dict[str, Any]] = []
        self._last_epoch_processed_on_tick: Optional[int] = None

    def submit_proposal(
        self,
        proposal_id: str,
        target_epoch: int,
        params: Dict[str, float],
        proposer_witness: str,
        rationale_hash: str,
    ) -> None:
        current_epoch = self.epoch_manager.get_current_epoch()
        if target_epoch <= current_epoch:
            raise ValueError(
                f"target_epoch ({target_epoch}) must be strictly in the future (current: {current_epoch})"
            )
        if proposal_id in self._proposals:
            raise ValueError(f"Proposal {proposal_id} already exists")

        proposal = MetabolicGovernanceProposal(
            proposal_id=proposal_id,
            target_epoch=target_epoch,
            params=params,
            proposer_witness=proposer_witness,
            created_at_epoch=current_epoch,
            rationale_hash=rationale_hash,
        )
        self._proposals[proposal_id] = proposal
        self._governance_log.append(
            {
                "event": "proposal_submitted",
                "proposal_id": proposal_id,
                "epoch": current_epoch,
                "target_epoch": target_epoch,
                "params": params,
            }
        )

    def ingest_metabolic_vote(self, frame: MetabolicVoteFrame) -> None:
        proposal = self._proposals.get(frame.proposal_id)
        if proposal is None:
            return

        if not (
            frame.target_epoch == proposal.target_epoch
            and frame.rationale_hash == proposal.rationale_hash
            and frame.params == proposal.params
        ):
            return

        if frame.witness_id in proposal.votes:
            return

        proposal.votes.add(frame.witness_id)

    def _proposal_satisfies_safety(self, proposal: MetabolicGovernanceProposal) -> bool:
        p = proposal.params
        lp = self.loom_params

        beta = p.get("lbi3_beta")
        if beta is None or not (0.0 < beta <= lp.lbi3_gov_beta_max):
            self._governance_log.append(
                {
                    "event": "safety_violation",
                    "proposal_id": proposal.proposal_id,
                    "reason": f"lbi3_beta out of bounds (0 < {beta} <= {lp.lbi3_gov_beta_max})",
                }
            )
            return False

        for weight_key in ("lbi3_w_heal", "lbi3_w_truth", "lbi3_w_rot"):
            w = p.get(weight_key)
            if w is None or not (0.0 <= w <= lp.lbi3_gov_weight_max):
                self._governance_log.append(
                    {
                        "event": "safety_violation",
                        "proposal_id": proposal.proposal_id,
                        "reason": f"{weight_key} out of bounds (0 <= {w} <= {lp.lbi3_gov_weight_max})",
                    }
                )
                return False

        m_min = p.get("lbi3_m_min")
        m_max = p.get("lbi3_m_max")
        if m_min is None or m_max is None:
            self._governance_log.append(
                {
                    "event": "safety_violation",
                    "proposal_id": proposal.proposal_id,
                    "reason": "lbi3_m_min or lbi3_m_max missing",
                }
            )
            return False
        if not (0.0 < m_min <= 1.0):
            self._governance_log.append(
                {
                    "event": "safety_violation",
                    "proposal_id": proposal.proposal_id,
                    "reason": f"lbi3_m_min out of bounds (0 < {m_min} <= 1.0)",
                }
            )
            return False
        if not (m_min <= m_max <= lp.lbi3_gov_m_factor_max):
            self._governance_log.append(
                {
                    "event": "safety_violation",
                    "proposal_id": proposal.proposal_id,
                    "reason": f"lbi3_m_max out of bounds or m_min > m_max ({m_min} <= {m_max} <= {lp.lbi3_gov_m_factor_max})",
                }
            )
            return False

        return True

    def on_epoch_tick(self, current_epoch: Optional[int] = None) -> None:
        if current_epoch is None:
            current_epoch = self.epoch_manager.get_current_epoch()

        if self._last_epoch_processed_on_tick == current_epoch:
            return
        self._last_epoch_processed_on_tick = current_epoch

        candidates: List[MetabolicGovernanceProposal] = [
            p
            for p in self._proposals.values()
            if p.target_epoch == current_epoch
            and not p.activated
            and not p.superseded
            and len(p.votes) >= self.loom_params.lbi3_gov_quorum
        ]

        if not candidates:
            return

        candidates.sort(key=lambda p: (p.created_at_epoch, p.proposal_id))
        winner = candidates[0]

        if not self._proposal_satisfies_safety(winner):
            winner.superseded = True
            reason = self._governance_log[-1].get("reason", "unknown") if self._governance_log else "unknown"
            self._governance_log.append(
                {
                    "event": "proposal_rejected_safety_envelope",
                    "proposal_id": winner.proposal_id,
                    "epoch": current_epoch,
                    "reason": reason,
                }
            )
            return

        for loser in candidates[1:]:
            loser.superseded = True
            self._governance_log.append(
                {
                    "event": "proposal_superseded",
                    "proposal_id": loser.proposal_id,
                    "epoch": current_epoch,
                    "reason": f"Superseded by {winner.proposal_id}",
                }
            )

        params = winner.params
        self.loom_params.lbi3_w_heal = params["lbi3_w_heal"]
        self.loom_params.lbi3_w_truth = params["lbi3_w_truth"]
        self.loom_params.lbi3_w_rot = params["lbi3_w_rot"]
        self.loom_params.lbi3_beta = params["lbi3_beta"]
        self.loom_params.lbi3_m_min = params["lbi3_m_min"]
        self.loom_params.lbi3_m_max = params["lbi3_m_max"]

        winner.activated = True
        self._governance_log.append(
            {
                "event": "proposal_activated",
                "proposal_id": winner.proposal_id,
                "epoch": current_epoch,
                "applied_params": params,
            }
        )

    @property
    def governance_log(self) -> List[Dict[str, Any]]:
        return list(self._governance_log)
