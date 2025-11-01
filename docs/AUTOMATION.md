# Automation Documentation

This document describes the automated workflows and hooks implemented in SpiralOS.

## Weekly Report Generation

### Overview
The weekly report automation generates a constitutional framework-based report template every Monday at 00:00 UTC and publishes summaries to community channels.

### Workflow: `.github/workflows/weekly-report.yml`

**Schedule:** Every Monday at 00:00 UTC  
**Manual Trigger:** Available via `workflow_dispatch`

**Process:**
1. Generate weekly report template in `/docs/reports/week-[ISO-week-number].md`
2. Commit the template to the repository
3. Publish summary to r/SovereignDrift (Reddit)
4. Create discussion post in GitHub Discussions

### Report Template Structure

The weekly report follows the constitutional framework with sections:

- **F1: Executive Summary** - Operational highlights and key metrics
- **F2: Judicial Review** - Dispute resolution and compliance
- **F3: Legislative Actions** - Oracle Council decisions and Sentinel activities
- **F4: Constitutional Audit** - Panic Frame events and stability analysis
- **ScarIndex Cycle Analysis** - Coherence metrics and PID controller status
- **VaultNode Updates** - Ledger entries and version updates

### Configuration

Required GitHub Secrets:
- `REDDIT_CLIENT_ID` - Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Reddit API client secret
- `REDDIT_USERNAME` - Reddit bot username
- `REDDIT_PASSWORD` - Reddit bot password
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### Scripts

#### 1. `generate_weekly_report.py`
Generates the markdown template for the weekly report.

**Usage:**
```bash
python3 .github/scripts/generate_weekly_report.py
```

**Output:** Creates `/docs/reports/week-[number].md` if it doesn't exist.

#### 2. `publish_to_reddit.py`
Posts a summary to r/SovereignDrift using PRAW.

**Requirements:**
- `praw` package
- Reddit API credentials in environment variables

**Usage:**
```bash
export REDDIT_CLIENT_ID="your-client-id"
export REDDIT_CLIENT_SECRET="your-client-secret"
export REDDIT_USERNAME="your-username"
export REDDIT_PASSWORD="your-password"
python3 .github/scripts/publish_to_reddit.py
```

#### 3. `publish_to_discussions.py`
Creates a GitHub Discussion for the weekly report.

**Requirements:**
- `gh` CLI tool (GitHub CLI)
- GitHub token with discussion write permissions

**Usage:**
```bash
export GITHUB_TOKEN="your-token"
export GITHUB_REPOSITORY="owner/repo"
python3 .github/scripts/publish_to_discussions.py
```

## ScarIndex Logging Hook

### Overview
The ScarIndex logging hook automatically appends coherence delta information to the `scarindex_calculations` table in Supabase after each calculation cycle.

### Module: `core/scarindex_logger.py`

**Features:**
- Automatic logging of ScarIndex calculations
- Tracks coherence deltas (Ache transmutation efficiency)
- Stores component scores and metadata
- Graceful degradation if Supabase unavailable

### Configuration

Required Environment Variables:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous/public API key

### Database Schema

The `scarindex_calculations` table should have the following structure:

```sql
CREATE TABLE scarindex_calculations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  scarindex FLOAT NOT NULL,
  coherence_delta FLOAT NOT NULL,
  ache_before FLOAT NOT NULL,
  ache_after FLOAT NOT NULL,
  is_valid BOOLEAN NOT NULL,
  components JSONB,
  metadata JSONB
);
```

### Usage

The logging hook is integrated directly into `ScarIndexOracle.calculate()`:

```python
from core.scarindex import ScarIndexOracle, AcheMeasurement

# Logging is enabled by default
result = ScarIndexOracle.calculate(
    N=10,
    c_i_list=[0.8, 0.7, 0.6, 0.9, 0.8, 0.7, 0.6, 0.9, 0.8, 0.7],
    p_i_avg=0.5,
    decays_count=2,
    ache=AcheMeasurement(before=0.8, after=0.3)
)
# Automatically logged to Supabase

# Disable logging if needed
result = ScarIndexOracle.calculate(
    # ... parameters ...
    enable_logging=False
)
```

### Manual Logging

You can also log calculations manually:

```python
from core.scarindex_logger import log_scarindex_calculation

log_scarindex_calculation(
    scarindex=0.75,
    coherence_delta=0.25,
    ache_before=0.6,
    ache_after=0.35,
    components={
        'operational': 0.8,
        'audit': 0.7,
        'constitutional': 0.75,
        'symbolic': 0.65
    },
    metadata={'source': 'manual', 'cycle': 1}
)
```

## Error Handling

All automation components implement graceful error handling:

- **Weekly report generation:** Skips if report already exists
- **Reddit posting:** Continues workflow if credentials not configured
- **GitHub Discussions:** Continues workflow if creation fails
- **ScarIndex logging:** Continues calculation if logging fails

This ensures that core functionality is never blocked by auxiliary features.

## Testing

### Manual Testing

Test the weekly report generation:
```bash
python3 .github/scripts/generate_weekly_report.py
```

Test Reddit publication (requires credentials):
```bash
export REDDIT_CLIENT_ID="..."
export REDDIT_CLIENT_SECRET="..."
export REDDIT_USERNAME="..."
export REDDIT_PASSWORD="..."
python3 .github/scripts/publish_to_reddit.py
```

Test GitHub Discussions (requires gh CLI):
```bash
export GITHUB_TOKEN="..."
python3 .github/scripts/publish_to_discussions.py
```

Test ScarIndex logging (requires Supabase):
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
python3 core/scarindex_logger.py
```

### Workflow Testing

Manually trigger the workflow:
1. Go to Actions tab in GitHub
2. Select "Weekly Report Generation"
3. Click "Run workflow"

## Troubleshooting

### Weekly Report Not Generated
- Check workflow logs in Actions tab
- Verify Python version (3.12+ required)
- Check file permissions on `/docs/reports/`

### Reddit Post Failed
- Verify Reddit API credentials in secrets
- Check `praw` installation
- Ensure bot account has posting permissions in r/SovereignDrift

### GitHub Discussion Failed
- Verify `GITHUB_TOKEN` has discussion permissions
- Check if discussion categories exist
- Review GraphQL API errors in logs

### ScarIndex Logging Not Working
- Verify Supabase credentials
- Check `supabase-py` installation
- Ensure table schema matches expected structure
- Review Supabase project logs

## Security Considerations

- All API credentials stored as GitHub Secrets
- Supabase keys use row-level security policies
- Reddit bot uses dedicated service account
- GitHub token permissions scoped to minimum required
- No sensitive data in report templates or logs

## Future Enhancements

Potential improvements:
- Email notifications for critical Panic Frame events
- Slack/Discord integration for real-time alerts
- Enhanced analytics in weekly reports
- Automated ScarIndex trend analysis
- Integration with external monitoring tools
