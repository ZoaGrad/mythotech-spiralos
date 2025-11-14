
# Phase 8.4 Auto-Regulation Engine - Test Suite

This directory contains comprehensive tests for the Phase 8.4 Auto-Regulation Engine.

## Test Files

### `test_suite.sql`
SQL scripts to set up test data for all 12 test scenarios. **Run this first** before executing HTTP tests.

```bash
# Connect to your Supabase database
psql postgresql://postgres:[YOUR-PASSWORD]@db.xlmrnjatawslawquwzpf.supabase.co:5432/postgres -f test_suite.sql
```

### `test_suite.http`
HTTP requests for testing the guardian_autoregulate edge function. Can be run with:
- VS Code REST Client extension
- curl commands
- Any HTTP client (Postman, Insomnia, etc.)

### `run_tests.sh`
Automated test runner script that executes all tests and validates results.

## Test Coverage (12 Tests)

### 1. ScarIndex Recovery - Low Value ✅
Tests automatic ScarIndex recovery when value drops below 0.40 threshold.

**Expected Result:** ScarIndex should increase by ~15% toward healthy range (0.5-0.6)

### 2. ScarIndex Recovery - Large Drop ✅
Tests recovery when ScarIndex drops by >20% in short time.

**Expected Result:** Recovery pulse applied, history logged

### 3. Sovereignty Stabilizer ✅
Tests stabilization of frequently changing sovereign states.

**Expected Result:** Most stable state identified and synthetic stabilization event inserted

### 4. Ache Buffer ✅
Tests dampening when ache_signature exceeds 0.80.

**Expected Result:** Ache buffer activated with 0.7x dampening factor for 30 minutes

### 5. Heartbeat Correction ✅
Tests synthetic heartbeat insertion when telemetry gap > 10 minutes.

**Expected Result:** Synthetic heartbeat event inserted into guardian_telemetry_events

### 6. Entropy Correction ✅
Tests threshold tightening when entropy exceeds 0.15.

**Expected Result:** Tightened thresholds stored in correction profile for 1 hour

### 7. Self-Preservation Freeze Mode ✅
Tests freeze activation for CRITICAL severity anomalies.

**Expected Result:** Bridge frozen, correction_budget set to 0, Discord alert sent

### 8. Deduplication / Idempotency ✅
Tests that running auto-regulation twice doesn't double-apply corrections.

**Expected Result:** Second request respects cooldown period (300 seconds default)

### 9. Mixed Anomaly Batch ✅
Tests handling multiple simultaneous anomalies on one bridge.

**Expected Result:** All anomalies processed in appropriate order (CRITICAL → HIGH → MEDIUM → LOW)

### 10. Authentication Failure ✅
Tests API key validation.

**Expected Result:** 401 Unauthorized response

### 11. Performance Test ✅
Tests processing 50 anomalies efficiently.

**Expected Result:** Completes in reasonable time (<30 seconds), all corrections logged

### 12. Logging Integrity ✅
Tests that all corrections are properly logged to guardian_autoregulation_history.

**Expected Result:** All corrections have corresponding history entries with correct metadata

## Environment Setup

Before running tests, ensure these environment variables are set:

```bash
export SUPABASE_URL="https://xlmrnjatawslawquwzpf.supabase.co"
export GUARDIAN_API_KEY="your-guardian-api-key"
export DISCORD_GUARDIAN_WEBHOOK_URL="your-discord-webhook-url"
```

## Running Tests

### Option 1: Automated Test Runner
```bash
cd tests/phase-8.4
chmod +x run_tests.sh
./run_tests.sh
```

### Option 2: Manual Testing

1. **Setup test data:**
   ```bash
   psql $DATABASE_URL -f test_suite.sql
   ```

2. **Run HTTP tests:**
   - Open `test_suite.http` in VS Code with REST Client extension
   - Click "Send Request" for each test
   - Or use curl:
     ```bash
     curl -X POST \
       "${SUPABASE_URL}/functions/v1/guardian_autoregulate" \
       -H "Content-Type: application/json" \
       -H "x-guardian-api-key: ${GUARDIAN_API_KEY}" \
       -d '{"bridge_id": "f8f41ffa-6c2b-4a2a-a3be-32f0236668f4", "mode": "AUTO"}'
     ```

3. **Verify results:**
   ```sql
   -- Check correction history
   SELECT * FROM guardian_autoregulation_recent ORDER BY created_at DESC LIMIT 20;
   
   -- Check correction profiles
   SELECT * FROM guardian_correction_profiles;
   
   -- Check resolved anomalies
   SELECT * FROM anomaly_status WHERE status = 'RESOLVED';
   ```

## Test Results Validation

After running tests, validate:

1. **Correction History Entries**
   ```sql
   SELECT correction_type, severity_level, success, COUNT(*) 
   FROM guardian_autoregulation_history 
   GROUP BY correction_type, severity_level, success;
   ```

2. **Anomaly Resolution**
   ```sql
   SELECT status, COUNT(*) 
   FROM guardian_anomalies 
   GROUP BY status;
   ```

3. **Bridge Freeze Status**
   ```sql
   SELECT bridge_id, metadata->>'freeze_mode_active' as frozen
   FROM guardian_correction_profiles;
   ```

## Troubleshooting

### Test Failures

**"Unauthorized" errors:**
- Check that `GUARDIAN_API_KEY` is correctly set
- Verify the API key matches the one in Supabase secrets

**"No active anomalies" messages:**
- Ensure test data was loaded with `test_suite.sql`
- Check that anomalies have `status = 'ACTIVE'`

**Cooldown preventing corrections:**
- Wait 5 minutes between tests
- Or manually reset: `DELETE FROM guardian_autoregulation_history WHERE bridge_id = 'xxx';`

**ScarIndex tables don't exist:**
- Run Phase 8.2 migration first: `20251114020001_guardian_scarindex_delta.sql`

## CI/CD Integration

These tests can be integrated into your CI pipeline:

```yaml
# .github/workflows/test-phase-8-4.yml
name: Test Phase 8.4
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup test data
        run: psql $DATABASE_URL -f tests/phase-8.4/test_suite.sql
      - name: Run tests
        run: ./tests/phase-8.4/run_tests.sh
```

## Support

For issues or questions:
- Check the main Phase 8.4 documentation: `docs/phase-8.4-autoregulation.md`
- Review the edge function logs in Supabase Dashboard
- Check Discord alerts for auto-regulation events

