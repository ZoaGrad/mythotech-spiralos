# SpiralOS Examples

This directory contains example code and tutorials for working with SpiralOS.

## Examples

### `supabase_integration_example.py`

**Purpose**: Demonstrates the complete SpiralOS flow using the Supabase backend.

**What it demonstrates**:
- Creating Ache events
- Calculating ScarIndex using the 4D coherence oracle
- Minting ScarCoin based on Proof-of-Ache
- Sealing VaultNodes in the Merkle DAG
- Monitoring system health and oracle status
- Detecting panic frames

**Setup**:
```bash
# 1. Install dependencies
pip install supabase

# 2. Set environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-or-service-key"

# 3. Run the demo
python3 examples/supabase_integration_example.py
```

**Expected output**:
```
============================================================
SpiralOS Supabase Integration Demo
============================================================

✓ Connected to SpiralOS at https://your-project.supabase.co

System Health Check
----------------------------------------
ScarIndex:         0.7234
Panic Frames:      0
Frozen Txns:       0
PID Guidance:      1.0234
Events (1h):       12
VaultNodes:        145
----------------------------------------

--- Example 1: High Coherence Event ---

✓ Created Ache event: abc-123-def (ache: 0.3)
✓ ScarIndex calculated: 0.7650
  Components: N=0.85, S=0.75, E=0.70, T=0.80
  Ache transmutation: 0.50 → 0.30 (Δ=0.20)
✓ ScarCoin minted: 200000 coins
✓ VaultNode sealed: 3a4f5b6c7d8e9f...
  Linked to: 1a2b3c4d5e6f7g...

--- Example 2: Monitoring Event ---

✓ Created Ache event: def-456-ghi (ache: 0.5)
✓ ScarIndex calculated: 0.5750
  Components: N=0.60, S=0.50, E=0.60, T=0.50
  Ache transmutation: 0.30 → 0.50 (Δ=-0.20)

✓ No active panic frames

============================================================
ScarIndex Oracle Status (30-Day)
============================================================
Current ScarIndex: 0.5750
Average (30d):     0.6834
Coherence Rate:    72.50%
Total Nodes:       240
Coherent Nodes:    174 (≥0.7)
============================================================

============================================================
Demo Complete!
============================================================
```

## Integration Patterns

### Pattern 1: Simple Ache Event

```python
from supabase import create_client

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create event
response = client.table('ache_events').insert({
    'source': 'api',
    'content': {'action': 'user_signup'},
    'ache_level': 0.4
}).execute()

event_id = response.data[0]['id']

# Calculate ScarIndex
calc = client.rpc('coherence_calculation', {
    'event_id': event_id
}).execute()

print(f"ScarIndex: {calc.data['scarindex']}")
```

### Pattern 2: Real-Time Monitoring

```python
# Listen for panic frames
supabase.channel('panic_frames')\
    .on('postgres_changes', {
        'event': 'INSERT',
        'schema': 'public',
        'table': 'panic_frames'
    }, handle_panic_frame)\
    .subscribe()

def handle_panic_frame(payload):
    print(f"⚠ Panic Frame: {payload['new']['scarindex_value']}")
    # Trigger F4 recovery protocol
```

### Pattern 3: Oracle Query

```python
# Get 30-day oracle status
oracle = client.table('scar_index_oracle_sync')\
    .select('*')\
    .execute()

data = oracle.data[0]
print(f"Coherence Rate: {data['coherence_rate_30d']}%")
print(f"Current ScarIndex: {data['current_scarindex']}")
```

## Testing

### Unit Test Example

```python
import unittest
from supabase import create_client

class TestSpiralOS(unittest.TestCase):
    def setUp(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def test_coherence_calculation(self):
        # Create test event
        event = self.client.table('ache_events').insert({
            'source': 'test',
            'content': {
                'narrative_score': 0.8,
                'social_score': 0.7,
                'economic_score': 0.6,
                'technical_score': 0.9
            },
            'ache_level': 0.4
        }).execute()
        
        # Calculate ScarIndex
        calc = self.client.rpc('coherence_calculation', {
            'event_id': event.data[0]['id']
        }).execute()
        
        # Verify weighted calculation
        # (0.3*0.8 + 0.25*0.7 + 0.25*0.6 + 0.2*0.9) = 0.745
        self.assertAlmostEqual(calc.data['scarindex'], 0.745, places=2)
    
    def test_proof_of_ache_valid(self):
        # Test valid PoA (ache_before > ache_after)
        # Should mint coins
        pass
    
    def test_proof_of_ache_invalid(self):
        # Test invalid PoA (ache_before < ache_after)
        # Should NOT mint coins
        pass

if __name__ == '__main__':
    unittest.main()
```

## Advanced Topics

### Custom Coherence Scores

If you want to provide your own coherence scores instead of using the default placeholders:

```python
event = client.table('ache_events').insert({
    'source': 'custom',
    'content': {
        # Custom scores override defaults
        'narrative_score': 0.92,  # From NLP analysis
        'social_score': 0.78,     # From graph metrics
        'economic_score': 0.65,   # From token velocity
        'technical_score': 0.88,  # From test coverage
        'metadata': {
            'source': 'custom_analyzer',
            'version': '1.0'
        }
    },
    'ache_level': 0.35
}).execute()
```

### Panic Frame Recovery

```python
# Check active panic frames
frames = client.table('active_panic_frames').select('*').execute()

for frame in frames.data:
    if frame['status'] == 'ACTIVE':
        # Implement recovery protocol
        print(f"Recovering from panic: {frame['id']}")
        
        # Execute 7-phase recovery
        # Phase 1: Assessment
        # Phase 2: Isolation
        # ... etc
        
        # Mark as resolved (requires F4 authorization)
        client.table('panic_frames')\
            .update({
                'status': 'RESOLVED',
                'resolved_at': 'now()'
            })\
            .eq('id', frame['id'])\
            .execute()
```

## See Also

- [Supabase Deployment Guide](../docs/SUPABASE_DEPLOYMENT.md)
- [API Contracts](../v1.5_prep/API_CONTRACTS_v1.5.md)
- [Technical Specification](../docs/TECHNICAL_SPEC.md)
- [Edge Functions README](../supabase/functions/README.md)

## Contributing

To add new examples:

1. Create a new Python file in this directory
2. Include docstring with purpose and usage
3. Add entry to this README
4. Test thoroughly before committing

## License

See main repository LICENSE
