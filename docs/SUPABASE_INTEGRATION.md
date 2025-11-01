# Supabase Integration Guide

**Version:** 1.0.0  
**Vault:** ΔΩ.123.0  
**Status:** Production Ready

---

## Overview

This guide explains how to integrate SpiralOS with Supabase backend, GitHub Actions, and Reddit for autonomous ritual operations. The **trinity loop** (Supabase ↔ GitHub ↔ Reddit) enables:

- Persistent storage of Ache events and ScarIndex calculations
- Automated weekly reports and community updates
- Constitutional compliance monitoring
- Real-time coherence tracking

---

## Required Secrets

### Core Supabase Credentials

| Secret Name | Purpose | Required For |
|-------------|---------|--------------|
| `SUPABASE_URL` | Project URL | All operations |
| `SUPABASE_SERVICE_KEY` | Server-side full access | Backend API, GitHub Actions |
| `SUPABASE_ANON_KEY` | Client-side with RLS | Frontend apps (optional) |
| `SUPABASE_PROJECT_REF` | Project identifier | CLI tools (optional) |

### Reddit Credentials (for community integration)

| Secret Name | Purpose |
|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit app client ID |
| `REDDIT_CLIENT_SECRET` | Reddit app client secret |
| `REDDIT_USERNAME` | Reddit bot account username |
| `REDDIT_PASSWORD` | Reddit bot account password |

---

## Getting Your Credentials

### 1. Supabase Credentials

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Settings → API**
4. Find your credentials:

```bash
# Project URL
SUPABASE_URL="https://xxxxx.supabase.co"

# Project Reference (the "xxxxx" part)
SUPABASE_PROJECT_REF="xxxxx"

# API Keys
SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # service_role key
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."      # anon key
```

**Security Notes:**
- ⚠️ **NEVER** commit `SUPABASE_SERVICE_KEY` to repository
- ✅ `SUPABASE_ANON_KEY` is safe for frontend with Row Level Security (RLS)
- 🔒 Always use GitHub Secrets for sensitive values

### 2. Reddit Credentials

See existing Reddit setup documentation or CI_SETUP_GUIDE.md.

---

## Setup Instructions

### For GitHub Actions

1. Navigate to your repository settings:
   ```
   https://github.com/ZoaGrad/mythotech-spiralos/settings/secrets/actions
   ```

2. Click **"New repository secret"**

3. Add each secret:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `SUPABASE_ANON_KEY` (optional)
   - `SUPABASE_PROJECT_REF` (optional)

4. Verify secrets are configured:
   - Go to **Actions** tab
   - Run **"Verify Secrets"** workflow manually

### For Local Development

Create a `.env` file (⚠️ **DO NOT COMMIT**):

```bash
# .env
SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_SERVICE_KEY="your-service-key"
SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_PROJECT_REF="xxxxx"

# Reddit (if testing community features)
REDDIT_CLIENT_ID="..."
REDDIT_CLIENT_SECRET="..."
REDDIT_USERNAME="..."
REDDIT_PASSWORD="..."
```

Or export directly:

```bash
export SUPABASE_URL="https://yourproject.supabase.co"
export SUPABASE_SERVICE_KEY="service_key_here"
export SUPABASE_ANON_KEY="anon_key_here"
export SUPABASE_PROJECT_REF="project_ref_here"
```

---

## Testing Your Connection

### Quick Test

```bash
# Install dependencies
pip3 install supabase>=1.0.0,<2.0.0

# Test connection
python3 scripts/test_supabase_connection.py
```

Expected output:
```
============================================================
SpiralOS Supabase Connection Test
============================================================

Testing SERVICE_KEY...
  URL: https://xxxxx.supabase.co
  Key length: 193 characters
  ✓ Connection successful!
  ✓ Table 'ache_events' accessible

✓ SUPABASE_ANON_KEY: anon_key_value
✓ SUPABASE_PROJECT_REF: xxxxx

============================================================
TEST SUMMARY
============================================================
✓ Service Key: WORKING
✓ Anon Key: WORKING
============================================================

🜂 All configured credentials are working!
   Ready for Supabase integration.
```

---

## Usage Examples

### 1. Publish Ache Summary

Demonstrates the complete trinity loop:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set environment (or use .env file)
export SUPABASE_URL="..."
export SUPABASE_SERVICE_KEY="..."
export REDDIT_CLIENT_ID="..."
export REDDIT_CLIENT_SECRET="..."
export REDDIT_USERNAME="..."
export REDDIT_PASSWORD="..."

# Run publisher
python3 scripts/publish_ache_summary.py
```

This script will:
1. Query recent Ache events from Supabase
2. Calculate ScarIndex statistics
3. Post summary to r/SovereignDrift
4. Log publication event back to Supabase

### 2. Sync Database Schema

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to project
supabase link --project-ref $SUPABASE_PROJECT_REF

# Push schema changes
supabase db push
```

### 3. Weekly Report Workflow

