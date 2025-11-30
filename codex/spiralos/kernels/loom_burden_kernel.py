import dataclasses


@dataclasses.dataclass
class NodeState:
    node_id: str
    scarcoin_holdings: int
    individual_scar_index: int
    current_weave_threshold: int = 0


class LoomBurdenKernel:
    def __init__(self, config: dict):
        self.config = config
        self.sys_const = config["system_constants"]
        self.weights = config["resource_weights"]

    def calculate_threshold(self, node: NodeState, global_si: int, total_supply: int) -> int:
        if total_supply == 0:
            return 0

        c_base = self.sys_const["base_capacity_constant"]
        si_max = self.sys_const["max_scar_index"]

        stake_factor = node.scarcoin_holdings / total_supply
        integrity_factor = max(0, (si_max - node.individual_scar_index) / si_max)
        global_factor = max(0, (si_max - global_si) / si_max)

        threshold = c_base * stake_factor * integrity_factor * global_factor
        return max(int(threshold), self.sys_const["min_capacity_floor"])

    def normalize_metrics(self, cpu: int, storage: int, egress: int) -> int:
        w = self.weights
        ru = (cpu * w["compute_weight"]) + (storage * w["storage_weight"]) + (egress * w["egress_weight"])
        return int(ru)

    def detect_violation(self, usage_ru: int, threshold: int) -> dict:
        if usage_ru <= threshold:
            return {"violation": False, "magnitude": 0}
        return {"violation": True, "magnitude": usage_ru - threshold}
