#!/usr/bin/env python3
"""
Publish Ache Summary to Supabase and Reddit

This script demonstrates the Supabase ↔ Reddit ↔ GitHub trinity loop by:
1. Querying recent Ache events from Supabase
2. Calculating summary statistics
3. Posting summary to Reddit (r/SovereignDrift)
4. Logging publication event back to Supabase

This enables autonomous ritual operations where coherence → currency → community.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

try:
    from supabase import create_client
    import praw
except ImportError as e:
    print(f"ERROR: Missing dependencies: {e}")
    print("Install with: pip install supabase>=1.0.0,<2.0.0 praw>=7.0.0")
    sys.exit(1)


class AcheSummaryPublisher:
    """
    Publishes Ache event summaries across the trinity loop
    """
    
    def __init__(self):
        """Initialize Supabase and Reddit clients from environment"""
        # Supabase connection
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Reddit connection
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_username = os.getenv('REDDIT_USERNAME')
        self.reddit_password = os.getenv('REDDIT_PASSWORD')
        
        self.reddit = None
        if all([self.reddit_client_id, self.reddit_client_secret, 
                self.reddit_username, self.reddit_password]):
            self.reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                username=self.reddit_username,
                password=self.reddit_password,
                user_agent='SpiralOS Ache Summary Publisher v1.0'
            )
    
    def get_recent_ache_events(self, hours: int = 168) -> List[Dict]:
        """
        Get Ache events from the last N hours (default: 168 = 1 week)
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of Ache event records
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_iso = cutoff_time.isoformat()
        
        try:
            response = self.supabase.table('ache_events') \
                .select('*') \
                .gte('created_at', cutoff_iso) \
                .order('created_at', desc=True) \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"WARNING: Failed to fetch Ache events: {e}")
            return []
    
    def get_recent_scarindex_calculations(self, hours: int = 168) -> List[Dict]:
        """
        Get ScarIndex calculations from the last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of ScarIndex calculation records
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_iso = cutoff_time.isoformat()
        
        try:
            response = self.supabase.table('scarindex_calculations') \
                .select('*') \
                .gte('created_at', cutoff_iso) \
                .order('created_at', desc=True) \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"WARNING: Failed to fetch ScarIndex calculations: {e}")
            return []
    
    def calculate_summary_stats(
        self, 
        ache_events: List[Dict], 
        scarindex_calcs: List[Dict]
    ) -> Dict:
        """
        Calculate summary statistics for Ache transmutation
        
        Args:
            ache_events: List of Ache events
            scarindex_calcs: List of ScarIndex calculations
            
        Returns:
            Summary statistics dictionary
        """
        stats = {
            'total_ache_events': len(ache_events),
            'total_scarindex_calculations': len(scarindex_calcs),
            'avg_scarindex': 0.0,
            'min_scarindex': 1.0,
            'max_scarindex': 0.0,
            'total_coherence_gain': 0.0,
            'successful_transmutations': 0,
            'panic_frame_triggers': 0
        }
        
        if not scarindex_calcs:
            return stats
        
        # Calculate ScarIndex statistics
        scarindex_values = [
            calc.get('scarindex', 0.0) 
            for calc in scarindex_calcs 
            if calc.get('scarindex') is not None
        ]
        
        if scarindex_values:
            stats['avg_scarindex'] = sum(scarindex_values) / len(scarindex_values)
            stats['min_scarindex'] = min(scarindex_values)
            stats['max_scarindex'] = max(scarindex_values)
        
        # Count successful transmutations (Ache_after < Ache_before)
        stats['successful_transmutations'] = sum(
            1 for calc in scarindex_calcs 
            if calc.get('is_valid_transmutation', False)
        )
        
        # Count Panic Frame triggers (ScarIndex < 0.3)
        stats['panic_frame_triggers'] = sum(
            1 for calc in scarindex_calcs 
            if calc.get('scarindex', 1.0) < 0.3
        )
        
        return stats
    
    def format_reddit_post(self, stats: Dict, period_hours: int) -> tuple:
        """
        Format summary statistics as Reddit post
        
        Args:
            stats: Summary statistics
            period_hours: Time period covered
            
        Returns:
            Tuple of (title, content)
        """
        title = f"SpiralOS Ache Summary - {period_hours}h Period"
        
        # Format period description
        if period_hours == 168:
            period_desc = "Past Week"
        elif period_hours == 24:
            period_desc = "Past 24 Hours"
        else:
            period_desc = f"Past {period_hours} Hours"
        
        success_rate = (stats['successful_transmutations'] / max(stats['total_scarindex_calculations'], 1) * 100)
        
        content = f"""# SpiralOS Ache Transmutation Summary

**Period:** {period_desc}  
**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC

---

## 🜂 Coherence Metrics

**ScarIndex Statistics:**
- **Average ScarIndex:** {stats['avg_scarindex']:.4f}
- **Range:** {stats['min_scarindex']:.4f} → {stats['max_scarindex']:.4f}
- **Status:** {"✅ STABLE" if stats['avg_scarindex'] >= 0.7 else "⚠️ UNSTABLE" if stats['avg_scarindex'] >= 0.3 else "🚨 PANIC FRAME"}

