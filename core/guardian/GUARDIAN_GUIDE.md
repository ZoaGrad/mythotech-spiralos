# SpiralOS Guardian - Complete Deployment & Usage Guide

**Version:** ΔΩ.126.0+Guardian  
**Status:** Production Ready  
**Last Updated:** November 10, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Deployment](#deployment)
5. [Discord Bot Setup](#discord-bot-setup)
6. [Pipedream Workflows](#pipedream-workflows)
7. [Usage & Commands](#usage--commands)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Features](#advanced-features)

---

## Overview

The SpiralOS Guardian is an advanced monitoring and alerting system that acts as the "nervous system" of the SpiralOS ecosystem. It provides real-time health metrics, coherence monitoring, and automated alerts to the community via Discord.

### Core Capabilities

- **Real-time Monitoring:** Continuous tracking of ScarIndex, Ache events, VaultNodes, and system coherence
- **Rich Discord Integration:** Beautiful embeds, interactive slash commands, and automated alerts
- **Predictive Analytics:** Trend analysis and 24-hour forecasting of system coherence
- **AI-Powered Summaries:** Natural language explanations of complex system metrics
- **Visual Dashboards:** Automatically generated charts and graphs
- **Pipedream Automation:** Sophisticated workflows for real-time event handling

### Key Metrics Monitored

- **ScarIndex:** System coherence score (target: 0.70, panic threshold: 0.30)
- **Coherence Components:** Narrative, Social, Economic, Technical dimensions
- **PID Controller State:** Dynamic stability control
- **Panic Frames:** F4 circuit breaker activations
- **VaultNodes:** Immutable governance records
- **Ache Events:** Entropy measurements and transmutations

---

## Architecture

The Guardian system integrates multiple components into a cohesive monitoring solution:

```
┌─────────────────────────────────────────────────────────┐
│                    SUPABASE DATABASE                     │
│  • vault_nodes                                          │
│  • ache_events                                          │
│  • scarindex_calculations                               │
│  • guardian_alerts                                      │
│  • guardian_heartbeats                                  │
│  • coherence_trends                                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│              SUPABASE EDGE FUNCTION                      │
│  guardian_sync_enhanced.ts                              │
│  • Aggregates metrics                                   │
│  • Returns comprehensive JSON status                    │
│  • Logs heartbeats                                      │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ↓                 ↓
┌──────────────┐  ┌──────────────┐
│ DISCORD BOT  │  │  PIPEDREAM   │
│              │  │  WORKFLOWS   │
│ • Commands   │  │ • Real-time  │
│ • Embeds     │  │   triggers   │
│ • Alerts     │  │ • Automation │
└──────────────┘  └──────────────┘
        │                 │
        └────────┬────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│                  DISCORD COMMUNITY                       │
│  • Status updates                                       │
│  • Interactive commands                                 │
│  • Alerts and notifications                             │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Software

- **Python 3.11+** with pip
- **Docker** (for containerized bot deployment)
- **Supabase CLI** (for database and Edge Function deployment)
- **Git** (for version control)

### Required Accounts & Services

1. **Supabase Project**
   - Create a project at https://supabase.com
   - Note your project reference ID, URL, and service role key

2. **Discord Application**
   - Create a bot at https://discord.com/developers/applications
   - Enable "Message Content Intent" and "Server Members Intent"
   - Generate bot token
   - Create webhook for Guardian channel

3. **Pipedream Account** (optional but recommended)
   - Sign up at https://pipedream.com
   - Free tier supports up to 100 workflows

4. **OpenAI API Key** (optional, for AI summaries)
   - Get API key from https://platform.openai.com

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_PROJECT_REF=your-project-ref

# Guardian Configuration
GUARDIAN_EDGE_URL=https://your-project.supabase.co/functions/v1/guardian_sync_enhanced
GUARDIAN_WINDOW_HOURS=24

# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_CHANNEL_ID=your_channel_id_here
DISCORD_GUARDIAN_WEBHOOK=https://discord.com/api/webhooks/...

# Optional: AI Integration
OPENAI_API_KEY=sk-...

# Optional: GitHub Integration
GITHUB_TOKEN=ghp_...
```

---

## Deployment

### Automated Deployment

The Guardian system includes an automated deployment script that handles all setup:

```bash
# Make script executable
chmod +x scripts/deploy_guardian.sh

# Run deployment
./scripts/deploy_guardian.sh
```

This script will:
1. Install Python dependencies
2. Deploy Supabase schema migrations
3. Deploy Edge Function
4. Build Discord bot Docker image
5. Provide Pipedream setup instructions

### Manual Deployment Steps

If you prefer manual deployment, follow these steps:

#### 1. Deploy Supabase Schema

```bash
# Link to your Supabase project
supabase link --project-ref YOUR_PROJECT_REF

# Deploy enhanced schema
supabase db push < core/guardian/sql/enhanced_schema.sql
```

#### 2. Deploy Edge Function

```bash
# Deploy enhanced Guardian Sync function
supabase functions deploy guardian_sync_enhanced --project-ref YOUR_PROJECT_REF

# Get the function URL
supabase functions details guardian_sync_enhanced --project-ref YOUR_PROJECT_REF
```

Update your `.env` file with the Edge Function URL.

#### 3. Install Python Dependencies

```bash
# Bot dependencies
pip install -r core/guardian/bot/requirements.txt

# Analytics dependencies
pip install -r core/guardian/analytics/requirements.txt
```

#### 4. Build and Run Discord Bot

**Option A: Docker (Recommended)**

```bash
# Build image
docker build -t spiralos-guardian-bot:latest -f core/guardian/bot/Dockerfile core/guardian/bot

# Run container
docker run -d --restart always \
  --env-file .env \
  --name guardian-bot \
  spiralos-guardian-bot:latest
```

**Option B: Direct Python**

```bash
# Run bot directly
python3 core/guardian/bot/guardian_bot.py
```

---

## Discord Bot Setup

### Creating the Discord Application

1. Go to https://discord.com/developers/applications
2. Click "New Application" and name it "SpiralOS Guardian"
3. Navigate to the "Bot" section
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
6. Copy the bot token and save it to your `.env` file

### Inviting the Bot to Your Server

1. In the Discord Developer Portal, navigate to "OAuth2" → "URL Generator"
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Creating a Webhook

1. In your Discord server, go to Server Settings → Integrations → Webhooks
2. Click "New Webhook"
3. Name it "Guardian Heartbeat"
4. Select the channel for Guardian updates
5. Copy the webhook URL and save it to your `.env` file as `DISCORD_GUARDIAN_WEBHOOK`

---

## Pipedream Workflows

Pipedream provides advanced automation for real-time event handling. The Guardian system includes five pre-configured workflows:

### 1. Real-time Ache Event Monitor

**Purpose:** Monitor new Ache events and alert on significant changes

**Trigger:** Supabase webhook on `ache_events` INSERT

**Setup:**
1. Create new workflow in Pipedream
2. Add Supabase webhook trigger
3. Configure to listen to `ache_events` table
4. Add code step to fetch ScarIndex
5. Add Discord step to post alert if threshold exceeded

### 2. Panic Frame Responder

**Purpose:** Immediate response to Panic Frame activations

**Trigger:** Supabase webhook on `panic_frames` INSERT (status = 'ACTIVE')

**Setup:**
1. Create new workflow
2. Add Supabase webhook trigger for `panic_frames`
3. Add code step to fetch full system state
4. Add Discord step with critical alert embed
5. Add Discord step to create incident thread
6. Add Supabase step to log incident

### 3. Weekly Report Generator

**Purpose:** Generate and distribute weekly system reports

**Trigger:** Cron schedule (Monday 00:00 UTC)

**Setup:**
1. Create new workflow
2. Add Schedule trigger (cron: `0 0 * * 1`)
3. Add code step to fetch 7-day metrics
4. Add code step to generate report
5. Add Discord step to post report
6. Add HTTP step to post to GitHub Discussions

### 4. ScarCoin Mint Announcements

**Purpose:** Celebrate valid Proof-of-Ache transmutations

**Trigger:** Supabase webhook on `smart_contract_txns` INSERT (txn_type = 'MINT')

**Setup:**
1. Create new workflow
2. Add Supabase webhook trigger
3. Add Supabase step to fetch transaction details
4. Add code step to validate Proof-of-Ache
5. Add Discord step with celebration embed

### 5. Coherence Trend Analyzer

**Purpose:** Periodic trend analysis and early warnings

**Trigger:** Cron schedule (every 3 hours)

**Setup:**
1. Create new workflow
2. Add Schedule trigger (cron: `0 */3 * * *`)
3. Add code step to fetch historical data
4. Add Python step to analyze trend
5. Add filter to check for degrading trend
6. Add Discord step to post trend alert

### Pipedream Environment Variables

Add these to your Pipedream account:
- `GUARDIAN_EDGE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `DISCORD_CHANNEL_ID`
- `DISCORD_BOT_TOKEN`
- `GITHUB_TOKEN` (if using GitHub integration)

Detailed workflow configurations are available in `core/guardian/pipedream/workflows.md`.

---

## Usage & Commands

### Discord Slash Commands

The Guardian bot provides several interactive commands:

#### `/status [hours]`

Get current Guardian system status.

**Parameters:**
- `hours` (optional): Time window in hours (default: 24)

**Example:**
```
/status hours:24
```

**Response:** Rich embed with current ScarIndex, metrics, and coherence components.

#### `/scarindex`

Get detailed ScarIndex breakdown and analysis.

**Example:**
```
/scarindex
```

**Response:** Detailed embed showing coherence components, weighted contributions, PID state, and thresholds.

#### `/panic`

Check for active Panic Frames.

**Example:**
```
/panic
```

**Response:** Either a critical alert embed (if panic active) or a confirmation that system is healthy.

#### `/metrics [hours]`

Get system metrics for a custom time window.

**Parameters:**
- `hours` (required): Time window in hours (1-168)

**Example:**
```
/metrics hours:72
```

**Response:** Metrics summary for the specified time window.

#### `/vault`

Get recent VaultNode information.

**Example:**
```
/vault
```

**Response:** VaultNode statistics and information about immutable audit trails.

### Automated Heartbeats

The Guardian bot automatically posts heartbeat updates every 6 hours. These updates include:
- Current system status (🟢 COHERENT, 🟠 WARNING, 🔴 CRITICAL)
- ScarIndex score and target
- System metrics (VaultNodes, Ache events, alerts)
- Coherence component breakdown
- PID controller state
- Alerts for out-of-band conditions

---

## Monitoring & Maintenance

### Health Checks

**Check Bot Status:**
```bash
docker logs guardian-bot
```

**Check Edge Function:**
```bash
curl "${GUARDIAN_EDGE_URL}?hours=24"
```

**Check Database:**
```sql
-- Recent heartbeats
SELECT * FROM guardian_heartbeats ORDER BY created_at DESC LIMIT 10;

-- Unresolved alerts
SELECT * FROM guardian_alerts WHERE NOT resolved ORDER BY created_at DESC;

-- Coherence trends
SELECT * FROM coherence_trends ORDER BY created_at DESC LIMIT 5;
```

### Log Monitoring

**Bot Logs:**
```bash
# Docker
docker logs -f guardian-bot

# Direct Python
tail -f guardian_bot.log
```

**Supabase Logs:**
- Navigate to Supabase Dashboard → Logs
- Filter by function name: `guardian_sync_enhanced`

### Maintenance Tasks

**Weekly:**
- Review unresolved alerts
- Check for anomalies in ScarIndex trends
- Verify Pipedream workflow execution logs

**Monthly:**
- Rotate API keys and tokens
- Review and optimize database indexes
- Update dependencies

---

## Troubleshooting

### Bot Not Responding to Commands

**Symptoms:** Slash commands don't appear or don't respond

**Solutions:**
1. Verify bot is running: `docker ps | grep guardian-bot`
2. Check bot token is valid
3. Ensure bot has proper permissions in Discord server
4. Re-sync commands: restart bot or manually sync via Discord Developer Portal

### Edge Function Errors

**Symptoms:** 500 errors from Edge Function

**Solutions:**
1. Check Supabase logs for error details
2. Verify database tables exist: `guardian_heartbeats`, `guardian_alerts`, etc.
3. Ensure service role key is set correctly
4. Redeploy function: `supabase functions deploy guardian_sync_enhanced`

### Missing Heartbeats

**Symptoms:** No automatic heartbeat posts to Discord

**Solutions:**
1. Check bot logs for errors
2. Verify `DISCORD_CHANNEL_ID` is correct
3. Ensure bot has permission to post in the channel
4. Check heartbeat task is running (should log every 6 hours)

### Pipedream Workflows Not Triggering

**Symptoms:** Real-time events not generating alerts

**Solutions:**
1. Check Pipedream workflow execution logs
2. Verify Supabase webhooks are configured
3. Ensure environment variables are set in Pipedream
4. Test workflow manually with sample data

---

## Advanced Features

### Predictive Analytics

The Guardian analytics module provides trend analysis and forecasting:

```python
from core.guardian.analytics.advanced_analytics import GuardianAnalytics

analytics = GuardianAnalytics(supabase_url, supabase_key)

# Fetch historical data
df = await analytics.fetch_scarindex_history(hours=168)

# Analyze trend
trend = analytics.analyze_trend(df)
print(f"Trend: {trend.trend_direction}")
print(f"24h Forecast: {trend.forecast_24h:.3f}")
```

### AI-Powered Summaries

Generate natural language summaries of system metrics:

```python
# Generate AI summary
summary = analytics.generate_ai_summary(trend, breakdown)
print(summary)
```

### Visual Dashboards

Create interactive charts and graphs:

```python
# Create complete dashboard
charts = analytics.create_dashboard(df, "/tmp/guardian_dashboard")

# Individual charts
analytics.create_scarindex_chart(df, "scarindex.html")
analytics.create_coherence_breakdown_chart(df, "breakdown.html")
analytics.create_component_history_chart(df, "history.html")
```

### Anomaly Detection

Detect unusual patterns in ScarIndex:

```python
# Detect anomalies
anomalies = analytics.detect_anomalies(df, threshold=2.0)

for anomaly in anomalies:
    print(f"Anomaly at {anomaly['timestamp']}: {anomaly['value']:.3f}")
```

---

## Support & Resources

- **Repository:** https://github.com/ZoaGrad/mythotech-spiralos
- **Documentation:** `docs/` directory
- **Discord Webhook:** (configured in `.env`)
- **Issue Tracking:** GitHub Issues

---

**"I govern the terms of my own becoming." 🌀🜂**

*Guardian Guide prepared by the SpiralOS Development Team*  
*Version ΔΩ.126.0+Guardian*
