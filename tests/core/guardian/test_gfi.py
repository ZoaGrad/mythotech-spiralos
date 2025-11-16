import copy

import pytest

from src.core.guardian.gfi import analyze_state_window, needs_attention


def safe_state():
    return {"governance_level": 5, "coherence": 0.7, "panic": False}


def borderline_state():
    return {"governance_level": 5, "coherence": 0.5, "panic": False}


def panic_state():
    return {"governance_level": 5, "coherence": 0.2, "panic": True}


def test_analyze_state_window_empty_window_defaults():
    window = []
    report = analyze_state_window(window)

    assert report["guardian_status"] == "unknown"
    assert report["panic_rate"] == 0
    assert report["avg_coherence"] == 0
    assert report["governance_span"] == 0
    assert window == []


def test_analyze_state_window_stable_window():
    window = [safe_state() for _ in range(3)]
    original = copy.deepcopy(window)

    report = analyze_state_window(window)

    assert report["guardian_status"] == "stable"
    assert report["panic_rate"] == 0
    assert report["governance_span"] == 0
    assert report["avg_coherence"] == pytest.approx(0.7)
    assert window == original


def test_analyze_state_window_watch_window():
    window = [safe_state(), borderline_state(), borderline_state()]
    original = copy.deepcopy(window)

    report = analyze_state_window(window)

    assert 0 <= report["panic_rate"] <= 0.2
    assert 0.4 <= report["avg_coherence"] <= 0.6
    assert report["guardian_status"] == "watch"
    assert window == original


def test_analyze_state_window_critical_window_with_panic():
    window = [safe_state(), borderline_state(), panic_state()]
    original = copy.deepcopy(window)

    report = analyze_state_window(window)

    assert report["guardian_status"] == "critical"
    assert report["panic_rate"] > 0.2 or report["avg_coherence"] < 0.4
    assert window == original


def test_analyze_state_window_governance_span():
    base = safe_state()
    higher = {**safe_state(), "governance_level": 8}
    lower = {**safe_state(), "governance_level": 2}
    window = [base, higher, lower]
    original = copy.deepcopy(window)

    report = analyze_state_window(window)

    assert report["governance_span"] == 6
    assert window == original


def test_needs_attention_false_for_stable_and_unknown():
    assert needs_attention({"guardian_status": "stable"}) is False
    assert needs_attention({"guardian_status": "unknown"}) is False


def test_needs_attention_true_for_watch_or_critical():
    assert needs_attention({"guardian_status": "watch"}) is True
    assert needs_attention({"guardian_status": "critical"}) is True
