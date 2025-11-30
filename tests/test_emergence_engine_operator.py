from dataclasses import dataclass
from typing import Dict, List, Optional

import pytest

from codex.operators.spiral.emergence_engine_operator import EmergenceEngineOperator
from spiralos.protocols.witness_protocol import (
    AcheEpochFrame,
    EmergenceProposalFrame,
    EmergenceVoteFrame,
)


class LoomParameterMesh:
    def __init__(
        self,
        lbi3_emerg_quorum: int = 3,
        lbi3_emerg_min_uptime_epochs: int = 2,
        lbi3_emerg_ache_trend_threshold: float = 0.05,
        lbi3_emerg_cooldown_epochs: int = 2,
        lbi3_emerg_max_organs_per_epoch: int = 1,
    ):
        self.lbi3_emerg_quorum = lbi3_emerg_quorum
        self.lbi3_emerg_min_uptime_epochs = lbi3_emerg_min_uptime_epochs
        self.lbi3_emerg_ache_trend_threshold = lbi3_emerg_ache_trend_threshold
        self.lbi3_emerg_cooldown_epochs = lbi3_emerg_cooldown_epochs
        self.lbi3_emerg_max_organs_per_epoch = lbi3_emerg_max_organs_per_epoch

        # Drift parameters consumed by stub drift operator
        self.lbi3_drift_cap_w_heal = 0.0
        self.lbi3_drift_cap_w_truth = 0.0
        self.lbi3_drift_cap_w_rot = 0.0
        self.lbi3_drift_cap_beta = 0.0
        self.lbi3_drift_cap_m_min = 0.0
        self.lbi3_drift_cap_m_max = 0.0
        self.lbi3_drift_ache_floor = 0.0
        self.lbi3_drift_ache_ceiling = 1.0
        self.lbi3_drift_kappa = 1.0


class EpochManager:
    def __init__(self, current_epoch: int = 0):
        self._current_epoch = current_epoch

    def get_current_epoch(self) -> int:
        return self._current_epoch

    def advance_epoch(self) -> int:
        self._current_epoch += 1
        return self._current_epoch


@dataclass
class StubMetabolicDriftOperator:
    should_validate: bool = True

    def validate_drift(self, proposal_params: Dict[str, float], epoch: Optional[int] = None) -> bool:
        return self.should_validate

    def _compute_drift_factor(self, epoch: int) -> float:
        return 1.0


def build_proposal(
    proposal_id: str,
    target_epoch: int,
    organ_id: str = "organ.alpha",
    ache_origin_context: Optional[Dict[str, float]] = None,
) -> EmergenceProposalFrame:
    return EmergenceProposalFrame(
        proposal_id=proposal_id,
        organ_id=organ_id,
        organ_type="metabolic",
        params={"lbi3_w_heal": 0.6},
        safety_envelope={"min_lbi3_w_heal": 0.1, "max_lbi3_w_heal": 1.0},
        ache_origin_context=ache_origin_context or {"ache_delta": 0.2},
        justification_hash="hash",
        target_epoch=target_epoch,
        proposer_witness="witness_A",
        witness_epoch=target_epoch - 1,
        multisig=["sig_A"],
    )


def ingest_votes(operator: EmergenceEngineOperator, proposal_id: str, voters: List[str]) -> None:
    for idx, witness in enumerate(voters, start=1):
        operator.ingest_emergence_vote(
            EmergenceVoteFrame(
                proposal_id=proposal_id,
                witness_id=witness,
                witness_epoch=operator.epoch_manager.get_current_epoch(),
                multisig=[f"sig_{idx}"],
            )
        )


def test_quorum_and_activation_flow():
    loom_params = LoomParameterMesh()
    epoch_manager = EpochManager(current_epoch=0)
    drift_operator = StubMetabolicDriftOperator()
    operator = EmergenceEngineOperator(epoch_manager, loom_params, drift_operator=drift_operator)

    epoch_manager.advance_epoch()  # 1
    operator.record_ache_epoch(AcheEpochFrame(epoch=1, ache_index=0.1, witness_id="w1", multisig=["sig"]))
    epoch_manager.advance_epoch()  # 2
    operator.record_ache_epoch(AcheEpochFrame(epoch=2, ache_index=0.3, witness_id="w2", multisig=["sig"]))

    proposal = build_proposal("prop-1", target_epoch=3)
    operator.submit_emergence_proposal(proposal)
    ingest_votes(operator, proposal.proposal_id, ["w1", "w2"])  # below quorum

    epoch_manager.advance_epoch()  # 7
    operator.on_epoch_tick(epoch_manager.get_current_epoch())
    assert not operator.activated_organs

    ingest_votes(operator, proposal.proposal_id, ["w3"])
    epoch_manager.advance_epoch()  # 3
    operator.on_epoch_tick(epoch_manager.get_current_epoch())

    assert len(operator.activated_organs) == 1
    assert operator.activated_organs[0].organ_id == "organ.alpha"
    assert any(entry["event"] == "emergence_proposal_activated" for entry in operator.emergence_log)


