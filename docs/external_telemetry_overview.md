# External Witness Telemetry (ΔΩ.12)

ΔΩ.12 introduces the External Witness Telemetry stack so SpiralOS can ingest
third-party signals without weakening deterministic rhythm and ScarIndex
contracts.

## Trust model
- **Allowlist-first:** sources and witness IDs must be explicitly allowlisted or
  they start from a neutral baseline.
- **Signature-aware:** optional per-witness signatures are verified via constant
  time comparison; failures are quarantined.
- **Trust scoring:** deterministic scoring clamps to `[0.0, 1.0]` and defaults to
  `0.5` before allowlist/signature boosts. Thresholds are enforced by the
  `TrustGate`.

## Adapter pipeline
1. **Schema validation:** `ExternalWitnessEvent` enforces strict field shape and
   coerces timestamps to UTC.
2. **Trust gate:** allowlist and signature checks compute a trust score; scores
   below the configured threshold are rejected.
3. **Rhythm gate:** stale events are rejected using `EXTERNAL_WITNESS_BOUNDS`
   (15m freshness window) and preserved deterministically in quarantine.
4. **Persistence:** accepted events land in `external_witness_events`; rejected
   events land in `external_quarantine` with a reason and raw payload.

## Rhythm gate
The rhythm gate reuses the ΔΩ.11 rhythm constants (`RhythmBounds`) to avoid drift
and enforces UTC timestamps for deterministic pulse checks. Freshness is computed
against a configurable `now_provider` to keep CI hermetic.

## Telemetry bus integration
The unified telemetry bus merges `external`, `internal`, and `heartbeat` kinds
through a single router. External events are converted into
`ExternalWitnessEvent` payloads before passing through the adapter. Heartbeat and
internal handlers remain isolated but share the same UTC coercion path.

## Supabase schema
- **`external_witness_events`**: primary table for accepted external signals
  with trust score, metadata, and UTC timestamps.
- **`external_quarantine`**: quarantine table for failed validations, including
  reason and raw payload for offline forensic review.
- **`external_scarindex_view`**: read-only projection to feed ScarIndex
  pipelines without touching the locked guardian schema.

## Test plan
- Schema validation and UTC coercion for external events.
- Trust gate allowlist/signature enforcement and thresholding.
- Rhythm gate freshness enforcement for stale events.
- Telemetry bus routing across external, internal, and heartbeat kinds.
- Migration presence and schema lock verification for new tables and view.
