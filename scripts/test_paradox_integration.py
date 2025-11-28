import unittest
import sys
import os
import uuid
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from core.paradox_layer import ParadoxEngine, ParadoxCandidate, ParadoxDetector
from core.mirror_layer import MirrorLayer
from core.coherence import CoherenceEngine
from core.db import db

class TestParadoxIntegration(unittest.TestCase):
    
    def setUp(self):
        self.mirror = MirrorLayer()
        self.coherence = CoherenceEngine()
        self.engine = ParadoxEngine(self.mirror, self.coherence)

    def test_paradox_detection_and_resolution(self):
        """
        Verify that the engine detects candidates and resolves them.
        Since we don't have real conflicts in DB, we mock the detector's scan_all.
        """
        print("\n🔹 Testing Paradox Detection & Resolution...")
        
        # Mock detector to return a synthetic candidate
        synthetic_candidate = ParadoxCandidate(
            entity_a_type="council_judgment",
            entity_a_id=str(uuid.uuid4()),
            entity_b_type="council_judgment",
            entity_b_id=str(uuid.uuid4()),
            paradox_kind="council_conflict",
            severity=0.8
        )
        
        self.engine.detector.scan_all = MagicMock(return_value=[synthetic_candidate])
        
        # Run cycle
        result = self.engine.run_cycle()
        
        self.assertEqual(result['candidates'], 1)
        self.assertEqual(result['resolved'], 1)
        print(f"✅ Paradox Cycle: {result}")

    def test_resolution_strategy_selection(self):
        """
        Verify that the resolver picks the correct strategy based on severity/kind.
        """
        print("\n🔹 Testing Strategy Selection...")
        
        resolver = self.engine.resolver
        
        # Case 1: Severe governance conflict -> prioritize
        c1 = ParadoxCandidate("gov", "1", "gov", "2", "governance_conflict", 0.9)
        s1 = resolver._choose_strategy(c1)
        self.assertEqual(s1, "prioritize")
        
        # Case 2: Mild reflection conflict -> reconcile
        c2 = ParadoxCandidate("ref", "1", "ref", "2", "reflection_conflict", 0.5)
        s2 = resolver._choose_strategy(c2)
        self.assertEqual(s2, "reconcile")
        
        print(f"✅ Strategies Verified: {s1}, {s2}")

if __name__ == '__main__':
    unittest.main()
