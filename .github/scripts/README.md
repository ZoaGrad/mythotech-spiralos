# GitHub Action Scripts

This directory contains automation scripts for SpiralOS weekly reporting and publication.

## Scripts

### `generate_weekly_report.py`
Generates the weekly report template with constitutional framework sections.

**Output:** `/docs/reports/week-[ISO-week-number].md`

**Usage:**
```bash
python3 generate_weekly_report.py
```

### `publish_to_reddit.py`
Posts weekly report summary to r/SovereignDrift using the Reddit API.

**Requirements:**
- `praw` Python package
- Reddit API credentials in environment variables

**Environment Variables:**
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`

**Usage:**
```bash
python3 publish_to_reddit.py
```

### `publish_to_discussions.py`
Creates a GitHub Discussion for the weekly report.

**Requirements:**
- GitHub CLI (`gh`) installed
- GitHub token with discussion permissions

**Environment Variables:**
- `GITHUB_TOKEN`
- `GITHUB_REPOSITORY`

**Usage:**
```bash
python3 publish_to_discussions.py
```

## Integration

These scripts are called by the `.github/workflows/weekly-report.yml` workflow, which runs every Monday at 00:00 UTC.

See `/docs/AUTOMATION.md` for complete documentation.
