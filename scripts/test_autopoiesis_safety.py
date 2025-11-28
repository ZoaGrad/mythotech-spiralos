import unittest
import sys
import os
from typing import Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.autopoiesis_safety import AutopoiesisSafetyCoordinator, StructuralIntent, WhitelistViolation, SafetyPolicyViolation
from core.teleology import TauVector
from core.coherence import CoherenceEngine
from core.db import db

class TestAutopoiesisSafety(unittest.TestCase):
    def setUp(self):
        self.tau = TauVector(components={"coherence_preservation": 1.0, "identity_refinement": 0.5})
        self.coherence = CoherenceEngine()
        self.coordinator = AutopoiesisSafetyCoordinator(self.tau, self.coherence)

    def test_whitelist_violation(self):
        intent = StructuralIntent(
            requester="test_agent",
            op_code="DROP_TABLE", # Not whitelisted
            target_schema="public",
            target_object="users",
            sql_diff="DROP TABLE users;",
            reason="Malicious intent",
            action_vector={"coherence_preservation": 1.0}
        )
        with self.assertRaises(WhitelistViolation):
            self.coordinator.submit_structural_intent(intent)

    def test_policy_violation_low_alignment(self):
        # J0_DEFAULT requires tau_min_alignment 0.707
        intent = StructuralIntent(
            requester="test_agent",
            op_code="ADD_COLUMN_NULLABLE",
            target_schema="public",
            target_object="test_table",
            sql_diff="ALTER TABLE test_table ADD COLUMN new_col TEXT;",
            reason="Testing policy",
            action_vector={"coherence_preservation": 0.1} # Low alignment
        )
        # 0.1 * 1.0 = 0.1 < 0.707
        with self.assertRaises(SafetyPolicyViolation):
            self.coordinator.submit_structural_intent(intent)

    def test_valid_submission(self):
        intent = StructuralIntent(
            requester="test_agent",
            op_code="ADD_COLUMN_NULLABLE",
            target_schema="public",
            target_object="test_table",
            sql_diff="ALTER TABLE test_table ADD COLUMN new_col TEXT;",
            reason="Valid change",
            action_vector={"coherence_preservation": 0.9} # High alignment
        )
        # 0.9 * 1.0 = 0.9 > 0.707
        change_id = self.coordinator.submit_structural_intent(intent)
        self.assertIsNotNone(change_id)
        print(f"Submitted valid change request: {change_id}")

if __name__ == '__main__':
    unittest.main()
