# Guardian Sync Edge Function

Real-time health monitoring endpoint for Spiralos Guardian system.

## Purpose

This Edge Function aggregates key metrics from your Spiralos instance and provides a single endpoint for health monitoring.

## Metrics Provided

- **VaultNodes**: Total count of vault nodes
- **AcheEvents**: Recent ache events in lookback window
- **ScarIndex (avg)**: Average ScarIndex in lookback period
- **ScarIndex (latest)**: Most recent ScarIndex value
- **Alerts (24h)**: Count of guardian alerts in last 24 hours

## API Endpoint

```
GET /functions/v1/guardian_sync?hours=24
```

### Query Parameters

- `hours` (optional): Lookback window in hours (default: 24)

### Response Format

```json
{
  "timestamp": "2025-11-10T16:45:00.000Z",
  "window_hours": 24,
  "metrics": [
    {"label": "VaultNodes", "value": 42},
    {"label": "AcheEvents(lookback)", "value": 156},
    {"label": "ScarIndex(avg)", "value": 0.876},
    {"label": "ScarIndex(latest)", "value": 0.912},
    {"label": "Alerts(24h)", "value": 3}
  ],
  "scar_status": "🟢",
  "scar_score": 0.912
}
```

### Status Indicators

- 🟠 **Hot/High**: ScarIndex ≥ 1.4
- 🟢 **Healthy**: ScarIndex 0.6 - 1.4
- 🔴 **Low/Unstable**: ScarIndex < 0.6

## Deployment

### Using Supabase CLI

```bash
supabase functions deploy guardian_sync --no-verify-jwt
```

### Environment Variables Required

The function requires these Supabase project environment variables:
- `SUPABASE_URL`: Automatically provided by Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Automatically provided by Supabase

## Dependencies

- `@supabase/functions@^2.4.1`: Edge runtime definitions
- `raw_sql` database function: See `supabase/migrations/20251110_guardian_sql_runner.sql`

## Usage Examples

### Basic Health Check

```bash
curl "https://your-project.supabase.co/functions/v1/guardian_sync?hours=24"
```

### Extended Lookback

```bash
curl "https://your-project.supabase.co/functions/v1/guardian_sync?hours=72"
```

### In GitHub Actions

```yaml
- name: Check Guardian Status
  run: |
    curl "${{ secrets.GUARDIAN_EDGE_URL }}?hours=24"
```

### In Discord Webhook

```bash
STATUS=$(curl -s "$GUARDIAN_EDGE_URL?hours=24")
curl -X POST "$DISCORD_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"embeds\": [{\"title\": \"Guardian Status\", \"description\": \"\`\`\`json\n$STATUS\n\`\`\`\"}]}"
```

## Security

- Uses service role key (not publicly accessible without auth)
- SQL queries are read-only via `raw_sql` function
- No user input directly in SQL (parameterized via function)

## Testing

```bash
# Test locally (requires supabase local setup)
supabase functions serve guardian_sync

# Test in another terminal
curl "http://localhost:54321/functions/v1/guardian_sync?hours=24"
```

## Troubleshooting

### Function returns 500

Check that the `raw_sql` function exists:
```sql
SELECT raw_sql('SELECT 1');
```

### Empty metrics

Verify database tables exist:
```sql
SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'vault_nodes');
SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ache_events');
SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'scarindex_calculations');
SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'guardian_alerts');
```

### Check logs

```bash
supabase functions logs guardian_sync --tail
```

## Updates

To update this function:

1. Modify `core/guardian/edge/guardian_sync.ts`
2. Copy to `supabase/functions/guardian_sync/index.ts`
3. Deploy: `supabase functions deploy guardian_sync`

Or use the automated deployment script: `./deploy_guardian.sh`
