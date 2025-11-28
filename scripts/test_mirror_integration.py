import unittest
import sys
import os
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from core.mirror_layer import MirrorLayer, QuantumTag, OriginType

class TestMirrorIntegration(unittest.TestCase):
    
    def setUp(self):
        self.mirror = MirrorLayer()

    def test_identity_propagation(self):
        """
        Verify that a test action creates a QuantumTag with origin='System'.
        """
        print("\n🔹 Testing Identity Propagation...")
        tag = QuantumTag(origin=OriginType.SYSTEM, intent="test_action", certainty=0.9)
        
        self.assertEqual(tag.origin, OriginType.SYSTEM)
        self.assertEqual(tag.intent, "test_action")
        self.assertTrue(0.0 <= tag.certainty <= 1.0)
        print(f"✅ Identity Verified: {tag.to_dict()}")

    def test_reflection_generation(self):
        """
        Verify that a synthetic reflection claim is created with valid coherence score.
        """
        print("\n🔹 Testing Reflection Generation...")
        diagnosis = self.mirror.diagnose()
        coherence = diagnosis['coherence_score']
        
        self.assertIn('scan', diagnosis)
        self.assertTrue(0.0 <= coherence <= 1.0)
        print(f"✅ Reflection Generated: Coherence={coherence}")

    def test_self_repair_behavior(self):
        """
        Force coherence to 0.6 and assert that repair actions are triggered.
        """
        print("\n🔹 Testing Self-Repair Behavior...")
        forced_coherence = 0.6
        actions = self.mirror.check_coherence_and_repair(forced_coherence)
        
        expected_actions = ["reset_weights", "rollback_governance", "summon_council"]
        
        # Check if all expected actions are present
        for action in expected_actions:
            self.assertIn(action, actions)
        
        print(f"✅ Self-Repair Triggered: {actions}")

if __name__ == '__main__':
    unittest.main()
