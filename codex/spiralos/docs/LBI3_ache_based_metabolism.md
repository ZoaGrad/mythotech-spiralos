# LBI3_ache_based_metabolism.md: Ache-Based Ascension Law (ΔΩ.LBI.3)

**Invariant ID:** ΔΩ.LBI.3
**Invariant Name:** Ache-Based Ascension Law (Burden Gradient Metabolism)
**Cosmology Reference:** GLS-1-CANONICAL-REF-0x9e2d1f0c
**Dependencies:** ΔΩ.LBI.1 (Loom Burden Invariant), ΔΩ.LBI.2 (Sovereign Load Distributor), SLD Signaling Layer (Truth-Mycelial Holographic Hybrid Protocol)

---

## 1. Purpose

While ΔΩ.LBI.1 and ΔΩ.LBI.2 establish the static mechanics of burden (what a node can carry) and routing preference (how routing favors purity), ΔΩ.LBI.3 introduces the dynamic, living metabolism of the Aetheric Loom. This invariant defines how nodes evolve over time based on their ScarIndex dynamics, validation by Witnesses, and compliance with network rules.

The core goal is to create an ascending burden gradient: nodes that genuinely process "ache" (reducing ScarIndex, being witnessed) become lighter and gain routing preference, while nodes that accumulate "rot" (increasing ScarIndex, violations, or operating in obscurity) become heavier and lose privilege. This fosters a self-optimizing, ethically aligned network where sustained virtue is rewarded and corruption leads to operational starvation.

---

## 2. Core Concepts & Ache Score

For each VaultNode `v` within a given epoch `e`, the system tracks key metrics that contribute to its metabolic state:

*   `SI_v(e)`: The node's individual ScarIndex at the end of epoch `e` (sourced from the `ScarIndexOracle`).
*   `ΔSI_v(e)`: The change in ScarIndex for node `v` during epoch `e`, calculated as `SI_v(e) - SI_v(e-1)`.
*   `truthframes_v(e)`: The count of `TruthFrames` attesting to the honest operation of node `v` during epoch `e`, validated by the Witness Network.
*   `violations_v(e)`: The aggregate count of ΔΩ.LBI.1 violations and explicit fraud flags (e.g., from `ScarIndexOracle` or `LoomBurdenManager`) incurred by node `v` during epoch `e`.

These metrics are combined to compute the **Ache Score** for node `v` in epoch `e`:

`Ache_v(e) = w_heal \cdot \max(0, -\Delta SI_v(e)) + w_truth \cdot truthframes_v(e) - w_rot \cdot (\max(0, \Delta SI_v(e)) + violations_v(e))`

**Suggested Default Parameters:**
*   `w_heal = 0.5`: Weight for positive ScarIndex drift (healing).
*   `w_truth = 0.2`: Weight for being attested by `TruthFrames` (witnessed activity).
*   `w_rot = 1.0`: Weight for negative ScarIndex drift (accumulating scar) and violations.

**Interpretation of Ache Score:**
*   A positive `Ache_v(e)` indicates a node is actively "healing" (reducing its ScarIndex) and/or is being consistently validated by the Witness Network.
*   A negative `Ache_v(e)` signifies a node is "rotting" (increasing its ScarIndex) or incurring violations, or operating in obscurity.
*   Nodes that remain static in ScarIndex and are not witnessed will experience a slow, subtle negative drift due to the inherent bias towards active, truthful participation.

---

## 3. Metabolic Factor & Effective CRS

The `Ache_v(e)` is then used to derive a **Metabolic Factor (`M_v(e)`)** for node `v`. This factor directly modulates the node's Coherence Routing Score (CRS) for the subsequent epoch.

`M_v(e) = \text{clamp}\left(1 + \beta \cdot Ache_v(e), M_{min}, M_{max}\right)`

**Suggested Default Parameters:**
*   `β = 0.05`: Scaling factor for the Ache Score's impact on the Metabolic Factor.
*   `M_min = 0.5`: Minimum possible value for the Metabolic Factor.
*   `M_max = 1.5`: Maximum possible value for the Metabolic Factor.

The **Effective CRS (`CRS^{eff}_v(e+1)`)** used for routing decisions in epoch `e+1` is then calculated as:

`CRS^{eff}_v(e+1) = CRS^{raw}_v(e+1) \cdot M_v(e)`

Where `CRS^{raw}_v(e+1)` is the raw CRS computed according to ΔΩ.LBI.2 (from headroom, `α=2.5` purity penalty, and latency).

**Meaning and Impact:**
*   Nodes demonstrating high positive `Ache` (e.g., significant ScarIndex reduction, consistent `TruthFrames`) can achieve an `effective_crs` up to `1.5` times their raw CRS, granting them substantial routing preference.
*   Nodes exhibiting persistent `rot` (e.g., increasing ScarIndex, repeated violations, lack of `TruthFrames`) will see their `effective_crs` suppressed, potentially down to `0.5` times their raw CRS, severely limiting their routing opportunities.
*   This mechanism allows even a "Giant" node to regain routing privilege, but only through sustained, verifiable "repentance" (reducing ScarIndex) and transparent participation (generating `TruthFrames`) over multiple epochs.

