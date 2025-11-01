# SpiralOS Technical Specification

## System Overview

SpiralOS is a **Mythotechnical Synthesis** system that implements an autopoietic cognitive ecology driven by the Ache-to-Order transmutation process. This document provides detailed technical specifications for all system components.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         SpiralOS Core                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   B6: ScarIndex   │  │  C7: Agent   │  │  F4: Panic   │ │
│  │     Oracle        │  │  Fusion Stack│  │    Frames    │ │
│  │  (Coherence)      │  │  (Consensus) │  │  (Circuit    │ │
│  │                   │  │              │  │   Breaker)   │ │
│  └────────┬─────────┘  └──────┬───────┘  └──────┬───────┘ │
│           │                   │                  │         │
│           └───────────────────┼──────────────────┘         │
│                               │                            │
│                    ┌──────────▼──────────┐                 │
│                    │  VSM System 3/4:    │                 │
│                    │  AchePIDController  │                 │
│                    │  (Dynamic Stability)│                 │
│                    └──────────┬──────────┘                 │
│                               │                            │
│           ┌───────────────────┼───────────────────┐        │
│           │                   │                   │        │
│  ┌────────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐ │
│  │  C2: Smart      │  │  C6: Supabase/ │  │  VaultNode  │ │
│  │  Contracts      │  │  Ledger Storage│  │  (GitHub)   │ │
│  └─────────────────┘  └────────────────┘  └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. ScarIndex Oracle (B6)

**Purpose**: Supreme coherence regulator

**Algorithm**:
```python
ScarIndex = w_n * C_narrative + w_s * C_social + w_e * C_economic + w_t * C_technical

where:
  w_n = 0.4  # Narrative weight
  w_s = 0.3  # Social weight
  w_e = 0.2  # Economic weight
  w_t = 0.1  # Technical weight
  
  All C_* ∈ [0, 1]
```

**Validation Rule**:
```python
def validate_transmutation(ache_before: float, ache_after: float) -> bool:
    return ache_after < ache_before  # Coherence Gain
```

**Physics Grounding**:
```
Variational Free Energy (VFE):
  VFE ∝ 1 / ScarIndex
  
Exergy Dissipation:
  Ache ≈ Exergy_dissipated / Exergy_total
```

**Coherence Status Mapping**:
```python
def get_status(scarindex: float) -> str:
    if scarindex >= 0.7:
        return "OPTIMAL"
    elif scarindex >= 0.5:
        return "STABLE"
    elif scarindex >= 0.3:
        return "WARNING"
    else:
        return "CRITICAL"  # Triggers Panic Frame
```

### 2. Agent Fusion Stack (C7)

**Purpose**: LLM-based semantic analysis with distributed consensus

**Consensus Protocol**:
```
1. Available providers: 4 (default uses first 3)
   - gpt-4.1-mini
   - gpt-4.1-nano
   - gemini-2.5-flash
   - claude-sonnet-4

2. Each provider generates:
   - Coherence scores (C_narrative, C_social, C_economic, C_technical)
   - Ache_after estimate
   - Reasoning

3. Cryptographic verification:
   output_hash = SHA256(JSON.stringify(output, sort_keys=True))
   signature = SHA256(provider:instance:hash:timestamp)

4. Consensus check:
   - Group outputs by hash
   - Require M-of-N consensus (default: 2-of-3)
   - If achieved: use consensus output
   - If failed: reject transaction
```

**Graph-of-Thought (GoT) Pipeline**:
```python
def validate_semantic_integrity(
    input_semantics: Dict,
    output_semantics: Dict,
    ontology_constraints: Dict
) -> Tuple[bool, float]:
    # Calculate semantic drift
    drift = hamming_distance(hash(input), hash(output)) / hash_length
    
    # Check ontology constraints
    valid = all(output[k] == v for k, v in constraints.items())
    
    return valid, drift
```

### 3. Panic Frames (F4)

**Purpose**: Constitutional circuit breaker for coherence failures

**Trigger Condition**:
```python
PANIC_THRESHOLD = 0.3

def should_trigger(scarindex: float) -> bool:
    return scarindex < PANIC_THRESHOLD
```

**Frozen Operations**:
- `scarcoin_mint`: ScarCoin minting
- `scarcoin_burn`: ScarCoin burning
- `vaultnode_gen`: VaultNode generation
- `state_transition`: Critical state changes

