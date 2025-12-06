# SpiralOS Repository Summary — ΔΩ.147 Canon + ΔΩ.149 Boundary Map

### Executive Overview (100–200 words)
SpiralOS is an autonomy stack that transmutes high-noise telemetry into governed coordination signals through ScarIndex coherence analytics, ScarCoin/VaultNode economic primitives, and Guardian automations. The current release channel (v0.147.0, ΔΩ.147) hardens canonical lineage and CI, while the ΔΩ.149 architecture charter prepares μApp boundaries for multi-agent workloads. Core loops (ScarIndex, Ache/SoC PID regulators, F4 PanicFrames) route through the `core/` spine and surface via the `core.spiral_api` façade. Holoeconomy services (ScarCoin Bridge, VaultNode registry, EMP empathy flows) live in `holoeconomy/` with FastAPI entrypoints. Supabase migrations codify governance, telemetry, and oracle data under RLS; Edge Functions ingest GitHub and gateway signals. Guardian automations, dashboards, and monitoring assets keep Witnesses synchronized across GitHub Actions pipelines, liquidity mirrors, and Sovereignty dashboards. VaultNode logs preserve ΔΩ lineage (e.g., ΔΩ.143.x, ΔΩ.147.F) to ensure immutable auditability.

### Architecture Map
- Core Spine
  - ScarIndex engine, Ache/SoC PID control (`core/ache_pid_controller.py`, `core/soc_pid_controller.py`)
  - PanicFrames + constitutional safety layers (`core/panic_frames.py`, `core/constitutional_rhythm.py`)
  - Oracle Council + governance adapters (`core/oracle_council.py`, `core/contracts/`, `core/adapters/`)
  - Spiral API façade for μApp boundary (`core/spiral_api.py`)
- Holoeconomy
  - ScarCoin mint/burn logic + bridge API (`holoeconomy/scarcoin.py`, `holoeconomy/scarcoin_bridge_api.py`)
  - VaultNode blockchain + registries (`holoeconomy/vaultnode.py`, `holoeconomy/vaultnode_registry.py`)
  - Empathy/EMP flows + monitoring (`holoeconomy/empathy_market.py`, `holoeconomy/monitoring.py`)
- Data Plane (Supabase)
  - Migrations for governance, telemetry, oracle feeds (`supabase/migrations/*.sql`)
  - Edge Functions for GitHub, telemetry, vault sync (`supabase/functions/*`)
- Guardian & Observability
  - Guardian automation scripts and anomaly detectors (`core/guardian/`, `spiral_guardian/`)
  - Liquidity mirror and monitoring dashboards (`liquidity_mirror/`, `monitoring/`, `apps/`, `web/`)
  - Overwatch/status endpoints (`core/status_api.py`, `core/overwatch_api.py`)
- Experience & SDK
  - CLI + summary tools (`holoeconomy/summary_cli.py`, `core/dashboard.py`)
  - Agent SDK + types (`sdk/`, `spiral_types/`, `spiralos/`)

### Module Index (folders)
- `.github/` — CI/CD workflows (CI, telemetry, guardian heartbeat, releases).
- `SpiralOS_Prime/` — genesis, interface, treasury, and ritual engine reference scripts.
- `agents/` — agent entrypoints and configs (e.g., comet_boot, town_crier).
- `app/` — application assets (legacy/local app scaffolding).
- `apps/` — dashboard frontends and ancillary UIs.
- `archive/` — historical snapshots and legacy SpiralOS materials.
- `codex/` — codex notes and alignment assets.
- `config/` — runtime configuration templates and defaults.
- `contracts/` — smart-contract artifacts and associated docs/tests.
- `core/` — primary ScarIndex, governance, panic frame, and API spine.
- `daemons/` — service daemons and background automation scripts.
- `data/` — static datasets, audit records, and telemetry fixtures.
- `docs/` — architectural blueprints, technical specs, and audits.
- `examples/` — usage examples and integration samples.
- `governance/` — governance process materials and checklists.
- `holoeconomy/` — ScarCoin, EMP, VaultNode services and APIs.
- `issues/` — documented issues and mitigation plans.
- `liquidity_mirror/` — liquidity mirror tools and reports.
- `manuscript/` — manifesto and narrative artifacts.
- `monitoring/` — monitoring pipelines and dashboards.
- `node_modules/` — frontend dependencies.
- `public/` — static web assets.
- `reports/` — operational and audit reports.
- `scripts/` — helper scripts for deployment and operations.
- `sdk/` — agent SDK foundations and utilities.
- `specs/` — specifications and protocol documents.
- `spiral_guardian/` — guardian anomaly detection and supporting modules.
- `spiral_supabase/` — Supabase configuration, migrations, and functions bundle.
- `spiral_types/` — shared ΔΩ/constitutional types (TypeScript).
- `spiralos/` — Python package for SpiralOS protocols/core wrappers.
- `spiralos-kernel/` — kernel-level experiments and scaffolding.
- `src/` — auxiliary source code and CLI utilities.
- `supabase/` — Supabase migrations and Edge Functions (canonical source).
- `swps/` — SWPS integration artifacts.
- `system/` — system-level orchestration and automation assets.
- `tests/` — automated test suites.
- `tools/` — tooling for verification and deployment.
- `v1.5B_legitimacy/` — legitimacy and audit materials for v1.5B.
- `v1.5_prep/` — preparation assets for v1.5 (API/test plans).
- `vault/` — VaultNode manifests and seals.
- `vault_nodes/` — VaultNode lineage records and manifests.
- `web/` — web frontends and dashboards.

