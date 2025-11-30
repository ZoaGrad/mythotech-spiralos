"""
Self-Organized Criticality (SOC) PID Controller

Enhances the AchePIDController to target Self-Organized Criticality state,
seeking the ideal power-law exponent for event sizes (τ ≈ 1.5).

SOC is a property of dynamical systems that have a critical point as an attractor.
Their macroscopic behavior exhibits the spatial or temporal scale-invariance
characteristic of the critical point of a phase transition, but without the need
to tune control parameters to a precise value.

In SpiralOS, SOC represents the optimal balance between:
- Creative exploration (Paradox Agent inducing instability)
- Structural regulation (Coherence maintenance)

The SOC PID Controller dynamically adjusts system parameters to maintain this
critical state, enabling "valley ascent dynamics" - controlled coherence dips
necessary to escape local optima and achieve higher global coherence maxima.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
from core.ache_pid_controller import AchePIDController


@dataclass
class SOCMetrics:
    """
    Self-Organized Criticality metrics

    Tracks power-law distribution of events and SOC state indicators.
    """

    tau: float = 0.0  # Power-law exponent (target ≈ 1.5)
    avalanche_sizes: List[float] = field(default_factory=list)
    correlation_length: float = 0.0
    susceptibility: float = 0.0
    fractal_dimension: float = 0.0

    # SOC state indicators
    is_critical: bool = False
    distance_from_criticality: float = 0.0

    def calculate_tau(self) -> float:
        """
        Calculate power-law exponent τ from avalanche size distribution

        For SOC, event sizes follow P(s) ~ s^(-τ)
        Target: τ ≈ 1.5 for optimal criticality
        """
        if len(self.avalanche_sizes) < 10:
            return 0.0

        # Log-log linear regression to estimate τ
        sizes = np.array(self.avalanche_sizes)
        sizes = sizes[sizes > 0]  # Remove zeros

        if len(sizes) < 10:
            return 0.0

        # Create bins
        bins = np.logspace(np.log10(sizes.min()), np.log10(sizes.max()), 20)
        hist, bin_edges = np.histogram(sizes, bins=bins)

        # Filter out zero counts
        nonzero = hist > 0
        if nonzero.sum() < 5:
            return 0.0

        log_sizes = np.log10(bin_edges[:-1][nonzero])
        log_counts = np.log10(hist[nonzero])

        # Linear regression: log(P) = -τ * log(s) + const
        tau_estimate = -np.polyfit(log_sizes, log_counts, 1)[0]

        self.tau = tau_estimate
        return tau_estimate

    def update_criticality_state(self, target_tau: float = 1.5, tolerance: float = 0.2):
        """
        Update SOC criticality state

        Args:
            target_tau: Target power-law exponent
            tolerance: Acceptable deviation from target
        """
        self.distance_from_criticality = abs(self.tau - target_tau)
        self.is_critical = self.distance_from_criticality <= tolerance

    def to_dict(self) -> Dict:
        return {
            "tau": self.tau,
            "avalanche_count": len(self.avalanche_sizes),
            "correlation_length": self.correlation_length,
            "susceptibility": self.susceptibility,
            "fractal_dimension": self.fractal_dimension,
            "is_critical": self.is_critical,
            "distance_from_criticality": self.distance_from_criticality,
        }


@dataclass
class ValleyAscentState:
    """
    Valley Ascent Dynamics state

    Tracks controlled coherence dips for escaping local optima.
    """

    in_descent: bool = False
    descent_start_scarindex: float = 0.0
    descent_depth: float = 0.0
    max_descent_depth: float = 0.2  # Maximum allowed coherence dip

    ascent_target: float = 0.0
    ascent_progress: float = 0.0

    local_optima_detected: bool = False
    global_maximum_estimate: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "in_descent": self.in_descent,
            "descent_start_scarindex": self.descent_start_scarindex,
            "descent_depth": self.descent_depth,
            "max_descent_depth": self.max_descent_depth,
            "ascent_target": self.ascent_target,
            "ascent_progress": self.ascent_progress,
            "local_optima_detected": self.local_optima_detected,
            "global_maximum_estimate": self.global_maximum_estimate,
        }


class SOCPIDController(AchePIDController):
    """
    Self-Organized Criticality PID Controller

    Extends AchePIDController to target SOC state and enable valley ascent dynamics.

    Key enhancements:
    1. SOC targeting: Adjust parameters to achieve τ ≈ 1.5
    2. Valley ascent: Allow controlled coherence dips to escape local optima
    3. Paradox parameter tuning: Dynamically adjust Paradox Agent parameters
    4. Complexity maximization: Shift from survival to complexity optimization
    """

    def __init__(
        self,
        target_scarindex: float = 0.7,
        target_tau: float = 1.5,
        kp: float = 1.0,
        ki: float = 0.5,
        kd: float = 0.2,
        min_guidance: float = 0.1,
        max_guidance: float = 2.0,
    ):
        super().__init__(target_scarindex, kp, ki, kd, min_guidance, max_guidance)

        # SOC parameters
        self.target_tau = target_tau
        self.soc_metrics = SOCMetrics()
        self.valley_ascent = ValleyAscentState()

        # Paradox Agent parameters
        self.paradox_intensity = 0.5  # How much instability to induce
        self.paradox_frequency = 0.1  # How often to induce instability

        # Complexity maximization
        self.complexity_weight = 0.3  # Weight for complexity vs coherence

    def update_soc(self, current_scarindex: float, event_size: float) -> Tuple[float, Dict]:
        """
        Update with SOC awareness

        Args:
            current_scarindex: Current ScarIndex value
            event_size: Size of current transmutation event

        Returns:
            Tuple of (guidance_scale, soc_state)
        """
        # Record avalanche size
        self.soc_metrics.avalanche_sizes.append(event_size)

        # Keep only recent avalanches (sliding window)
        if len(self.soc_metrics.avalanche_sizes) > 1000:
            self.soc_metrics.avalanche_sizes = self.soc_metrics.avalanche_sizes[-1000:]

        # Calculate τ periodically
        if len(self.soc_metrics.avalanche_sizes) % 50 == 0:
            self.soc_metrics.calculate_tau()
            self.soc_metrics.update_criticality_state(self.target_tau)

        # Standard PID update
        base_guidance = self.update(current_scarindex)

        # SOC adjustment
        soc_adjustment = self._calculate_soc_adjustment()

        # Valley ascent adjustment
        valley_adjustment = self._calculate_valley_ascent_adjustment(current_scarindex)

        # Combine adjustments
        final_guidance = base_guidance * (1.0 + soc_adjustment + valley_adjustment)
        final_guidance = np.clip(final_guidance, self.min_guidance, self.max_guidance)

        self.guidance_scale = final_guidance

        # Persist SOC state to Supabase
        try:
            from core.db import get_supabase
            from datetime import datetime, timezone
            supabase = get_supabase()
            
            soc_status = {
                "base_guidance": base_guidance,
                "soc_adjustment": soc_adjustment,
                "valley_adjustment": valley_adjustment,
                "final_guidance": final_guidance,
                "soc_metrics": self.soc_metrics.to_dict(),
                "valley_state": self.valley_ascent.to_dict(),
            }
            
            supabase.table("coherence_signals").insert({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scarindex_value": current_scarindex,
                "panic_frame_triggered": False, # Managed by ScarIndex/PanicFrameManager
                "control_action_taken": "SOC_ADJUSTMENT",
                "signal_data": soc_status
            }).execute()
            
        except Exception as e:
            # Log but don't fail
            print(f"Failed to persist SOC state: {e}")

        return final_guidance, {
            "base_guidance": base_guidance,
            "soc_adjustment": soc_adjustment,
            "valley_adjustment": valley_adjustment,
            "final_guidance": final_guidance,
            "soc_metrics": self.soc_metrics.to_dict(),
            "valley_state": self.valley_ascent.to_dict(),
        }

    def _calculate_soc_adjustment(self) -> float:
        """
        Calculate SOC-based adjustment to guidance scale

        If τ < target: Increase instability (higher guidance)
        If τ > target: Decrease instability (lower guidance)
        """
        if self.soc_metrics.tau == 0:
            return 0.0

        tau_error = self.target_tau - self.soc_metrics.tau

        # Proportional adjustment based on τ error
        soc_adjustment = tau_error * 0.2  # Tuning factor

        return soc_adjustment

    def _calculate_valley_ascent_adjustment(self, current_scarindex: float) -> float:
        """
        Calculate valley ascent adjustment

        Implements controlled coherence dips to escape local optima.
        """
        # Detect local optima (coherence plateau)
        if len(self.error_history) >= 10:
            recent_errors = self.error_history[-10:]
            error_variance = np.var(recent_errors)

            # Low variance + non-zero error = local optimum
            if error_variance < 0.001 and abs(self.error) > 0.05:
                self.valley_ascent.local_optima_detected = True
                self.valley_ascent.global_maximum_estimate = current_scarindex + abs(self.error)

        # If local optimum detected and not already descending, initiate descent
        if (
            self.valley_ascent.local_optima_detected and not self.valley_ascent.in_descent and current_scarindex > 0.5
        ):  # Safety: don't descend if already low

            self.valley_ascent.in_descent = True
            self.valley_ascent.descent_start_scarindex = current_scarindex
            self.valley_ascent.ascent_target = self.valley_ascent.global_maximum_estimate

        # During descent: temporarily increase guidance to induce coherence dip
        if self.valley_ascent.in_descent:
            self.valley_ascent.descent_depth = self.valley_ascent.descent_start_scarindex - current_scarindex

            # Check if descent complete
            if self.valley_ascent.descent_depth >= self.valley_ascent.max_descent_depth:
                # Switch to ascent
                self.valley_ascent.in_descent = False
                self.valley_ascent.local_optima_detected = False
                return -0.3  # Reduce guidance to allow recovery

            # Continue descent
            return 0.5  # Increase guidance to induce dip

        # During ascent: monitor progress toward global maximum
        if not self.valley_ascent.in_descent and self.valley_ascent.ascent_target > 0:

            self.valley_ascent.ascent_progress = (current_scarindex - self.valley_ascent.descent_start_scarindex) / (
                self.valley_ascent.ascent_target - self.valley_ascent.descent_start_scarindex
            )

            # If reached target, reset
            if current_scarindex >= self.valley_ascent.ascent_target:
                self.valley_ascent.ascent_target = 0.0
                self.valley_ascent.ascent_progress = 0.0

        return 0.0

    def adjust_paradox_parameters(self) -> Dict[str, float]:
        """
        Dynamically adjust Paradox Agent parameters based on SOC state

        Returns:
            Updated paradox parameters
        """
        # If below criticality, increase paradox intensity
        if self.soc_metrics.tau < self.target_tau:
            self.paradox_intensity = min(1.0, self.paradox_intensity + 0.1)
            self.paradox_frequency = min(0.5, self.paradox_frequency + 0.05)

        # If above criticality, decrease paradox intensity
        elif self.soc_metrics.tau > self.target_tau:
            self.paradox_intensity = max(0.1, self.paradox_intensity - 0.1)
            self.paradox_frequency = max(0.01, self.paradox_frequency - 0.05)

        return {"paradox_intensity": self.paradox_intensity, "paradox_frequency": self.paradox_frequency}

    def calculate_complexity_fitness(self, scarindex: float, tau: float, residue: float) -> float:
        """
        Calculate fitness function balancing coherence and complexity

        Shifts from pure coherence maximization to complexity maximization.

        Args:
            scarindex: Current ScarIndex
            tau: Current power-law exponent
            residue: Current residue level

        Returns:
            Composite fitness score
        """
        # Coherence component
        coherence_fitness = scarindex

        # Complexity component (proximity to critical τ)
        tau_error = abs(tau - self.target_tau)
        complexity_fitness = 1.0 / (1.0 + tau_error)

        # Residue penalty
        residue_penalty = 1.0 / (1.0 + residue)

        # Weighted combination
        fitness = (
            (1.0 - self.complexity_weight) * coherence_fitness + self.complexity_weight * complexity_fitness
        ) * residue_penalty

        return fitness

    def get_soc_status(self) -> Dict:
        """Get comprehensive SOC controller status"""
        base_status = self.get_state().to_dict()

        soc_status = {
            **base_status,
            "soc_metrics": self.soc_metrics.to_dict(),
            "valley_ascent": self.valley_ascent.to_dict(),
            "paradox_parameters": {"intensity": self.paradox_intensity, "frequency": self.paradox_frequency},
            "complexity_weight": self.complexity_weight,
            "target_tau": self.target_tau,
        }

        return soc_status


# Example usage
def example_soc_pid():
    """Example of SOC PID Controller"""
    print("=" * 70)
    print("Self-Organized Criticality PID Controller")
    print("=" * 70)
    print()

    controller = SOCPIDController(target_scarindex=0.7, target_tau=1.5, kp=1.0, ki=0.5, kd=0.2)

    print(f"Target ScarIndex: {controller.target_scarindex}")
    print(f"Target τ (tau): {controller.target_tau}")
    print()

    # Simulate system evolution
    print("Simulating system evolution toward SOC...")
    print("-" * 70)

    current_scarindex = 0.5

    for step in range(100):
        # Simulate event size (power-law distributed)
        event_size = np.random.pareto(1.5) + 1.0

        # Update with SOC awareness
        guidance, soc_state = controller.update_soc(current_scarindex, event_size)

        # Simulate system response
        current_scarindex += (controller.target_scarindex - current_scarindex) * 0.1
        current_scarindex += np.random.normal(0, 0.02)  # Noise
        current_scarindex = np.clip(current_scarindex, 0.0, 1.0)

        # Print status every 20 steps
        if step % 20 == 0:
            print(f"\nStep {step}:")
            print(f"  ScarIndex: {current_scarindex:.4f}")
            print(f"  Guidance: {guidance:.4f}")
            print(f"  τ (tau): {soc_state['soc_metrics']['tau']:.4f}")
            print(f"  Critical: {soc_state['soc_metrics']['is_critical']}")
            print(f"  Valley Descent: {soc_state['valley_state']['in_descent']}")

    # Final status
    print("\n" + "=" * 70)
    print("Final SOC Status")
    print("=" * 70)

    status = controller.get_soc_status()

    print(f"\nScarIndex: {current_scarindex:.4f}")
    print(f"Target: {status['target_scarindex']:.4f}")
    print(f"Error: {status['error']:.4f}")

    print("\nSOC Metrics:")
    print(f"  τ (tau): {status['soc_metrics']['tau']:.4f}")
    print(f"  Target τ: {status['target_tau']:.4f}")
    print(f"  Critical: {status['soc_metrics']['is_critical']}")
    print(f"  Distance from criticality: {status['soc_metrics']['distance_from_criticality']:.4f}")

    print("\nParadox Parameters:")
    print(f"  Intensity: {status['paradox_parameters']['intensity']:.4f}")
    print(f"  Frequency: {status['paradox_parameters']['frequency']:.4f}")

    # Calculate complexity fitness
    fitness = controller.calculate_complexity_fitness(
        scarindex=current_scarindex, tau=status["soc_metrics"]["tau"], residue=0.1
    )
    print(f"\nComplexity Fitness: {fitness:.4f}")


if __name__ == "__main__":
    example_soc_pid()
