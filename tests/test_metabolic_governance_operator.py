import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


class LoomParameterMesh:
    def __init__(self):
        self.lbi3_w_heal = 0.5
        self.lbi3_w_truth = 0.2
        self.lbi3_w_rot = 1.0
        self.lbi3_beta = 0.05
        self.lbi3_m_min = 0.5
        self.lbi3_m_max = 1.5
        self.lbi3_gov_quorum = 3
        self.lbi3_gov_beta_max = 1.0
        self.lbi3_gov_weight_max = 10.0
        self.lbi3_gov_m_factor_max = 3.0


class EpochManager:
    def __init__(self, current_epoch: int = 0):
        self._current_epoch = current_epoch

    def get_current_epoch(self) -> int:
        return self._current_epoch

    def advance_epoch(self):
        self._current_epoch += 1


@dataclass
class MetabolicVoteFrame:
    proposal_id: str
    params: Dict[str, float]
    target_epoch: int
    rationale_hash: str
    witness_id: str
    witness_epoch: int
    multisig: List[str] = field(default_factory=list)


from codex.operators.spiral.metabolic_governance_operator import (
    MetabolicGovernanceOperator,
    MetabolicGovernanceProposal,
)


@pytest.fixture
def setup_governance_operator():
    loom_params = LoomParameterMesh()
    epoch_manager = EpochManager(current_epoch=10)
    operator = MetabolicGovernanceOperator(epoch_manager, loom_params)
    return operator, epoch_manager, loom_params


def create_test_proposal(
    operator: MetabolicGovernanceOperator,
    target_epoch: int,
    params: Dict[str, float],
    proposer_witness: str = "witness_A",
    rationale_hash: str = "hash_abc",
    proposal_id: Optional[str] = None,
    created_at_epoch: Optional[int] = None,
) -> MetabolicGovernanceProposal:
    if proposal_id is None:
        proposal_id = str(uuid4())

    if created_at_epoch is None:
        created_at_epoch = operator.epoch_manager.get_current_epoch()

    operator.submit_proposal(
        proposal_id=proposal_id,
        target_epoch=target_epoch,
        params=params,
        proposer_witness=proposer_witness,
        rationale_hash=rationale_hash,
    )
    return operator._proposals[proposal_id]


def create_test_vote(
    proposal: MetabolicGovernanceProposal, witness_id: str
) -> MetabolicVoteFrame:
    return MetabolicVoteFrame(
        proposal_id=proposal.proposal_id,
        params=proposal.params,
        target_epoch=proposal.target_epoch,
        rationale_hash=proposal.rationale_hash,
        witness_id=witness_id,
        witness_epoch=proposal.created_at_epoch + 1,
        multisig=[f"sig_{witness_id}"],
    )


