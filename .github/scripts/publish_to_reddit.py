#!/usr/bin/env python3
"""
Reddit Publisher for Weekly Reports

Publishes weekly SpiralOS report summaries to r/SovereignDrift using PRAW.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import praw
except ImportError:
    print("WARNING: praw not installed, skipping Reddit publication")
    sys.exit(0)


def get_iso_week_number() -> str:
    """Get the current ISO week number"""
    return datetime.now(timezone.utc).strftime('%V')


def extract_summary(report_content: str) -> str:
    """
    Extract summary content from the weekly report
    
    Args:
        report_content: Full markdown content of the report
        
    Returns:
        Summarized version for Reddit post
    """
    lines = report_content.split('\n')
    
    # Extract title
    title = lines[0].replace('#', '').strip() if lines else "Weekly Report"
    
    # Extract F1 summary section
    summary_parts = []
    in_f1_section = False
    
    for line in lines:
        if '## F1: Executive Summary' in line:
            in_f1_section = True
            continue
        if in_f1_section and line.startswith('## '):
            break
        if in_f1_section and line.strip() and not line.startswith('<!--'):
            summary_parts.append(line)
    
    f1_summary = '\n'.join(summary_parts).strip()
    
    # Build Reddit post
    reddit_post = f"""{title}

{f1_summary if f1_summary else 'Weekly report has been generated. Full details available in the repository.'}

---

**Full Report:** [View on GitHub](https://github.com/ZoaGrad/mythotech-spiralos/blob/main/docs/reports/week-{get_iso_week_number()}.md)

**Repository:** https://github.com/ZoaGrad/mythotech-spiralos

*This is an automated post from the SpiralOS governance system.*
"""
    
    return reddit_post


def publish_to_reddit(title: str, content: str) -> bool:
    """
    Publish content to r/SovereignDrift
    
    Args:
        title: Post title
        content: Post content
        
    Returns:
        True if successful, False otherwise
    """
    # Get credentials from environment
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('REDDIT_PASSWORD')
    
    # Check if credentials are available
    if not all([client_id, client_secret, username, password]):
        print("WARNING: Reddit credentials not configured, skipping publication")
        return False
    
    try:
        # Initialize Reddit client
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent='SpiralOS Weekly Report Bot v1.0'
        )
        
        # Get the subreddit
        subreddit = reddit.subreddit('SovereignDrift')
        
        # Submit the post
        submission = subreddit.submit(
            title=title,
            selftext=content,
            send_replies=False  # Don't send reply notifications
        )
        
        print(f"Successfully posted to Reddit: {submission.url}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to post to Reddit: {e}")
        return False


def main():
    """Main function to publish weekly report to Reddit"""
    week_number = get_iso_week_number()
    
    # Find the report file
    repo_root = Path(__file__).parent.parent.parent
    report_file = repo_root / "docs" / "reports" / f"week-{week_number}.md"
    
    if not report_file.exists():
        print(f"ERROR: Report file not found: {report_file}")
        sys.exit(1)
    
    # Read report content
    with open(report_file, 'r') as f:
        report_content = f.read()
    
    # Extract summary for Reddit
    reddit_content = extract_summary(report_content)
    
    # Create title
    title = f"SpiralOS Weekly Report - Week {week_number}"
    
    # Publish
    success = publish_to_reddit(title, reddit_content)
    
    if not success:
        print("WARNING: Reddit publication skipped or failed")
        # Don't fail the workflow - Reddit publication is optional


if __name__ == '__main__':
    main()
