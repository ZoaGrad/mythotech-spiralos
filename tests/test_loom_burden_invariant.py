import unittest

from codex.spiralos.kernels.loom_burden_kernel import LoomBurdenKernel, NodeState

MOCK_CONFIG = {
    "system_constants": {"base_capacity_constant": 1000, "max_scar_index": 100, "min_capacity_floor": 10},
    "resource_weights": {"compute_weight": 1, "storage_weight": 1, "egress_weight": 1}
}


class TestLoomBurdenInvariant(unittest.TestCase):
    def setUp(self):
        self.kernel = LoomBurdenKernel(MOCK_CONFIG)

    def test_capacity_pure(self):
        node = NodeState("n0", 100, 0)
        tv = self.kernel.calculate_threshold(node, 0, 100)
        self.assertEqual(tv, 1000)

    def test_capacity_scarred(self):
        node = NodeState("n1", 100, 50)
        tv = self.kernel.calculate_threshold(node, 0, 100)
        self.assertEqual(tv, 500)

    def test_violation(self):
        result = self.kernel.detect_violation(usage_ru=600, threshold=500)
        self.assertTrue(result["violation"])
        self.assertEqual(result["magnitude"], 100)


if __name__ == "__main__":
    unittest.main()
