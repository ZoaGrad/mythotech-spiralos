import copy

import pytest

from holoeconomy.price_oracle import compute_price
from holoeconomy.scarcoin_mint import (
    compute_burn_amount,
    compute_mint_amount,
    mint_or_burn,
)


def make_state(gov: int, coh: float, panic: bool) -> dict:
    return {"governance_level": gov, "coherence": coh, "panic": panic}


class TestComputeMintAmount:
    def test_high_coherence_no_panic_strong_mint(self):
        state = make_state(4, 0.8, False)
        original = copy.deepcopy(state)

        result = compute_mint_amount(state)

        expected = (0.8 * 2.0) + (0.1 * 4)
        assert pytest.approx(expected) == result
        assert state == original

    def test_low_coherence_with_panic_weak_mint(self):
        state = make_state(1, 0.3, True)
        original = copy.deepcopy(state)

        result = compute_mint_amount(state)

        expected = max(0.0, (0.3 * 2.0) + (0.1 * 1) - 0.5)
        assert pytest.approx(expected) == result
        assert state == original

    def test_upper_clamp_excessive_inputs(self):
        state = make_state(20, 3.0, False)
        original = copy.deepcopy(state)

        result = compute_mint_amount(state)

        assert result == 5.0
        assert state == original

    def test_lower_clamp_negative_contributions(self):
        state = make_state(0, 0.0, True)
        original = copy.deepcopy(state)

        result = compute_mint_amount(state)

        assert result == 0.0
        assert state == original


class TestComputeBurnAmount:
    def test_panic_and_low_coherence_strong_burn(self):
        state = make_state(0, 0.1, True)
        original = copy.deepcopy(state)

        result = compute_burn_amount(state)

        expected = (0.4) + (0.2 * (1.0 - 0.1))
        assert pytest.approx(expected) == result
        assert state == original

    def test_high_coherence_no_panic_low_burn(self):
        state = make_state(0, 0.95, False)
        original = copy.deepcopy(state)

        result = compute_burn_amount(state)

        expected = 0.2 * (1.0 - 0.95)
        assert pytest.approx(expected) == result
        assert state == original

    def test_clamp_out_of_range_values(self):
        state = make_state(0, -15.0, True)
        original = copy.deepcopy(state)

        result = compute_burn_amount(state)

        assert result == 3.0
        assert state == original


class TestMintOrBurn:
    def test_mint_path(self):
        state = make_state(2, 0.7, False)
        original = copy.deepcopy(state)

        decision = mint_or_burn(state)

        expected_price = compute_price(state)
        expected_mint = compute_mint_amount(state)

        assert decision["action"] == "mint"
        assert decision["amount"] == expected_mint
        assert decision["price"] == expected_price
        assert state == original

    def test_burn_path(self):
        state = make_state(0, 0.2, True)
        original = copy.deepcopy(state)

        decision = mint_or_burn(state)

        expected_price = compute_price(state)
        expected_burn = compute_burn_amount(state)

        assert decision["action"] == "burn"
        assert decision["amount"] == expected_burn
        assert decision["price"] == expected_price
        assert state == original

    def test_none_path(self):
        state = make_state(-10, 0.6, False)
        original = copy.deepcopy(state)

        first_decision = mint_or_burn(state)
        second_decision = mint_or_burn(state)

        expected_price = compute_price(state)

        assert first_decision == second_decision
        assert first_decision["action"] == "none"
        assert first_decision["amount"] == 0.0
        assert first_decision["price"] == expected_price
        assert state == original
