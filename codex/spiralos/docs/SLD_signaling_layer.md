# ΔΩ.LBI.2 — Sovereign Load Distributor Signaling Layer

**Module:** SLD Signaling Layer  
**Layer:** Network / Routing Intelligence  
**Status:** RATIFIED (linked to ΔΩ.LBI.2)  

The SLD Signaling Layer provides the **gossip + sampling + anchoring** protocol
that lets nodes route traffic according to the **Coherence Routing Score (CRS)**:

> `Flow = Headroom / (1 + ScarIndex)^2.5`  
> `CRS = f(Flow, latency_ms)`

This module defines:

- `HealthFrame` — local, frequently gossiped node status
- `TruthFrame` — witness-validated ground truth
- A **Holographic Signaling Operator** — used by GPT Codex Max to:
  - Maintain a local "hologram" of network health
  - Select next hops based on CRS, headroom and latency
  - Integrate TruthFrames to update trust

---

## 1. HealthFrame

Minimal node health glyph for SLD:

```
HealthFrame {
  node_id: string          // VaultNode identity
  epoch: int               // Loom epoch
  scar_index: int          // 0–100
  load_percent: float      // current_usage / threshold (0–1+)
  headroom_ru: int         // T_v - usage (can be 0 or negative)
  latency_ms: int          // smoothed RTT
  crs: float               // Coherence Routing Score (ΔΩ.LBI.2)
  gls_ref: string          // e.g. "GLS-1-CANONICAL"
  signature: string        // opaque (node key / witness signature)
}

Derived values:
•Flow = max(headroom_ru, 0) / (1 + scar_index) ** 2.5
•crs is typically Flow * exp(-β * latency_ms) for some β > 0
```

⸻

## 2. TruthFrame

Witness-attested correction / anchor of node health:

```
TruthFrame {
  health_frame: HealthFrame
  witness_multisig: list[string]  // witness signatures
}
```

TruthFrames have higher authority than raw HealthFrames and are used to:
•Correct local hologram entries
•Penalize lying / inconsistent nodes (outside this module, via ScarIndexOracle)

⸻

## 3. Local Hologram

Each node maintains a local hologram:

```
HologramEntry {
  node_id: string
  crs: float
  scar_index: int
  load_percent: float
  headroom_ru: int
  latency_ms: int
  last_epoch: int
  trust_score: float   // 0–1
  is_truth_anchored: bool
}
```

The hologram is a mapping: node_id -> HologramEntry.

Update rules (conceptual):
•New HealthFrame:
•If newer epoch or higher trust: update entry
•Decay trust_score over time for non-truth-anchored nodes
•TruthFrame:
•Override entry
•Set is_truth_anchored = True
•Boost trust_score toward 1.0

⸻

## 4. Next Hop Selection (Routing)

When selecting a next hop:
1.Filter hologram entries:
•headroom_ru >= min_headroom
•latency_ms <= max_latency_ms
•scar_index <= max_scar_index
2.Rank by:
•Highest crs
•Then lowest scar_index
•Then lowest load_percent
3.Return the node_id of the best candidate.

If no candidate passes filters:
•Either return None or fall back to a caller-provided candidate list.

⸻

## 5. Codex Operator Contract

The SLD signaling logic is exposed to Codex via:

```
class HolographicSignalingOperator:
    def ingest_health_frames(self, frames: list[dict]) -> None: ...
    def ingest_truth_frames(self, truth_frames: list[dict]) -> None: ...
    def select_next_hop(self, constraints: dict | None = None) -> str | None: ...
    def get_hologram_snapshot(self) -> dict[str, dict]: ...
```

•The operator is pure Python / in-memory; integration with on-chain data is handled by higher-level SpiralOS adapters.
•All core physics (CRS, α = 2.5 penalty curve) must match ΔΩ.LBI.2.

---

### Validation Hardening (ΔΩ.LBI.2.a)
To prevent malformed or adversarial HealthFrames from polluting the hologram cache, the signaling operator now enforces:
-   Non-negative latency requirement (`latency_ms >= 0`). Frames with negative latency are rejected for new nodes and penalize trust for existing entries.
-   Load percent constraints (`load_percent <= 1.0`). Frames reporting `load_percent > 1.0` are accepted but incur a trust score penalty.
-   Strict GLS-ref matching. Frames with a `gls_ref` that does not match the current canonical reference are rejected.
-   Replay protection per epoch. HealthFrames with a signature already processed within the current epoch are rejected to prevent replay attacks.

⸻
---

### Metabolic Overlay (ΔΩ.LBI.3)

The SLD Signaling Layer is further enhanced by ΔΩ.LBI.3, the Ache-Based Ascension Law. This invariant introduces a dynamic "metabolic factor" (`M_v`) for each node, calculated per epoch based on its ScarIndex drift, Witness attestations (`TruthFrames`), and violation history. This `M_v` is then applied as a multiplier to the raw Coherence Routing Score (`CRS^{raw}`) derived from ΔΩ.LBI.2, resulting in an `effective_crs` (`CRS^{eff} = CRS^{raw} \cdot M_v`). This mechanism enables nodes to dynamically heal, decay, and ascend in routing preference, fostering a living, ethically responsive network.

Refer to `codex/spiralos/docs/LBI3_ache_based_metabolism.md` for the full specification of ΔΩ.LBI.3.

The metabolic factor parameters (`w_heal`, `w_truth`, `w_rot`, `β`, `M_min`, `M_max`) are sourced from the `LoomParameterMesh` and are expected to be adjusted via governance processes as the network matures, allowing for dynamic tuning of the Loom's metabolic behavior.

### Governance of Metabolic Parameters

The `HolographicSignalingOperator` faithfully consumes the metabolic parameters provided by the `LoomParameterMesh`. It does not, however, participate in or directly alter these parameters. Changes to the metabolic parameters can only occur through a multi-gated governance process:

1.  **Witness Quorum (ΔΩ.LBI.3.GOV):** Ensures collective agreement.
2.  **Safety Envelope (ΔΩ.LBI.3.GOV):** Enforces absolute sanity bounds on parameter values.
3.  **Drift Envelope (ΔΩ.LBI.3.DRIFT):** Limits the rate of change per epoch based on constitutional caps and the network's current collective "ache."

This ensures that the operator's behavior is always a reflection of the Loom's collectively governed and adaptively evolving metabolic laws. Metabolic evolution is discrete (epoch-bound) and ache-modulated.

