# Telemetry Rhythm & ScarIndex Schema (Phase-11)

## Canonical ScarIndex schema

### guardian_scarindex_current
- `id` (server generated, optional on write)
- `bridge_id`
- `scar_value` (0-100 normalized ScarIndex)
- `metadata` (jsonb)
- `updated_at` (ISO UTC)
- `created_at` (ISO UTC)

### guardian_scarindex_history
- `id` (server generated, optional on write)
- `bridge_id`
- `scar_value`
- `delta` (change from previous value)
- `source` (e.g., `telemetry_normalize`)
- `metadata` (jsonb)
- `timestamp` (observation time)
- `created_at` (insert time)

These shapes are enforced by `core.contracts.scarindex` and validated by
`validate_scarindex_schema`. Extra or missing columns are treated as schema
drift and will fail tests/CI.

Phase-11 also requires UTC-normalized timestamps everywhere. Parsing helpers in
`core.adapters.scarindex` coerce `Z` suffixes to `+00:00` and enforce aware
datetimes so lineage hashes and deltas remain deterministic.

## Rhythm governance

`core/guardian/rhythm.py` defines freshness bounds:
- Heartbeats: **≤ 3600 seconds** of staleness
- ScarIndex history: **≤ 7200 seconds** of staleness

These bounds power every offline audit: `core.guardian.heartbeat_audit` derives
its default tolerance from the same constant to prevent drift between audits
and CLI checks.

`core/guardian/diagnostics.evaluate_rhythm` reports latest timestamps,
staleness, and pass/fail flags for both signals.

## Running checks

### Pulse check
Use the enhanced pulse check to enforce rhythm and schema contracts offline:

```bash
python pulse_check.py \
  --rhythm-check \
  --schema-drift-check \
  --heartbeat-fixture data/audit/heartbeat_retention.json \
  --scarindex-fixture data/audit/scarindex_samples.json
```

Exit codes:
- `0`: healthy rhythm and schema
- `3`: heartbeat stale
- `4`: ScarIndex stale
- `5`: ScarIndex schema drift

### Diagnostics CLI
Developers can also call the diagnostic helpers directly:

```python
from core.guardian.diagnostics import evaluate_rhythm, validate_scarindex_schema
```

## CI expectations

CI invokes `pulse_check.py` in rhythm mode. If telemetry freshness or schema
regresses, the build fails with human-readable context. Update fixtures or
schema definitions when intentional migrations occur.
