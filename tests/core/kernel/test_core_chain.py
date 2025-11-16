import pytest

from src.core.kernel.core_chain import apply_signal, is_safe, next_state, validate_transition


def default_state():
    return {
        "governance_level": 5,
        "coherence": 0.6,
        "panic": False,
    }


def test_apply_signal_weighted_average_and_panic_rules():
    state = default_state()
    signal = {"coherence": 0.2, "panic": False}

    result = apply_signal(state, signal)

    expected_coherence = 0.7 * state["coherence"] + 0.3 * signal["coherence"]
    assert pytest.approx(result["coherence"]) == expected_coherence
    assert result["panic"] is True
    assert result["governance_level"] == state["governance_level"]
    assert state == default_state()  # state not mutated


def test_apply_signal_triggers_panic_when_signal_requests():
    state = default_state()
    signal = {"coherence": 0.9, "panic": True}

    result = apply_signal(state, signal)

    assert result["panic"] is True
    assert result["coherence"] == pytest.approx(0.7 * 0.6 + 0.3 * 0.9)
    assert state["panic"] is False


def test_is_safe_checks_panic_and_threshold():
    assert is_safe(default_state()) is True
    assert is_safe({**default_state(), "panic": True}) is False
    assert is_safe({**default_state(), "coherence": 0.2}) is False


def test_next_state_safe_and_unsafe_progression():
    safe_state = default_state()
    result_safe = next_state(safe_state)

    assert result_safe is not safe_state
    assert result_safe["governance_level"] == min(10, safe_state["governance_level"] + 1)
    assert result_safe["panic"] is False

    unsafe_state = {**default_state(), "panic": True}
    result_unsafe = next_state(unsafe_state)

    assert result_unsafe["governance_level"] == max(0, unsafe_state["governance_level"] - 1)
    assert result_unsafe["panic"] is False  # coherence >= 0.5 resets panic

    low_level_state = {"governance_level": 0, "coherence": 0.1, "panic": True}
    result_low = next_state(low_level_state)
    assert result_low["governance_level"] == 0


def test_next_state_caps_governance_bounds():
    high_state = {"governance_level": 10, "coherence": 0.8, "panic": False}
    result_high = next_state(high_state)
    assert result_high["governance_level"] == 10

    low_state = {"governance_level": 0, "coherence": 0.1, "panic": False}
    result_low = next_state(low_state)
    assert result_low["governance_level"] == 0


def test_validate_transition_rejects_invalid_changes():
    old = default_state()
    valid_new = {"governance_level": 6, "coherence": 0.6, "panic": False}
    assert validate_transition(old, valid_new) is True

    invalid_jump = {"governance_level": 7, "coherence": 0.6, "panic": False}
    assert validate_transition(old, invalid_jump) is False

    invalid_coherence = {"governance_level": 5, "coherence": 1.1, "panic": False}
    assert validate_transition(old, invalid_coherence) is False

    panic_reset_without_safety = {"governance_level": 5, "coherence": 0.4, "panic": False}
    panic_old = {**old, "panic": True, "coherence": 0.4}
    assert validate_transition(panic_old, panic_reset_without_safety) is False


def test_apply_signal_returns_new_instance():
    state = default_state()
    signal = {"coherence": 0.4, "panic": False}
    result = apply_signal(state, signal)
    assert result is not state
    assert state == default_state()


def test_validate_transition_allows_panic_reset_when_coherent():
    old = {"governance_level": 5, "coherence": 0.6, "panic": True}
    new = {"governance_level": 4, "coherence": 0.6, "panic": False}
    assert validate_transition(old, new) is True