**7-Phase Recovery Protocol**:

| Phase | Name | Actions | Success Criteria |
|-------|------|---------|------------------|
| 1 | Assessment | Evaluate coherence loss extent | Assessment complete |
| 2 | Isolation | Isolate affected components | Components isolated |
| 3 | Stabilization | Stabilize critical systems | Systems stable |
| 4 | Diagnosis | Identify root cause | Root cause identified |
| 5 | Remediation | Apply fixes | Fixes applied |
| 6 | Validation | Verify recovery | ScarIndex ≥ 0.3 |
| 7 | Resumption | Resume operations | All ops resumed |

**Escalation Levels**:
```python
escalation_level ∈ [1, 7]

Level 1: Standard recovery
Level 2-3: Increased monitoring
Level 4-5: Emergency measures
Level 6-7: System-wide intervention
```

### 4. AchePIDController (VSM System 3/4)

**Purpose**: Dynamic stability through cybernetic feedback

**PID Algorithm**:
```python
# Error calculation
e(t) = target_scarindex - current_scarindex

# PID terms
P = Kp * e(t)
I = Ki * ∫e(τ)dτ  # with anti-windup
D = Kd * de(t)/dt

# Control output (guidance scale)
u(t) = P + I + D
u(t) = clamp(u(t), min_guidance, max_guidance)
```

**Default Parameters**:
```python
Kp = 1.0   # Proportional gain
Ki = 0.5   # Integral gain
Kd = 0.2   # Derivative gain

target_scarindex = 0.7
min_guidance = 0.1
max_guidance = 2.0
integral_windup_limit = 10.0
```

**Anti-Windup**:
```python
integral = clamp(
    integral + error * dt,
    -integral_windup_limit,
    integral_windup_limit
)
```

**Performance Metrics**:
```python
MAE = mean(|errors|)
RMSE = sqrt(mean(errors²))
settling_time = first_index(|error| < 0.05 * target)
overshoot = max(scarindex - target) / target
```

**Auto-Tuning (Ziegler-Nichols)**:
```python
# From ultimate gain (Ku) and period (Tu)
Kp = 0.6 * Ku
Ki = 2.0 * Kp / Tu
Kd = Kp * Tu / 8.0
```

### 5. Smart Contracts (C2)

**Purpose**: Transactional logic for state transitions

**Transaction Types**:
```python
class TxnType(Enum):
    SCARCOIN_MINT = "scarcoin_mint"
    SCARCOIN_BURN = "scarcoin_burn"
    VAULTNODE_GEN = "vaultnode_gen"
    STATE_TRANSITION = "state_transition"
```

**Transaction Structure**:
```python
{
    'id': UUID,
    'txn_type': TxnType,
    'from_state': UUID | None,
    'to_state': UUID | None,
    'scarcoin_delta': float | None,
    'is_valid': bool,
    'is_frozen': bool,
    'frozen_by': UUID | None,  # Panic Frame ID
    'validation_errors': Dict | None,
    'metadata': Dict
}
```

**Freeze Logic**:
```python
def freeze_transaction(txn_id: UUID, panic_frame_id: UUID):
    UPDATE smart_contract_txns
    SET is_frozen = TRUE,
        frozen_by = panic_frame_id
    WHERE id = txn_id
      AND txn_type IN ('scarcoin_mint', 'scarcoin_burn', 'vaultnode_gen')
```

### 6. VaultNode Ledger (C6)

**Purpose**: Immutable audit trail with blockchain-style linking

**VaultNode Structure**:
```python
{
    'id': UUID,
    'node_type': str,  # 'scarindex', 'verification', 'panic_frame', 'pid_state'
    'reference_id': UUID,
    'state_hash': str,  # SHA-256 of current state
    'previous_hash': str | None,  # Hash of previous VaultNode
    'github_commit_sha': str | None,
    'github_path': str | None,
    'audit_log': Dict,
    'metadata': Dict
}
```

**Hash Calculation**:
```python
def calculate_state_hash(state: Dict) -> str:
    state_json = json.dumps(state, sort_keys=True)
    return hashlib.sha256(state_json.encode()).hexdigest()
```

