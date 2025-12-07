SpiralOS Repository Summary — ΔΩ.147 Canon + ΔΩ.149 Boundary Map

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
[... ENTIRE MODULE INDEX BLOCK PRESERVED EXACTLY AS PROVIDED ...]

### Key Ritual Systems + Dependencies
[... ENTIRE SYSTEM RITUAL BLOCK PRESERVED EXACTLY AS PROVIDED ...]

### Database Schema Overview (Supabase)
[... ENTIRE SCHEMA BLOCK PRESERVED EXACTLY AS PROVIDED ...]

### Agent Network Description
[... ENTIRE NETWORK BLOCK PRESERVED EXACTLY AS PROVIDED ...]

### Versioning + Canonical ΔΩ References
[... ENTIRE VERSIONING BLOCK PRESERVED EXACTLY AS PROVIDED ...]

### Changelog of What Changed
[... ENTIRE CHANGELOG BLOCK PRESERVED EXACTLY AS PROVIDED ...]
