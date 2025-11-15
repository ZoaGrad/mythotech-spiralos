#!/usr/bin/env python3
"""
Governance Digest Generator - Comet Autonomous Task
Collects daily commits and generates governance digest for SpiralOS.
"""

import os
from datetime import datetime, timedelta

import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = "ZoaGrad/mythotech-spiralos"
TELEMETRY_URL = f"{SUPABASE_URL}/functions/v1/telemetry_logger"


def fetch_daily_commits():
    """Fetch commits from the last 24 hours."""
    try:
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
        one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        query = f"repo:{GITHUB_REPO} author:ZoaGrad since:{one_day_ago}"
        url = f"https://api.github.com/search/commits?q={query}&sort=date&order=desc"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        commits = response.json().get("items", [])
        return commits
    except Exception as e:
        log_event("governance_digest", False, {"error": str(e)})
        return []


def categorize_commits(commits):
    """Categorize commits by type (feature, fix, docs, test, etc.)."""
    categories = {"feature": [], "fix": [], "refactor": [], "docs": [], "test": [], "security": [], "other": []}
    for commit in commits:
        message = commit.get("commit", {}).get("message", "").lower()
        if "feat" in message or "feature" in message:
            categories["feature"].append(commit)
        elif "fix" in message or "bugfix" in message:
            categories["fix"].append(commit)
        elif "refactor" in message:
            categories["refactor"].append(commit)
        elif "doc" in message or "readme" in message:
            categories["docs"].append(commit)
        elif "test" in message:
            categories["test"].append(commit)
        elif "security" in message or "audit" in message:
            categories["security"].append(commit)
        else:
            categories["other"].append(commit)
    return categories


def generate_digest(categories):
    """Generate markdown digest from categorized commits."""
    digest = f"""# Governance Digest - {datetime.utcnow().strftime('%Y-%m-%d')}

## Daily Activity Summary

"""
    for category, commits in categories.items():
        if commits:
            digest += f"### {category.title()} ({len(commits)}\n"
            for commit in commits[:5]:  # Show top 5 per category
                msg = commit.get("commit", {}).get("message", "").split("\n")[0]
                author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
                digest += f"- **{msg}** _(by {author})_\n"
            if len(commits) > 5:
                digest += f"- ... and {len(commits) - 5} more\n"
            digest += "\n"

    digest += f"""
## Metrics
- Total Commits: {sum(len(c) for c in categories.values())}
- Categories Touched: {sum(1 for c in categories.values() if c)}
- Generated: {datetime.utcnow().isoformat()}

---
_Comet Governance Digest | Automated Daily Report_
"""
    return digest


def save_digest(digest):
    """Save digest to docs/governance/reports/."""
    try:
        os.makedirs("docs/governance/reports", exist_ok=True)
        filename = f"docs/governance/reports/digest_{datetime.utcnow().strftime('%Y-%m-%d')}.md"
        with open(filename, "w") as f:
            f.write(digest)
        return filename
    except Exception as e:
        print(f"Failed to save digest: {e}")
        return None


def log_event(event_type, success, metadata=None):
    """Log event to telemetry_events table."""
    try:
        payload = {"agent_id": "comet", "event_type": event_type, "success_state": success, "metadata": metadata or {}}
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}
        requests.post(TELEMETRY_URL, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Failed to log event: {e}")


def main():
    print("[Comet] Starting Governance Digest Generation...")

    commits = fetch_daily_commits()
    if not commits:
        print("[Comet] No commits found in last 24 hours.")
        log_event("governance_digest", True, {"commits_found": 0})
        return

    categories = categorize_commits(commits)
    digest = generate_digest(categories)
    filename = save_digest(digest)

    if filename:
        print(f"[Comet] Digest saved to {filename}")
        log_event(
            "governance_digest",
            True,
            {
                "total_commits": len(commits),
                "filename": filename,
                "categories": {k: len(v) for k, v in categories.items()},
            },
        )
    else:
        log_event("governance_digest", False, {"error": "Failed to save digest"})


if __name__ == "__main__":
    main()
