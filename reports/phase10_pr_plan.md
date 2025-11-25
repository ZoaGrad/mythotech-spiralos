# Phase-10 Stabilization PR Plan

## Scope
- Telemetry v2 normalization for Guardian ingest.
- ScarIndex schema alignment between Python contracts and Supabase migrations.
- Guardian heartbeat retention audit with offline/online reconciliation paths.
- Diagnostics CLI smoke tests regenerated to guard the new audit surface.

## Sequence executed
1. **Telemetry v2 normalization** — Added envelope-aware parsing and metadata enrichment in `telemetry_normalize` so v1 and v2 payloads share the same normalized shape.
2. **ScarIndex schema alignment** — Projected `ScarIndexState` into `guardian_scarindex_current` and `guardian_scarindex_history` compatible models with adapter helpers for Supabase writes.
3. **Heartbeat retention audit** — Introduced offline audit utilities plus CLI hooks to reconcile fixture data with live Supabase heartbeats when available.
4. **Diagnostics smoke coverage** — Expanded `pulse_check` tests to exercise the new heartbeat audit paths and verify exit-code semantics for stale data.

## Validation hints
- Run `python -m pytest tests/test_pulse_check.py` to validate diagnostics flows.
- For live reconciliation, execute `python pulse_check.py --require-supabase --audit-heartbeats` with populated `.env`.
