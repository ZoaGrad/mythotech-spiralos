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