def test_quorum_requirement(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    target_epoch = epoch_manager.get_current_epoch() + 1

    new_params = {
        "lbi3_w_heal": 0.6,
        "lbi3_beta": 0.06,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal = create_test_proposal(operator, target_epoch, new_params)

    operator.ingest_metabolic_vote(create_test_vote(proposal, "witness_1"))
    operator.ingest_metabolic_vote(create_test_vote(proposal, "witness_2"))
    epoch_manager.advance_epoch()
    operator.on_epoch_tick()
    assert not proposal.activated
    assert loom_params.lbi3_w_heal == 0.5

    epoch_manager.advance_epoch()
    target_epoch = epoch_manager.get_current_epoch() + 1
    proposal_2 = create_test_proposal(operator, target_epoch, new_params, proposal_id="prop_2")
    operator.ingest_metabolic_vote(create_test_vote(proposal_2, "witness_1"))
    operator.ingest_metabolic_vote(create_test_vote(proposal_2, "witness_2"))
    operator.ingest_metabolic_vote(create_test_vote(proposal_2, "witness_3"))

    epoch_manager.advance_epoch()
    operator.on_epoch_tick()
    assert proposal_2.activated
    assert loom_params.lbi3_w_heal == 0.6


def test_application_at_target_epoch_only(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    initial_epoch = epoch_manager.get_current_epoch()
    target_epoch = initial_epoch + 2
    new_params = {
        "lbi3_w_heal": 0.7,
        "lbi3_beta": 0.05,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal = create_test_proposal(operator, target_epoch, new_params)

    for i in range(1, loom_params.lbi3_gov_quorum + 1):
        operator.ingest_metabolic_vote(create_test_vote(proposal, f"witness_{i}"))

    operator.on_epoch_tick(initial_epoch)
    assert not proposal.activated
    assert loom_params.lbi3_w_heal == 0.5

    epoch_manager.advance_epoch()
    operator.on_epoch_tick()
    assert not proposal.activated
    assert loom_params.lbi3_w_heal == 0.5

    epoch_manager.advance_epoch()
    operator.on_epoch_tick()
    assert proposal.activated
    assert loom_params.lbi3_w_heal == 0.7


def test_rejection_of_unsafe_proposal(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    target_epoch = epoch_manager.get_current_epoch() + 1

    unsafe_params = {
        "lbi3_w_heal": 0.5,
        "lbi3_beta": 1.1,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal = create_test_proposal(operator, target_epoch, unsafe_params)

    for i in range(1, loom_params.lbi3_gov_quorum + 1):
        operator.ingest_metabolic_vote(create_test_vote(proposal, f"witness_{i}"))

    epoch_manager.advance_epoch()
    operator.on_epoch_tick()

    assert not proposal.activated
    assert proposal.superseded
    assert loom_params.lbi3_beta == 0.05
    assert any("safety_violation" in entry["event"] for entry in operator.governance_log)


def test_deterministic_selection_for_multiple_proposals(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    target_epoch = epoch_manager.get_current_epoch() + 2

    params_a = {
        "lbi3_w_heal": 0.8,
        "lbi3_beta": 0.05,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal_a = create_test_proposal(
        operator,
        target_epoch,
        params_a,
        proposal_id="prop_A",
        created_at_epoch=epoch_manager.get_current_epoch(),
    )
    for i in range(1, loom_params.lbi3_gov_quorum + 1):
        operator.ingest_metabolic_vote(create_test_vote(proposal_a, f"witness_A_{i}"))

    epoch_manager.advance_epoch()
    params_b = {
        "lbi3_w_heal": 0.9,
        "lbi3_beta": 0.05,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal_b = create_test_proposal(
        operator,
        target_epoch,
        params_b,
        proposal_id="prop_B",
        created_at_epoch=epoch_manager.get_current_epoch(),
    )
    for i in range(1, loom_params.lbi3_gov_quorum + 1):
        operator.ingest_metabolic_vote(create_test_vote(proposal_b, f"witness_B_{i}"))

    epoch_manager.advance_epoch()
    operator.on_epoch_tick()

    assert proposal_a.activated
    assert not proposal_b.activated
    assert proposal_b.superseded
    assert loom_params.lbi3_w_heal == 0.8
    assert any(
        entry["proposal_id"] == "prop_B" and entry["event"] == "proposal_superseded"
        for entry in operator.governance_log
    )


def test_loom_parameter_mesh_invariance_without_quorum(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    target_epoch = epoch_manager.get_current_epoch() + 1
    new_params = {
        "lbi3_w_heal": 0.6,
        "lbi3_beta": 0.06,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal = create_test_proposal(operator, target_epoch, new_params)

    operator.ingest_metabolic_vote(create_test_vote(proposal, "witness_1"))

    initial_w_heal = loom_params.lbi3_w_heal
    initial_beta = loom_params.lbi3_beta

    epoch_manager.advance_epoch()
    operator.on_epoch_tick()

    assert not proposal.activated
    assert loom_params.lbi3_w_heal == initial_w_heal
    assert loom_params.lbi3_beta == initial_beta


def test_proposal_submission_validation(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    current_epoch = epoch_manager.get_current_epoch()
    valid_params = {
        "lbi3_w_heal": 0.6,
        "lbi3_beta": 0.06,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }

    with pytest.raises(ValueError, match=r"target_epoch .*must be strictly in the future"):
        operator.submit_proposal("invalid_past_prop", current_epoch - 1, valid_params, "w_X", "hash")

    with pytest.raises(ValueError, match=r"target_epoch .*must be strictly in the future"):
        operator.submit_proposal("invalid_current_prop", current_epoch, valid_params, "w_X", "hash")

    create_test_proposal(operator, current_epoch + 1, valid_params, proposal_id="duplicate_id")
    with pytest.raises(ValueError, match="Proposal duplicate_id already exists"):
        operator.submit_proposal("duplicate_id", current_epoch + 2, valid_params, "w_Y", "hash")


def test_ingest_metabolic_vote_mismatched_details(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    target_epoch = epoch_manager.get_current_epoch() + 1
    params = {
        "lbi3_w_heal": 0.6,
        "lbi3_beta": 0.06,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal = create_test_proposal(operator, target_epoch, params, proposal_id="test_mismatch")

    mismatched_params_vote = create_test_vote(proposal, "witness_mismatch_params")
    mismatched_params_vote.params = {
        "lbi3_w_heal": 0.7,
        "lbi3_beta": 0.06,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    operator.ingest_metabolic_vote(mismatched_params_vote)
    assert "witness_mismatch_params" not in proposal.votes

    mismatched_epoch_vote = create_test_vote(proposal, "witness_mismatch_epoch")
    mismatched_epoch_vote.target_epoch += 1
    operator.ingest_metabolic_vote(mismatched_epoch_vote)
    assert "witness_mismatch_epoch" not in proposal.votes

    mismatched_hash_vote = create_test_vote(proposal, "witness_mismatch_hash")
    mismatched_hash_vote.rationale_hash = "different_hash"
    operator.ingest_metabolic_vote(mismatched_hash_vote)
    assert "witness_mismatch_hash" not in proposal.votes

    valid_vote = create_test_vote(proposal, "witness_valid")
    operator.ingest_metabolic_vote(valid_vote)
    assert "witness_valid" in proposal.votes


def test_on_epoch_tick_only_once_per_epoch(setup_governance_operator):
    operator, epoch_manager, loom_params = setup_governance_operator
    target_epoch = epoch_manager.get_current_epoch() + 1
    new_params = {
        "lbi3_w_heal": 0.6,
        "lbi3_beta": 0.06,
        "lbi3_w_truth": 0.2,
        "lbi3_w_rot": 1.0,
        "lbi3_m_min": 0.5,
        "lbi3_m_max": 1.5,
    }
    proposal = create_test_proposal(operator, target_epoch, new_params)

    for i in range(1, loom_params.lbi3_gov_quorum + 1):
        operator.ingest_metabolic_vote(create_test_vote(proposal, f"witness_{i}"))

    epoch_manager.advance_epoch()

    operator.on_epoch_tick()
    assert proposal.activated
    assert loom_params.lbi3_w_heal == 0.6

    loom_params.lbi3_w_heal = 0.999
    operator.on_epoch_tick()
    assert loom_params.lbi3_w_heal == 0.999
    assert (
        len([log for log in operator.governance_log if log["event"] == "proposal_activated"])
        == 1
    )