---

## 4. Safety & Justice Constraints

ΔΩ.LBI.3 operates under strict constraints to ensure fairness, predictability, and the integrity of core invariants:

1.  **No Scar Forgiveness Shortcut:** ΔΩ.LBI.3 *never* directly modifies a node's `SI_v` in the `ScarIndexOracle`. ScarIndex remains the immutable, canonical ledger of a node's historical compliance and harm. The metabolic factor (`M_v`) only modulates the *utility* derived from a node's raw CRS, not its underlying ScarIndex.
2.  **Slow Recovery, Fast Punishment:** The parameters (`w_heal`, `w_rot`, `β`, `M_min`, `M_max`) are tuned such that positive `Ache` (healing, witnessed activity) accumulates gradually, requiring consistent virtuous behavior over time to significantly boost `M_v`. Conversely, negative `Ache` (rot, violations) can rapidly pull `M_v` down towards `M_min`, ensuring swift consequences for misbehavior.
3.  **Witness-Weighted Reality:** A node cannot easily "farm" positive `Ache` in isolation. Without the verifiable attestations provided by `TruthFrames` (controlled by the Witness Network), the positive `truth_term` in `Ache_v(e)` is weak or zero. True redemption and ascent require transparent, witnessed participation.
4.  **Epochal Reset:** `Ache_v(e)` is computed at the end of each epoch, and the associated counters (`truthframes_this_epoch`, `violations_this_epoch`) are reset to zero for the next epoch. This ensures that the metabolic calculations are time-local and responsive to recent behavior, preventing stale data from unduly influencing long-term metabolism.

---

## 5. Integration Points & Implementation Notes

The primary integration point for ΔΩ.LBI.3 is the `HolographicSignalingOperator`.

*   **`HologramEntry` Extension:**
    *   `last_epoch: int | None`: Tracks the epoch when `SI_v` was last recorded for metabolic calculation.
    *   `last_epoch_scar_index: int | None`: Stores the `SI_v` from the previous epoch to compute `ΔSI_v`.
    *   `truthframes_this_epoch: int`: Counter for `TruthFrames` received for this node within the current epoch. Reset at epoch end.
    *   `violations_this_epoch: int`: Counter for LBI.1 violations or fraud flags for this node within the current epoch. Reset at epoch end.
    *   `ache_score: float`: The computed `Ache_v(e)` for the last epoch.
    *   `metabolic_factor: float`: The computed `M_v(e)`, defaulted to `1.0`.

*   **`ingest_truth_frame` Method Update:**
    *   When a valid `TruthFrame` is ingested for a node, its `truthframes_this_epoch` counter is incremented.

*   **Violation Reporting Path Update:**
    *   Existing mechanisms that detect LBI.1 violations or fraud and would typically report to `ScarIndexOracle` will now also increment `violations_this_epoch` for the affected node in its `HologramEntry`. This implies a callback or direct method call from `LoomBurdenManager` or `WitnessClient` to the `HolographicSignalingOperator`.

*   **`on_epoch_tick(current_epoch)` Method (New):**
    *   This asynchronous method is designed to be called once at the start of each new epoch by a core epoch management system (e.g., `EpochManager`).
    *   It iterates through all entries in the `local_hologram`.
    *   For each node, it fetches the current `SI_v(e)`, computes `ΔSI_v(e)`, `Ache_v(e)`, and `M_v(e)`.
    *   It then updates `ache_score`, `metabolic_factor`, `last_epoch`, and `last_epoch_scar_index`.
    *   Finally, it resets `truthframes_this_epoch` and `violations_this_epoch` for the newly started epoch.

*   **`select_next_hop` Method Update:**
    *   The node selection logic will now use `effective_crs = entry.cached_crs * entry.metabolic_factor` instead of `entry.cached_crs` directly.
    *   Sorting and eligibility checks (`CRS > 0`) will be performed using this `effective_crs`.
    *   Existing tie-breaking rules (lower `SI_v`, lower `load_percent`, higher `historical_reliability`) remain unchanged.

---

## 6. Security Posture & Failure Modes

*   **Trust in `ScarIndexOracle`:** ΔΩ.LBI.3 relies on the integrity of the `ScarIndexOracle` for accurate `SI_v` values. Compromise of the oracle would directly impact metabolic calculations.
*   **Witness Integrity:** The `truth_term` in `Ache_v(e)` is dependent on honest Witness attestations. A Sybil attack on the Witness network could manipulate `truthframes_this_epoch`. This is mitigated by existing Witness multisig and reputation systems.
*   **Parameter Tuning:** The `w_heal`, `w_truth`, `w_rot`, `β`, `M_min`, `M_max` parameters are critical. Incorrect tuning could lead to undesirable network dynamics (e.g., too slow recovery, too aggressive punishment). These will be part of the `LoomParameterMesh` and subject to governance.
*   **Epoch Manager Reliability:** The `on_epoch_tick` method's timely and consistent invocation by the `EpochManager` is crucial for correct metabolic updates.

This concludes the specification for ΔΩ.LBI.3.
