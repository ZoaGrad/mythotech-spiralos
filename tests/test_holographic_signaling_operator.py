import unittest

from codex.spiralos.operators.spiral.holographic_signaling_operator import (
    HolographicSignalingOperator,
)


class TestHolographicSignalingOperator(unittest.TestCase):
    def setUp(self) -> None:
        self.op = HolographicSignalingOperator(alpha=2.5, latency_weight=0.2)

    def test_basic_ingest_and_select(self):
        frames = [
            {
                "node_id": "pure_fast",
                "epoch": 1,
                "scar_index": 0,
                "load_percent": 0.3,
                "headroom_ru": 7000,
                "latency_ms": 50,
            },
            {
                "node_id": "scarred_heavy",
                "epoch": 1,
                "scar_index": 50,
                "load_percent": 0.9,
                "headroom_ru": 10000,
                "latency_ms": 30,
            },
        ]

        self.op.ingest_health_frames(frames)
        next_hop = self.op.select_next_hop(
            {
                "min_headroom_ru": 1000,
                "max_latency_ms": 200,
                "max_scar_index": 100,
            }
        )

        # We expect "pure_fast" to win despite slightly higher latency,
        # because its scar_index is much lower and α=2.5 penalizes heavily.
        self.assertEqual(next_hop, "pure_fast")

    def test_truth_frame_overrides_gossip(self):
        # Initial gossip: node claims to be pure and fast
        gossip_frame = {
            "node_id": "node_x",
            "epoch": 5,
            "scar_index": 0,
            "load_percent": 0.2,
            "headroom_ru": 8000,
            "latency_ms": 40,
        }
        self.op.ingest_health_frames([gossip_frame])

        hologram_before = self.op.get_hologram_snapshot()
        self.assertIn("node_x", hologram_before)
        self.assertEqual(hologram_before["node_x"]["scar_index"], 0)

        # Truth: node is actually scarred (SI=60) and overloaded
        truth_frame = {
            "health_frame": {
                "node_id": "node_x",
                "epoch": 6,
                "scar_index": 60,
                "load_percent": 1.1,
                "headroom_ru": -500,
                "latency_ms": 120,
            },
            "witness_multisig": ["sig_a", "sig_b"],
        }

        self.op.ingest_truth_frames([truth_frame])
        hologram_after = self.op.get_hologram_snapshot()

        self.assertEqual(hologram_after["node_x"]["scar_index"], 60)
        self.assertTrue(hologram_after["node_x"]["is_truth_anchored"])
        self.assertLess(hologram_after["node_x"]["crs"], hologram_before["node_x"]["crs"])

    def test_constraints_filter_out_bad_nodes(self):
        frames = [
            {
                "node_id": "good_node",
                "epoch": 1,
                "scar_index": 2,
                "load_percent": 0.4,
                "headroom_ru": 5000,
                "latency_ms": 80,
            },
            {
                "node_id": "too_scarred",
                "epoch": 1,
                "scar_index": 90,
                "load_percent": 0.1,
                "headroom_ru": 9000,
                "latency_ms": 10,
            },
        ]
        self.op.ingest_health_frames(frames)

        hop = self.op.select_next_hop(
            {
                "max_scar_index": 10,
                "min_headroom_ru": 1000,
                "max_latency_ms": 200,
            }
        )
        self.assertEqual(hop, "good_node")

    def test_no_candidates_returns_none(self):
        frames = [
            {
                "node_id": "overloaded",
                "epoch": 1,
                "scar_index": 10,
                "load_percent": 1.5,
                "headroom_ru": -1000,
                "latency_ms": 50,
            }
        ]
        self.op.ingest_health_frames(frames)
        hop = self.op.select_next_hop({"min_headroom_ru": 1})
        self.assertIsNone(hop)


if __name__ == "__main__":
    unittest.main()
