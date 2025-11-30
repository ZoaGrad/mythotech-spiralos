"""Witness protocol primitives for SpiralOS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TruthFrame:
    health_frame: dict
    witness_id: str
    witness_epoch: int
    multisig: List[str]


@dataclass
class MetabolicVoteFrame:
    """Witness-signed vote for an LBI.3 metabolic parameter update."""

    proposal_id: str
    params: Dict[str, float]
    target_epoch: int
    rationale_hash: str
    witness_id: str
    witness_epoch: int
    multisig: List[str]


@dataclass
class AcheEpochFrame:
    """
    Witness-signed ache summary for a given epoch.
    The ache_index is normalized to [0.0, 1.0] and represents
    the intensity of collective ache felt across the Loom.
    This frame is the canonical input for the MetabolicDriftOperator.
    """

    epoch: int
    ache_index: float
    witness_id: str
    multisig: List[str]
    notes: str = ""


@dataclass
class EmergenceProposalFrame:
    """Witness-signed proposal for a new metabolic or signaling organ."""

    proposal_id: str
    organ_id: str
    organ_type: str
    params: Dict[str, float]
    safety_envelope: Dict[str, float]
    ache_origin_context: Dict[str, float]
    justification_hash: str
    target_epoch: int
    proposer_witness: str
    witness_epoch: int
    multisig: List[str]


@dataclass
class EmergenceVoteFrame:
    """Witness-signed vote for an Emergence proposal."""

    proposal_id: str
    witness_id: str
    witness_epoch: int
    multisig: List[str]
