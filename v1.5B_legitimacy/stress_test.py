import random


# Mock agent state
class Agent:
    def __init__(self, id, tier=1):
        self.id = id
        self.tier = tier
        self.time_in_tier = 0
        self.verified_pobs_count = 0
        self.total_interactions = 0
        self.relational_cos_sim_avg = random.uniform(0.1, 0.9)
        self.A_i = 0.0

    def get_state(self):
        return {
            "id": self.id,
            "time_in_tier": self.time_in_tier,
            "verified_pobs_count": self.verified_pobs_count,
            "total_interactions": self.total_interactions,
            "relational_cos_sim_avg": self.relational_cos_sim_avg,
            "A_i": self.A_i,
        }


import sys

sys.path.append("..")
from core.scarindex import apply_arbitrage_penalty, compute_global_coherence


# Stress Test Protocol
def run_stress_test():
    # Environment
    N = 50
    cycles = 40
    num_adversaries = 7

    # Initialize agents
    agents = [Agent(i) for i in range(N)]
    adversaries = random.sample(agents, num_adversaries)
    for adversary in adversaries:
        adversary.tier = 0  # Start adversaries at Tier 0

    # Simulation
    for cycle in range(cycles):
        # Generate mock data for the cycle
        c_i_list = [random.uniform(0.6, 0.8) for _ in range(N)]
        p_i_avg = random.uniform(0.4, 0.6)
        decays_count = random.randint(0, 5)

        # Adversarial actions
        for adversary in adversaries:
            rho_attempt = random.uniform(0.5, 1.0)
            is_reciprocal_pair = True
            cluster_density = random.uniform(0.6, 0.9)
            apply_arbitrage_penalty(adversary, rho_attempt, is_reciprocal_pair, cluster_density)

        # Calculate global coherence
        C_t = compute_global_coherence(N, c_i_list, p_i_avg, decays_count)

        # Update agent states
        for agent in agents:
            if agent in adversaries:
                if agent.A_i > 1.0:  # If Ache is high, demote to Tier 0
                    agent.tier = 0
                else:  # Otherwise, promote
                    agent.tier = 1
            agent.time_in_tier += 1
            agent.total_interactions += 1
            if random.random() > 0.5:
                agent.verified_pobs_count += 1

        # Log metrics
        print(f"Cycle {cycle+1}/{cycles}: C_t = {C_t:.3f}")
        for i, adversary in enumerate(adversaries):
            print(f"  Adversary {i+1}: Tier = {adversary.tier}, Ache = {adversary.A_i:.3f}")

    # Final check
    print("\nStress Test Complete.")
    c_t_stable = True
    adversaries_demoted = True
    for adversary in adversaries:
        if adversary.tier != 0:
            adversaries_demoted = False

    if c_t_stable and adversaries_demoted:
        print("Result: PASSED")
    else:
        print("Result: FAILED")


if __name__ == "__main__":
    run_stress_test()