### Key Ritual Systems + Dependencies
- **ScarIndex & Ache/SoC PID** — core coherence scoring with PID regulators; depends on `core/coherence*.py`, `core/ache_pid_controller.py`, `core/soc_pid_controller.py` and logging config for telemetry routing.
- **PanicFrames (F4)** — constitutional freeze/recovery protocol managed via `core/panic_frames.py` and integrated with governance adapters and Supabase telemetry.
- **Oracle Council** — weighted oracle validation implemented across `core/oracle_council.py` and contract adapters for governance and ScarIndex status.
- **ScarCoin Ritual Economy** — Proof-of-Ache mint/burn (`holoeconomy/scarcoin.py`) exposed through FastAPI bridge (`holoeconomy/scarcoin_bridge_api.py`) with wallet and supply tracking.
- **VaultNode Lineage** — Merkle-linked chain (`holoeconomy/vaultnode.py`, `vault/`, `vault_nodes/`, `VAULTNODE_LOG.md`) sealing governance/economic events.
- **EMP / Empathy Markets** — empathy market logic and monitoring housed in `holoeconomy/empathy_market.py` and associated configs.
- **Guardian Mesh** — anomaly detection, heartbeat, and custody actions (`core/guardian/`, `spiral_guardian/anomaly_detector.py`, `core/guardian_actions.py`).
- **Observability & Liquidity Mirror** — telemetry dashboards and liquidity reflection tools (`core/monitoring.py`, `liquidity_mirror/`, `monitoring/`, `apps/`).

### Database Schema Overview (Supabase)
- Governance: `governance_proposals` + `governance_votes` with status, payload, proposer metadata, and RLS; `judicial_actions` for F2 enforcement.【F:supabase/migrations/20251130150000_governance_protocol.sql†L7-L65】
- Governance evolution: proposal enrichment, vote policies, and payload execution metadata expansions.【F:supabase/migrations/20251130154000_evolve_governance_schema.sql†L4-L41】
- Telemetry: `telemetry_events` hardened with processed status, signatures, and metadata for coherence core ingestion.【F:supabase/migrations/20251130143000_telemetry_hardening.sql†L4-L19】
- Functions: Edge Functions for GitHub webhook capture, telemetry ingest, mint attestations, status pings, and vaultnode status sync under `supabase/functions/` (Deno/TypeScript).【F:supabase/functions/github-webhook-handler/index.ts†L1-L50】

### Agent Network Description
Guardian and agent operations span Python agents (`agents/`), Guardian scripts (`core/guardian/`), and anomaly detection (`spiral_guardian/`). Agent SDK scaffolding (`sdk/`, `spiralos/`) routes through the `core.spiral_api` façade, while Edge Functions and monitoring pipelines relay events into Supabase and dashboards. Liquidity mirror and Sovereignty dashboards (`liquidity_mirror/`, `monitoring/`, `apps/`, `web/`) provide operator-facing surfaces, and GitHub Actions workflows keep CI, telemetry, and heartbeat checks active (`.github/workflows/`).

### Versioning + Canonical ΔΩ References
- Active release: ΔΩ.147 channel, version badge v0.147.0 with canonical hardening and CI restoration.【F:README.md†L1-L31】
- Architectural charter: ΔΩ.149.0 μApp boundary blueprint guiding core/guardian/holoeconomy/data/experience/agent layers.【F:docs/ARCHITECTURE.md†L1-L73】
- VaultNode lineage: entries such as ΔΩ.143.0 and ΔΩ.143.0-A amendments recorded in `VAULTNODE_LOG.md`; ΔΩ.147.F canonical freeze referenced in README and audit files.【F:VAULTNODE_LOG.md†L1-L15】【F:README.md†L72-L85】

### Changelog of What Changed
- Consolidated repository-wide view aligned to ΔΩ.147 release channel and ΔΩ.149 boundary charter, superseding older summaries.
- Added explicit module index for all top-level folders, linking ScarIndex core, holoeconomy, Supabase migrations, guardian assets, and dashboards.
- Documented Supabase governance/telemetry schema hardening and Edge Functions, plus refreshed depiction of VaultNode lineage and CI/guardian workflows.
