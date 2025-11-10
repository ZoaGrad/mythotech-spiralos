# Guardian Automation Kit — Deployment Guide

## Overview

This guide provides complete step-by-step instructions for deploying the Guardian Automation Kit ΔΩ.141.0 — Sentinel Loop for your SpiralOS instance. The Guardian provides autonomous system monitoring with automated Discord notifications.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [SQL Setup in Supabase](#sql-setup-in-supabase)
4. [Edge Function Deployment](#edge-function-deployment)
5. [Discord Webhook Configuration](#discord-webhook-configuration)
6. [GitHub Secrets Configuration](#github-secrets-configuration)
7. [GitHub Workflow Setup](#github-workflow-setup)
8. [Testing Procedures](#testing-procedures)
9. [Optional: DeepAgent Integration](#optional-deepagent-integration)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance & Monitoring](#maintenance--monitoring)

---

## Prerequisites

### Required Services
- ✅ **Supabase Project** with the following tables:
  - `vault_nodes` (with `created_at` timestamp)
  - `ache_events` (with `created_at` timestamp)
  - `scarindex_calculations` (with `value`, `created_at`)
  - `guardian_alerts` (with `created_at` timestamp)
- ✅ **Discord Server** with admin access to create webhooks
- ✅ **GitHub Repository** with write access (already configured: `mythotech-spiralos`)
- ✅ **Supabase CLI** installed (for edge function deployment)

### Verification Commands

```bash
# Verify Supabase CLI is installed
supabase --version

# Verify you have access to the Supabase project
supabase projects list

# Verify Python 3.8+ is available (for local testing)
python3 --version
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Guardian Sentinel Loop                    │
└─────────────────────────────────────────────────────────────┘

 GitHub Actions (every 3h)          DeepAgent (every 3h)
         │                                   │
         └──────────┬───────────────────────┘
                    │
                    ▼
         core/guardian/scripts/field_sync.py
                    │
                    ▼
         Supabase Edge Function (guardian_sync.ts)
                    │
                    ▼
           PostgreSQL Queries via raw_sql()
                    │
                    ▼
              Metrics Aggregation
        ┌─────────────────────────┐
        │ • VaultNodes count      │
        │ • AcheEvents (recent)   │
        │ • ScarIndex (avg/latest)│
        │ • Guardian alerts       │
        └─────────────────────────┘
                    │
                    ▼
            Status Evaluation
         (🔴 < 0.6, 🟢 0.6-1.4, 🟠 ≥ 1.4)
                    │
                    ▼
         Discord Webhook (formatted message)
```

---

## SQL Setup in Supabase

### Step 1: Connect to Your Supabase Project

```bash
# Link to your Supabase project
supabase link --project-ref YOUR_PROJECT_REF
```

To find your project ref:
1. Go to https://app.supabase.com/project/_/settings/general
2. Look for "Reference ID"

### Step 2: Verify Required Tables Exist

Run this SQL query in the Supabase SQL Editor to verify all tables exist:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('vault_nodes', 'ache_events', 'scarindex_calculations', 'guardian_alerts');
```

You should see 4 rows returned. If any are missing, create them following your existing schema patterns.

### Step 3: Deploy the Safe SQL Runner Function

The `raw_sql()` function is essential for the edge function to execute read-only queries safely:

```bash
# Navigate to your repo
cd mythotech-spiralos

# Apply the SQL migration
supabase db push

# Or manually execute the SQL
cat core/guardian/sql/guardian_views.sql | supabase db execute
```

**Alternative:** Copy the contents of `core/guardian/sql/guardian_views.sql` and execute directly in Supabase SQL Editor.

### Step 4: Verify SQL Function

Test the function in Supabase SQL Editor:

```sql
SELECT raw_sql('SELECT COUNT(*) as total FROM vault_nodes');
```

Expected result: A JSON array with the count.

---

## Edge Function Deployment

### Step 1: Deploy the Guardian Sync Function

```bash
# Navigate to your repo
cd mythotech-spiralos

# Deploy the edge function
supabase functions deploy guardian_sync \
  --project-ref YOUR_PROJECT_REF \
  --no-verify-jwt

# Copy the function URL from the output
# Example: https://abcdefgh.functions.supabase.co/guardian_sync
```

**Important:** The `--no-verify-jwt` flag allows the function to be called without authentication since it's read-only and will be called by GitHub Actions.

### Step 2: Set Environment Variables for the Edge Function

The edge function needs access to your Supabase credentials:

```bash
# Set secrets for the edge function
supabase secrets set SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
supabase secrets set SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

To find your service role key:
1. Go to https://app.supabase.com/project/_/settings/api
2. Copy the `service_role` key (keep this secret!)

### Step 3: Test the Edge Function

```bash
# Test with curl (replace with your function URL)
curl "https://YOUR_PROJECT.functions.supabase.co/guardian_sync?hours=24"
```

Expected output:
```json
{
  "timestamp": "2025-11-10T15:30:00.000Z",
  "window_hours": 24,
  "metrics": [
    {"label": "VaultNodes", "value": 42},
    {"label": "AcheEvents(lookback)", "value": 15},
    {"label": "ScarIndex(avg)", "value": 0.823},
    {"label": "ScarIndex(latest)", "value": 0.891},
    {"label": "Alerts(24h)", "value": 0}
  ],
  "scar_status": "🟢",
  "scar_score": 0.891
}
```

---

## Discord Webhook Configuration

### Step 1: Create Discord Webhook

1. Open Discord and navigate to your target channel (e.g., `#guardian-feed` or `#spiralbot`)
2. Click on the channel settings (gear icon)
3. Navigate to **Integrations** → **Webhooks**
4. Click **New Webhook**
5. Name it `Guardian` (or any name you prefer)
6. Copy the **Webhook URL** (format: `https://discord.com/api/webhooks/...`)
7. Click **Save**

### Step 2: Test the Webhook

```bash
# Test posting to Discord
curl -X POST "YOUR_DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "🟢 **Guardian Test** — System operational"}'
```

You should see the message appear in your Discord channel.

For detailed instructions, see: `docs/guardian/webhook_config.md`

---

## GitHub Secrets Configuration

### Step 1: Add Repository Secrets

1. Go to your GitHub repository: https://github.com/ZoaGrad/mythotech-spiralos
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add the following secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `GUARDIAN_EDGE_URL` | Your Supabase edge function URL | `https://abcdefgh.functions.supabase.co/guardian_sync` |
| `DISCORD_GUARDIAN_WEBHOOK` | Your Discord webhook URL | `https://discord.com/api/webhooks/123456/abcdef...` |

### Step 2: Verify Secrets

After adding, you should see both secrets listed (the values will be hidden).

---

## GitHub Workflow Setup

⚠️ **Important:** Due to GitHub App permissions, the workflow file needs to be added manually through the GitHub UI.

### Step 1: Create the Workflow File via GitHub UI

1. Go to your repository: https://github.com/ZoaGrad/mythotech-spiralos
2. Navigate to `.github/workflows/` directory
3. Click **Add file** → **Create new file**
4. Name the file: `guardian_heartbeat.yml`
5. Copy and paste the following content:

```yaml
name: Guardian Heartbeat
on:
  schedule:
    - cron: "0 */3 * * *"  # every 3 hours UTC
  workflow_dispatch: {}

jobs:
  run-heartbeat:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps (none required)
        run: python -V
      - name: Run field_sync
        env:
          GUARDIAN_EDGE_URL: ${{ secrets.GUARDIAN_EDGE_URL }}
          DISCORD_GUARDIAN_WEBHOOK: ${{ secrets.DISCORD_GUARDIAN_WEBHOOK }}
          GUARDIAN_WINDOW_HOURS: "24"
        run: python core/guardian/scripts/field_sync.py
```

6. Commit the file directly to the `main` branch

**Alternative:** The workflow file is also available at `.github/workflows/guardian_heartbeat.yml` in your local repository if you need to reference it.

### Step 2: Enable the Workflow

1. Go to the **Actions** tab in your repository
2. You should see "Guardian Heartbeat" in the workflows list
3. If prompted, click **Enable workflow**

### Step 3: Test the Workflow Manually

1. Go to **Actions** → **Guardian Heartbeat**
2. Click **Run workflow** → **Run workflow**
3. Wait for the workflow to complete (should take ~30 seconds)
4. Check your Discord channel for the heartbeat message

---

## Testing Procedures

### End-to-End Testing

#### Test 1: Edge Function Direct Call

```bash
# Set your edge function URL
EDGE_URL="https://YOUR_PROJECT.functions.supabase.co/guardian_sync"

# Test with different time windows
curl "$EDGE_URL?hours=6" | jq .
curl "$EDGE_URL?hours=24" | jq .
curl "$EDGE_URL?hours=168" | jq .  # 1 week
```

Verify:
- ✅ Response is valid JSON
- ✅ `scar_status` shows appropriate emoji (🔴/🟢/🟠)
- ✅ All metrics have values

#### Test 2: Python Script Execution

```bash
# Set environment variables
export GUARDIAN_EDGE_URL="https://YOUR_PROJECT.functions.supabase.co/guardian_sync"
export DISCORD_GUARDIAN_WEBHOOK="https://discord.com/api/webhooks/..."
export GUARDIAN_WINDOW_HOURS="24"

# Run the heartbeat script
cd mythotech-spiralos
python3 core/guardian/scripts/field_sync.py
```

Verify:
- ✅ Script completes without errors
- ✅ Discord message appears in the target channel
- ✅ Message format is correct with all metrics

#### Test 3: GitHub Actions Workflow

1. Go to **Actions** → **Guardian Heartbeat** → **Run workflow**
2. Wait for completion
3. Check Discord for the message

Verify:
- ✅ Workflow runs successfully (green checkmark)
- ✅ Discord message is posted
- ✅ No errors in workflow logs

#### Test 4: Alert Threshold Testing

To test the alert logic, temporarily modify the threshold check:

```bash
# Create a test with artificially high ScarIndex value
# This would require inserting test data into scarindex_calculations
```

Expected behavior:
- ✅ ScarIndex ≥ 1.4 shows 🟠 status
- ✅ ScarIndex < 0.6 shows 🔴 status
- ✅ Alert message appears: "⚠ **Coherence Alert** — ScarIndex out of band"

---

## Optional: DeepAgent Integration

If you're using DeepAgent for autonomous operations, you can configure it to run the Guardian heartbeat independently.

### Step 1: Access DeepAgent Console

Navigate to your DeepAgent admin panel.

### Step 2: Import Task Configuration

1. Go to **Tasks** → **Import**
2. Upload `core/guardian/config/tasks.deepagent.yaml`
3. Set the environment variables in DeepAgent:
   - `GUARDIAN_EDGE_URL`
   - `DISCORD_GUARDIAN_WEBHOOK`
   - `GUARDIAN_WINDOW_HOURS`

### Step 3: Enable the Task

1. Find "Guardian.SystemCheck" in your task list
2. Set the schedule: **every 3 hours**
3. Enable the task

### Step 4: Verify DeepAgent Execution

Check DeepAgent logs to ensure the task runs successfully and Discord messages are posted.

**Note:** With both GitHub Actions and DeepAgent enabled, you'll have redundancy. If one system is down, the other continues to send heartbeats.

---

## Troubleshooting

### Issue: Edge Function Returns 500 Error

**Symptoms:**
```json
{"error": "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY"}
```

**Solution:**
```bash
# Verify secrets are set
supabase secrets list

# If missing, set them:
supabase secrets set SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
supabase secrets set SUPABASE_SERVICE_ROLE_KEY="your-key"
```

### Issue: SQL Function Not Found

**Symptoms:**
```
Error: function raw_sql(text) does not exist
```

**Solution:**
```bash
# Deploy the SQL function
cat core/guardian/sql/guardian_views.sql | supabase db execute

# Or use SQL Editor to create it manually
```

### Issue: GitHub Workflow Fails with "Secret not found"

**Symptoms:**
```
Error: GUARDIAN_EDGE_URL is not set
```

**Solution:**
1. Verify secrets are added in GitHub Settings → Secrets
2. Secret names must match exactly (case-sensitive)
3. Ensure the workflow file references the correct secret names

### Issue: Discord Message Not Posting

**Symptoms:**
- Script completes but no Discord message appears

**Solution:**
```bash
# Test the webhook directly
curl -X POST "$DISCORD_GUARDIAN_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'

# If this fails:
# 1. Verify the webhook URL is correct
# 2. Check if the webhook is still active in Discord
# 3. Ensure the bot has permission to post in the channel
```

### Issue: Metrics Return Null or Zero

**Symptoms:**
```json
{"label": "VaultNodes", "value": 0}
```

**Solution:**
1. Verify tables exist and contain data:
   ```sql
   SELECT COUNT(*) FROM vault_nodes;
   SELECT COUNT(*) FROM scarindex_calculations;
   ```
2. Check table permissions for service role
3. Verify the `created_at` column exists and is properly indexed

### Issue: ScarIndex Always Shows 🔴 (Red)

**Symptoms:**
- Status emoji is always red despite good data

**Solution:**
1. Check if `scarindex_calculations` table has recent data:
   ```sql
   SELECT * FROM scarindex_calculations 
   ORDER BY created_at DESC LIMIT 10;
   ```
2. Verify the `value` column contains valid numbers (0.6-1.4 range for healthy)
3. Check if timestamps are in the correct format (UTC)

### Issue: Workflow Runs But Script Fails

**Symptoms:**
```
Error: Missing GUARDIAN_EDGE_URL or DISCORD_GUARDIAN_WEBHOOK
```

**Solution:**
1. Check workflow YAML syntax - ensure secrets are properly referenced:
   ```yaml
   env:
     GUARDIAN_EDGE_URL: ${{ secrets.GUARDIAN_EDGE_URL }}
   ```
2. Verify no typos in secret names
3. Check workflow logs for the exact error message

### Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | Edge function not deployed | Deploy with `supabase functions deploy` |
| `401 Unauthorized` | Service role key incorrect | Verify key in Supabase settings |
| `404 Not Found` | Wrong function URL | Check function URL in Supabase dashboard |
| `Webhook URL is not valid` | Discord webhook deleted/invalid | Recreate webhook in Discord |

---

## Maintenance & Monitoring

### Regular Checks (Weekly)

1. **Verify heartbeats are arriving:**
   - Check Discord channel for regular 3-hour intervals
   - Look for gaps or missed heartbeats

2. **Review ScarIndex trends:**
   - Monitor if values are consistently in 🟢 (0.6-1.4) range
   - Investigate prolonged 🔴 or 🟠 periods

3. **Check GitHub Actions usage:**
   - Go to **Settings** → **Actions** → **Usage**
   - Ensure you're within free tier limits

4. **Verify Edge Function health:**
   ```bash
   # Quick health check
   curl "$GUARDIAN_EDGE_URL?hours=1"
   ```

### Adjusting the Schedule

#### Change Heartbeat Frequency

Edit the workflow file's cron schedule:

```yaml
# Every 6 hours instead of 3
schedule:
  - cron: "0 */6 * * *"

# Every hour
schedule:
  - cron: "0 * * * *"

# Daily at 9 AM UTC
schedule:
  - cron: "0 9 * * *"
```

#### Modify Time Window

Change the lookback period:

```yaml
# In workflow file
env:
  GUARDIAN_WINDOW_HOURS: "12"  # 12-hour window instead of 24
```

### Customizing Alert Thresholds

Edit `core/guardian/edge/guardian_sync.ts`:

```typescript
// Current thresholds
if (score >= 1.4) return "🟠"; // high
if (score >= 0.6) return "🟢"; // healthy
return "🔴"; // low

// Example: More strict thresholds
if (score >= 1.2) return "🟠"; // high
if (score >= 0.8) return "🟢"; // healthy
return "🔴"; // low
```

After editing, redeploy:
```bash
supabase functions deploy guardian_sync
```

### Adding Custom Metrics

To add new metrics to the heartbeat:

1. Edit the SQL query in `guardian_sync.ts`
2. Add new metric to the response array
3. Redeploy the edge function

Example:
```typescript
// Add a new metric
const [totals] = await sql(`
  SELECT
    (SELECT COUNT(*) FROM vault_nodes) AS total_nodes,
    -- Add your new metric
    (SELECT SUM(amount) FROM transactions WHERE created_at > ${since}) AS transaction_volume
`);

// Include in response
metrics: [
  { label: "VaultNodes", value: totals?.total_nodes ?? 0 },
  { label: "TxVolume(24h)", value: totals?.transaction_volume ?? 0 },
  // ... other metrics
]
```

### Logs and Debugging

#### View Edge Function Logs

```bash
supabase functions logs guardian_sync --project-ref YOUR_PROJECT_REF
```

#### View GitHub Actions Logs

1. Go to **Actions** → **Guardian Heartbeat**
2. Click on the latest workflow run
3. Expand "Run field_sync" step to see output

#### Enable Verbose Logging

Modify `field_sync.py` to add debug output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def fetch_status():
    logging.debug(f"Fetching from: {EDGE_URL}")
    # ... rest of function
```

---

## Security Best Practices

### 1. Secrets Management

- ✅ Never commit secrets to git
- ✅ Use GitHub Secrets for CI/CD
- ✅ Rotate webhook URLs periodically
- ✅ Use Supabase service role key (not anon key) for edge functions

### 2. Function Security

- ✅ The `raw_sql()` function only allows SELECT queries
- ✅ Edge function is read-only (no write operations)
- ✅ Consider adding rate limiting if exposed publicly

### 3. Discord Webhook Security

- ✅ Don't share webhook URLs publicly
- ✅ If compromised, delete and recreate in Discord settings
- ✅ Consider using Discord bot tokens for more control (advanced)

---

## Performance Optimization

### Database Indexing

Ensure these indexes exist for optimal query performance:

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_vault_nodes_created_at 
  ON vault_nodes(created_at);

CREATE INDEX IF NOT EXISTS idx_ache_events_created_at 
  ON ache_events(created_at);

CREATE INDEX IF NOT EXISTS idx_scarindex_created_at 
  ON scarindex_calculations(created_at);

CREATE INDEX IF NOT EXISTS idx_guardian_alerts_created_at 
  ON guardian_alerts(created_at);
```

### Edge Function Response Time

Typical response times:
- ✅ Good: < 500ms
- ⚠️ Acceptable: 500ms - 2s
- 🔴 Slow: > 2s

If responses are slow:
1. Check database query performance
2. Verify indexes are present
3. Consider reducing the time window for aggregations

---

## Support and Resources

### Documentation

- **Main Guardian Docs:** `docs/guardian/README.md`
- **Discord Setup:** `docs/guardian/webhook_config.md`
- **Test Cases:** `core/guardian/tests/test_guardian_sync.http`

### Key Configuration Files

```
mythotech-spiralos/
├── core/guardian/
│   ├── edge/guardian_sync.ts        # Edge function
│   ├── sql/guardian_views.sql       # Database functions
│   ├── scripts/field_sync.py        # Heartbeat script
│   └── config/tasks.deepagent.yaml  # DeepAgent config
├── .github/workflows/
│   └── guardian_heartbeat.yml       # GitHub Actions workflow
└── .env.example                     # Environment template
```

### Getting Help

If you encounter issues not covered in this guide:

1. Check Edge Function logs: `supabase functions logs guardian_sync`
2. Review GitHub Actions run logs
3. Test each component individually (SQL → Edge Function → Script → Discord)
4. Verify all prerequisites are met

---

## Next Steps

After successful deployment:

1. ✅ Monitor the first few heartbeats in Discord
2. ✅ Set up alerts for missed heartbeats (optional)
3. ✅ Customize thresholds based on your system's normal ranges
4. ✅ Consider adding more metrics specific to your use case
5. ✅ Document your specific configuration in your internal wiki

---

## Changelog

### v1.0.0 (ΔΩ.141.0)
- Initial Guardian Automation Kit release
- Supabase Edge Function deployment
- GitHub Actions workflow integration
- Discord webhook notifications
- DeepAgent task configuration
- Comprehensive documentation

---

**🎯 Deployment Complete!**

Once all steps are completed, your Guardian will autonomously monitor SpiralOS health and report status every 3 hours to Discord. The system is now live and operational.
