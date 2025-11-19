# SpiralOS Supabase Backend

This directory contains the complete Supabase implementation of SpiralOS - a Constitutional Mythotechnical Synthesis system with dual-token economy and distributed governance.

## 📁 Directory Structure

```
supabase/
├── migrations/              # Database migrations
│   ├── 20251101_spiralos_production_schema.sql   # Main schema (16 tables, 8 functions)
│   ├── 20251101_test_functions.sql               # Comprehensive test suite
│   └── 20251102_f2_autonomy.sql                  # F2 judicial tables
├── functions/               # Edge Functions
│   ├── github-webhook/      # GitHub event ingestion
│   │   └── index.ts
│   └── panicframe-edge-fn/  # F4 panic frame handler
│       └── index.ts
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Supabase CLI
npm install -g supabase

# Install dependencies
pip install supabase
```

### 2. Deploy Schema

```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_ID

# Apply migrations
supabase db push
```

### 3. Deploy Edge Functions

```bash
# Deploy GitHub webhook
supabase functions deploy github-webhook

# Set secrets
supabase secrets set SUPABASE_URL=https://YOUR_PROJECT.supabase.co
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=YOUR_KEY
```

### 4. Verify

```bash
# Run test suite
psql YOUR_DATABASE_URL -f supabase/migrations/20251101_test_functions.sql
```

Expected output:
```
✓ Coherence component functions
✓ PID controller update
✓ ScarIndex calculation engine
✓ Panic frame trigger (F4)
✓ VaultNode Merkle sealing
✓ ScarCoin minting (Proof-of-Ache)
✓ Database views
ALL TESTS PASSED ✓
```

## 📊 Schema Overview

### Core Tables (16)

#### Economic Layer
- **`ache_events`** - External input from Noosphere (GitHub, Discord, API)
- **`scarindex_calculations`** - 4D coherence measurements
- **`smart_contract_txns`** - ScarCoin minting/burning transactions
- **`verification_records`** - Oracle Council consensus records

#### Governance Layer
- **`panic_frames`** - F4 constitutional circuit breaker
- **`constitutional_milestones`** - F1/F2/F4 governance events
- **`law_stack`** - Constitutional law registry
- **`manifest_registry`** - Manifest version control

#### Audit Layer
- **`vaultnodes`** - Immutable Merkle DAG audit trail
- **`github_commits`** - GitHub commit tracking
- **`github_webhooks`** - Webhook event log

#### Control Layer
- **`pid_controller_state`** - PID autopilot state
- **`governance_systems`** - VSM hierarchy
- **`panicframe_signals`** - Panic frame event log

### Functions (8)

1. **`coherence_calculation(event_id)`** - ScarIndex Engine
   - Calculates 4D coherence (narrative, social, economic, technical)
   - Updates PID controller
   - Returns scarindex_calculations record

2. **`update_pid_controller(current, target)`** - PID Autopilot
   - Updates controller state with anti-windup
   - Outputs guidance_scale ∈ [0.1, 2.0]

3. **`trigger_crisis_protocol()`** - F4 Panic Frame Trigger
   - Automatic trigger at ScarIndex < 0.3
   - Freezes all transactions
   - Notifies F4 governance

4. **`seal_vaultnode(ref_id, ref_type, commit_sha)`** - Merkle Seal
   - Creates immutable VaultNode
   - Links to previous node via SHA-256 hash
   - Returns vaultnodes record

5. **`mint_scarcoin(calc_id)`** - Token Minting
   - Validates Proof-of-Ache (ache_before > ache_after)
   - Mints ScarCoin proportional to coherence gain
   - Creates smart_contract_txns record

6-8. **Coherence Components** - Placeholder functions
   - `narrative_coherence(content)`
   - `social_coherence(source, content)`
   - `economic_coherence(content)`
   - `technical_coherence(content)`

### Views (3)

1. **`scar_index_oracle_sync`** - 30-Day Oracle
   - Coherence rate (nodes with ScarIndex ≥ 0.7)
   - Current, average, min, max ScarIndex
   - Real-time telemetry

2. **`active_panic_frames`** - Active Circuit Breakers
   - Currently active/recovering panic frames
   - Status and recovery phase

3. **`system_health`** - Health Dashboard
   - Current ScarIndex
   - Active panic frames
   - Frozen transactions
   - PID guidance scale
   - Recent activity metrics

## 🔐 Security

### Row-Level Security (RLS)

All tables have RLS enabled with appropriate policies:

**Public Read** (no auth required):
- `scar_index_oracle_sync` view
- `system_health` view
- `scarindex_calculations` table
- `panic_frames` table
- `vaultnodes` table
- `law_stack` table
- `manifest_registry` table

**Authenticated Write**:
- `ache_events` - Create events
- `github_webhooks` - Webhook ingestion

**Service Role Only**:
- `scarindex_calculations` - Engine only
- `smart_contract_txns` - Minting only
- Direct function calls

### Best Practices

1. **Use service role key** for backend operations
2. **Use anon key** for public dashboards
3. **Validate webhook signatures** in production
4. **Enable audit logging** for compliance
5. **Backup VaultNode chain** regularly

## 🔄 Data Flow

