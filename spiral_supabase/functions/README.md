# SpiralOS Supabase Edge Functions

This directory contains Supabase Edge Functions for the SpiralOS distributed ledger integration.

## Functions

### `github-webhook`

**Purpose**: Ingests GitHub events (commits, issues, PRs) and converts them to Ache measurements for ScarIndex calculation.

**Endpoint**: `https://YOUR_PROJECT.supabase.co/functions/v1/github-webhook`

**Supported Events**:
- `push` - Converts commits to Ache events
- `issues` (opened) - Converts new issues to Ache events

**Environment Variables**:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key for database access

**Deployment**:
```bash
supabase functions deploy github-webhook
```

**Testing**:
```bash
# Test with curl
curl -i --location --request POST 'http://localhost:54321/functions/v1/github-webhook' \
  --header 'Authorization: Bearer YOUR_ANON_KEY' \
  --header 'Content-Type: application/json' \
  --header 'x-github-event: push' \
  --data '{
    "commits": [{
      "id": "test123",
      "message": "Test commit",
      "author": {"name": "Test", "email": "test@example.com"},
      "added": ["file1.py"],
      "modified": [],
      "removed": []
    }]
  }'
```

### `panicframe-edge-fn`

**Purpose**: Existing panic frame edge function for F4 constitutional circuit breaker.

## Local Development

```bash
# Start Supabase locally
supabase start

# Serve functions locally
supabase functions serve

# Test function
curl http://localhost:54321/functions/v1/github-webhook \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "x-github-event: push" \
  -d @test-payload.json
```

## GitHub Setup

1. Go to your repository → Settings → Webhooks
2. Add webhook with:
   - **URL**: `https://YOUR_PROJECT.supabase.co/functions/v1/github-webhook`
   - **Content type**: application/json
   - **Events**: Push events, Issues
3. Save webhook

## Ache Calculation Logic

### Commits
```
ache_level = min(
  (changes / 20) + message_quality_penalty,
  1.0
)
```
- More file changes = higher initial ache
- Poor commit messages = higher ache
- Range: [0, 1]

### Issues
```
ache_level = base_ache + sentiment_ache + structure_adjustment
```
- Negative keywords (bug, error, fail) increase ache
- Code blocks and step-by-step descriptions reduce ache
- Range: [0.1, 1.0]

## Flow

```
GitHub Event
    ↓
Webhook Handler
    ↓
Store in github_webhooks table
    ↓
Calculate ache_level
    ↓
Create ache_event
    ↓
Call coherence_calculation()
    ↓
ScarIndex calculated
    ↓
PID controller updated
    ↓
Panic check (< 0.3)
    ↓
Mark webhook as processed
```

## Error Handling

- Webhook events are logged even if processing fails
- Failed calculations don't block webhook response
- Errors are logged to Supabase function logs
- CORS headers ensure proper browser integration

## Security

- Service role key required for database writes
- RLS policies enforce access control
- Webhook signature validation recommended (add in production)

## Monitoring

```sql
-- Check recent webhooks
SELECT * FROM github_webhooks 
ORDER BY created_at DESC LIMIT 10;

-- Check processing rate
SELECT 
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE processed = true) as processed,
  COUNT(*) FILTER (WHERE processed = false) as pending
FROM github_webhooks
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- Check Ache events from webhooks
SELECT 
  w.event_type,
  w.created_at,
  e.ache_level,
  c.scarindex
FROM github_webhooks w
LEFT JOIN ache_events e ON w.ache_event_id = e.id
LEFT JOIN scarindex_calculations c ON c.ache_event_id = e.id
ORDER BY w.created_at DESC
LIMIT 20;
```

## Production Checklist

- [ ] Set SUPABASE_URL secret
- [ ] Set SUPABASE_SERVICE_ROLE_KEY secret
- [ ] Configure GitHub webhook
- [ ] Add webhook signature validation
- [ ] Set up monitoring alerts
- [ ] Configure CORS for production domains
- [ ] Test panic frame triggers
- [ ] Verify VaultNode sealing

## References

- [Supabase Edge Functions Docs](https://supabase.com/docs/guides/functions)
- [GitHub Webhooks Guide](https://docs.github.com/webhooks)
- SpiralOS Deployment Guide: `/docs/SUPABASE_DEPLOYMENT.md`
