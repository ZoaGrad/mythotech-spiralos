# ΔΩ.150 CoreChain — Deterministic Kernel State Machine

## ΔΩ.150 Context
SpiralOS CoreChain is the kernel-level state machine that safeguards governance continuity across the six μApp strata. It tracks governance_level, coherence, and panic as the minimal canonical state propagated between μApps, ensuring that ΔΩ.149 symbolic contracts remain enforceable during ΔΩ.150 operational hardening. CoreChain elevates the kernel by converting contract-level safety envelopes into executable transitions that are deterministic, auditable, and free of side effects.

## Module Overview
- **Purpose:** Provide pure functions that apply external signals, evaluate safety, progress kernel state, and validate transitions without mutating inputs or performing I/O.
- **Safety envelope:** Encodes systemic health through `coherence` (0.0–1.0), `panic` (boolean), and bounded `governance_level` (0–10). Panic propagation and coherence thresholds define when the kernel must contract authority or can safely expand.
- **Determinism & immutability:** Every function returns a new state dictionary; no randomness or side effects are permitted. This guarantees reproducible governance decisions and prevents cross-μApp drift.

## State Model Specification
Each state is a mapping with required keys:
- `governance_level` (int): Bounded authority index in [0, 10].
- `coherence` (float): Systemic coherence in [0.0, 1.0]; clamped by transitions.
- `panic` (bool): Emergency flag propagated by signals or low coherence.

Invariants enforced:
- **apply_signal:** clamps coherence to [0.0, 1.0]; propagates panic on explicit panic or coherence < 0.3; preserves governance_level unchanged.
- **is_safe:** rejects any state with panic=True or coherence < 0.25.
- **next_state:** increments/decrements governance_level by at most 1, clamped to [0, 10]; resets panic only when coherence ≥ 0.5.
- **validate_transition:** forbids governance jumps beyond ±1, enforces coherence bounds, and disallows panic True→False unless coherence ≥ 0.5.

## Transition Logic
- **Weighted coherence update:** `coherence' = clamp(0.7 * coherence + 0.3 * signal_coherence, 0.0, 1.0)`
- **Panic propagation:** `panic' = panic or signal.panic or (signal_coherence < 0.3)`
- **Safety check:** unsafe if `panic'` is True or `coherence' < 0.25`.
- **Governance bounds:**
  - Safe → `governance_level' = min(10, governance_level + 1)`
  - Unsafe → `governance_level' = max(0, governance_level - 1)`
- **Panic reset:** panic may reset to False only when coherence ≥ 0.5 (as performed in `next_state`).

## Public API Reference

### apply_signal(state: dict, signal: dict) -> dict
| Argument | Type | Description |
| --- | --- | --- |
| state | dict | Current kernel state mapping. |
| signal | dict | Incoming signal containing optional `coherence` and `panic`. |

**Returns:** New state dict with updated coherence and panic; governance_level unchanged.  
**Raises:** None (expects callable types per contract).  
**Invariants:** No mutation; coherence clamped; panic propagated on explicit panic or coherence < 0.3.

### is_safe(state: dict) -> bool
| Argument | Type | Description |
| --- | --- | --- |
| state | dict | State to evaluate. |

**Returns:** `False` if panic is True or coherence < 0.25; `True` otherwise.  
**Raises:** None.  
**Invariants:** Pure boolean predicate; no mutation.

### next_state(state: dict) -> dict
| Argument | Type | Description |
| --- | --- | --- |
| state | dict | State to project forward. |

**Returns:** New state with governance_level adjusted by ±1 (clamped 0–10) based on safety; panic reset only if coherence ≥ 0.5.  
**Raises:** None.  
**Invariants:** Pure, no mutation; preserves coherence; bounds governance movement to single-step transitions.

### validate_transition(old: dict, new: dict) -> bool
| Argument | Type | Description |
| --- | --- | --- |
| old | dict | Prior state. |
| new | dict | Proposed next state. |

**Returns:** `True` if coherence remains in [0.0, 1.0], governance_level delta ∈ {−1, 0, +1}, and panic True→False only when coherence ≥ 0.5; otherwise `False`.  
**Raises:** None.  
**Invariants:** Side-effect free validation guard for downstream μApps.

## Usage Examples
```python
from core.kernel.core_chain import apply_signal, is_safe, next_state, validate_transition

state = {"governance_level": 5, "coherence": 0.6, "panic": False}
signal = {"coherence": 0.4, "panic": False}

# Apply weighted coherence update and panic propagation
updated = apply_signal(state, signal)
assert updated == {"governance_level": 5, "coherence": 0.54, "panic": False}

# Assess safety and step forward
if is_safe(updated):
    projected = next_state(updated)
    assert projected["governance_level"] == 6
else:
    projected = next_state(updated)
    assert projected["governance_level"] == 4

# Transition validation
assert validate_transition(updated, projected)
```

```python
# Unsafe signal leading to panic and recovery
state = {"governance_level": 3, "coherence": 0.35, "panic": False}
signal = {"coherence": 0.1, "panic": False}
updated = apply_signal(state, signal)
assert updated["panic"] is True  # panic due to low coherence

projected = next_state(updated)
# governance_level contracts while unsafe, cannot drop below 0
assert 0 <= projected["governance_level"] <= 10

# A later coherent signal can restore safety and allow panic reset
recovered = apply_signal(projected, {"coherence": 0.7, "panic": False})
restored = next_state(recovered)
assert restored["panic"] is False
assert validate_transition(projected, restored)
```

```python
# Illegal transition detection
old = {"governance_level": 5, "coherence": 0.6, "panic": True}
new = {"governance_level": 7, "coherence": 0.9, "panic": False}
assert validate_transition(old, new) is False  # governance jump > 1 and panic reset without gating
```

## Integration Notes
- **Guardian layer:** consumes `next_state` to monitor drift and trigger PanicFrame interventions when governance contracts or panic persists.
- **ScarIndex:** feeds coherence and panic signals into `apply_signal`, ensuring observed scar metrics directly influence kernel safety envelopes.
- **HoloEconomy engine:** reads coherence and panic to modulate economic safeguards; governance_level bounds gate authority-sensitive flows.

## Cross-References
- **ΔΩ.149 Architectural Contract:** CoreChain enforces the deterministic, side-effect-free kernel invariants mandated for the core μApp boundary.
- **Protocol Adapter:** Upstream agent-sdk protocol_adapter normalizes inbound frames that become CoreChain signals, preserving JSON-only payload guarantees.
- **Future ΔΩ.151 expansion:** CoreChain remains the foundational state conduit for additional kernel nodes while maintaining the same governance bounds and panic gating.