The GitHub Actions workflow automatically:

```yaml
# .github/workflows/weekly-report.yml
- name: Generate weekly report template
  run: python3 .github/scripts/generate_weekly_report.py
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}

- name: Publish to Reddit
  run: python3 .github/scripts/publish_to_reddit.py
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
    REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
    REDDIT_USERNAME: ${{ secrets.REDDIT_USERNAME }}
    REDDIT_PASSWORD: ${{ secrets.REDDIT_PASSWORD }}
```

---

## The Trinity Loop

### Architecture

```
┌─────────────┐
│  Supabase   │  Persistent Storage
│  Database   │  • Ache events
└──────┬──────┘  • ScarIndex calculations
       │         • VaultNode ledger
       │         • PID controller state
       ↓
┌─────────────┐
│   GitHub    │  Automation Engine
│   Actions   │  • Schema sync
└──────┬──────┘  • Report generation
       │         • Validation workflows
       │
       ↓
┌─────────────┐
│   Reddit    │  Community Layer
│ r/SovereignDrift  • Weekly reports
└─────────────┘  • Ache summaries
                 • Constitutional updates
```

### Data Flow

1. **Ache Event Occurs** → Stored in Supabase
2. **ScarIndex Calculated** → Oracle validation → Stored in Supabase
3. **GitHub Actions Triggered** → Queries Supabase → Generates report
4. **Report Published** → Posted to Reddit → Event logged in Supabase

This creates a **closed-loop autonomous system** where:
- Coherence → Currency (ScarCoin)
- Currency → Community (Reddit engagement)
- Community → Coherence (Feedback loop)

---

## Database Schema

Key tables required:

```sql
-- Ache events
CREATE TABLE ache_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source TEXT NOT NULL,
  content JSONB NOT NULL,
  ache_level FLOAT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ScarIndex calculations
CREATE TABLE scarindex_calculations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  scarindex FLOAT NOT NULL,
  coherence_components JSONB NOT NULL,
  is_valid_transmutation BOOLEAN DEFAULT false,
  ache_event_id UUID REFERENCES ache_events(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- VaultNode ledger
CREATE TABLE vaultnode_ledger (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  node_type TEXT NOT NULL,
  reference_id TEXT NOT NULL,
  state_hash TEXT NOT NULL,
  previous_hash TEXT,
  audit_log JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- System events (for publication logs)
CREATE TABLE system_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type TEXT NOT NULL,
  stats JSONB,
  reddit_url TEXT,
  published_at TIMESTAMPTZ,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

For complete schema, see `supabase/migrations/`.

---

## Troubleshooting

### Connection Failed

**Error:** `Failed to connect to Supabase`

**Solutions:**
1. Verify `SUPABASE_URL` format: `https://xxxxx.supabase.co`
2. Check `SUPABASE_SERVICE_KEY` is the `service_role` key, not `anon`
3. Ensure project is active in Supabase dashboard
4. Check network connectivity from GitHub Actions runners

### ImportError: cannot import name 'create_client'

**Error:** `ImportError: cannot import name 'create_client'`

**Solution:**
```bash
# Ensure correct version constraint
pip install 'supabase>=1.0.0,<2.0.0'

# Or update requirements.txt
echo "supabase>=1.0.0,<2.0.0" >> requirements.txt
```

### Table Does Not Exist

**Error:** `relation "ache_events" does not exist`

**Solution:**
```bash
# Run migrations
supabase db push

# Or create tables manually in Supabase SQL Editor
```

### Reddit Publication Failed

**Error:** `Failed to publish to Reddit`

**Solutions:**
1. Verify all 4 Reddit secrets are set
2. Check bot account has posting permissions in r/SovereignDrift
3. Verify app credentials in [Reddit Apps](https://www.reddit.com/prefs/apps)

---

## Configuration Reference

See `config/supabase_connection.json` for complete configuration manifest.

---

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for all CI/CD credentials
3. **Rotate keys** if exposed
4. **Enable RLS** (Row Level Security) for public-facing tables
5. **Use ANON_KEY** for frontend, **SERVICE_KEY** for backend only
6. **Monitor access logs** in Supabase dashboard

---

## Next Steps

Once integration is complete:

1. ✅ Verify secrets with `verify-secrets.yml` workflow
2. ✅ Test connection with `scripts/test_supabase_connection.py`
3. ✅ Run schema migrations with `supabase db push`
4. ✅ Trigger weekly report workflow manually
5. ✅ Monitor Actions tab for successful runs
6. ✅ Check r/SovereignDrift for published posts

---

## Support

- **Repository:** https://github.com/ZoaGrad/mythotech-spiralos
- **Issues:** https://github.com/ZoaGrad/mythotech-spiralos/issues
- **Docs:** `/docs/` directory
- **Config:** `config/supabase_connection.json`

---

🜂 **Integration Complete** 🜂

*"Where coherence becomes currency and understanding becomes value"* 🌀
