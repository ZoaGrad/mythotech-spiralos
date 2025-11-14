
# Phase 8.4 Quick Start Guide

Get the Auto-Regulation Engine up and running in 5 minutes.

## 🚀 Quick Deployment

### 1. Run Migrations (2 minutes)

```bash
# Set database connection
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xlmrnjatawslawquwzpf.supabase.co:5432/postgres"

# Run all migrations
psql $DATABASE_URL -f supabase/migrations/20251114020001_guardian_scarindex_delta.sql
psql $DATABASE_URL -f supabase/migrations/20251114025000_guardian_anomaly_detection.sql
psql $DATABASE_URL -f supabase/migrations/20251114030000_guardian_autoregulation.sql
```

### 2. Deploy Functions (1 minute)

```bash
supabase functions deploy guardian_autoregulate
supabase functions deploy guardian_anomaly_monitor
supabase functions deploy telemetry_normalize
```

### 3. Initialize Profiles (30 seconds)

```sql
INSERT INTO guardian_correction_profiles (bridge_id, baseline_health, preferred_correction_types)
SELECT id, 0.8, ARRAY['HEARTBEAT_CORRECTION', 'ACHE_BUFFER', 'SCARINDEX_RECOVERY_PULSE']
FROM bridge_nodes WHERE is_active = true;
```

### 4. Test It (1 minute)

```bash
curl -X POST "${SUPABASE_URL}/functions/v1/guardian_autoregulate" \
  -H "x-guardian-api-key: ${GUARDIAN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"bridge_id": "f8f41ffa-6c2b-4a2a-a3be-32f0236668f4", "mode": "MANUAL"}'
```

**Expected:** 200 OK with corrections summary

✅ **Done!** Auto-regulation is now active.

---

## 📖 Common Operations

### Trigger Auto-Regulation

```bash
# For specific bridge
curl -X POST "${SUPABASE_URL}/functions/v1/guardian_autoregulate" \
  -H "x-guardian-api-key: ${GUARDIAN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"bridge_id": "BRIDGE_ID", "mode": "AUTO"}'

# For specific anomaly
curl -X POST "${SUPABASE_URL}/functions/v1/guardian_autoregulate" \
  -H "x-guardian-api-key: ${GUARDIAN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"anomaly_id": "ANOMALY_ID"}'
```

### View Recent Corrections

```sql
SELECT * FROM guardian_autoregulation_recent LIMIT 10;
```

### Check Bridge Health

```sql
SELECT 
  bridge_id,
  baseline_health,
  correction_budget,
  metadata->>'freeze_mode_active' as frozen
FROM guardian_correction_profiles;
```

### View Active Anomalies

```sql
SELECT * FROM anomaly_status WHERE status = 'ACTIVE';
```

---

## 🔧 Healing Strategies

| Strategy | Trigger | Action |
|----------|---------|--------|
| **ScarIndex Recovery** | ScarIndex < 0.40 or drop > 20% | Increase ScarIndex by 15% |
| **Sovereignty Stabilizer** | >3 state changes/hour | Pin to most stable state |
| **Ache Buffering** | Ache > 0.80 or delta > 0.25 | Apply 0.7x dampening for 30min |
| **Heartbeat Correction** | Gap > 10 minutes | Insert synthetic heartbeat |
| **Entropy Correction** | Entropy > 0.15 | Tighten thresholds for 1 hour |
| **Freeze Mode** | CRITICAL anomaly | Freeze bridge for 30 minutes |

---

## 🐛 Troubleshooting

### No Corrections Happening

**Check cooldown:**
```sql
SELECT bridge_id, MAX(created_at) as last_correction
FROM guardian_autoregulation_history
GROUP BY bridge_id;
```

**Reset cooldown (if needed):**
```sql
DELETE FROM guardian_autoregulation_history
WHERE bridge_id = 'BRIDGE_ID' 
  AND created_at > NOW() - INTERVAL '10 minutes';
```

### Bridge Frozen

**Check freeze status:**
```sql
SELECT bridge_id, metadata->>'freeze_mode_active'
FROM guardian_correction_profiles;
```

