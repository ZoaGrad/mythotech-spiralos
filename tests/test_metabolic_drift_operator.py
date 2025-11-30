import math
from typing import Dict

import pytest

from codex.operators.spiral.metabolic_drift_operator import MetabolicDriftOperator, PARAM_KEYS
from spiralos.protocols.witness_protocol import AcheEpochFrame


class LoomParameterMesh:
    def __init__(self):
        self.lbi3_w_heal = 0.5
        self.lbi3_w_truth = 0.2
        self.lbi3_w_rot = 1.0
        self.lbi3_beta = 0.05
        self.lbi3_m_min = 0.5
        self.lbi3_m_max = 1.5
        self.lbi3_drift_cap_w_heal = 0.10
        self.lbi3_drift_cap_w_truth = 0.10
        self.lbi3_drift_cap_w_rot = 0.10
        self.lbi3_drift_cap_beta = 0.02
        self.lbi3_drift_cap_m_min = 0.10
        self.lbi3_drift_cap_m_max = 0.10
        self.lbi3_drift_ache_floor = 0.10
        self.lbi3_drift_ache_ceiling = 1.00
        self.lbi3_drift_kappa = 1.5


class EpochManager:
    def __init__(self, current_epoch: int = 0):
        self._current_epoch = current_epoch

    def get_current_epoch(self) -> int:
        return self._current_epoch

    def advance_epoch(self) -> None:
        self._current_epoch += 1


@pytest.fixture
def setup_drift():
    lp = LoomParameterMesh()
    em = EpochManager(current_epoch=5)
    op = MetabolicDriftOperator(em, lp)
    return op, lp, em


def get_default_params(lp: LoomParameterMesh) -> Dict[str, float]:
    return {
        "lbi3_w_heal": lp.lbi3_w_heal,
        "lbi3_w_truth": lp.lbi3_w_truth,
        "lbi3_w_rot": lp.lbi3_w_rot,
        "lbi3_beta": lp.lbi3_beta,
        "lbi3_m_min": lp.lbi3_m_min,
        "lbi3_m_max": lp.lbi3_m_max,
    }


def test_no_ache_blocks_nontrivial_drift(setup_drift):
    op, lp, em = setup_drift

    assert op._compute_drift_factor(em.get_current_epoch()) == 0.0

    proposed_params = get_default_params(lp)
    proposed_params["lbi3_w_heal"] = lp.lbi3_w_heal + 0.01
    assert not op.validate_drift(proposed_params, em.get_current_epoch())
    assert any(e["event"] == "drift_blocked_no_ache" for e in op.drift_log)

    proposed_params_no_change = get_default_params(lp)
    assert op.validate_drift(proposed_params_no_change, em.get_current_epoch())


def test_ache_allows_drift_within_caps(setup_drift):
    op, lp, em = setup_drift
    epoch = em.get_current_epoch()
    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch, ache_index=1.0))

    assert op._compute_drift_factor(epoch) == 1.0

    proposed_params = get_default_params(lp)
    proposed_params["lbi3_w_heal"] = lp.lbi3_w_heal + 0.05
    proposed_params["lbi3_beta"] = lp.lbi3_beta + 0.01

    assert op.validate_drift(proposed_params, epoch)
    assert any(e["event"] == "drift_accepted" for e in op.drift_log)


def test_violation_when_delta_exceeds_ache_scaled_cap(setup_drift):
    op, lp, em = setup_drift
    epoch = em.get_current_epoch()
    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch, ache_index=0.3))

    expected_drift_factor = math.pow(
        (0.3 - lp.lbi3_drift_ache_floor) / (lp.lbi3_drift_ache_ceiling - lp.lbi3_drift_ache_floor),
        lp.lbi3_drift_kappa,
    )
    assert math.isclose(op._compute_drift_factor(epoch), expected_drift_factor)

    proposed_params = get_default_params(lp)
    proposed_params["lbi3_w_heal"] = lp.lbi3_w_heal + 0.02

    assert not op.validate_drift(proposed_params, epoch)
    assert any(e["event"] == "drift_violation" for e in op.drift_log)


def test_drift_factor_kappa_curve(setup_drift):
    op, lp, em = setup_drift
    epoch = em.get_current_epoch()

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch, ache_index=lp.lbi3_drift_ache_floor - 0.01))
    assert op._compute_drift_factor(epoch) == 0.0

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch, ache_index=lp.lbi3_drift_ache_ceiling + 0.1))
    assert op._compute_drift_factor(epoch) == 1.0

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch, ache_index=0.5))
    expected_drift_factor = math.pow(
        (0.5 - lp.lbi3_drift_ache_floor) / (lp.lbi3_drift_ache_ceiling - lp.lbi3_drift_ache_floor),
        lp.lbi3_drift_kappa,
    )
    assert math.isclose(op._compute_drift_factor(epoch), expected_drift_factor)


def test_ingest_ache_epoch_frame_stale_data(setup_drift):
    op, lp, em = setup_drift
    em.advance_epoch()
    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch=em.get_current_epoch() - 1, ache_index=0.5))
    assert op._current_ache_index == 0.0
    assert op._ache_epoch is None

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch=em.get_current_epoch(), ache_index=0.8))
    assert op._current_ache_index == 0.8
    assert op._ache_epoch == em.get_current_epoch()

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch=em.get_current_epoch(), ache_index=0.9))
    assert op._current_ache_index == 0.9


def test_drift_factor_no_ache_epoch_frame_for_current_epoch(setup_drift):
    op, lp, em = setup_drift
    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch=em.get_current_epoch() - 1, ache_index=0.5))
    assert op._compute_drift_factor(em.get_current_epoch()) == 0.0

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch=em.get_current_epoch() + 1, ache_index=0.5))
    assert op._compute_drift_factor(em.get_current_epoch()) == 0.0

    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch=em.get_current_epoch(), ache_index=0.5))
    assert op._compute_drift_factor(em.get_current_epoch()) > 0.0


def test_all_param_keys_covered(setup_drift):
    op, lp, em = setup_drift
    epoch = em.get_current_epoch()
    op.ingest_ache_epoch_frame(AcheEpochFrame(epoch, ache_index=1.0))

    params = get_default_params(lp)
    for key in PARAM_KEYS:
        assert key in params

    for key in PARAM_KEYS:
        cap_attr = f"lbi3_drift_cap_{key.split('lbi3_', 1)[1]}"
        cap = getattr(lp, cap_attr)
        params[key] = getattr(lp, key) + (cap * 0.5)

    assert op.validate_drift(params, epoch)
    assert any(e["event"] == "drift_accepted" for e in op.drift_log)
