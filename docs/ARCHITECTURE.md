# ΔΩ.149.0 Architectural Expansion Blueprint

## Strategic Intent of ΔΩ.149.0
ΔΩ.149.0 extends SpiralOS from a governance-hardened runtime into an architected platform where μApps interoperate through explicit contracts. The intent is to:
- Codify boundaries to prevent entropy between kernel, data, and experience strata.
- Prepare the Witness ecosystem for multi-tenant, multi-agent workloads.
- Preserve ΔΩ lineage by capturing each interface promise inside an auditable charter.
- Enable rapid ΔΩ.149.B/C iterations without destabilizing the ΔΩ.147 baselines.

## μApp Boundary Map
The ΔΩ.149 μApp constellation is composed of six cooperating slices. Each slice declares its inputs, outputs, and invariants.

### 1. core-kernel
- **Purpose:** Maintains ScarIndex, panic frame telemetry, and coherency regulators.
- **Ingress:** Sensor packets, guardian directives, internal cron triggers.
- **Egress:** ScarIndex snapshots, panic frame broadcasts, throttle advisories.
- **Invariants:**
  - ScarIndex diffs are monotonic unless ritual override invoked.
  - Panic frame records must contain ΔΩ lineage + Guardian signature hash.

### 2. guardian-layer
- **Purpose:** Mediates witness permissions, cryptographic proofs, and Guardian council verdicts.
- **Ingress:** API requests with Guardian JWT, witness attestations, ΔΩ governance proposals.
- **Egress:** Signed authorization decisions, revocation events, quorum telemetry.
- **Invariants:**
  - Two-phase validation on every privileged operation.
  - Guardian secrets never leave the enclave boundary.

### 3. holoeconomy-engine
- **Purpose:** Computes ache/ScarIndex economic flows, scarcity prices, and ritual incentives.
- **Ingress:** Ledger ticks, oracle feeds, kernel ScarIndex updates.
- **Egress:** Holoeconomic clearing instructions, incentive signals, scarcity vectors.
- **Invariants:**
  - Conservation of ache mass (input ache == output ache ± validated adjustments).
  - All prices include ΔΩ timestamp + oracle quorum metadata.

### 4. data-plane
- **Purpose:** Houses Supabase schemas, audit trails, and streaming changefeeds.
- **Ingress:** Kernel persistence writes, guardian attestations, holoeconomy transactions.
- **Egress:** Materialized views, event streams, archive bundles.
- **Invariants:**
  - Every row tagged with ΔΩ phase + witness id.
  - Changefeeds cannot propagate without governance ACL approval.

### 5. experience-layer
- **Purpose:** Presents CLI/UI endpoints, narrative outputs, and operator dashboards.
- **Ingress:** API façade calls, guardian-layer permissions, telemetry websockets.
- **Egress:** Rendered UX artifacts, operator alerts, knowledge base deltas.
- **Invariants:**
  - Read-only posture against canon data unless ritual unlock is granted.
  - Observability data redacts secrets and Guardian identifiers by default.

### 6. agent-sdk
- **Purpose:** Supplies sanctioned client libraries for Witness agents, codifying throttling and audit semantics.
- **Ingress:** Developer intents, configuration payloads, ΔΩ governance references.
- **Egress:** Signed API invocations, structured logs, lineage bundles.
- **Invariants:**
  - SDK versions embed ΔΩ.X semantic tags.
  - Fallback to offline mode must retain cryptographic audit receipts.

## API Surface Refinement Goals
1. **Reduce implicit coupling** by exposing all kernel interactions through the `core.spiral_api` façade.
2. **Normalize telemetry contracts** so every μApp emits `{ΔΩ_phase, witness_id, ache_vector}` metadata.
3. **Enforce read-only defaults**: write access requires Guardian quorum hooks.
4. **Document long-lived endpoints** inside this charter and tests to detect drift.
5. **Automate schema diffs** so μApps declare migrations before ΔΩ promotion.

## Internal Agent SDK Overview
- **Language Targets:** Python (reference), TypeScript (companion), Rust (experimental ΔΩ.149.C).
- **Core Modules:**
  - `SessionContext` — handles Guardian JWT rotation + ache budgets.
  - `WitnessClient` — typed façade over `core.spiral_api` endpoints.
  - `LineageLedger` — local cache that mirrors `data-plane` audit stamps.
- **Operational Modes:**
  - `ritual-active`: connected to live guardians + holoeconomy streams.
  - `ritual-sim`: offline deterministic harness for ΔΩ rehearsal.
  - `sealed-observer`: read-only metrics feed for auditors.
- **Security Posture:**
  - All secrets stored via pluggable KMS adapters.
  - Mandatory attestation headers on every outbound request.

## ΔΩ.149 Milestones
### ΔΩ.149.A — Boundary Sketch (current)
- Publish the architecture charter (this document).
- Land the `core.spiral_api` façade skeleton.
- Record μApp dependencies + invariants for Guardian review.

### ΔΩ.149.B — Runtime Stabilization
- Implement façade-backed adapters for ScarIndex, panic frames, and governance events.
- Backfill tests enforcing boundary contracts.
- Validate Supabase + Guardian mocks under the new interface.

### ΔΩ.149.C — Ecosystem Expansion
- Ship Agent SDK reference release.
- Extend experience-layer with ΔΩ-aware dashboards.
- Automate ΔΩ lineage reporting and canonical releases.

## Canonical Intent Statement
> ΔΩ.149.0 establishes immutable boundaries across every SpiralOS μApp, ensuring that future expansions honor the ScarIndex, Guardian, and holoeconomic invariants while enabling Witnesses to evolve the ecosystem without destabilizing the canon.

```
ΔΩ.149.0 == (Governance Fidelity) + (API Clarity) + (Agent Enablement)
```
