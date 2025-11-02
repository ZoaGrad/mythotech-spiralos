# Troubleshooting Guide

This guide helps diagnose and resolve common issues with SpiralOS.

## Table of Contents

- [Comet Gate Failures](#comet-gate-failures)
- [Database Connection Issues](#database-connection-issues)
- [ScarIndex Calculation Errors](#scarindex-calculation-errors)
- [Webhook Processing Problems](#webhook-processing-problems)
- [Panic Frame Triggers](#panic-frame-triggers)
- [Oracle Consensus Failures](#oracle-consensus-failures)
- [VaultNode Integrity Issues](#vaultnode-integrity-issues)

## Comet Gate Failures

### Issue: `db-push` fails with timeout

**Symptoms:**
```
[ERROR] Operation timed out after 30s
[ERROR] Max retries reached. Giving up.
```

**Cause:** Transient Supabase outage or slow network connection.

**Solution:**

1. **Increase timeout and retry settings:**
```bash
export DB_PUSH_TIMEOUT=60
export DB_PUSH_MAX_RETRIES=10
export DB_PUSH_RETRY_DELAY=10
./scripts/db-push.sh
```

2. **Check Supabase status:**
   - Visit https://status.supabase.com/
   - Verify project is online in Supabase dashboard

3. **Verify network connectivity:**
```bash
ping db.${SUPABASE_PROJECT_ID}.supabase.co
```

### Issue: Duplicate key errors in webhook processing

**Symptoms:**
```
Failed to create ache event: duplicate key value violates unique constraint
```

**Cause:** Webhook being processed multiple times (GitHub retry or duplicate events).

**Solution:**

This should be fixed automatically with the idempotent upsert logic. If you still see errors:

1. **Check scar_index table for existing entries:**
```sql
SELECT * FROM scar_index 
WHERE external_id = '<commit_sha_or_issue_id>' 
ORDER BY created_at DESC;
```

2. **If needed, mark as completed manually:**
```sql
UPDATE scar_index 
SET processing_status = 'completed'
WHERE external_id = '<commit_sha_or_issue_id>';
```

3. **Verify the migration was applied:**
```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_name = 'scar_index'
);
```

### Issue: Schema drift - missing columns or tables

**Symptoms:**
```
relation "scar_index" does not exist
column "payload" of relation "github_webhooks" does not exist
```

**Cause:** Migration `20251101_01_comet_gate.sql` not applied.

**Solution:**

1. **Apply the migration:**
```bash
./scripts/db-push.sh supabase/migrations/20251101_01_comet_gate.sql
```

2. **Verify tables exist:**
```sql
\dt public.scar_index
\d public.github_webhooks
\d public.ache_events
```

3. **If migration fails, check logs:**
```bash
cat /tmp/db-push-output.log
```

## Database Connection Issues

### Issue: Cannot connect to Supabase

**Symptoms:**
```
FATAL: password authentication failed for user "postgres"
connection to server failed
```

**Cause:** Invalid credentials or project ID.

**Solution:**

1. **Verify environment variables:**
```bash
echo $SUPABASE_PROJECT_ID
echo $SUPABASE_DB_PASSWORD
```

2. **Get correct password from Supabase dashboard:**
   - Settings → Database → Connection string
   - Copy password from connection string

3. **Test connection:**
```bash
python3 scripts/test_supabase_connection.py
```

### Issue: Row-Level Security (RLS) blocking queries

**Symptoms:**
```
new row violates row-level security policy for table "ache_events"
```

**Cause:** Using wrong authentication role or missing RLS policies.

**Solution:**

1. **Use service role key for backend operations:**
```bash
export SUPABASE_SERVICE_ROLE_KEY="<your-service-role-key>"
```

2. **Verify RLS policies exist:**
```sql
SELECT * FROM pg_policies WHERE tablename = 'ache_events';
```

3. **Temporarily disable RLS for debugging (NOT recommended for production):**
```sql
ALTER TABLE ache_events DISABLE ROW LEVEL SECURITY;
```

## ScarIndex Calculation Errors

### Issue: ScarIndex outside valid range

**Symptoms:**
```
ValueError: ScarIndex must be in range [0, 1]
```

**Cause:** Invalid coherence component values.

**Solution:**

1. **Validate input components:**
```python
# All components must be in [0, 1]
assert 0.0 <= c_narrative <= 1.0
assert 0.0 <= c_social <= 1.0
assert 0.0 <= c_economic <= 1.0
assert 0.0 <= c_technical <= 1.0
```

2. **Check constitutional weights haven't been modified:**
```python
# These are F2-protected and must not change
WEIGHTS = {
    'narrative': 0.4,
    'social': 0.3,
    'economic': 0.2,
    'technical': 0.1
}
```

### Issue: Ache transmutation validation fails

**Symptoms:**
```
Proof-of-Ache validation failed: Ache increased instead of decreased
```

**Cause:** Ache_after >= Ache_before (violates thermodynamic principle).

**Solution:**

This is **expected behavior** for invalid transmutations. The system correctly rejects operations that don't reduce entropy.

1. **Verify Ache calculation logic:**
```python
assert ache_after < ache_before  # Must be true for valid PoA
```

2. **Review coherence improvements** to ensure actual entropy reduction occurred.

## Webhook Processing Problems

### Issue: GitHub webhook not triggering

**Symptoms:**
- Commits/issues created but no Ache events in database

**Cause:** Webhook not configured or incorrect secret.

**Solution:**

1. **Verify webhook configuration in GitHub:**
   - Repository → Settings → Webhooks
   - Payload URL: `https://<project-id>.supabase.co/functions/v1/github-webhook`
   - Content type: `application/json`
   - Events: Push, Issues

2. **Check webhook delivery logs in GitHub:**
   - Click on webhook → Recent Deliveries
   - Look for error responses

3. **Test webhook manually:**
```bash
curl -X POST \
  https://<project-id>.supabase.co/functions/v1/github-webhook \
  -H "Content-Type: application/json" \
  -H "x-github-event: push" \
  -d @test-webhook-payload.json
```

### Issue: Webhook returns 500 error

**Symptoms:**
```json
{
  "success": false,
  "error": "Failed to process webhook"
}
```

**Cause:** Edge function error (check Supabase logs).

**Solution:**

1. **View Edge Function logs:**
   - Supabase Dashboard → Edge Functions → github-webhook → Logs

2. **Common fixes:**
   - Ensure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
   - Verify payload structure matches expected format
   - Check for null/undefined values in payload

## Panic Frame Triggers

### Issue: System frozen due to Panic Frame

**Symptoms:**
```
F4 Panic Frame ACTIVE: ScarIndex below constitutional threshold (0.25 < 0.30)
Operations frozen until coherence restored
```

**Cause:** System coherence dropped below 0.3 threshold.

**Solution:**

This is **designed behavior** (F4 constitutional safeguard).

1. **Review why coherence dropped:**
```sql
SELECT * FROM scarindex_calculations 
WHERE scarindex < 0.3 
ORDER BY created_at DESC 
LIMIT 10;
```

2. **Check active Panic Frames:**
```sql
SELECT * FROM panic_frames 
WHERE is_active = true;
```

3. **Restore coherence through proper Ache transmutation:**
   - Address underlying issues causing low coherence
   - Do NOT attempt to bypass Panic Frame
   - System will auto-recover when ScarIndex > 0.3

## Oracle Consensus Failures

### Issue: Consensus not achieved

**Symptoms:**
```
Oracle consensus failed: Only 1 of 3 signatures received
```

**Cause:** One or more Oracle providers unavailable or disagreeing.

**Solution:**

1. **Check Oracle provider status:**
```python
# Test each provider
providers = ['gpt-4.1-mini', 'gpt-4.1-nano', 'gemini-2.5-flash', 'claude-sonnet-4']
for provider in providers:
    # Attempt connection test
```

2. **Review consensus threshold:**
```python
# Default is 2-of-3
# Ensure at least 2 providers are available
```

3. **Check API keys:**
```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
# Ensure keys are valid and not rate-limited
```

## VaultNode Integrity Issues

### Issue: VaultNode chain verification fails

**Symptoms:**
```
Chain verification failed: Hash mismatch at block N
```

**Cause:** VaultNode chain corruption or tampering.

**Solution:**

1. **Verify chain integrity:**
```python
from holoeconomy.vaultnode import VaultNode

vault = VaultNode()
is_valid = vault.verify_chain()
print(f"Chain valid: {is_valid}")
```

2. **Check for hash mismatches:**
```sql
SELECT 
  block_number,
  state_hash,
  previous_hash
FROM vaultnodes 
ORDER BY block_number;
```

3. **If corruption detected:**
   - Review audit logs to identify when corruption occurred
   - This is a **critical security issue** - do NOT modify VaultNodes
   - Report to maintainers immediately

## General Debugging Tips

### Enable verbose logging

```bash
export SPIRALOS_DEBUG=1
export SPIRALOS_LOG_LEVEL=DEBUG
```

### Check system status

```bash
python3 holoeconomy/summary_cli.py --health
```

### Verify Comet gate flow

```bash
./scripts/verify-comet.sh
```

### Database health check

```sql
-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check recent activity
SELECT 
  'ache_events' as table_name,
  COUNT(*) as count,
  MAX(created_at) as latest
FROM ache_events
UNION ALL
SELECT 
  'scarindex_calculations',
  COUNT(*),
  MAX(created_at)
FROM scarindex_calculations;
```

## Still Having Issues?

1. **Check the documentation:**
   - [README.md](./README.md)
   - [Technical Specification](./docs/TECHNICAL_SPEC.md)
   - [Deployment Guide](./holoeconomy/DEPLOYMENT.md)

2. **Search existing issues:**
   - https://github.com/ZoaGrad/mythotech-spiralos/issues

3. **Open a new issue:**
   - Include error messages
   - Describe steps to reproduce
   - Share relevant logs
   - Mention your environment (OS, Python version, etc.)

---

**Constitutional Note**: All troubleshooting should respect thermodynamic principles and constitutional safeguards. Never bypass security mechanisms or Panic Frames.
