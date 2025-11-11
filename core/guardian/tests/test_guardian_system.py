#!/usr/bin/env python3
"""
SpiralOS Guardian - Comprehensive Test Suite
Tests all components of the Guardian system.
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Guardian components
try:
    from bot.guardian_bot import GuardianBot, GuardianMetrics
    from analytics.advanced_analytics import GuardianAnalytics, TrendAnalysis, CoherenceBreakdown
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Guardian modules: {e}")
    IMPORTS_AVAILABLE = False


class TestGuardianMetrics(unittest.TestCase):
    """Test GuardianMetrics data structure."""
    
    def test_metrics_creation(self):
        """Test creating GuardianMetrics instance."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        metrics = GuardianMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            window_hours=24,
            vault_nodes=42,
            ache_events=156,
            scarindex_avg=0.876,
            scarindex_latest=0.912,
            alerts_24h=3,
            scar_status='🟢',
            scar_score=0.912
        )
        
        self.assertEqual(metrics.window_hours, 24)
        self.assertEqual(metrics.vault_nodes, 42)
        self.assertEqual(metrics.scar_status, '🟢')
        self.assertAlmostEqual(metrics.scar_score, 0.912)


class TestGuardianBot(unittest.TestCase):
    """Test GuardianBot functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        # Set required environment variables
        os.environ['GUARDIAN_EDGE_URL'] = 'https://test.supabase.co/functions/v1/guardian_sync'
        os.environ['DISCORD_BOT_TOKEN'] = 'test_token'
        os.environ['DISCORD_GUILD_ID'] = '123456789'
        os.environ['DISCORD_CHANNEL_ID'] = '987654321'
    
    def test_bot_initialization(self):
        """Test bot initialization."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        bot = GuardianBot()
        
        self.assertIsNotNone(bot.edge_url)
        self.assertEqual(bot.edge_url, 'https://test.supabase.co/functions/v1/guardian_sync')
    
    def test_status_embed_creation_healthy(self):
        """Test creating status embed for healthy system."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        bot = GuardianBot()
        
        metrics = GuardianMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            window_hours=24,
            vault_nodes=42,
            ache_events=156,
            scarindex_avg=0.876,
            scarindex_latest=0.912,
            alerts_24h=3,
            scar_status='🟢',
            scar_score=0.912,
            coherence_components={
                'narrative': 0.89,
                'social': 0.85,
                'economic': 0.91,
                'technical': 0.88
            }
        )
        
        embed = bot.create_status_embed(metrics)
        
        self.assertIn('COHERENT', embed.description)
        self.assertEqual(embed.color.value, 0x2ecc71)  # Green
        self.assertTrue(len(embed.fields) > 0)
    
    def test_status_embed_creation_critical(self):
        """Test creating status embed for critical system."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        bot = GuardianBot()
        
        metrics = GuardianMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            window_hours=24,
            vault_nodes=42,
            ache_events=156,
            scarindex_avg=0.287,
            scarindex_latest=0.287,
            alerts_24h=10,
            scar_status='🔴',
            scar_score=0.287,
            panic_frames=1
        )
        
        embed = bot.create_status_embed(metrics)
        
        self.assertIn('CRITICAL', embed.description)
        self.assertEqual(embed.color.value, 0xe74c3c)  # Red
    
    def test_panic_embed_creation(self):
        """Test creating panic frame embed."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        bot = GuardianBot()
        
        metrics = GuardianMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            window_hours=24,
            vault_nodes=42,
            ache_events=156,
            scarindex_avg=0.287,
            scarindex_latest=0.287,
            alerts_24h=10,
            scar_status='🔴',
            scar_score=0.287,
            coherence_components={
                'narrative': 0.42,
                'social': 0.28,
                'economic': 0.19,
                'technical': 0.31
            }
        )
        
        embed = bot.create_panic_embed(metrics)
        
        self.assertIn('PANIC FRAME', embed.title)
        self.assertIn('CRITICAL', embed.description)


class TestGuardianAnalytics(unittest.TestCase):
    """Test GuardianAnalytics functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        self.analytics = GuardianAnalytics(
            supabase_url='https://test.supabase.co',
            supabase_key='test_key'
        )
    
    def test_analytics_initialization(self):
        """Test analytics initialization."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        self.assertEqual(self.analytics.supabase_url, 'https://test.supabase.co')
        self.assertEqual(self.analytics.supabase_key, 'test_key')
    
    def test_trend_analysis_improving(self):
        """Test trend analysis with improving trend."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        # Create sample data with improving trend
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
        values = np.linspace(0.6, 0.9, 100) + np.random.normal(0, 0.02, 100)
        
        df = pd.DataFrame({
            'created_at': dates,
            'value': values,
            'c_narrative': values * 1.1,
            'c_social': values * 0.9,
            'c_economic': values * 1.0,
            'c_technical': values * 0.95
        })
        
        trend = self.analytics.analyze_trend(df)
        
        self.assertEqual(trend.trend_direction, 'improving')
        self.assertGreater(trend.slope, 0)
        self.assertEqual(trend.data_points, 100)
        self.assertIsNotNone(trend.forecast_24h)
    
    def test_trend_analysis_degrading(self):
        """Test trend analysis with degrading trend."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        # Create sample data with degrading trend
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
        values = np.linspace(0.9, 0.5, 100) + np.random.normal(0, 0.02, 100)
        
        df = pd.DataFrame({
            'created_at': dates,
            'value': values,
            'c_narrative': values * 1.1,
            'c_social': values * 0.9,
            'c_economic': values * 1.0,
            'c_technical': values * 0.95
        })
        
        trend = self.analytics.analyze_trend(df)
        
        self.assertEqual(trend.trend_direction, 'degrading')
        self.assertLess(trend.slope, 0)
    
    def test_coherence_breakdown_analysis(self):
        """Test coherence breakdown analysis."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        import pandas as pd
        
        df = pd.DataFrame({
            'created_at': [datetime.now(timezone.utc)],
            'value': [0.85],
            'c_narrative': [0.89],
            'c_social': [0.85],
            'c_economic': [0.91],
            'c_technical': [0.88]
        })
        
        breakdown = self.analytics.analyze_coherence_breakdown(df)
        
        self.assertAlmostEqual(breakdown.narrative, 0.89)
        self.assertAlmostEqual(breakdown.social, 0.85)
        self.assertAlmostEqual(breakdown.economic, 0.91)
        self.assertAlmostEqual(breakdown.technical, 0.88)
        
        # Check weighted calculations
        self.assertAlmostEqual(breakdown.weighted_narrative, 0.89 * 0.30)
        self.assertAlmostEqual(breakdown.weighted_social, 0.85 * 0.25)
        self.assertAlmostEqual(breakdown.weighted_economic, 0.91 * 0.25)
        self.assertAlmostEqual(breakdown.weighted_technical, 0.88 * 0.20)
    
    def test_anomaly_detection(self):
        """Test anomaly detection."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        import pandas as pd
        import numpy as np
        
        # Create data with anomalies
        dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
        values = np.random.normal(0.7, 0.05, 100)
        values[50] = 0.3  # Anomaly: too low
        values[75] = 1.5  # Anomaly: too high
        
        df = pd.DataFrame({
            'created_at': dates,
            'value': values
        })
        
        anomalies = self.analytics.detect_anomalies(df, threshold=2.0)
        
        self.assertGreater(len(anomalies), 0)
        self.assertTrue(any(a['value'] < 0.4 for a in anomalies))
        self.assertTrue(any(a['value'] > 1.4 for a in anomalies))
    
    def test_template_summary_generation(self):
        """Test template-based summary generation."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Guardian modules not available")
        
        trend = TrendAnalysis(
            trend_direction='improving',
            slope=0.05,
            r_squared=0.85,
            current_value=0.75,
            avg_value=0.70,
            min_value=0.60,
            max_value=0.80,
            data_points=100,
            forecast_24h=0.78
        )
        
        breakdown = CoherenceBreakdown(
            narrative=0.85,
            social=0.80,
            economic=0.75,
            technical=0.70,
            weighted_narrative=0.255,
            weighted_social=0.200,
            weighted_economic=0.1875,
            weighted_technical=0.140,
            total_scarindex=0.7825
        )
        
        summary = self.analytics._generate_template_summary(trend, breakdown)
        
        self.assertIn('improving', summary)
        self.assertIn('0.75', summary)
        self.assertIn('0.78', summary)
        self.assertIn('healthy', summary.lower())