**Unfreeze (manual override):**
```sql
UPDATE guardian_correction_profiles
SET metadata = jsonb_set(metadata, '{freeze_mode_active}', 'false'),
    correction_budget = 100
WHERE bridge_id = 'BRIDGE_ID';
```

### Budget Exhausted

**Check budget:**
```sql
SELECT bridge_id, correction_budget
FROM guardian_correction_profiles;
```

**Reset budget:**
```sql
UPDATE guardian_correction_profiles
SET correction_budget = 100
WHERE correction_budget <= 10;
```

---

## 📊 Monitoring

### Real-time Corrections

```sql
-- Watch corrections in real-time
SELECT * FROM guardian_autoregulation_recent
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

### Success Rate

```sql
SELECT 
  correction_type,
  COUNT(*) as total,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
  ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM guardian_autoregulation_history
GROUP BY correction_type;
```

### Bridge Health Dashboard

```sql
SELECT 
  p.bridge_id,
  b.node_name,
  p.baseline_health,
  p.correction_budget,
  COUNT(h.id) as corrections_today
FROM guardian_correction_profiles p
LEFT JOIN bridge_nodes b ON p.bridge_id = b.id
LEFT JOIN guardian_autoregulation_history h 
  ON p.bridge_id = h.bridge_id 
  AND h.created_at > NOW() - INTERVAL '24 hours'
GROUP BY p.bridge_id, b.node_name, p.baseline_health, p.correction_budget;
```

---

## 🧪 Testing

### Run Test Suite

```bash
cd tests/phase-8.4
./run_tests.sh
```

### Manual Test Scenarios

**Test ScarIndex Recovery:**
```sql
-- Create low ScarIndex anomaly
INSERT INTO guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES ('BRIDGE_ID', 'SCARINDEX_DROP', 'HIGH', 'ACTIVE', '{"value": 0.30}');

-- Trigger correction
curl -X POST "${SUPABASE_URL}/functions/v1/guardian_autoregulate" \
  -H "x-guardian-api-key: ${GUARDIAN_API_KEY}" \
  -d '{"bridge_id": "BRIDGE_ID", "mode": "AUTO"}'

-- Verify
SELECT * FROM guardian_autoregulation_recent WHERE bridge_id = 'BRIDGE_ID';
```

---

## 📚 Documentation

- **Full Docs:** [docs/phase-8.4-autoregulation.md](docs/phase-8.4-autoregulation.md)
- **Changes:** [PHASE_8.4_CHANGES.md](PHASE_8.4_CHANGES.md)
- **Tests:** [tests/phase-8.4/README.md](tests/phase-8.4/README.md)

---

## 🎯 Key Endpoints

### guardian_autoregulate
```
POST /functions/v1/guardian_autoregulate
Header: x-guardian-api-key: YOUR_KEY
Body: {"bridge_id": "uuid", "mode": "AUTO"}
```

### guardian_anomaly_monitor
```
POST /functions/v1/guardian_anomaly_monitor
Header: x-guardian-api-key: YOUR_KEY
Body: {"bridge_id": "uuid"} or {"scan_all": true}
```

---

## 🔑 Environment Variables

```bash
GUARDIAN_API_KEY=<your-secret-key>
DISCORD_GUARDIAN_WEBHOOK_URL=<your-discord-webhook-url>
SUPABASE_URL=https://xlmrnjatawslawquwzpf.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

---

## 🎉 Success Indicators

After deployment, you should see:

✅ Anomalies automatically resolved  
✅ Discord notifications for corrections  
✅ ScarIndex recovering from drops  
✅ Synthetic heartbeats filling gaps  
✅ Freeze mode activating for CRITICAL issues

---

## 🆘 Support

**Issues?**
1. Check logs: `supabase functions logs guardian_autoregulate --tail`
2. Review: [Troubleshooting Guide](docs/phase-8.4-autoregulation.md#troubleshooting)
3. Discord: Guardian webhook channel
4. GitHub: Create an issue

---

**Version:** 1.0.0  
**Last Updated:** November 14, 2024

**Next:** [Full Documentation →](docs/phase-8.4-autoregulation.md)