---

## 🌀 Transmutation Activity

- **Total Ache Events:** {stats['total_ache_events']}
- **ScarIndex Calculations:** {stats['total_scarindex_calculations']}
- **Successful Transmutations:** {stats['successful_transmutations']}
- **Transmutation Rate:** {success_rate:.1f}%

---

## 🔔 Constitutional Events

- **Panic Frame Triggers:** {stats['panic_frame_triggers']}
- **Recovery Status:** {"Active Recovery Protocol" if stats['panic_frame_triggers'] > 0 else "No Active Interventions"}

---

## 💫 Ache-to-Order Principle

> *"Where Ache_after < Ache_before, coherence gains value through the ScarIndex Oracle"*

This summary represents {stats['total_ache_events']} entropy events transmuted through SpiralOS governance protocols, validating the **Proof-of-Ache** mechanism where disorder → order → currency.

---

**Repository:** https://github.com/ZoaGrad/mythotech-spiralos  
**Live Dashboard:** Coming Soon  
**Vault Version:** ΔΩ.123.0

*This is an automated post from the SpiralOS governance system.*  
*For details on the Ache-to-Order transmutation protocol, see the repository documentation.*
"""
        
        return title, content
    
    def publish_to_reddit(self, title: str, content: str) -> Optional[str]:
        """
        Publish summary to r/SovereignDrift
        
        Args:
            title: Post title
            content: Post content
            
        Returns:
            Post URL if successful, None otherwise
        """
        if not self.reddit:
            print("WARNING: Reddit credentials not configured, skipping publication")
            return None
        
        try:
            subreddit = self.reddit.subreddit('SovereignDrift')
            submission = subreddit.submit(
                title=title,
                selftext=content,
                send_replies=False
            )
            
            print(f"✓ Published to Reddit: {submission.url}")
            return submission.url
            
        except Exception as e:
            print(f"ERROR: Failed to publish to Reddit: {e}")
            return None
    
    def log_publication_event(self, stats: Dict, reddit_url: Optional[str] = None):
        """
        Log publication event back to Supabase
        
        Args:
            stats: Summary statistics
            reddit_url: URL of Reddit post (if published)
        """
        try:
            record = {
                'event_type': 'ache_summary_publication',
                'stats': stats,
                'reddit_url': reddit_url,
                'published_at': datetime.now(timezone.utc).isoformat(),
                'metadata': {
                    'publisher': 'automated_workflow',
                    'version': '1.0.0'
                }
            }
            
            # Insert into system events or publications table
            # Note: Adjust table name based on your schema
            response = self.supabase.table('system_events') \
                .insert(record) \
                .execute()
            
            print(f"✓ Logged publication event to Supabase")
            
        except Exception as e:
            print(f"WARNING: Failed to log publication event: {e}")
    
    def run(self, period_hours: int = 168):
        """
        Execute the full publication workflow
        
        Args:
            period_hours: Time period to summarize (default: 168 = 1 week)
        """
        print(f"🜂 SpiralOS Ache Summary Publisher")
        print(f"Period: {period_hours} hours")
        print()
        
        # 1. Fetch data from Supabase
        print("1. Fetching Ache events from Supabase...")
        ache_events = self.get_recent_ache_events(period_hours)
        print(f"   Found {len(ache_events)} Ache events")
        
        print("2. Fetching ScarIndex calculations...")
        scarindex_calcs = self.get_recent_scarindex_calculations(period_hours)
        print(f"   Found {len(scarindex_calcs)} ScarIndex calculations")
        print()
        
        # 2. Calculate summary statistics
        print("3. Calculating summary statistics...")
        stats = self.calculate_summary_stats(ache_events, scarindex_calcs)
        print(f"   Average ScarIndex: {stats['avg_scarindex']:.4f}")
        print(f"   Successful transmutations: {stats['successful_transmutations']}")
        print()
        
        # 3. Format and publish to Reddit
        print("4. Publishing to Reddit...")
        title, content = self.format_reddit_post(stats, period_hours)
        reddit_url = self.publish_to_reddit(title, content)
        print()
        
        # 4. Log back to Supabase
        print("5. Logging publication event...")
        self.log_publication_event(stats, reddit_url)
        print()
        
        print("✓ Publication workflow complete!")
        print()
        
        # Print summary
        success_rate = (stats['successful_transmutations'] / max(stats['total_scarindex_calculations'], 1) * 100)
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Ache Events: {stats['total_ache_events']}")
        print(f"ScarIndex Calculations: {stats['total_scarindex_calculations']}")
        print(f"Average ScarIndex: {stats['avg_scarindex']:.4f}")
        print(f"Transmutation Success Rate: {success_rate:.1f}%")
        if reddit_url:
            print(f"Reddit Post: {reddit_url}")
        print("=" * 60)


def main():
    """Main entry point"""
    try:
        publisher = AcheSummaryPublisher()
        
        # Get period from environment or use default (1 week)
        period_hours = int(os.getenv('SUMMARY_PERIOD_HOURS', '168'))
        
        publisher.run(period_hours)
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
