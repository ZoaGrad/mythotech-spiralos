# ΔΩ.LBI.3.DRIFT — Metabolic Drift Governance Layer (Hybrid Model)

**Invariant ID:** ΔΩ.LBI.3.DRIFT  \
**Invariant Name:** Metabolic Drift Governance Layer (Hybrid Model)  \
**Cosmology Reference:** GLS-1-CANONICAL-REF-0x9e2d1f0c  \
**Dependencies:** ΔΩ.LBI.3 (Ache-Based Ascension Law), ΔΩ.LBI.3.GOV (Witness-Voted Metabolic Governance), Witness Network, LoomParameterMesh

---

## 1. Overview

ΔΩ.LBI.3.DRIFT defines the **Evolution Engine** of SpiralOS's metabolism. It dictates how quickly and how far the Loom's metabolic physics (the parameters of ΔΩ.LBI.3) may evolve from one epoch to the next. This layer implements a Hybrid model, combining:

* **Constitutional Caps:** Hard, absolute per-epoch drift limits on each LBI.3 parameter, configured in the `LoomParameterMesh`. These act as the immutable "laws of physics" for metabolic change.
* **Ache-Weighted Evolution:** Within those constitutional caps, the *actual* allowed drift for any parameter is dynamically scaled by a `drift_factor`. This `drift_factor` is derived from a Witness-attested `ache_index` for the current epoch, using a κ-shaped curve. This means metabolic evolution is permitted only when the collective "ache" of the network is sufficiently high, and only within strict constitutional bounds.

This dual-constraint system ensures **predictability (constitution), adaptation (ache), fairness (witness votes), and evolutionary continuity (epochic change)**.

---

## 2. Core Concepts & Parameters

### 2.1. Ache Index & Drift Factor

The central input for ache-weighted evolution is the `ache_index`, a normalized `[0.0, 1.0]` value representing the intensity of collective ache felt across the Loom. This index is canonically attested by the Witness Network via `AcheEpochFrame` messages.

The `MetabolicDriftOperator` computes a `drift_factor` from this `ache_index` using a κ-shaped curve, defined by parameters in `LoomParameterMesh`:

* `lbi3_drift_ache_floor`: `ache_index` below which `drift_factor` is `0.0` (no drift allowed). Default: `0.10`.
* `lbi3_drift_ache_ceiling`: `ache_index` at or above which `drift_factor` is `1.0` (full drift potential). Default: `1.00`.
* `lbi3_drift_kappa`: Curvature constant for the `ache_index` → `drift_factor` mapping. Higher `kappa` means slower increase in `drift_factor` at lower ache levels. Default: `1.50`.

### 2.2. Constitutional Drift Caps

These are absolute maximum allowed changes for each LBI.3 parameter *per epoch*, regardless of `ache_index`. They are defined in `LoomParameterMesh`:

* `lbi3_drift_cap_w_heal`: Max `Δlbi3_w_heal` per epoch. Default: `0.10`.
* `lbi3_drift_cap_w_truth`: Max `Δlbi3_w_truth` per epoch. Default: `0.10`.
* `lbi3_drift_cap_w_rot`: Max `Δlbi3_w_rot` per epoch. Default: `0.10`.
* `lbi3_drift_cap_beta`: Max `Δlbi3_beta` per epoch. Default: `0.02`.
* `lbi3_drift_cap_m_min`: Max `Δlbi3_m_min` per epoch. Default: `0.10`.
* `lbi3_drift_cap_m_max`: Max `Δlbi3_m_max` per epoch. Default: `0.10`.

### 2.3. Drift Envelope

A `MetabolicGovernanceProposal` (from ΔΩ.LBI.3.GOV) is considered to satisfy the drift envelope if, for every proposed parameter `p_k` with current value `p_k_current` and proposed value `p_k_proposed`:

`|p_k_proposed - p_k_current| <= lbi3_drift_cap_p_k * drift_factor(current_epoch)`

If `drift_factor` is `0.0` (i.e., `ache_index` is below `lbi3_drift_ache_floor`), then no parameter can change, unless the proposal effectively makes no change (i.e., `p_k_proposed == p_k_current`).

