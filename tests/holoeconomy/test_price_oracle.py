import math

import pytest

from src.holoeconomy.price_oracle import classify_price_level, compute_price


def test_compute_price_includes_coherence_and_governance_without_panic():
    state = {"governance_level": 6, "coherence": 0.8, "panic": False}
    price = compute_price(state)
    expected = 1.0 + 0.8 + 0.05 * 6
    assert math.isclose(price, expected)
    assert state == {"governance_level": 6, "coherence": 0.8, "panic": False}


def test_compute_price_applies_panic_penalty_and_clamp_lower_bound():
    state = {"governance_level": 0, "coherence": -5.0, "panic": True}
    price = compute_price(state)
    assert price == pytest.approx(0.1)


def test_compute_price_clamps_upper_bound_with_high_inputs():
    state = {"governance_level": 10, "coherence": 2.0, "panic": False}
    price = compute_price(state)
    assert price == pytest.approx(3.0)


def test_classify_price_level_ranges():
    assert classify_price_level(2.5) == "high"
    assert classify_price_level(1.0) == "medium"
    assert classify_price_level(1.99) == "medium"
    assert classify_price_level(0.99) == "low"


def test_compute_price_deterministic_for_same_state():
    state = {"governance_level": 3, "coherence": 0.55, "panic": False}
    first = compute_price(state)
    second = compute_price(state)
    assert first == pytest.approx(second)


def test_compute_price_handles_non_integer_governance_via_cast():
    state = {"governance_level": 4.9, "coherence": 0.5, "panic": False}
    price = compute_price(state)
    expected = 1.0 + 0.5 + 0.05 * 4
    assert price == pytest.approx(expected)