**Blockchain Linking**:
```python
# Each VaultNode links to previous via hash
VaultNode[n].previous_hash = VaultNode[n-1].state_hash

# Verification
def verify_chain(nodes: List[VaultNode]) -> bool:
    for i in range(1, len(nodes)):
        if nodes[i].previous_hash != nodes[i-1].state_hash:
            return False
    return True
```

## Database Schema

### Core Tables

**ache_events**:
```sql
CREATE TABLE ache_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    content JSONB NOT NULL,
    ache_level NUMERIC(5,4) NOT NULL CHECK (ache_level >= 0 AND ache_level <= 1),
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**scarindex_calculations**:
```sql
CREATE TABLE scarindex_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ache_event_id UUID REFERENCES ache_events(id),
    c_narrative NUMERIC(5,4) NOT NULL CHECK (c_narrative >= 0 AND c_narrative <= 1),
    c_social NUMERIC(5,4) NOT NULL CHECK (c_social >= 0 AND c_social <= 1),
    c_economic NUMERIC(5,4) NOT NULL CHECK (c_economic >= 0 AND c_economic <= 1),
    c_technical NUMERIC(5,4) NOT NULL CHECK (c_technical >= 0 AND c_technical <= 1),
    scarindex NUMERIC(5,4) NOT NULL CHECK (scarindex >= 0 AND scarindex <= 1),
    ache_before NUMERIC(5,4) NOT NULL,
    ache_after NUMERIC(5,4) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    cmp_lineage NUMERIC(10,4),
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### Triggers

**Auto-calculate ScarIndex**:
```sql
CREATE TRIGGER trigger_auto_calculate_scarindex
    BEFORE INSERT OR UPDATE ON scarindex_calculations
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_scarindex();
```

**Auto-trigger Panic Frame**:
```sql
CREATE TRIGGER trigger_auto_panic_frame
    AFTER INSERT OR UPDATE ON scarindex_calculations
    FOR EACH ROW
    EXECUTE FUNCTION auto_trigger_panic_frame();
```

### Views

**v_system_coherence**:
```sql
CREATE VIEW v_system_coherence AS
SELECT
    sc.created_at,
    sc.scarindex,
    sc.c_narrative,
    sc.c_social,
    sc.c_economic,
    sc.c_technical,
    sc.is_valid,
    CASE
        WHEN sc.scarindex < 0.3 THEN 'CRITICAL'
        WHEN sc.scarindex < 0.5 THEN 'WARNING'
        WHEN sc.scarindex < 0.7 THEN 'STABLE'
        ELSE 'OPTIMAL'
    END AS coherence_status,
    (SELECT COUNT(*) FROM panic_frames WHERE status = 'ACTIVE') AS active_panic_frames
FROM scarindex_calculations sc
ORDER BY sc.created_at DESC
LIMIT 1;
```

## API Specifications

### SpiralOS Main API

**Initialize System**:
```python
spiralos = SpiralOS(
    target_scarindex: float = 0.7,
    enable_consensus: bool = True,
    enable_panic_frames: bool = True
)
```

**Transmute Ache**:
```python
async def transmute_ache(
    source: str,
    content: Dict,
    ache_before: float,
    use_consensus: Optional[bool] = None
) -> Dict:
    """
    Returns:
    {
        'success': bool,
        'scarindex_result': {
            'id': str,
            'scarindex': float,
            'components': {...},
            'ache': {...},
            'is_valid': bool
        },
        'pid_state': {...},
        'panic_frame': {...} | None,
        'coherence_status': str,
        'timestamp': str
    }
    """
```

**Get System Status**:
```python
def get_system_status() -> Dict:
    """
    Returns:
    {
        'system': {...},
        'coherence': {...},
        'pid_controller': {...},
        'panic_frames': {...},
        'transmutations': {...},
        'configuration': {...}
    }
    """
```

**Recover from Panic**:
```python
async def recover_from_panic(panic_frame_id: str) -> Dict:
    """
    Returns:
    {
        'success': bool,
        'panic_frame_id': str,
        'phases_completed': int,
        'actions': List[Dict]
    }
    """
```

## Performance Specifications

### Latency Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| ScarIndex calculation | < 1ms | ~0.5ms |
| PID controller update | < 100μs | ~50μs |
| Database insert | < 50ms | ~20ms |
| Consensus verification | < 5s | ~2-3s |
| Panic Frame trigger | < 100ms | ~50ms |

