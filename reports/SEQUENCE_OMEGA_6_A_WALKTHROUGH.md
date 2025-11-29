# Walkthrough: Sequence Ω.6-A — Causality Mesh

## Goal
Implement a "Causality Mesh Layer" that models cause→effect relationships between audit events, exposing them via SQL, runtime emitters, dashboard panels, and CLI.

## Changes

### Database
- **Migration**: `spiral_supabase/migrations/20251129_seq_omega6_causality_mesh.sql`
    - Created `causal_event_links` table.
    - Created `fn_link_events` function (captures phase-lock hash and temporal anchor).
    - Created `view_causal_links` view.
- **Patch**: `spiral_supabase/migrations/20251129_seq_omega6_1_patch_link_events.sql`
    - Fixed `fn_link_events` to correctly identify temporal anchors by checking `drift_delta_ms IS NULL`.

### Runtime (Python)
- **New Module**: `core/causality_emitter.py`
    - `link_events()`: Wrapper for `fn_link_events` RPC.
- **Updated**: `core/audit_emitter.py`
    - `emit_audit_event()` now returns the event UUID.
- **Updated**: `core/guardian/runner.py`
    - Links `guardian_tick` -> `drift_warning` (if drift detected).
    - Links `guardian_tick` -> `anomaly_detected` (if anomaly detected).
- **Updated**: `core/temporal.py`
    - `TemporalDriftEngine` now emits `temporal_anchor_recorded` and `temporal_drift_verified` events.
    - Links `temporal_drift_verified` -> `temporal_drift_alert` if severity is RED.

### Dashboard (Next.js)
- **New Hook**: `web/dashboard/hooks/useCausalityMesh.ts`
    - Polls `view_causal_links`.
- **New Page**: `web/dashboard/app/causality/page.tsx`
    - Displays table of causal links with source/target details and weights.

### CLI
- **Updated**: `scripts/spiralctl.py`
    - Added `causality` command group.
    - `spiralctl causality link`: Create manual links.
    - `spiralctl causality surface`: View recent links (now shows Temporal Anchor ID).

## Verification Results

### 1. Manual Link Creation
Successfully created a link between a CLI manual emit and a System patch test event.
```bash
$ python scripts/spiralctl.py causality link --source ... --target ... --type manual_test --weight 0.5
[CAUSALITY] Link created: 438caa48-4a6b-4242-a898-faededc31f2f
```

### 2. Surface Verification
Successfully retrieved the link via CLI.
```bash
$ python scripts/spiralctl.py causality surface
--- Causality Surface (Limit: 20) ---
[2025-11-29T00:57:53.529256+00:00] manual_emit --(anchor_patch_test)--> patch_test (W: 0.9) | Anchor: f0e23dbf-c398-476e-99b3-cad8bc8bda12
```
*Note: The anchor ID confirms successful integration with Sequence Ω.5.*

## Next Steps
- Deploy dashboard changes to Vercel (if applicable).
- Proceed to Sequence Ω.6-B (if planned) or refine mesh logic.