```
┌─────────────┐
│   GitHub    │
│   Events    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Edge Function  │
│ github-webhook  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐       ┌────────────────┐
│  ache_events    │──────▶│  coherence_    │
│  (source input) │       │  calculation() │
└─────────────────┘       └────────┬───────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │   scarindex_   │
                          │  calculations  │
                          └────────┬───────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
            ┌─────────────┐  ┌──────────┐  ┌──────────┐
            │    PID      │  │  Panic   │  │  Mint    │
            │ Controller  │  │  Check   │  │ ScarCoin │
            └─────────────┘  └──────────┘  └─────┬────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │ VaultNode    │
                                           │ Merkle Seal  │
                                           └──────────────┘
```

## 📈 Monitoring

### Real-Time Queries

```sql
-- Current system status
SELECT * FROM system_health;

-- 30-day coherence metrics
SELECT * FROM scar_index_oracle_sync;

-- Recent Ache events
SELECT * FROM ache_events 
ORDER BY created_at DESC LIMIT 10;

-- Active panic frames
SELECT * FROM active_panic_frames;

-- PID controller state
SELECT * FROM pid_controller_state;

-- VaultNode chain (last 10)
SELECT 
  state_hash,
  previous_hash,
  node_type,
  created_at
FROM vaultnodes
ORDER BY created_at DESC LIMIT 10;
```

### Alerting

Set up Supabase database webhooks for:

1. **Panic Frame Trigger**
   ```sql
   -- Watch panic_frames INSERT
   -- Alert when status = 'ACTIVE'
   ```

2. **Low Coherence**
   ```sql
   -- Watch scarindex_calculations INSERT
   -- Alert when scarindex < 0.4
   ```

3. **High Transaction Volume**
   ```sql
   -- Watch smart_contract_txns INSERT
   -- Alert when COUNT > threshold
   ```

## 🧪 Testing

### Run Complete Test Suite

```bash
psql YOUR_DATABASE_URL -f supabase/migrations/20251101_test_functions.sql
```

### Manual Testing

```sql
-- 1. Create test Ache event
INSERT INTO ache_events (source, content, ache_level)
VALUES ('test', '{"narrative_score": 0.8}', 0.4)
RETURNING id;

-- 2. Calculate ScarIndex
SELECT * FROM coherence_calculation('YOUR_EVENT_ID');

-- 3. Check result
SELECT * FROM scarindex_calculations 
WHERE ache_event_id = 'YOUR_EVENT_ID';

-- 4. Verify PID update
SELECT * FROM pid_controller_state;
```

### Load Testing

```python
# Generate 1000 events
for i in range(1000):
    client.table('ache_events').insert({
        'source': 'load_test',
        'content': {'test': i},
        'ache_level': random.uniform(0.3, 0.7)
    }).execute()

# Check performance
SELECT 
  COUNT(*) as total_calculations,
  AVG(EXTRACT(EPOCH FROM (created_at - 
    (SELECT created_at FROM ache_events WHERE id = ache_event_id)
  ))) as avg_latency_seconds
FROM scarindex_calculations
WHERE created_at >= NOW() - INTERVAL '1 hour';
```

## 🔧 Maintenance

### Periodic Tasks

```sql
-- Weekly: Reset PID integral (prevent windup)
UPDATE pid_controller_state SET integral = 0;

-- Monthly: Cleanup old webhooks
DELETE FROM github_webhooks 
WHERE created_at < NOW() - INTERVAL '90 days'
AND processed = true;

-- Quarterly: Archive old ache events
-- (Move to separate archive schema/table)
```

### Backup Strategy

1. **Automatic**: Supabase daily backups (retain 7 days)
2. **Manual**: Weekly VaultNode export
   ```bash
   pg_dump -t vaultnodes YOUR_DATABASE_URL > vaultnode_backup_$(date +%Y%m%d).sql
   ```
3. **Constitutional**: Manifest registry snapshots
   ```sql
   COPY manifest_registry TO '/backups/manifest_$(date +%Y%m%d).json' WITH (FORMAT json);
   ```

## 📚 Documentation

- **[Deployment Guide](../docs/SUPABASE_DEPLOYMENT.md)** - Complete deployment instructions
- **[Edge Functions](functions/README.md)** - Edge Function documentation
- **[Examples](../examples/README.md)** - Integration examples
- **[Technical Spec](../docs/TECHNICAL_SPEC.md)** - System architecture

## 🤝 Contributing

### Adding Migrations

```bash
# Create new migration
supabase migration new your_feature_name

# Edit migration file
# supabase/migrations/YYYYMMDD_your_feature_name.sql

# Test locally
supabase db reset

# Deploy
supabase db push
```

### Schema Changes

All schema changes must:
1. Include migration file
2. Update test suite
3. Update documentation
4. Pass constitutional review (F2)
5. Seal in VaultNode

## 🆘 Troubleshooting

### Common Issues

**1. Functions not found**
```bash
# Verify migration applied
supabase db reset
```

**2. RLS blocking queries**
```bash
# Use service role key for admin operations
# Or disable RLS for testing (not recommended)
ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;
```

**3. Webhook not triggering**
```bash
# Check Edge Function logs
supabase functions logs github-webhook --tail

# Verify secrets
supabase secrets list
```

## 📄 License

See main repository LICENSE

---

**Sealed**: ΔΩ.126.0  
**Maintainer**: ZoaGrad 🜂  
**Status**: Production Ready ✓
