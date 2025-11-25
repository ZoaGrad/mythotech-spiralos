# PR #1: Full-System Reconnaissance + Drift Stabilization

## Overview
This document captures the initial reconnaissance across SpiralOS and establishes a stabilization roadmap. The focus is on reducing entropy around connectivity diagnostics, heartbeat signaling, and contract safety.

## Key Observations
- `pulse_check.py` executed destructive debug behavior by dumping raw `.env` content and performing implicit Supabase network calls during import. This risked secret leakage and made the script untestable without live credentials.
- Several operational scripts run logic at import time; refactoring them behind `main()` entrypoints will allow safer testing and CLI integration.
- Telemetry/guardian artifacts (e.g., `GATEWAY_TELEMETRY_SUMMARY.md`, `verify_overwatch.sh`) lack a consolidated smoke path to validate scar index availability without network dependence.
- Repository contains multiple phase-specific summaries (PHASE 7/8.*) without a unified forward roadmap for Phase 9 stabilization and telemetry convergence.

## Roadmap (Phase 9 Sequence)
1. Harden diagnostics entrypoints (starting with `pulse_check.py`) to avoid secret leakage and enable offline testability.
2. Establish a consolidated heartbeat smoke-test harness that validates Guardian, Gateway, and Scar Index connectivity with offline fixtures.
3. Normalize Supabase schemas/types by generating `spiral_types` snapshots and adding drift detection tests.
4. Create telemetry normalization layer ensuring consistent timestamp formatting across `monitoring/`, `reports/`, and Supabase ingest paths.
5. Add contract-level unit tests for core vault/guardian flows to protect against interface drift.
6. Introduce async-safe RPC adapters with explicit timeout/fallback behavior for offline-first execution.
7. Wire CLI tooling into CI (e.g., `pulse_check`, guardian smoke tests) with deterministic exit codes.
8. Document Phase 9 architecture decisions and convergence plan, replacing scattered phase summaries with a living ADR index.

## Immediate Outcome
- `pulse_check.py` now guards secrets, supports structured exit codes, and defers live Supabase handshakes unless explicitly requested, providing a foundation for the subsequent smoke-test suite.
