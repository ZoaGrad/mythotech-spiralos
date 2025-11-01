#!/usr/bin/env python3
"""
GitHub Discussions Publisher for Weekly Reports

Creates discussion posts in the repository for weekly reports.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess


def get_iso_week_number() -> str:
    """Get the current ISO week number"""
    return datetime.now(timezone.utc).strftime('%V')


def get_iso_year() -> str:
    """Get the current ISO year"""
    return datetime.now(timezone.utc).strftime('%G')


def extract_summary(report_content: str) -> str:
    """
    Extract summary content from the weekly report
    
    Args:
        report_content: Full markdown content of the report
        
    Returns:
        Summarized version for discussion post
    """
    lines = report_content.split('\n')
    
    # Find key sections and extract highlights
    summary_parts = []
    current_section = None
    section_content = []
    
    for line in lines:
        if line.startswith('## F1:'):
            current_section = 'F1'
            section_content = []
        elif line.startswith('## F2:'):
            current_section = 'F2'
            section_content = []
        elif line.startswith('## F3:'):
            current_section = 'F3'
            section_content = []
        elif line.startswith('## F4:'):
            current_section = 'F4'
            section_content = []
        elif line.startswith('## ScarIndex'):
            current_section = 'ScarIndex'
            section_content = []
        elif line.startswith('## ') and current_section:
            # Save previous section
            if section_content:
                summary_parts.append((current_section, '\n'.join(section_content)))
            current_section = None
            section_content = []
        elif current_section and line.strip() and not line.startswith('<!--'):
            section_content.append(line)
    
    # Save last section
    if current_section and section_content:
        summary_parts.append((current_section, '\n'.join(section_content)))
    
    # Build discussion content
    discussion_content = f"""# Weekly Report Discussion - Week {get_iso_week_number()}, {get_iso_year()}

This discussion thread is for the weekly SpiralOS governance report.

"""
    
    # Add highlights from each section
    for section, content in summary_parts[:4]:  # First 4 sections
        # Trim content to avoid overly long posts
        trimmed = content[:500] + "..." if len(content) > 500 else content
        discussion_content += f"## {section} Highlights\n\n{trimmed}\n\n"
    
    discussion_content += f"""
---

**Full Report:** [View in Repository](/docs/reports/week-{get_iso_week_number()}.md)

Please use this thread to:
- Discuss the weekly findings
- Raise questions about ScarIndex trends
- Propose governance improvements
- Share insights on coherence metrics

*This discussion was created automatically by the SpiralOS governance system.*
"""
    
    return discussion_content


def create_github_discussion(title: str, body: str) -> bool:
    """
    Create a GitHub Discussion using the GitHub GraphQL API
    
    Args:
        title: Discussion title
        body: Discussion body (markdown)
        
    Returns:
        True if successful, False otherwise
    """
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPOSITORY', 'ZoaGrad/mythotech-spiralos')
    
    if not token:
        print("WARNING: GITHUB_TOKEN not available, skipping discussion creation")
        return False
    
    # Split repo into owner and name
    try:
        owner, repo_name = repo.split('/')
    except ValueError:
        print(f"ERROR: Invalid repository format: {repo}")
        return False
    
    # First, get the repository ID and category ID
    # We'll use the General category or create "Weekly Reports" if it exists
    query_repo = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        id
        discussionCategories(first: 10) {
          nodes {
            id
            name
          }
        }
      }
    }
    """
    
    variables_repo = {
        "owner": owner,
        "repo": repo_name
    }
    
    try:
        # Query for repository and categories
        result = subprocess.run(
            ['gh', 'api', 'graphql', '-f', f'query={query_repo}', 
             '-F', f'owner={owner}', '-F', f'repo={repo_name}'],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, 'GH_TOKEN': token}
        )
        
        data = json.loads(result.stdout)
        repo_id = data['data']['repository']['id']
        
        # Find Weekly Reports or General category
        category_id = None
        categories = data['data']['repository']['discussionCategories']['nodes']
        
        for cat in categories:
            if cat['name'] in ['Weekly Reports', 'General', 'Announcements']:
                category_id = cat['id']
                print(f"Using discussion category: {cat['name']}")
                break
        
        if not category_id and categories:
            # Use first available category
            category_id = categories[0]['id']
            print(f"Using discussion category: {categories[0]['name']}")
        
        if not category_id:
            print("WARNING: No discussion categories found")
            return False
        
        # Create the discussion
        mutation = """
        mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
          createDiscussion(input: {
            repositoryId: $repositoryId,
            categoryId: $categoryId,
            title: $title,
            body: $body
          }) {
            discussion {
              url
            }
          }
        }
        """
        
        # Create discussion using gh CLI with proper parameter passing
        # -F flags properly escape and pass parameters to prevent injection
        result = subprocess.run(
            ['gh', 'api', 'graphql', '-f', f'query={mutation}',
             '-F', f'repositoryId={repo_id}',
             '-F', f'categoryId={category_id}',
             '-F', f'title={title}',
             '-F', f'body={body}'],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, 'GH_TOKEN': token}
        )
        
        data = json.loads(result.stdout)
        discussion_url = data['data']['createDiscussion']['discussion']['url']
        
        print(f"Successfully created discussion: {discussion_url}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create discussion: {e.stderr}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error creating discussion: {e}")
        return False


def main():
    """Main function to create GitHub Discussion for weekly report"""
    week_number = get_iso_week_number()
    year = get_iso_year()
    
    # Find the report file
    repo_root = Path(__file__).parent.parent.parent
    report_file = repo_root / "docs" / "reports" / f"week-{week_number}.md"
    
    if not report_file.exists():
        print(f"ERROR: Report file not found: {report_file}")
        sys.exit(1)
    
    # Read report content
    with open(report_file, 'r') as f:
        report_content = f.read()
    
    # Extract summary for discussion
    discussion_body = extract_summary(report_content)
    
    # Create title
    title = f"Weekly Report Discussion - Week {week_number}, {year}"
    
    # Create discussion
    success = create_github_discussion(title, discussion_body)
    
    if not success:
        print("WARNING: Discussion creation skipped or failed")
        # Don't fail the workflow - discussion creation is optional


if __name__ == '__main__':
    main()
