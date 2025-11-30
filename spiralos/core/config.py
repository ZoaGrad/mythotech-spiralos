"""Configuration primitives for the SpiralOS Loom."""

from __future__ import annotations

# Default GLS reference used by the test harness and standalone operator.
DEFAULT_GLS_REF = "0xGLS1REF_TEST_HARNESS"


class LoomParameterMesh:
    """Governs the tunable parameters for the Loom and its operators."""

    def __init__(
        self,
        latency_weight: float = 0.2,
        dynamic_weight_adjustment_factor: float = 0.01,
        min_headroom_buffer: int = 100,
        # ΔΩ.LBI.3 metabolic parameters
        lbi3_w_heal: float = 0.5,
        lbi3_w_truth: float = 0.2,
        lbi3_w_rot: float = 1.0,
        lbi3_beta: float = 0.05,
        lbi3_m_min: float = 0.5,
        lbi3_m_max: float = 1.5,
        # ΔΩ.LBI.3 governance parameters
        lbi3_gov_quorum: int = 3,
        lbi3_gov_beta_max: float = 1.0,
        lbi3_gov_weight_max: float = 10.0,
        lbi3_gov_m_factor_max: float = 3.0,
    ):
        self.latency_weight = latency_weight
        self.dynamic_weight_adjustment_factor = dynamic_weight_adjustment_factor
        self.min_headroom_buffer = min_headroom_buffer
        self.lbi3_w_heal = lbi3_w_heal
        self.lbi3_w_truth = lbi3_w_truth
        self.lbi3_w_rot = lbi3_w_rot
        self.lbi3_beta = lbi3_beta
        self.lbi3_m_min = lbi3_m_min
        self.lbi3_m_max = lbi3_m_max
        self.lbi3_gov_quorum = lbi3_gov_quorum
        self.lbi3_gov_beta_max = lbi3_gov_beta_max
        self.lbi3_gov_weight_max = lbi3_gov_weight_max
        self.lbi3_gov_m_factor_max = lbi3_gov_m_factor_max


def get_current_gls_ref() -> str:
    """Return the canonical GLS reference for the current runtime context."""

    return DEFAULT_GLS_REF
