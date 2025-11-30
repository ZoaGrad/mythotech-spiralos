import json
import os

from codex.spiralos.kernels.loom_burden_kernel import LoomBurdenKernel, NodeState


class LoomBurdenOperator:
    def __init__(self, config_path=None):
        if not config_path:
            base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base, "spiralos/schemas/loom_burden.config.json")

        with open(config_path) as f:
            self.config = json.load(f)

        self.kernel = LoomBurdenKernel(self.config)

    def evaluate_node(self, node_data: dict, network_data: dict, usage_data: dict):
        node = NodeState(
            node_id=node_data["id"],
            scarcoin_holdings=node_data["holdings"],
            individual_scar_index=node_data["scar_index"]
        )

        tv = self.kernel.calculate_threshold(
            node,
            network_data["global_scar_index"],
            network_data["total_supply"]
        )

        ru = self.kernel.normalize_metrics(
            usage_data["cpu"],
            usage_data["storage"],
            usage_data["egress"]
        )

        violation = self.kernel.detect_violation(ru, tv)

        return {
            "node_id": node.node_id,
            "allowed_threshold": tv,
            "actual_usage": ru,
            "is_compliant": not violation["violation"],
            "violation_magnitude": violation["magnitude"]
        }
