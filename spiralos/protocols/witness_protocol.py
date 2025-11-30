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
