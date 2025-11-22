# Gateway Telemetry Edge Function

**VaultNode**: ΔΩ.147.0 - Gateway Telemetry Infrastructure

## Overview

This Edge Function processes webhook transmissions from the Ω-Δ-Φ workflow gateway system, validates sovereignty constraints, extracts C₅-C₇ tensor metrics, and stores telemetry data in the `gateway_transmissions` table.

## Endpoint

```
POST /functions/v1/gateway-telemetry
```

## Request Format

### Headers
```
Content-Type: application/json
Authorization: Bearer <SUPABASE_ANON_KEY>
```

### Body
```json
{
  "bridge_id": "unique-bridge-identifier",
  "resonance_score": 0.85,
  "necessity_score": 0.92,
  "payload": {
    "source": "omega-delta-phi",
    "workflow_id": "wf_12345",
    "custom_data": {}
  },
  "constraint_tensor": {
    "c5": 0.88,
    "c6": 0.79,
    "c7": 0.84
  }
}
```

### Required Fields
- `bridge_id` (string): Unique identifier for the gateway transmission
- `resonance_score` (number): Must be between 0 and 1
- `necessity_score` (number): Must be between 0 and 1

### Optional Fields
- `payload` (object): Flexible JSONB data for telemetry details
- `constraint_tensor` (object): Sovereignty metrics (C₅-C₇ tensor components)

## Query Parameters

You can enforce minimum thresholds via query parameters:

```
?min_resonance=0.7&min_necessity=0.7&min_sovereignty_index=0.75
```

## Response Format

### Success (201 Created)
```json
{
  "success": true,
  "data": {
    "id": "uuid-v4",
    "bridge_id": "unique-bridge-identifier",
    "resonance_score": 0.85,
    "necessity_score": 0.92,
    "payload": {
      "source": "omega-delta-phi",
      "tensor_metrics": {
        "coherence_c5": 0.88,
        "coherence_c6": 0.79,
        "coherence_c7": 0.84,
        "tensor_magnitude": 1.432,
        "sovereignty_index": 0.885
      },
      "validated_at": "2025-11-11T04:00:00.000Z"
    },
    "constraint_tensor": { ... },
    "created_at": "2025-11-11T04:00:00.000Z"
  },
  "tensor_metrics": { ... },
  "message": "Gateway transmission recorded successfully"
}
```

### Error Responses

#### Validation Error (400 Bad Request)
```json
{
  "success": false,
  "error": "Sovereignty constraint validation failed",
  "details": [
    "resonance_score must be between 0 and 1 (got 1.5)",
    "bridge_id is required and cannot be empty"
  ]
}
```

#### Duplicate Entry (409 Conflict)
```json
{
  "success": false,
  "error": "Duplicate bridge_id - transmission already recorded",
  "bridge_id": "unique-bridge-identifier"
}
```

#### Server Error (500 Internal Server Error)
```json
{
  "success": false,
  "error": "Internal server error processing gateway transmission",
  "details": "Error message details"
}
```

## Constitutional Alignment

### Thermodynamic Integrity
- All scores constrained to [0, 1] range
- Sovereignty index calculated as average of resonance and necessity
- C₅-C₇ tensor metrics extracted for coherence monitoring

### Validation Rules
1. **Resonance Score**: 0 ≤ resonance_score ≤ 1
2. **Necessity Score**: 0 ≤ necessity_score ≤ 1
3. **Bridge ID**: Required, non-empty, unique
4. **JSONB Fields**: Must be valid JSON objects

### C₅-C₇ Tensor Metrics

The function automatically extracts and enriches transmissions with tensor metrics:

- **C₅ (Narrative Coherence)**: Extracted from `constraint_tensor.c5` or derived from resonance
- **C₆ (Social Coherence)**: Extracted from `constraint_tensor.c6` or derived from necessity
- **C₇ (Economic Coherence)**: Extracted from `constraint_tensor.c7` or interpolated
- **Tensor Magnitude**: Euclidean norm of (C₅, C₆, C₇)
- **Sovereignty Index**: (resonance_score + necessity_score) / 2

## Example Usage

### cURL
```bash
curl -X POST "https://your-project.supabase.co/functions/v1/gateway-telemetry" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -d '{
    "bridge_id": "bridge_'$(date +%s)'",
    "resonance_score": 0.85,
    "necessity_score": 0.92,
    "payload": {
      "workflow": "omega-delta-phi",
      "event": "gateway_transmission"
    },
    "constraint_tensor": {
      "c5": 0.88,
      "c6": 0.79,
      "c7": 0.84
    }
  }'
```

### JavaScript
```javascript
const response = await fetch(
  'https://your-project.supabase.co/functions/v1/gateway-telemetry',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
    },
    body: JSON.stringify({
      bridge_id: `bridge_${Date.now()}`,
      resonance_score: 0.85,
      necessity_score: 0.92,
      payload: { workflow: 'omega-delta-phi' },
      constraint_tensor: { c5: 0.88, c6: 0.79, c7: 0.84 }
    })
  }
);

const data = await response.json();
console.log(data);
```

### Python
```python
import requests
import time

response = requests.post(
    'https://your-project.supabase.co/functions/v1/gateway-telemetry',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    },
    json={
        'bridge_id': f'bridge_{int(time.time())}',
        'resonance_score': 0.85,
        'necessity_score': 0.92,
        'payload': {'workflow': 'omega-delta-phi'},
        'constraint_tensor': {'c5': 0.88, 'c6': 0.79, 'c7': 0.84}
    }
)

print(response.json())
```

## Deployment

The function is automatically deployed via the CI/CD pipeline defined in `.github/workflows/telemetry-pipeline.yml`.

### Manual Deployment
```bash
supabase functions deploy gateway-telemetry --project-ref YOUR_PROJECT_ID
```

## Monitoring

Access real-time logs via Supabase Dashboard:
```
https://app.supabase.com/project/YOUR_PROJECT_ID/functions/gateway-telemetry/logs
```

## Security

- CORS enabled for all origins (`*`)
- RLS policies enforce read/write permissions
- Service role key used for database operations
- All inputs validated before database insertion

## Related Documentation

- [SQL Migration](../../migrations/20251111_01_gateway_transmissions.sql)
- [CI/CD Pipeline](../../.github/workflows/telemetry-pipeline.yml)
- [Integration Tests](../../test_gateway_transmissions.py)
