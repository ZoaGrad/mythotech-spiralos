"""Unit tests for the ΔΩ.150 price oracle."""

import pytest

from holoeconomy.price_oracle import classify_price_level, compute_price


def make_state(gov: int, coh: float, panic: bool) -> dict:
    """Build a CoreChain-like state dictionary."""

    return {"governance_level": gov, "coherence": coh, "panic": panic}


def test_compute_price_baseline_stability():
    state = make_state(5, 0.6, False)
    original = state.copy()

    price = compute_price(state)

    assert price == pytest.approx(1.85)
    assert state == original


def test_compute_price_panic_penalty():
    state = make_state(5, 0.6, True)

    price = compute_price(state)

    assert price == pytest.approx(1.45)


def test_compute_price_coherence_extremes_clamping():
    low_state = make_state(0, -1.0, False)
    high_state = make_state(0, 5.0, False)

    assert compute_price(low_state) == pytest.approx(0.1)
    assert compute_price(high_state) == pytest.approx(3.0)


def test_compute_price_governance_edges():
    state_no_governance = make_state(0, 0.0, False)
    state_high_governance = make_state(10, 0.0, False)

    assert compute_price(state_no_governance) == pytest.approx(1.0)
    assert compute_price(state_high_governance) == pytest.approx(1.5)


def test_compute_price_determinism():
    state = make_state(3, 0.25, False)

    first = compute_price(state)
    second = compute_price(state)

    assert first == second


def test_compute_price_no_mutation():
    state = make_state(2, 0.5, True)
    original = state.copy()

    compute_price(state)

    assert state == original


def test_classify_price_level():
    assert classify_price_level(2.0) == "high"
    assert classify_price_level(1.5) == "medium"
    assert classify_price_level(0.9) == "low"