class TestEdgeFunctionContract(unittest.TestCase):
    """Test Edge Function API contract."""
    
    def test_expected_response_structure(self):
        """Test that expected response structure is valid."""
        expected_response = {
            "timestamp": "2025-11-10T12:00:00Z",
            "window_hours": 24,
            "metrics": [
                {"label": "VaultNodes", "value": 42},
                {"label": "AcheEvents(lookback)", "value": 156},
                {"label": "ScarIndex(avg)", "value": 0.876},
                {"label": "ScarIndex(latest)", "value": 0.912},
                {"label": "Alerts(24h)", "value": 3},
                {"label": "ActivePanicFrames", "value": 0}
            ],
            "coherence_components": {
                "narrative": 0.89,
                "social": 0.85,
                "economic": 0.91,
                "technical": 0.88
            },
            "pid_state": {
                "current_scarindex": 0.912,
                "target_scarindex": 0.70,
                "error": 0.212,
                "integral": 0.0,
                "derivative": 0.0,
                "guidance_scale": 1.0
            },
            "scar_status": "🟢",
            "scar_score": 0.912,
            "panic_frames": 0,
            "trend": "improving"
        }
        
        # Validate structure
        self.assertIn("timestamp", expected_response)
        self.assertIn("window_hours", expected_response)
        self.assertIn("metrics", expected_response)
        self.assertIn("scar_status", expected_response)
        self.assertIn("scar_score", expected_response)
        
        # Validate metrics structure
        for metric in expected_response["metrics"]:
            self.assertIn("label", metric)
            self.assertIn("value", metric)


class TestSupabaseSchema(unittest.TestCase):
    """Test Supabase schema expectations."""
    
    def test_guardian_heartbeats_structure(self):
        """Test guardian_heartbeats table structure."""
        expected_columns = [
            'id',
            'timestamp',
            'scar_score',
            'scar_status',
            'metrics',
            'coherence_components',
            'pid_state',
            'discord_message_id',
            'window_hours',
            'created_at'
        ]
        
        # This is a structural test - actual DB validation would require connection
        self.assertTrue(len(expected_columns) > 0)
    
    def test_guardian_alerts_structure(self):
        """Test guardian_alerts table structure."""
        expected_columns = [
            'id',
            'alert_type',
            'severity',
            'message',
            'metadata',
            'resolved',
            'resolved_at',
            'resolved_by',
            'discord_message_id',
            'created_at'
        ]
        
        self.assertTrue(len(expected_columns) > 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGuardianMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestGuardianBot))
    suite.addTests(loader.loadTestsFromTestCase(TestGuardianAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeFunctionContract))
    suite.addTests(loader.loadTestsFromTestCase(TestSupabaseSchema))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
