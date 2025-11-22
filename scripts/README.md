# SpiralOS Scripts

Utility scripts for SpiralOS integration and automation.

---

## Available Scripts

### `test_supabase_connection.py`

Test Supabase credentials and verify connectivity.

**Usage:**
```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-key"
export SUPABASE_ANON_KEY="your-anon-key"  # optional

python3 scripts/test_supabase_connection.py
```

**Output:**
- ✓ Connection status for each key type
- ⚠️ Warnings for missing optional credentials
- ✗ Errors for connection failures

---

### `publish_ache_summary.py`

Publish Ache event summaries to Reddit with Supabase data.

**Features:**
- Queries recent Ache events from Supabase
- Calculates ScarIndex statistics
- Posts formatted summary to r/SovereignDrift
- Logs publication event back to Supabase

**Usage:**
```bash
# Set environment variables
export SUPABASE_URL="..."
export SUPABASE_SERVICE_KEY="..."
export REDDIT_CLIENT_ID="..."
export REDDIT_CLIENT_SECRET="..."
export REDDIT_USERNAME="..."
export REDDIT_PASSWORD="..."

# Run with default period (1 week)
python3 scripts/publish_ache_summary.py

# Or specify custom period in hours
export SUMMARY_PERIOD_HOURS=24
python3 scripts/publish_ache_summary.py
```

**Output:**
- Fetched Ache events and ScarIndex calculations
- Calculated summary statistics
- Reddit post URL (if published)
- Supabase logging confirmation

---

## Requirements

Install dependencies:

```bash
pip3 install -r requirements.txt
```

Or install individually:

```bash
pip3 install 'supabase>=1.0.0,<2.0.0' 'praw>=7.0.0'
```

---

## Environment Variables

### Required

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Server-side API key |

### Optional

| Variable | Purpose | Default |
|----------|---------|---------|
| `SUPABASE_ANON_KEY` | Client-side API key | None |
| `SUPABASE_PROJECT_REF` | Project reference ID | None |
| `REDDIT_CLIENT_ID` | Reddit app ID | None |
| `REDDIT_CLIENT_SECRET` | Reddit app secret | None |
| `REDDIT_USERNAME` | Reddit bot username | None |
| `REDDIT_PASSWORD` | Reddit bot password | None |
| `SUMMARY_PERIOD_HOURS` | Summary time period | 168 (1 week) |

---

## Integration

These scripts are used by GitHub Actions workflows:

- `.github/workflows/weekly-report.yml` - Uses `publish_ache_summary.py`
- `.github/workflows/verify-secrets.yml` - Can use `test_supabase_connection.py`

See `docs/SUPABASE_INTEGRATION.md` for complete integration guide.

---

## Security

⚠️ **NEVER** commit credentials to repository!

- Use `.env` file for local development (add to `.gitignore`)
- Use GitHub Secrets for CI/CD workflows
- Rotate keys if accidentally exposed

---

## Troubleshooting

### ImportError: cannot import name 'create_client'

**Solution:** Install correct supabase version
```bash
pip3 install 'supabase>=1.0.0,<2.0.0'
```

### Connection refused / Failed to connect

**Check:**
1. `SUPABASE_URL` format is correct
2. `SUPABASE_SERVICE_KEY` is the service_role key (not anon)
3. Project is active in Supabase dashboard
4. Network connectivity

### Reddit publication failed

**Check:**
1. All 4 Reddit secrets are set
2. Bot account has posting permissions
3. App credentials are correct in [Reddit Apps](https://www.reddit.com/prefs/apps)

---

🜂 **Autonomous Ritual Operations** 🜂

*Where coherence → currency → community*