def test_cooldown_and_max_organs_per_epoch():
    loom_params = LoomParameterMesh(lbi3_emerg_max_organs_per_epoch=1, lbi3_emerg_min_uptime_epochs=1)
    epoch_manager = EpochManager(current_epoch=5)
    operator = EmergenceEngineOperator(epoch_manager, loom_params, drift_operator=StubMetabolicDriftOperator())

    operator.record_ache_epoch(AcheEpochFrame(epoch=5, ache_index=0.2, witness_id="w1", multisig=["sig"]))
    epoch_manager.advance_epoch()  # 6
    operator.record_ache_epoch(AcheEpochFrame(epoch=6, ache_index=0.5, witness_id="w2", multisig=["sig"]))

    proposal_a = build_proposal("prop-A", target_epoch=7, organ_id="organ.A")
    proposal_b = build_proposal("prop-B", target_epoch=7, organ_id="organ.B")
    operator.submit_emergence_proposal(proposal_a)
    operator.submit_emergence_proposal(proposal_b)
    ingest_votes(operator, proposal_a.proposal_id, ["w1", "w2", "w3"])
    ingest_votes(operator, proposal_b.proposal_id, ["w1", "w2", "w3"])

    epoch_manager.advance_epoch()  # 7
    operator.on_epoch_tick(epoch_manager.get_current_epoch())
    assert len(operator.activated_organs) == 1
    assert {p.proposal_id for p in operator._proposals.values() if p.activated} == {"prop-A"}

    # Cooldown should block activations in the next epoch
    proposal_c = build_proposal("prop-C", target_epoch=8, organ_id="organ.C")
    operator.submit_emergence_proposal(proposal_c)
    ingest_votes(operator, proposal_c.proposal_id, ["w1", "w2", "w3"])
    epoch_manager.advance_epoch()  # 8
    operator.on_epoch_tick(epoch_manager.get_current_epoch())

    assert not any(p.proposal_id == "prop-C" and p.activated for p in operator._proposals.values())
    assert any(entry["event"] == "emergence_blocked_cooldown" for entry in operator.emergence_log)


def test_rejection_on_drift_violation():
    loom_params = LoomParameterMesh(lbi3_emerg_min_uptime_epochs=1)
    epoch_manager = EpochManager(current_epoch=3)
    drift_operator = StubMetabolicDriftOperator(should_validate=False)
    operator = EmergenceEngineOperator(epoch_manager, loom_params, drift_operator=drift_operator)

    operator.record_ache_epoch(AcheEpochFrame(epoch=3, ache_index=0.2, witness_id="w1", multisig=["sig"]))
    epoch_manager.advance_epoch()  # 4
    operator.record_ache_epoch(AcheEpochFrame(epoch=4, ache_index=0.4, witness_id="w2", multisig=["sig"]))

    proposal = build_proposal("prop-drift", target_epoch=5)
    operator.submit_emergence_proposal(proposal)
    ingest_votes(operator, proposal.proposal_id, ["w1", "w2", "w3"])

    epoch_manager.advance_epoch()  # 5
    operator.on_epoch_tick(epoch_manager.get_current_epoch())

    assert not any(p.activated for p in operator._proposals.values())
    assert any(entry["event"] == "emergence_rejected_drift_envelope" for entry in operator.emergence_log)


def test_ache_trend_gate_enforced():
    loom_params = LoomParameterMesh(lbi3_emerg_min_uptime_epochs=1, lbi3_emerg_ache_trend_threshold=0.5)
    epoch_manager = EpochManager(current_epoch=2)
    operator = EmergenceEngineOperator(epoch_manager, loom_params, drift_operator=StubMetabolicDriftOperator())

    operator.record_ache_epoch(AcheEpochFrame(epoch=2, ache_index=0.2, witness_id="w1", multisig=["sig"]))
    epoch_manager.advance_epoch()  # 3, ache trend insufficient
    operator.record_ache_epoch(AcheEpochFrame(epoch=3, ache_index=0.25, witness_id="w2", multisig=["sig"]))

    proposal = build_proposal("prop-trend", target_epoch=4)
    operator.submit_emergence_proposal(proposal)
    ingest_votes(operator, proposal.proposal_id, ["w1", "w2", "w3"])

    epoch_manager.advance_epoch()  # 4
    operator.on_epoch_tick(epoch_manager.get_current_epoch())
    assert not any(p.activated for p in operator._proposals.values())
    assert any(entry["event"] == "emergence_blocked_ache_trend" for entry in operator.emergence_log)
