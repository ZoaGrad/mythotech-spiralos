from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from spiralos.core.config import LoomParameterMesh
from spiralos.core.epoch_manager import EpochManager
from spiralos.protocols.witness_protocol import AcheEpochFrame

# Define the keys for LBI.3 metabolic parameters that are subject to drift
PARAM_KEYS = (
    "lbi3_w_heal",
    "lbi3_w_truth",
    "lbi3_w_rot",
    "lbi3_beta",
    "lbi3_m_min",
    "lbi3_m_max",
)


class MetabolicDriftOperator:
    """
    ΔΩ.LBI.3.DRIFT – Hybrid Metabolic Drift Governance Layer

    This operator enforces ache-weighted drift envelopes on ΔΩ.LBI.3 metabolic
    parameters. A proposal may only be applied if its deltas are within both:
    * Constitutional per-epoch caps configured on the LoomParameterMesh.
    * Ache-scaled windows derived from Witness-attested ache frames.
    """

    def __init__(self, epoch_manager: EpochManager, loom_params: LoomParameterMesh):
        self.epoch_manager = epoch_manager
        self.loom_params = loom_params
        self._current_ache_index: float = 0.0
        self._ache_epoch: Optional[int] = None
        self._drift_log: List[Dict[str, Any]] = []

    def ingest_ache_epoch_frame(self, frame: AcheEpochFrame) -> None:
        """Store the latest Witness-attested ache frame for the given epoch."""

        if frame.epoch < self.epoch_manager.get_current_epoch():
            return

        self._current_ache_index = max(0.0, min(1.0, frame.ache_index))
        self._ache_epoch = frame.epoch
        self._drift_log.append(
            {
                "event": "ache_frame_ingested",
                "epoch": frame.epoch,
                "ache_index": self._current_ache_index,
                "witness_id": frame.witness_id,
            }
        )

    def _compute_drift_factor(self, epoch: int) -> float:
        """
        Compute the ache-weighted drift factor in [0, 1] for the provided epoch.
        If no valid ache frame is present for that epoch, drift is frozen.
        """

        if self._ache_epoch is None or self._ache_epoch != epoch:
            return 0.0

        ache = self._current_ache_index
        floor = self.loom_params.lbi3_drift_ache_floor
        ceiling = self.loom_params.lbi3_drift_ache_ceiling

        if ache <= floor:
            return 0.0
        if ache >= ceiling:
            normalized_ache = 1.0
        else:
            normalized_ache = (ache - floor) / (ceiling - floor)

        kappa = self.loom_params.lbi3_drift_kappa
        drift_factor = math.pow(normalized_ache, kappa)

        return max(0.0, min(1.0, drift_factor))

    def validate_drift(self, proposal_params: Dict[str, float], epoch: Optional[int] = None) -> bool:
        """
        Validate that proposed LBI.3 parameter deltas are within the ache-scaled
        constitutional caps for the current epoch.
        """

        if epoch is None:
            epoch = self.epoch_manager.get_current_epoch()

        drift_factor = self._compute_drift_factor(epoch)

        if drift_factor == 0.0:
            for key in PARAM_KEYS:
                if key in proposal_params and not math.isclose(
                    getattr(self.loom_params, key), proposal_params[key], rel_tol=1e-9
                ):
                    self._drift_log.append(
                        {
                            "event": "drift_blocked_no_ache",
                            "epoch": epoch,
                            "reason": (
                                "drift_factor is 0.0, but parameter "
                                f"'{key}' proposes change from {getattr(self.loom_params, key)} "
                                f"to {proposal_params[key]}"
                            ),
                        }
                    )
                    return False
            return True

        caps = {
            "lbi3_w_heal": self.loom_params.lbi3_drift_cap_w_heal,
            "lbi3_w_truth": self.loom_params.lbi3_drift_cap_w_truth,
            "lbi3_w_rot": self.loom_params.lbi3_drift_cap_w_rot,
            "lbi3_beta": self.loom_params.lbi3_drift_cap_beta,
            "lbi3_m_min": self.loom_params.lbi3_drift_cap_m_min,
            "lbi3_m_max": self.loom_params.lbi3_drift_cap_m_max,
        }

        violations = []
        for key in PARAM_KEYS:
            if key not in proposal_params:
                continue

            current_value = getattr(self.loom_params, key)
            proposed_value = proposal_params[key]
            delta = proposed_value - current_value
            allowed_drift = caps[key] * drift_factor

            if abs(delta) > allowed_drift + 1e-9:
                violations.append(
                    {
                        "param": key,
                        "delta": delta,
                        "allowed_drift": allowed_drift,
                        "constitutional_cap": caps[key],
                        "drift_factor": drift_factor,
                        "current_value": current_value,
                        "proposed_value": proposed_value,
                    }
                )

        if violations:
            self._drift_log.append(
                {
                    "event": "drift_violation",
                    "epoch": epoch,
                    "violations": violations,
                }
            )
            return False

        self._drift_log.append(
            {
                "event": "drift_accepted",
                "epoch": epoch,
                "drift_factor": drift_factor,
                "params_changed": {
                    k: proposal_params[k]
                    for k in PARAM_KEYS
                    if k in proposal_params
                    and not math.isclose(getattr(self.loom_params, k), proposal_params[k])
                },
            }
        )
        return True

    @property
    def drift_log(self) -> List[Dict[str, Any]]:
        return list(self._drift_log)