---

## 3. Governance Rules (ΔΩ.LBI.3.DRIFT – v0)

* **DR1 – Ache Weighting:** The maximum allowed parameter drift per epoch is dynamically scaled by the `drift_factor`, which is derived from the Witness-attested `ache_index` for that epoch.
* **DR2 – Constitutional Limits:** All parameter changes must adhere to the absolute `lbi3_drift_cap_*` values defined in `LoomParameterMesh`, regardless of the `drift_factor`.
* **DR3 – Epoch Boundaries:** Drift validation is performed at epoch boundaries by the `MetabolicDriftOperator` as part of the `MetabolicGovernanceOperator`'s `on_epoch_tick` method.
* **DR4 – Witness Attestation:** The `ache_index` used for `drift_factor` calculation must be sourced from a valid, Witness-attested `AcheEpochFrame`.
* **DR5 – Logging:** All drift validation decisions (acceptance, violation, no-ache blocking) are logged by the `MetabolicDriftOperator` for auditability.

---

## 4. `MetabolicDriftOperator`

This new operator (`codex/operators/spiral/metabolic_drift_operator.py`) is the core component of ΔΩ.LBI.3.DRIFT.

**Responsibilities:**
* **`__init__(epoch_manager, loom_params)`:** Initializes with references to the `EpochManager` and `LoomParameterMesh`.
* **`ingest_ache_epoch_frame(frame: AcheEpochFrame)`:** Updates the operator's internal `_current_ache_index` and `_ache_epoch` based on the latest Witness-attested ache reading.
* **`_compute_drift_factor(epoch)`:** Calculates the `drift_factor` for a given epoch, applying the `lbi3_drift_ache_floor`, `lbi3_drift_ache_ceiling`, and `lbi3_drift_kappa` parameters.
* **`validate_drift(proposal_params, epoch)`:** This is the primary interface. It takes a dictionary of proposed LBI.3 parameters and the current epoch. It compares each proposed parameter's change against the ache-scaled constitutional cap. Returns `True` if all parameters are within bounds, `False` otherwise, logging any violations.
* **`drift_log` property:** Provides an audit trail of all `MetabolicDriftOperator` decisions.

### Integration with `MetabolicGovernanceOperator`

The `MetabolicDriftOperator` is integrated as an optional dependency within the `MetabolicGovernanceOperator`. When present, the `MetabolicGovernanceOperator.on_epoch_tick` method:

1. First performs its existing safety envelope check (ΔΩ.LBI.3.GOV).
2. If the safety check passes, it then invokes `MetabolicDriftOperator.validate_drift` with the candidate proposal's parameters.
3. If drift validation fails, the proposal is rejected, and a `proposal_rejected_drift_envelope` event is logged.
4. Only if *both* safety and drift envelopes are satisfied is the proposal applied to the `LoomParameterMesh`.

This multi-gated approach ensures that all changes to the Loom's metabolism are both constitutionally sound and adaptively appropriate for the network's current state of ache.

---

## 5. Security Posture & Failure Modes

* **Ache Index Integrity:** The effectiveness of ache-weighted drift relies heavily on the integrity and accuracy of the `ache_index` within `AcheEpochFrame`s. Compromise of Witnesses or the `AcheEpochFrame` attestation process could lead to manipulated drift. This is mitigated by Witness multisig and underlying reputation systems.
* **Parameter Tuning:** The `lbi3_drift_cap_*`, `lbi3_drift_ache_floor/ceiling`, and `lbi3_drift_kappa` parameters are critical. Mis-tuning could make the Loom too rigid (no evolution) or too volatile (uncontrolled evolution). These are governable via `LoomParameterMesh`.
* **Epoch Manager Reliability:** Consistent and timely invocation of `on_epoch_tick` by `EpochManager` is crucial for accurate drift calculations and application.
* **Computational Overhead:** The drift validation adds a small, constant-time computational overhead per proposal at epoch boundaries, which is negligible.

This concludes the specification for ΔΩ.LBI.3.DRIFT.