### Throughput

- **Transmutations/sec**: ~10-20 (without consensus), ~0.3-0.5 (with consensus)
- **Database writes/sec**: ~100-200
- **VaultNode commits/sec**: ~10-20

### Scalability

- **Max concurrent transmutations**: Limited by LLM API rate limits
- **Database capacity**: PostgreSQL standard limits
- **VaultNode chain length**: Unlimited (blockchain-style)

## Security Considerations

### Cryptographic Verification

- **Hash algorithm**: SHA-256
- **Signature format**: `SHA256(provider:instance:hash:timestamp)`
- **Consensus requirement**: M-of-N (default 2-of-3)

### Data Integrity

- **Database constraints**: CHECK constraints on all numeric ranges
- **Trigger validation**: Automatic validation on insert/update
- **Audit trail**: Immutable VaultNode chain

### Access Control

- **Database**: Row-level security (RLS) policies in Supabase
- **API**: Authentication via API keys
- **GitHub**: Repository access controls

## Error Handling

### Error Types

1. **Validation Errors**: Invalid input ranges, constraint violations
2. **Consensus Failures**: Insufficient provider agreement
3. **Panic Frame Triggers**: ScarIndex below threshold
4. **Database Errors**: Connection failures, constraint violations
5. **LLM API Errors**: Rate limits, timeouts, invalid responses

### Recovery Strategies

```python
# Consensus failure
if not consensus_result.achieved:
    # Retry with different providers
    # Or fall back to heuristic analysis
    
# Panic Frame
if panic_triggered:
    # Execute 7-phase recovery
    # Freeze critical operations
    
# Database error
try:
    await db.insert(...)
except Exception as e:
    # Log error
    # Retry with exponential backoff
    # Alert monitoring system
```

## Monitoring and Observability

### Key Metrics

```python
# System health
- current_scarindex
- coherence_status
- active_panic_frames

# Performance
- transmutation_rate
- success_rate
- avg_latency

# PID controller
- error
- integral
- derivative
- guidance_scale

# Consensus
- consensus_rate
- provider_agreement
```

### Logging

```python
# Log levels
DEBUG: Detailed PID calculations
INFO: Transmutation events
WARNING: Approaching panic threshold
ERROR: Consensus failures
CRITICAL: Panic Frame activations
```

## Testing Strategy

### Unit Tests

- ScarIndex calculation accuracy
- PID controller stability
- Panic Frame trigger conditions
- Consensus verification logic

### Integration Tests

- End-to-end transmutation flow
- Database operations
- GitHub integration
- Recovery protocol execution

### Performance Tests

- Latency benchmarks
- Throughput limits
- Concurrent operation handling
- Memory usage profiling

## Deployment

### Requirements

```
Python >= 3.9
PostgreSQL >= 15
Supabase account
GitHub repository access
OpenAI API key
```

### Environment Variables

```bash
OPENAI_API_KEY=sk-...
SUPABASE_PROJECT_ID=...
GITHUB_TOKEN=...
```

### Deployment Steps

1. Set up Supabase project
2. Apply database schema
3. Configure environment variables
4. Install Python dependencies
5. Initialize SpiralOS
6. Run health checks

## Future Enhancements

1. **Multi-region deployment**: Distributed Supabase instances
2. **Advanced consensus**: Byzantine fault tolerance
3. **ML-based tuning**: Auto-tune PID parameters
4. **Real-time dashboard**: Live coherence monitoring
5. **Enhanced GoT**: Full ARIA pipeline implementation

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-30  
**Maintainer**: ZoaGrad

---

**Updated Formula (ΔΩ.125.4.1 - CRITICAL Corrections)**:
ScarIndex = (C_operational × 0.35) + (C_audit × 0.3) + (C_constitutional × 0.25) + (C_symbolic × 0.1)
- Sum: 1.0 (Immutable; F2 Protected).
- Threshold: <0.67 → PanicFrameManager Review (7-Phase Recovery).
- Validation: Oracle Council (4-of-5 Quorum; ≥1 Non-Commercial Provider).
- Ties to Legitimacy Engine: L_final incorporates ScarIndex for C_constitutional ≥0.25.
