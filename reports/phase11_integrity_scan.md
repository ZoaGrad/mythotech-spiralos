# Phase-11 Integrity Sweep Report

**Scope:** ScarIndex contracts, Guardian telemetry rhythm, heartbeat/telemetry normalization, and Supabase schema alignment.

## Actions completed
- Normalized ScarIndex adapter timestamp parsing to enforce UTC-aware datetimes and honor `Z`-terminated payloads.
- Unified heartbeat retention audits with the Phase-11 rhythm governance constants (3600s heartbeat freshness).
- Added a Supabase migration to backfill `created_at` on `guardian_scarindex_history` for locked schema parity.
- Extended tests to assert adapter projections respect the locked schema and timestamp normalization rules.
- Updated telemetry documentation to reflect UTC normalization expectations and rhythm-bound reuse across auditors.

## Findings
- Previous timestamp parsing treated `Z` timestamps as invalid and silently replaced them with `datetime.now()`, risking lineage drift. Fixed via explicit UTC coercion.
- Heartbeat audits used an implicit 60-minute default; this now derives from `HEARTBEAT_BOUNDS` to prevent divergence from CLI checks.
- Database schema lacked the documented `created_at` column on `guardian_scarindex_history`; migration added for determinism and auditing.

## Next checks
- Apply the new migration to staging/production and verify Supabase tables now expose `created_at` with UTC defaults.
- Reconcile any downstream analytics/BI tooling that assumed the history table lacked `created_at`.
