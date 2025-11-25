# Sovereign Map — SpiralOS ΔΩ.147

This map captures the current surface area of the SpiralOS repository and the relationships between its subsystems. It is intended to be a living orientation document for Sovereign Architect iterations.

## Topology

- **Core** (`src/core/`): orchestration, telemetry analytics, and the Oracle.
- **Governance** (`src/governance/`): panic protocols and ingress filters for upstream signals.
- **Economy + Holoeconomy** (`src/economy/`, `src/holoeconomy/`): minting, ledger flows, and price oracles bridging to VaultNode storage.
- **Vault** (`src/vault/`): fossil/archive managers for long-lived artifacts.
- **Constitution** (`src/constitution/`): clause registry.
- **Agent SDK** (`src/agent_sdk/`): protocol adapters for μApp communications.
- **Tests** (`tests/`): Python + JS integration suites and phase-specific verification bundles.

## Component Notes

### Core
- `scarindex` computes the ScarIndex from Ache deltas with entropy penalties for regressions. Heavy Ache growth hard-caps the score to 0.20 to trigger fail-safes. 【F:src/core/scarindex.py†L4-L34】
- `oracle` wraps the Gemini 2.0 Flash model via `google.generativeai`, enforcing a read-only narrative interpretation role. Initialization fails fast if `GEMINI_API_KEY` is absent. 【F:src/core/oracle.py†L1-L61】

### Governance
- `panic_protocol` and `ingress_filters` (not shown here) gate inbound telemetry; adjudication routines coordinate responses.

### Economy & Holoeconomy
- `ledger` orchestrates wallet creation, balance retrieval, P2P transfers, and transaction history using the Vault client. Transfers auto-provision receiver wallets and surface user-facing error hints. 【F:src/economy/ledger.py†L1-L87】
- `scarcoin_mint` and `price_oracle` anchor the Holoeconomy surface; tests in `tests/holoeconomy/` exercise minting invariants and price feeds.

### Agent SDK
- `protocol_adapter` defines deterministic JSON encoding/decoding (`SymbolicEncoder`) plus route-aware framing (`TranslationCircuit`). Frames carry lineage and protocol metadata, rejecting unknown fields unless explicitly whitelisted. 【F:src/agent_sdk/protocol_adapter.py†L1-L197】

### Vault & Constitution
- `fossil_manager` handles archival persistence hooks; `clauses` provides the constitutional clause surface for policy-aware modules.

### Tests
- Suites cover Guardian auth, Supabase integration, webhook batching, agent SDK protocol hygiene, and telemetry normalization (Python + JavaScript). The `tests/phase-8.4/` bundle includes HTTP + SQL fixtures for scenario replay.

## Cross-System Dependencies

- The economic layer depends on `src/core.database` for wallet + transfer RPCs, tying coherence metrics (ScarIndex) to VaultNode-backed storage. 【F:src/economy/ledger.py†L1-L32】
- Oracle invocations rely on external Gemini access; local runs require `GEMINI_API_KEY` in the environment. 【F:src/core/oracle.py†L1-L25】
- Agent SDK frames provide a stable ingress path for μApps, and their determinism supports webhook and Guardian test suites. 【F:src/agent_sdk/protocol_adapter.py†L49-L197】

## Immediate Hardening Targets

- **Configuration Failsafes:** add graceful degradation paths when `GEMINI_API_KEY` is missing to keep non-Oracle functionality runnable in CI.
- **Vault Client Isolation:** extract a shim around `src/core.database` to simplify offline testing and allow mock injection for ledger tests.
- **Telemetry Coverage:** extend `tests/phase-8.4/` to simulate entropy spikes and verify ScarIndex penalties.

## Test/Run Quickstart

- Python surface: `pytest -v`
- JavaScript telemetry normalization: `npm test tests/test_telemetry_normalize.js`

## Stewardship Notes

This map should be updated after each ΔΩ cycle. Keep entries concise, cite module boundaries, and capture cross-cutting dependencies that affect CI, deployment, or security posture.
