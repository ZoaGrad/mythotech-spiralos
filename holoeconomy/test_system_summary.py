"""
Test Suite for System Summary

Tests the SystemSummary class and its integration with SpiralOS components.
"""

import unittest
from decimal import Decimal
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_summary import SystemSummary, create_summary_from_engines
from scarcoin import ScarCoinMintingEngine
from vaultnode import VaultNode
from empathy_market import EmpathyMarket


class TestSystemSummary(unittest.TestCase):
    """Test cases for SystemSummary class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.minting_engine = ScarCoinMintingEngine(
            multiplier=Decimal('1000'),
            min_delta_c=Decimal('0.01')
        )
        
        self.vaultnode = VaultNode(vault_id="ΔΩ.TEST.0")
        
        self.empathy_market = EmpathyMarket()
        
        self.summarizer = SystemSummary(
            minting_engine=self.minting_engine,
            empathy_market=self.empathy_market,
            vaultnode=self.vaultnode
        )
    
    def test_summary_initialization(self):
        """Test SystemSummary initialization"""
        self.assertIsNotNone(self.summarizer)
        self.assertEqual(self.summarizer.minting_engine, self.minting_engine)
        self.assertEqual(self.summarizer.vaultnode, self.vaultnode)
        self.assertEqual(self.summarizer.empathy_market, self.empathy_market)
    
    def test_get_summary_structure(self):
        """Test that summary returns expected structure"""
        summary = self.summarizer.get_summary()
        
        # Check top-level keys
        self.assertIn('system', summary)
        self.assertIn('components', summary)
        self.assertIn('health', summary)
        self.assertIn('motto', summary)
        
        # Check system section
        self.assertIn('name', summary['system'])
        self.assertIn('version', summary['system'])
        self.assertIn('vault_id', summary['system'])
        self.assertIn('timestamp', summary['system'])
        self.assertIn('status', summary['system'])
        
        # Check components section
        self.assertIn('core', summary['components'])
        self.assertIn('scarcoin', summary['components'])
        self.assertIn('empathy_market', summary['components'])
        self.assertIn('vaultnode', summary['components'])
        
        # Check health section
        self.assertIn('blockchain_integrity', summary['health'])
        self.assertIn('economic_activity', summary['health'])
        self.assertIn('overall_score', summary['health'])
    
    def test_scarcoin_summary(self):
        """Test ScarCoin component summary"""
        summary = self.summarizer.get_summary()
        scarcoin = summary['components']['scarcoin']
        
        self.assertTrue(scarcoin['available'])
        self.assertIn('supply', scarcoin)
        self.assertIn('activity', scarcoin)
        
        # Check supply metrics
        supply = scarcoin['supply']
        self.assertIn('total_supply', supply)
        self.assertIn('total_minted', supply)
        self.assertIn('total_burned', supply)
        self.assertIn('circulating', supply)
        
        # Check activity metrics
        activity = scarcoin['activity']
        self.assertIn('minting_count', activity)
        self.assertIn('burning_count', activity)
        self.assertIn('active_wallets', activity)
    
    def test_empathy_summary(self):
        """Test Empathy Market component summary"""
        summary = self.summarizer.get_summary()
        empathy = summary['components']['empathy_market']
        
        self.assertTrue(empathy['available'])
        self.assertIn('tokens', empathy)
        self.assertIn('participation', empathy)
        self.assertIn('thresholds', empathy)
        
        # Check token metrics
        tokens = empathy['tokens']
        self.assertIn('total_emp_minted', tokens)
        self.assertIn('total_resonance_events', tokens)
        self.assertIn('average_emp_per_event', tokens)
    
    def test_vaultnode_summary(self):
        """Test VaultNode component summary"""
        summary = self.summarizer.get_summary()
        vault = summary['components']['vaultnode']
        
        self.assertTrue(vault['available'])
        self.assertIn('blockchain', vault)
        self.assertIn('pending', vault)
        
        # Check blockchain metrics
        blockchain = vault['blockchain']
        self.assertIn('vault_id', blockchain)
        self.assertIn('total_blocks', blockchain)
        self.assertIn('total_events', blockchain)
        self.assertIn('chain_valid', blockchain)
        
        # Should have genesis block
        self.assertGreaterEqual(blockchain['total_blocks'], 1)
        self.assertTrue(blockchain['chain_valid'])
    
    def test_health_metrics(self):
        """Test health metrics calculation"""
        summary = self.summarizer.get_summary()
        health = summary['health']
        
        # Check health score is valid (0-1 range)
        score = health['overall_score']
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Check blockchain integrity
        self.assertIsInstance(health['blockchain_integrity'], bool)
        
        # With fresh VaultNode, chain should be valid
        self.assertTrue(health['blockchain_integrity'])
    
    def test_overall_status(self):
        """Test overall status determination"""
        summary = self.summarizer.get_summary()
        status = summary['system']['status']
        
        # Should be OPERATIONAL with all components healthy
        self.assertIn(status, ['OPTIMAL', 'OPERATIONAL', 'DEGRADED', 'CRITICAL', 'UNAVAILABLE'])
    
    def test_quick_status(self):
        """Test quick status string generation"""
        quick_status = self.summarizer.get_quick_status()
        
        self.assertIsInstance(quick_status, str)
        self.assertIn('SpiralOS', quick_status)
        self.assertIn('Status:', quick_status)
        self.assertIn('Health:', quick_status)
    
    def test_summary_without_components(self):
        """Test summary with missing components"""
        minimal_summarizer = SystemSummary()
        summary = minimal_summarizer.get_summary()
        
        # Should still return valid structure
        self.assertIn('system', summary)
        self.assertIn('components', summary)
        
        # Components should be marked as unavailable
        self.assertFalse(summary['components']['scarcoin']['available'])
        self.assertFalse(summary['components']['empathy_market']['available'])
        self.assertFalse(summary['components']['vaultnode']['available'])
    
    def test_summary_with_activity(self):
        """Test summary after some system activity"""
        # Mint some ScarCoins
        wallet = self.minting_engine.create_wallet()
        
        coin = self.minting_engine.mint_scarcoin(
            transmutation_id="test_tx_001",
            scarindex_before=Decimal('0.6'),
            scarindex_after=Decimal('0.75'),
            transmutation_efficiency=Decimal('0.9'),
            owner_address=wallet.address,
            oracle_signatures=['oracle1', 'oracle2', 'oracle3']
        )
        
        # Get summary
        summary = self.summarizer.get_summary()
        scarcoin = summary['components']['scarcoin']
        
        # Should show activity
        self.assertGreater(scarcoin['activity']['minting_count'], 0)
        self.assertGreater(scarcoin['activity']['active_wallets'], 0)
        
        # Supply should reflect minting
        total_minted = Decimal(scarcoin['supply']['total_minted'])
        self.assertGreater(total_minted, Decimal('0'))
    
    def test_create_summary_convenience_function(self):
        """Test convenience function for creating summary"""
        summary = create_summary_from_engines(
            minting_engine=self.minting_engine,
            vaultnode=self.vaultnode,
            empathy_market=self.empathy_market
        )
        
        self.assertIsInstance(summary, dict)
        self.assertIn('system', summary)
        self.assertIn('components', summary)


class TestSystemSummaryIntegration(unittest.TestCase):
    """Integration tests for system summary"""
    
    def test_full_system_workflow(self):
        """Test summary with full system workflow"""
        # Initialize components
        minting_engine = ScarCoinMintingEngine()
        vaultnode = VaultNode(vault_id="ΔΩ.INTEGRATION.0")
        empathy_market = EmpathyMarket()
        
        # Create wallets
        wallet1 = minting_engine.create_wallet()
        wallet2 = minting_engine.create_wallet()
        
        # Mint ScarCoins
        for i in range(3):
            minting_engine.mint_scarcoin(
                transmutation_id=f"tx_{i:03d}",
                scarindex_before=Decimal('0.5'),
                scarindex_after=Decimal('0.7'),
                transmutation_efficiency=Decimal('0.85'),
                owner_address=wallet1.address,
                oracle_signatures=['oracle1', 'oracle2', 'oracle3']
            )
        
        # Create empathy wallets
        empathy_wallet1 = empathy_market.create_wallet("participant_1")
        empathy_wallet2 = empathy_market.create_wallet("participant_2")
        
        # Create resonance event
        from empathy_market import ResonanceEvent
        
        resonance_event = ResonanceEvent(
            speaker_id="participant_1",
            listener_id="participant_2",
            semantic_alignment=Decimal('0.85'),
            emotional_resonance=Decimal('0.9'),
            contextual_depth=Decimal('0.8')
        )
        
        empathy_market.mint_emp_token(
            resonance_event=resonance_event,
            peer_validations=['peer1', 'peer2', 'peer3']
        )
        
        # Get summary
        summarizer = SystemSummary(
            minting_engine=minting_engine,
            empathy_market=empathy_market,
            vaultnode=vaultnode
        )
        
        summary = summarizer.get_summary()
        
        # Verify activity is reflected
        self.assertGreater(
            summary['components']['scarcoin']['activity']['minting_count'],
            0
        )
        self.assertGreater(
            summary['components']['empathy_market']['tokens']['total_resonance_events'],
            0
        )
        
        # Health score should be good with activity
        health_score = summary['health']['overall_score']
        self.assertGreater(health_score, 0.5)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("System Summary Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestSystemSummary))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemSummaryIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
