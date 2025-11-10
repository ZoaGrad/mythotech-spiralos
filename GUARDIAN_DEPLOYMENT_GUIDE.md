# Guardian Automation Kit - Deployment Guide

## Overview

The Guardian Automation Kit monitors your Spiralos instance and provides real-time health metrics. This guide covers deployment to Supabase.

## Components

1. **SQL Function** (`raw_sql`): A secure, read-only SQL runner for Edge Function queries
2. **Edge Function** (`guardian_sync`): Aggregates metrics and provides status endpoint

## Prerequisites

- Supabase CLI installed
- Supabase project with credentials:
  - `SUPABASE_PROJECT_REF`
  - `SUPABASE_SERVICE_ROLE_KEY`
- GitHub repository secrets configured
- Discord webhook URL (optional, for notifications)

## Deployment Methods

### Method 1: Automated Deployment (GitHub Actions)

The repository includes a GitHub Actions workflow that automatically deploys on push to main.

1. **Ensure GitHub Secrets are configured:**
   - `SUPABASE_PROJECT_REF`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `DISCORD_GUARDIAN_WEBHOOK`

2. **Trigger deployment:**
   ```bash
   # Push to main branch
   git push origin main
   
   # Or manually trigger via GitHub UI
   # Actions tab → Deploy Guardian to Supabase → Run workflow
   ```

3. **Monitor deployment:**
   - Check the Actions tab in GitHub
   - Discord notification will be sent on success

### Method 2: Manual Deployment (Shell Script)

Use the `deploy_guardian.sh` script for local deployment.

1. **Set environment variables:**
   ```bash
   export SUPABASE_PROJECT_REF="your_project_ref"
   export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
   ```

2. **Run deployment script:**
   ```bash
   ./deploy_guardian.sh
   ```

3. **The script will:**
   - Verify Supabase CLI installation
   - Link to your Supabase project
   - Deploy SQL migrations
   - Deploy Edge Function
   - Test the deployment
   - Save the Edge URL to `.env`

### Method 3: Manual CLI Commands

For granular control, use Supabase CLI commands directly.

1. **Link to Supabase project:**
   ```bash
   supabase link --project-ref $SUPABASE_PROJECT_REF
   ```

2. **Deploy SQL migrations:**
   ```bash
   supabase db push
   ```

3. **Deploy Edge Function:**
   ```bash
   supabase functions deploy guardian_sync --no-verify-jwt
   ```

## File Structure

```
mythotech-spiralos/
├── core/guardian/
│   ├── sql/
│   │   └── guardian_views.sql          # Source SQL function
│   └── edge/
│       └── guardian_sync.ts            # Source Edge Function
├── supabase/
│   ├── migrations/
│   │   └── 20251110_guardian_sql_runner.sql  # Deployed migration
│   └── functions/
│       └── guardian_sync/
│           └── index.ts                # Deployed Edge Function
├── deploy_guardian.sh                   # Deployment script
└── .github/workflows/
    └── deploy_guardian.yml              # GitHub Actions workflow
```

## Post-Deployment

### 1. Get Edge Function URL

After deployment, your Edge Function URL will be:
```
https://<SUPABASE_PROJECT_REF>.supabase.co/functions/v1/guardian_sync
```

### 2. Add to GitHub Secrets

Add the Edge Function URL as a GitHub secret:
```bash
gh secret set GUARDIAN_EDGE_URL --body "https://<PROJECT_REF>.supabase.co/functions/v1/guardian_sync"
```

Or via GitHub UI:
- Settings → Secrets and variables → Actions → New repository secret
- Name: `GUARDIAN_EDGE_URL`
- Value: Your Edge Function URL

### 3. Test the Deployment

Test the Edge Function:
```bash
curl "https://<PROJECT_REF>.supabase.co/functions/v1/guardian_sync?hours=24"
```

Expected response:
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

### 4. Set Up Monitoring (Optional)

Create a GitHub Actions workflow to periodically call the Edge Function and send results to Discord:

```yaml
name: Guardian Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Call Guardian Edge Function
        run: |
          RESPONSE=$(curl -s "${{ secrets.GUARDIAN_EDGE_URL }}?hours=24")
          echo "Guardian Status: $RESPONSE"
          
          # Send to Discord
          curl -X POST "${{ secrets.DISCORD_GUARDIAN_WEBHOOK }}" \
            -H "Content-Type: application/json" \
            -d "{\"content\": \"🛡️ Guardian Health Check\", \"embeds\": [{\"description\": \"\`\`\`json\n$RESPONSE\n\`\`\`\"}]}"
```

## Troubleshooting

### Common Issues

1. **"Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY"**
   - Ensure environment variables are set in Supabase project settings
   - Check that secrets are properly configured in GitHub

2. **"raw_sql function not found"**
   - SQL migration didn't deploy
   - Run: `supabase db push` manually

3. **Edge Function returns 500**
   - Check Supabase logs: `supabase functions logs guardian_sync`
   - Verify database tables exist (vault_nodes, ache_events, etc.)

4. **GitHub Actions deployment fails**
   - Verify all secrets are set correctly
   - Check that SUPABASE_SERVICE_ROLE_KEY has sufficient permissions

### Debug Commands

```bash
# Check Supabase status
supabase status

# View function logs
supabase functions logs guardian_sync --tail

# List deployed functions
supabase functions list

# Test SQL function directly
psql "postgresql://..." -c "SELECT raw_sql('SELECT 1 as test');"
```

## Security Notes

- The `raw_sql` function is restricted to SELECT queries only
- Uses SECURITY DEFINER with proper grants
- Edge Function requires service role key (not exposed publicly)
- Discord webhook should be kept secret

## Updates

To update the Guardian components:

1. Modify files in `core/guardian/`
2. Copy to `supabase/` directories (script does this automatically)
3. Push to main branch (triggers auto-deployment)
4. Or run `./deploy_guardian.sh` manually

## Support

For issues or questions:
- Check GitHub Issues
- Review Supabase logs
- Test individual components separately

---

**Deployment Date:** 2025-11-10  
**Version:** 1.0.0  
**Deployed By:** Guardian Automation Kit Setup
